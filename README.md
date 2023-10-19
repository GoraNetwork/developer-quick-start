# Gora developer quick start package

This repository is intended to help developers writing their first blockchain
application using Gora decentralized oracle. Here you will find:

 * Example application that can be used as a template
 * Step-by-step instructions on how to deploy and test it
 * Info on commands and tools for troubleshooting your Gora applications

## Prerequisites and environment

There are three essential pieces to form a Gora development environment:

 * An Algorand node, providing a local simulated Algorand network
 * Gora smart contracts deployed to this network
 * A Gora node instance, running and connected to the above

All instructions are written and tested for Linux. Mac users have reported
success with most of the tools used here and are welcome to follow this guide
at their own risk.

### Algorand software

The following Algorand software must be installed and functioning:

 * [Algorand Sandbox](https://github.com/algorand/sandbox "Algorand Sandbox GitHub page").
 * [Algorand Beaker framework](https://github.com/algorand-devrel/beaker "Algorand Beaker GitHub page")

You may use Algokit (Algorand's simplified environment setup tool) to bootstrap
and manage the above, but it will not be covered here. Algorand Sandbox must run
a local Algorand network which is its default mode of operation. But make sure
not to start it on testnet or devnet unintentionally.

There are two modes in which Algorand Sandbox can run a local network: with
transactions confirmed on time period basis, or with instant confirmation of
each transaction in its own round. The second mode speeds up development cycle
significantly, and is therefore recommended. To start it, run `sandbox up dev`
in sandbox directory.

### Gora software

Both Gora smart contracts and Gora node are managed with Gora CLI tool.
It is available for download here: https://download.goracle.io/latest-release/
Once downloaded, it must be made executable by running `chmod +x ./goracle`. 
Running it without arguments will list available commands. To get help on a
command's options, run `goracle help <command name>`, e.g. `goracle help docker-start`.

**Warning** Do NOT follow normal Gora node setup process for node operators.
A node for local development node must not connect to the public Gora network.

### Gora node

## Example app

The example app [example_const.py](https://github.com/GoraNetwork/developer-quick-start/blob/main/example_const.py "Example app on Github")
demonstrates the use or Gora decentralized oracle with a test oracle source.
That source is built into Gora and always returns the value of `1`, allowing
for reliable testing and minimal support code. Once the user understands this
example app and can execute it successfully in their development environment,
they should be all set for extending it to query other Gora sources in their
own custom apps.

The example app is built with Algorand's [Beaker framework](https://algorand-devrel.github.io/beaker/html/index.html "Official Beaker documentation")
and is extensively commented to make it accessible for novice developers.

Be advised that the way you build your applications with Beaker changed at one
point, replacing Python subclassing with decorators as means of adding custom
functionality. If you are using additional Beaker documentation or examples,
make sure that they are current.

## Deployment and testing

## Troubleshooting
