# Gora Developer Quick Start for EVM-compatible blockchains

Here you will find examples and support tools for developing smart contracts with
[Gora](https://gora.io/) on [Base](https://base.org/) and potentially other
EVM-compatible blockchains.

> [!NOTE]
> For developing *Algorand* applications and for general information on Gora
> Developer Quick Start, go [here](../README.md).

## Included Solidity examples

The following extensively commented examples are provided as hands-on
documentation and possibly templates for your own  applications:

 * [`example_basic.sol`](./example_basic.sol "Example app on Github")
   - getting data from a public JSON API
 * [`example_off_chain.sol`](./example_off_chain.sol "Example app on Github")
   - getting data from multiple APIs and processing it with off-chain computation

## Instant start for experienced Solidity developers

> [!CAUTION]
> If you are not too experienced with Solidity, or just want to run Gora examples
> or experiment modifying them, please skip to the next section.

Consider source code examples linked above. For deployment, supply *Gora main
smart contract address* as the first argument to the constructor, depending on
the public network you are deploying to:

  * Base Sepolia: `0xcb201275cb25a589f3877912815d5f17f66d4f13`
  * Base Mainnet: `0xd4c99f88095f32df993030d9a6080e3be723f617`

Once you deploy your smart contract, you should be ready to issue Gora requests
and receive Gora responses. For Base Sepolia, there is currently no fee for
Gora requests. But for Base Mainnet, you must ensure you have some Gora tokens
on the querying account's balance to pay for them.

> [!NOTE]
> To develop your own applications with Gora and to deploy them to production
> networks, you are expected to use tools of your own choice. Gora does not try
> to bind you to any specific EVM toolchain.

## Setting up local development environment

Following the steps below will set you up with a complete environment for
compiling and deploying Gora smart contract examples.

* **Repository cloning and prerequisites**

  * Ensure that you are running Linux by executing: `uname`. This should print
    out: `Linux`.
  * Check out the developer quick start repository by running:
    ```
    git clone https://github.com/GoraNetwork/developer-quick-start
    ```
  * Change to `evm` subdirectory and install NPM dependencies:
    ```
    cd developer-quick-start/evm
    npm i
    ```

 * **Target blockchain network**

   *This package can deploy and run examples using its local built-in blockchain
   network, or a public network such as [Base Sepolia](https://sepolia.basescan.org/).
   We generally recommend using the local network for development and trying things
   out. But for users who do not want to install [Docker](https://docker.io/), have
   a funded public network account and are OK with longer deploy/test iterations,
   the public network option may be preferable.*

## Using a public EVM network such as Base

Public network

Gora smart contract addresses for Base mainnet and testnet networks are as follows:

 * Base mainnet: `0xd4c99F88095F32dF993030d9a6080e3BE723F617`
 * Base Sepolia testnet: `0xcB201275Cb25A589f3877912815d5f17f66D4f13`

 For deployment to public blockchain networks, Gora does not require any specific
 toolchain. Smart contract addresses listed above and the knowledge of basic
 APIs given in the examples is all you need to start using Gora with EVM
 development tools of your choice.

 To learn how to use Gora from your smart contracts, it is best to read
 extensively commented Solidity examples in this repository:

 * [`example_basic.sol`](https://github.com/GoraNetwork/developer-quick-start/blob/main/evm/example_basic.sol "Example app on Github")
 * [`example_off_chain.sol`](https://github.com/GoraNetwork/developer-quick-start/blob/main/evm/example_off_chain.sol "Example app on Github")

 You should then be able to integrate Gora calls and response handling into your
 smart contracts with ease. If you would like to run the examples or debug your
 Gora applications locally, read on.

## Setting up your Gora EVM development environment

 * Check the prerequisites:
   ```
   uname
   ```
   should print out `Linux`. Make sure you have [Docker](https://docker.com/).
   installed. Your Libc version version must be at least `2.32` which can be
   checked by executing `/lib/libc.so.6`. If it is older, please upgrade your
   OS.

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

### Off-chain computation example: [`example_off_chain.sol`](https://github.com/GoraNetwork/developer-quick-start/blob/main/evm/example_off_chain.sol "Example app on Github")

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

 * Gora smart contracts (files with `.compiled` extension), already compiled
   into combined JSON format.

`start_dev_env` script starts Geth instance, deploys Gora smart contracts and
stays in the foreground, displaying log messages from the above as they come.
Contrary to Gora Developer Quick Start package for Algorand, it must be running
at all times to run Gora smart contracts locally. There is no way to start a
Gora node or its local blockchain on-demand on per-example basis.  To end your
development session and terminate the script, hit Ctrl-C in the terminal window
running it.
