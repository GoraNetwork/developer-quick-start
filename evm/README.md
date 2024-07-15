# Gora developer quick start package for Ethereum

Here you will find examples and support tools for developing smart contracts with
Gora on EVM networks. For general information on Gora Developer Quick Start
package as well as on developing Algorand applications, go [here](https://github.com/GoraNetwork/developer-quick-start/README.md).
EVM Gora examples are modelled after Algorand Gora examples, but the toolset and
execution workflow differ.

## Setting up your Gora EVM development environment

Gora EVM development environment relies on the following pieces of software:

 * Solidity compiler (`solc` binary). Used to compile examples and potentially
   developer's own code.

 * Geth EVM node software (`geth` binary). Provides local blockchain
   functionality to model master (L1) and slave (L2) EVM networks. Both
   instances of Geth are run in development mode (with `--dev` switch).
   Hardhat is not used because it has shown issues with multiple concurrent
   connections and was lagging behind recent Ethereum forks feature-wise.

 * Mock Axelar cross-chain bridge (`axelar_relayer.js`). Relays cross-chain
   messages between local master and slave networks provided by Geth.
   The script is essentially a wrapper client written by Gora around Axelar
   local development API.

 * Gora smart contracts (files with `.compiled` extension), already compiled
   into combined JSON format.

These are included in this repository, but the NPM modules required to run the
Axelar bridge locally need to be installed by running:
```
npm i @axelar-network/axelar-local-dev
```

Once the modules install correctly, you should be able to activate your
development environment by running:
```
./start_dev_env.sh
```

This script will start Geth instances and the Axelar relayer, deploy Gora
smart contracts and stay in the foreground, displaying log messages from the
above as they come. Contrary to Gora Developer Quick Start package for Algorand,
it must be running at all times to run Gora smart contracts locally. There is no
way to start a Gora node or its local blockchain on-demand on per-example
basis. To end your development session and terminate the script, hit Ctrl-C in
the terminal window running it.

## Running examples or your own code

Examples are provides as Solidity source code files which are compiled and
deployed every time they are run.

### Basic example: [`example_basic.sol`](https://github.com/GoraNetwork/developer-quick-start/blob/main/evm/example_basic.sol "Example app on Github")

Demonstrates the use of Gora for querying arbitrary HTTP endpoints responding in
JSON format. <http://jsontest.com> free public website is used as the test data
provider, so Internet connection is required to run this example.

### Off-chain computation example: [`example_off_chain.sol`](https://github.com/GoraNetwork/developer-quick-start/blob/main/evm/example_offchain.sol "Example app on Github")

Demonstrates Gora's arbitrary off-chain computation capability. Essentially
identical to the Off-chain computation example for Gora on Algorand.

## Troubleshooting

Gora troubleshooting tools for EVM chains are not yet as developed as for Algorand,
but they are catching up. Currently you can use CLI `inspect` command to display
details of past Gora reques(s) still stored on blockchain, e.g.:
```
gora inspect --evm-network default --rounds 32
```
will display all requests commited in round 32. Specifying round ranges or
request IDs is possible, run `gora help inspect` for details. Please be aware,
however, that once the development environment is stopped, all data on the
local blockchains is lost.