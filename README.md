# Gora developer quick start package

This repository is intended to help developers writing their first blockchain
application using Gora decentralized oracle. Here you will find:

 * Example application that can be used as a template
 * Step-by-step instructions on how to deploy and test it
 * Info on commands and tools for troubleshooting your Gora applications

All instructions are written and tested for Linux. Mac users have reported
success with most of the tools used here and are welcome to follow this guide
at their own risk. The reader must be comfortable with using command-line
tools, the Algorand blockchain and Python programming.

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

You may use Algokit (Algorand's simplified environment setup tool) to bootstrap
and manage the above. Algorand Sandbox must run a local Algorand network. This
is its default mode of operation, but make sure not to start it on testnet or
devnet unintentionally.

There are two modes in which Algorand Sandbox can run a local network: with
transactions confirmed on time period basis, or with instant confirmation of
each transaction in its own round. The second mode speeds up development cycle
significantly, and is therefore recommended. To start it, run `sandbox up dev`
in sandbox directory. Be advised that Algorand Indexer may not work in this
mode, but it is not required for Gora development.

To check that an Algorand development node is up and running on your host, execute:
`curl http://localhost:4001/versions`. You should get a JSON response with
version information fields, including `"genesis_id":"sandnet-v1"`.

### Gora software

Both Gora smart contracts and Gora node are managed with Gora CLI tool.
It is available for download here: https://download.goracle.io/latest-release/
Once downloaded, it must be made executable by running `chmod +x ./goracle`. 

Running the CLI tool without arguments will list available commands. To get help on a
command, run `goracle help <command name>`, for example: `goracle help docker-start`.

**Warning** Do NOT follow normal Gora node setup process for node operators, it
is essentially different.

### Gora node

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

## Deployment and testing

## Troubleshooting
