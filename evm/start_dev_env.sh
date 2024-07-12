#!/bin/bash

NODE_BIN=/usr/bin/node
GETH_BIN=./geth

MASTER_ADDR=$(cat ./master_addr.txt)
NODE_STAKE=10000

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
$NODE_BIN ./axelar_relayer.js >$AXELAR_LOG 2>&1 &
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

# Configure and start local Gora node.
GORA_DEV_CLI_TOOL="${GORA_DEV_CLI_TOOL:-../gora_cli}"
export GORA_CONFIG_FILE='./.gora'
export GORA_CONFIG="
{
  \"blockchain\": {
    \"evm\": {
      \"networks\": {
        \"ethereumSepolia\": null,
        \"baseSepolia\": null,
        \"default\": {
          \"type\": \"testnet\",
          \"slave\": \"slave\",
          \"disableVrfCounting\": true,
          \"server\": \"$GETH_URL_default\",
          \"mainContract\": \"$(cat ./main_default.addr)\",
          \"privKey\": \"$(cat ./master_key.txt)\"
        },
        \"slave\": {
          \"type\": \"testnet\",
          \"disableVrfCounting\": true,
          \"server\": \"$GETH_URL_slave\",
          \"mainContract\": \"$(cat ./main_slave.addr)\",
          \"privKey\": \"$(cat ./master_key.txt)\"
        }
      }
    }
  },
  \"deployment\": {
    \"id\": \"gora-nr-dev\",
    \"logLevel\": 5,
    \"stackTrace\": 1
    $GORA_DEV_EVM_CONFIG_DEPL_EXTRA
  }
}
"
echo "Setting devlopment node's stake"
$GORA_DEV_CLI_TOOL evm-set --network default --setup-master-slave \
                   --stake $NODE_STAKE

GORA_LOG=./gora.log
LOGS+=" $GORA_LOG"
$GORA_DEV_CLI_TOOL docker-start >$GORA_LOG 2>&1 &
PIDS+=" $!"

echo "-----------------------------------------------------------------------------"
echo "Tailing log files, Ctrl-C to stop and terminate all child processes"
echo "-----------------------------------------------------------------------------"
tail -n +1  -F $LOGS
killall $CHILD_PIDS
