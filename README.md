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
setup of Gora software. You may need to enter it if it differs from `4001`.

**Warning!*** By default, Algorand Sandbox runs its local network automatically
confirming new transactions on time period basis. This is currently the
recommended mode for Gora development. The "dev" mode of Algorand Sandbox which
confirms every transaction instantly and places it in its own round is not
supported by Gora. It is incompatible with security mechanisms of Gora smart
contracts.

### Gora software

To install and configure Gora software for the development environment, run
`python3 setup.py` and follow the prompts. Gora tools will be downloaded and
config files created for you automatically in the checkout directory.
**Warning!** *Do NOT follow normal Gora node setup process.*

When the above script finishes, you should have Gora smart contracts deployed to
local network in your Algorand Sandbox install, as well as Gora node
configuration to use it. It will form a local development single-node Gora
network necessary to serve locally tested applications. For it to work, this
Gora node must be running when an application request is made. The demo
applications in this repository ensure this by running the node temporarily if
it is not already executing. To test your own applications, you should run
the node continuously. To start it with log output to the terminal, change to
the checkout directory and run: `GORACLE_CONFIG_FILE=./.goracle ./goracle docker-start`.
To make it run in background, add `--background` switch to the above command;
to see node's messages, run `docker logs goracle-nr-dev`.

**Warning!** *Do not add more nodes to this setup as it can break oracle
consensus and stop request processing.*

## Example apps

This repository includes several example [PyTeal](https://pyteal.readthedocs.io/en/stable/ "PyTeal official website")
applications demonstrating the use of Gora oracle. They will be considered below
more or less in the order of complexity.

### Basic example

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
