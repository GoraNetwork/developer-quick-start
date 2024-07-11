#!/bin/bash

NODE_BIN=/usr/bin/node
GETH_BIN=./geth

MASTER_ADDR=$(cat ./master_addr.txt)

GETH_HOST=http://localhost
GETH_PORT_default=8546
GETH_PORT_slave=8547
GETH_URL_default=$GETH_HOST:$GETH_PORT_default
GETH_URL_slave=$GETH_HOST:$GETH_PORT_slave

FUND_AMOUNT=2000
FUND_DELAY=2
FUND_CODE="eth.sendTransaction({from: eth.accounts[0], to: \"$MASTER_ADDR\", value: web3.toWei($MASTER_ADDR, \"ether\")})"

echo 'Preparing Gora local EVM development environment'

for CHAIN in 'default' 'slave'; do

  GETH_PORT_VAR="GETH_PORT_$CHAIN"
  export GETH_HTTP_PORT=${!GETH_PORT_VAR} # must export for geth to pick up
  GETH_URL="$GETH_HOST:$GETH_HTTP_PORT"
  GETH_LOG="geth_$CHAIN.log"

  echo "Starting $GETH_BIN on $GETH_URL, see $GETH_LOG for saved output"
  $GETH_BIN --dev --http --ipcdisable >$GETH_LOG 2>&1 &
  CHILD_PIDS+=" $!"
  LOGS+=" ./$GETH_LOG"

  sleep $FUND_DELAY
  echo "Funding '$MASTER_ADDR' with '$FUND_AMOUNT'"
  $GETH_BIN --vmdebug --verbosity 5 --exec "$FUND_CODE" attach $GETH_URL

done

AXELAR_LOG=axelar.log
echo "Starting local Axelar relayer, see $AXELAR_LOG for saved output"
$NODE_BIN ./mock_axelar.js >$AXELAR_LOG 2>&1 &
CHILD_PIDS+=" $!"
LOGS+=" ./$AXELAR_LOG"

sleep 5

echo "Deploying Gora smart contracts"
export GORA_DEV_EVM_DEPLOY_KEY=./master_key.txt

GORA_DEV_EVM_DEPLOY_CONSTR_ARG_0=$MASTER_ADDR \
GORA_DEV_EVM_DEPLOY_CONSTR_ARG_1="GORA token" \
GORA_DEV_EVM_DEPLOY_CONSTR_ARG_2=GORA \
  $NODE_BIN ./deploy.js $GETH_URL_default \
          token token_default.addr GoraToken.sol
echo 0x0000000000000000000000000000000000000000 > token_slave.addr

for CHAIN in 'default' 'slave'; do
  GETH_URL_VAR="GETH_URL_$CHAIN"
  $NODE_BIN ./deploy.js ${!GETH_URL_VAR} vrf_lib vrf_lib_$CHAIN.addr
  GORA_DEV_EVM_DEPLOY_CONSTR_ARG_0=$(cat ./vrf_lib_$CHAIN.addr) \
  GORA_DEV_EVM_DEPLOY_CONSTR_ARG_1=$(cat ./token_$CHAIN.addr) \
  GORA_DEV_EVM_DEPLOY_CONSTR_ARG_2=$(cat ./axelar_gw_$CHAIN.addr) \
  GORA_DEV_EVM_DEPLOY_CONSTR_ARG_3=$(cat ./axelar_gas_$CHAIN.addr) \
    $NODE_BIN deploy.js ${!GETH_URL_VAR} main main_$CHAIN.addr
done

echo "--------------------------------------------------------------------------------"
echo "Tailing log files, Ctrl-C to stop and terminate all child processes"
echo "--------------------------------------------------------------------------------"
tail -F $LOGS
killall $CHILD_PIDS
