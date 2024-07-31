# Gora developer quick start package for Ethereum

Here you will find examples and support tools for developing smart contracts with
Gora on EVM networks. For general information on Gora Developer Quick Start
package as well as on developing Algorand applications, go [here](https://github.com/GoraNetwork/developer-quick-start/README.md).
EVM Gora examples are modelled after Algorand Gora examples, but the toolset and
execution workflow differ.

## Setting up your Gora EVM development environment

 * Check out the developer quick start repository by running:
   ```
   git clone https://github.com/GoraNetwork/developer-quick-start
   ```

 * Change to EVM subdirectory and install the NPM dependencies:
   ```
   cd developer-quick-start/evm
   npm i
   ```
 * Start the development environment by running the command below. It must
   be left running for the duration of your development session. To terminate
   it hit, Ctrl-C.
   ```
   ./start_dev_env
   ```

## Running examples or your own code

To run the included examples, open another terminal window and change
to the same directory in which you ran the setup script above. Then run:
```
./run_example basic
```
or
```
./run_example off_chain
```

This should compile, deploy and run the examples, providing detailed information
on the outcome. Examples are provided as commented Solidity source code and can
be used as tests or templates for your own apps.

### Basic example: [`example_basic.sol`](https://github.com/GoraNetwork/developer-quick-start/blob/main/evm/example_basic.sol "Example app on Github")

Demonstrates the use of Gora for querying arbitrary HTTP endpoints responding in
JSON format. <http://jsontest.com> free public website is used as the test data
provider, so Internet connection is required to run this example.

### Off-chain computation example: [`example_off_chain.sol`](https://github.com/GoraNetwork/developer-quick-start/blob/main/evm/example_offchain.sol "Example app on Github")

Demonstrates Gora's arbitrary off-chain computation capability. Essentially
identical to the Off-chain computation example for Gora on Algorand.

## Composition of the development environment

Gora EVM development environment relies on the following pieces of software:

 * Solidity compiler (`solc` binary). Used to compile examples and potentially
   developer's own code.

 * Geth EVM node software (`geth` binary). Provides local blockchain
   functionality to model master (L1) and slave (L2) EVM networks. Both
   instances of Geth are run in development mode (with `--dev` switch).
   Hardhat is not used because it has shown issues with multiple concurrent
   connections and was lagging behind recent Ethereum forks feature-wise.

 * Mock Axelar cross-chain bridge (`axelar_relayer`). Relays cross-chain
   messages between local master and slave networks provided by Geth.
   The script is essentially a wrapper client written by Gora around Axelar
   local development API.

 * Gora smart contracts (files with `.compiled` extension), already compiled
   into combined JSON format.

`start_dev_env` script starts Geth instances and the Axelar relayer, deploys Gora
smart contracts and stays in the foreground, displaying log messages from the
above as they come. Contrary to Gora Developer Quick Start package for Algorand,
it must be running at all times to run Gora smart contracts locally. There is no
way to start a Gora node or its local blockchain on-demand on per-example basis.
To end your development session and terminate the script, hit Ctrl-C in the
terminal window running it.
