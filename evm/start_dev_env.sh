#!/bin/bash

GETH_BIN=./geth
MASTER_ADDR=$(cat ./master_addr.txt)

FUND_AMOUNT=2000
FUND_DELAY=2
FUND_CODE="eth.sendTransaction({from: eth.accounts[0], to: \"$MASTER_ADDR\", value: web3.toWei($MASTER_ADDR, \"ether\")})"

for GETH_HTTP_PORT in 8546 8547; do

  GETH_URL="http://localhost:$GETH_HTTP_PORT"
  export GETH_HTTP_PORT

  GETH_LOG="geth_$GETH_HTTP_PORT.log"
  echo "Starting $GETH_BIN on $GETH_URL, see $GETH_LOG for output"
  $GETH_BIN --dev --http --ipcdisable >$GETH_LOG 2>&1 &

  sleep $FUND_DELAY
  echo "Funding address '$MASTER_ADDR' with amount '$FUND_AMOUNT'"
  $GETH_BIN --vmdebug --verbosity 5 --exec "$FUND_CODE" attach $GETH_URL
  echo 'Done'

done