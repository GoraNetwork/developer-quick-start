# Gora developer quick start package

This repository is intended to help developers writing their first blockchain
application using Gora decentralized oracle. Here you will find:

 * Example application that can be used as a template
 * Step-by-step instructions on how to deploy and test it
 * Info on commands and tools for troubleshooting your Gora applications

All instructions here are written and tested for Linux. Mac users have reported
success with most of the tools used here and are welcome to follow this guide at
their own risk. The reader must be comfortable with using command-line tools,
the Algorand blockchain and Python programming.

## Prerequisites and environment

There are four essential pieces to form a Gora development environment:

 * An Algorand node, providing a local simulated Algorand network
 * Algorand Python toolset for smart contracts and external blockchain interaction
 * Gora smart contracts deployed to this network
 * A Gora node instance, running and connected to the above

### Algorand software

The following Algorand software must be installed and functioning:

 * [Algorand Sandbox](https://github.com/algorand/sandbox "Algorand Sandbox GitHub page").
 * [Algorand Beaker framework](https://github.com/algorand-devrel/beaker "Algorand Beaker GitHub page")

Refer to documentation at the above links for download and installation
instructions. If using a different package to setup your Algorand node, such as
AlgoKit, find out its Algod API connection port number and have it handy during
setup of Gora software as you may need to override the default value of `4001`.

**Warning!*** By default, Algorand Sandbox runs its local network automatically
confirming new transactions on time period basis. This is currently the
recommended mode for Gora development. The "dev" mode of Algorand Sandbox which
confirms every transaction instantly and places it in its own round is not
supported by Gora. It is incompatible with security mechanisms of Gora smart
contracts.

### Gora software

Both Gora smart contracts and Gora node are managed with Gora CLI tool.
Download it [here](https://download.goracle.io/latest-dev/linux/goracle "Gora CLI tool Linux binary"),
then make it executable by running `chmod +x ./goracle`.  Running the CLI tool
without arguments will list available commands. To get help on a command, run
`./goracle help <command name>`, for example: `./goracle help docker-start`.

**Warning!** Do NOT follow normal Gora node setup process for live network
operators when setting up a development node.

To set up your development node, run: `GORACLE_CONFIG_FILE= ./goracle dev-init`.
This would clone Gora smart contracts from testnet to your local Algorand
Sandbox network and create a config file for your development node. By default,
this file is called `~/.goracle_dev`. Now you should be ready to start your
development node as: `GORACLE_CONFIG_FILE=~/.goracle_dev ./goracle docker-start`.

This will form a single-node Gora network for local end-to-end testing of your
applications. This node will pick up your local Gora requests and process them
like a production network would, logging various debugging information to
standard output.

**Warning!** do not stop the node. You must have your development node up and
running to process requests from the example app or from any Gora-enabled apps
which you will be developing locally.

## Example app

The example app [example_const.py](https://github.com/GoraNetwork/developer-quick-start/blob/main/example_const.py "Example app on Github")
demonstrates the use of Gora with a test oracle source. That source is built
into Gora and always returns the value of `1`, allowing for reliable testing and
minimal support code. Once the user understands this example app and can execute
it successfully in their development environment, they should be all set for
extending it to query other Gora sources in their own custom apps.

The example app is built with Algorand's [Beaker framework](https://algorand-devrel.github.io/beaker/html/index.html "Official Beaker documentation")
and is extensively commented to make it accessible for novice developers.

Be advised that the way you build your applications with Beaker changed at one
point, replacing Python subclassing with decorators as means of adding custom
functionality. If you are using additional Beaker documentation or examples,
make sure that they are current.

To run the example app, you must to point it to your local Gora network via
environment variables. Check output of your Gora development node for messages
like: `Main smart contract: "<number>"`, `Token asset ID: "<number>"`.
These contain values defining your local Gora development network. Now you can
use them to execute the example app:
`GORA_TOKEN_ASSET_ID=<token asset ID> GORA_MAIN_APP_ID=<main app ID> python3 example_const.py`

Once the app compiles and executes, the node should pick up its request, showing
a message like `Processing oracle request "<request ID>"`. When a message starting
with `Submitted <number> vote(s) on request "<request ID>"`appears, it means
that the request has been processed and the destination method app should have
been called with the response.

Algorand [Dapp Flow](https://app.dappflow.org/explorer/home) web app can be used
to trace applicable transactions and confirm that the destination call has been
made and values updated. **Warning!** You may get an error message from Dapp Flow about "disabled parameter:
application-id". This is a minor issue and should not affect operation.
