# Gora Developer Quick Start for EVM-compatible blockchains

Here you will find examples and support tools for developing smart contracts with
[Gora](https://gora.io/) on [Base](https://base.org/) and potentially other
EVM-compatible blockchains.

> [!NOTE]
> *For developing Algorand applications and for general information on Gora
> Developer Quick Start, go [here](../README.md).*

## Included Solidity examples

The following extensively commented examples are provided as hands-on
documentation and potential templates for your own  applications:

 * [`example_basic.sol`](./example_basic.sol "Example app on Github") -
   querying arbitrary HTTP JSON endpoints

 * [`example_off_chain.sol`](./example_off_chain.sol "Example app on Github") -
   getting data from multiple APIs and processing it with off-chain computation

## Instant start for experienced Solidity developers

> [!CAUTION]
> *If you are not too experienced with Solidity, or just want to run Gora examples
> or experiment modifying them, please skip to the next section.*

Consider source code examples linked in the previous section. Integrate the APIs
exposed in them into your own smart contracts, or deploy an example using your
preferred setup, then modify it to build your app. For deployment, supply *Gora
main smart contract address* as the first argument to the constructor, depending
on the public network you are deploying to:

  * Base Sepolia: `0xcb201275cb25a589f3877912815d5f17f66d4f13`
  * Base Mainnet: `0xd4c99f88095f32df993030d9a6080e3be723f617`

Once deployed, your smart contract should be able ready to issue Gora requests
and receive Gora responses. For Base Sepolia, there is currently no fee for Gora
requests. For Base Mainnet, you must have some Gora tokens on the querying
account's balance to pay for requests.

> [!NOTE]
> *To develop your own applications with Gora and to deploy them to production
> networks, you are expected to use tools of your own choice. Gora does not try
> to bind you to any specific EVM toolchain.*

## Setting up local development environment

Following the steps below will set you up with a complete environment for
compiling and deploying Gora smart contract examples.

### 1. Check operating system compatibility

Open a terminal session and execute: `uname`. If this prints out `Linux`,
continue to the next step. If the output is anything else, you may proceed
at your own risk, but with a non-Unix OS you will almost certainly fail.

### 2. Clone this repository

Install [Git](https://git-scm.com/) if not already done so, then run:
```
$ git clone https://github.com/GoraNetwork/developer-quick-start
```
You should get an output like:
```
Cloning into 'developer-quick-start'...
remote: Enumerating objects: 790, done.
remote: Counting objects: 100% (232/232), done.
remote: Compressing objects: 100% (145/145), done.
remote: Total 790 (delta 156), reused 159 (delta 85), pack-reused 558 (from 1)
Receiving objects: 100% (790/790), 67.78 MiB | 1.43 MiB/s, done.
Resolving deltas: 100% (469/469), done.
$
```

### 3. Change to EVM subdirectory and install NPM dependencies

Execute the following two commands:
```
$ cd developer-quick-start/evm
$ npm i
```

You should then see something like this:
```
added 9 packages, and audited 10 packages in 3s
3 packages are looking for funding
  run `npm fund` for details
found 0 vulnerabilities
$
```

If no errors popped up, proceed to the next step.

###  4. Setup target blockchain network

> [!IMPORTANT]
> *Examples can be run on either local built-in blockchain network, or a public
> network such as [Base Sepolia](https://sepolia.basescan.org/). We generally
> recommend using the local network for development and trying things out. But
> for users who do not want to install [Docker](https://docker.io/), have a
> funded public network account and are OK with longer deploy/test iterations,
> the public network option may be preferable.*

#### Option 1: Use local development blockchain network

Run `./start_dev_env`. The script will start up, displaying log output from
local EVM nodes as well as local Gora node. It must be running while you deploy
and run the example scripts. It is the default configuration for running examples,
so no additional setup will be necessary. To terminate the script, ending the
development session, hit, `Ctrl-C`.

#### Option 2: Use a public network

Public network configuration is set via environment variables. For example,
to use Base Sepolia you would execute:
```
$ export GORA_EXAMPLE_EVM_MAIN_ADDR=0xcb201275cb25a589f3877912815d5f17f66d4f13
$ export GORA_EXAMPLE_EVM_API_URL=https://sepolia.base.org
$ export GORA_EXAMPLE_EVM_KEY=./my_base_sepolia_private_hex_key.txt
```
`./my_base_sepolia_private_hex_key.txt` is the example path to a text file
containing private key for the account you want to use for deployment,
in hex form. It can usually be found in account tools section of wallet
software such as Metamask.

The environment variables will be picked up by the example-running script
discussed below. It should be possible to deploy example scripts to any public
EVM network using this method. Deploying to a mainnets is, however, strongly
discouraged for security reasons.

## Running and modifying the examples

If using local development environment (option 1 in step 4 above), open another
terminal window and change to the same directory in which you started the setup
script. For public network configurtion (option 2 in step 4), please remain in
the same terminal session.

Then execute:
```
./run_example basic
```
or
```
./run_example off_chain
```

This should compile, deploy and run the example, providing detailed information
on the outcome. For further details, consider [Included Solidity examples](#included-solidity-examples)
section above. You are welcome to modify the examples source code and try it
repeating the step above.

## Composition of the development environment

Gora EVM local development environment relies on the following pieces of software:

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
