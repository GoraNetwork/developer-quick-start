#!/bin/bash

set -x

NODE_BIN=/usr/bin/node
GETH_BIN=./geth

NODE_STAKE=10000
GETH_HOST=http://localhost
GETH_PORT_default=8546
GETH_PORT_slave=8547
GETH_URL_default=$GETH_HOST:$GETH_PORT_default
GETH_URL_slave=$GETH_HOST:$GETH_PORT_slave

FUND_AMOUNT=200000
FUND_DELAY=2

echo 'Preparing Gora local EVM development environment'

for CHAIN in 'default' 'slave'; do

  MASTER_ADDR=$(cat ./master_addr_$CHAIN.txt)
  FUND_CODE="eth.sendTransaction({from: eth.accounts[0], to: \"$MASTER_ADDR\", value: web3.toWei($MASTER_ADDR, \"ether\")})"

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
$NODE_BIN ./axelar_relayer.js 250 \
          $GETH_URL_default $(cat ./master_key_default.txt) \
          $GETH_URL_slave $(cat ./master_key_slave.txt) \
          >$AXELAR_LOG 2>&1 &
CHILD_PIDS+=" $!"
LOGS+=" ./$AXELAR_LOG"

sleep 5

echo "Deploying Gora smart contracts"

export GORA_DEV_EVM_DEPLOY_KEY="./master_key_default.txt"
GORA_DEV_EVM_DEPLOY_CONSTR_ARG_0="$(cat ./master_addr_default.txt)" \
GORA_DEV_EVM_DEPLOY_CONSTR_ARG_1='GORA token' \
GORA_DEV_EVM_DEPLOY_CONSTR_ARG_2='GORA' \
  $NODE_BIN ./deploy.js "$GETH_URL_default" token token_default.addr GoraToken.sol
echo 0x0000000000000000000000000000000000000000 > token_slave.addr

for CHAIN in 'default' 'slave'; do
  export GORA_DEV_EVM_DEPLOY_KEY="./master_key_$CHAIN.txt"
  GETH_URL_VAR="GETH_URL_$CHAIN"
  GORA_DEV_EVM_DEPLOY_CONSTR_ARG_0=$(cat ./token_$CHAIN.addr) \
  GORA_DEV_EVM_DEPLOY_CONSTR_ARG_1=$(cat ./axelar_gw_$CHAIN.addr) \
  GORA_DEV_EVM_DEPLOY_CONSTR_ARG_2=$(cat ./axelar_gas_$CHAIN.addr) \
    $NODE_BIN deploy.js ${!GETH_URL_VAR} main main_$CHAIN.addr
done

# Configure and start local Gora node.
GORA_DEV_CLI_TOOL="${GORA_DEV_CLI_TOOL:-../gora_cli}"
export GORA_CONFIG_FILE='./.gora'
export GORA_CONFIG="
{
  \"blockchain\": {
    \"evm\": {
      \"networkDefaults\": {
        \"polling\": 500,
        \"voteEth\": 300000,
        \"stakeEth\": 300000
      },
      \"networks\": {
        \"default\": {
          \"type\": \"testnet\",
          \"slave\": \"slave\",
          \"server\": \"$GETH_URL_default\",
          \"mainContract\": \"$(cat ./main_default.addr)\",
          \"privKey\": \"$(cat ./master_key_default.txt)\"
        },
        \"slave\": {
          \"type\": \"testnet\",
          \"server\": \"$GETH_URL_slave\",
          \"mainContract\": \"$(cat ./main_slave.addr)\",
          \"privKey\": \"$(cat ./master_key_slave.txt)\"
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
echo "Setting up master/slave network info"
$GORA_DEV_CLI_TOOL evm-set --network default --update-master \
                   --setup-master-slave chain_0,chain_1
sleep 5

echo "Setting devlopment node's stake"
$GORA_DEV_CLI_TOOL evm-set --network default --stake $NODE_STAKE

GORA_LOG=./gora.log
LOGS+=" $GORA_LOG"
$GORA_DEV_CLI_TOOL docker-start >$GORA_LOG 2>&1 &
CHILD_PIDS+=" $!"

echo "-----------------------------------------------------------------------------"
echo "Tailing log files, Ctrl-C to stop and terminate all child processes"
echo "-----------------------------------------------------------------------------"
tail -n +1 -F $LOGS
kill $CHILD_PIDS
