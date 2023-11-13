# Gora developer quick start package

This repository is here to help developers writing their first blockchain
applications using Gora decentralized oracle.

Here you will find:

 * Instructions on how to setup and use a local Gora development environment
 * Example applications that can be used as templates
 * Info on commands and tools for troubleshooting your Gora applications

All instructions are written and tested on Linux. Mac users reported success
with most of the steps described here and are welcome to follow them at their
own risk. Readers must be comfortable with using command-line tools, the
Algorand blockchain and Python programming language.

## Setting up your Gora development environment

There are four essential pieces to a Gora development environment:

 * An Algorand node providing local simulated Algorand network
 * Algorand Python libraries for smart contracts and blockchain APIs
 * Deployed Gora smart contracts
 * A Gora development-only node running and connected to the above

### Algorand software

The following Algorand software must be installed and functioning:

 * [Algorand Sandbox](https://github.com/algorand/sandbox "Algorand Sandbox GitHub page").
 * [Algorand Beaker framework](https://github.com/algorand-devrel/beaker "Algorand Beaker GitHub page")

Refer to documentation at the above links for download and installation
instructions. If using a different package to setup your Algorand node, such as
AlgoKit, find out its Algod API connection port number and have it handy. If it
differs from `4001`, you will need to enter it during setup of Gora software.

**Warning!** *By default, Algorand Sandbox runs its local network automatically
confirming new transactions on time period basis. This is currently the
recommended mode for Gora app development. The "dev" mode of Algorand Sandbox which
confirms every transaction instantly and places it in its own round is not
currently supported. It is incompatible with security mechanisms of Gora smart
contracts.*

### Gora software

To install and configure Gora software for your development environment, run
`python3 setup.py` and follow the prompts. Gora tools will be downloaded and
config files created for you automatically in the checkout directory.
**Warning!** *Do NOT follow normal Gora node setup process.*

When the above script finishes, you will have Gora smart contracts deployed to
local network in your Algorand Sandbox install and a Gora node set up for them.
This will form a local development-only single-node Gora network necessary to
serve your locally tested applications.

For local oracle requests to be served, your development Gora node must be
running whenever they are made. There are two ways to ensure this. One is to run
it temporarily from a script that executes your application test cycle. This is
what example apps in this repository do; details can be gleaned from their
source code.  Another way is to run the node continuously for the duration of
your development session. To start it with output to the terminal, change to
the checkout directory and run: `GORACLE_CONFIG_FILE=./.goracle ./goracle
docker-start`.  To make it run in the background, add `--background` switch to the
above command; to see node's log messages, run `docker logs goracle-nr-dev`.

**Warning!** *Do not add more nodes with non-zero stakes to this setup. It can
break oracle consensus and stop request processing.*

## Example applications

This repository includes several example [PyTeal](https://pyteal.readthedocs.io/en/stable/ "PyTeal official website")
applications demonstrating the use of Gora oracle. They will be considered below
in the order of complexity. Example apps are built with Algorand's
[Beaker framework](https://algorand-devrel.github.io/beaker/html/index.html "Official Beaker documentation")
and are commented to make them accessible for novice developers.

**Warning!** *Algorand's Beaker framework was updated at one point to replace
Python subclassing with decorators as means of adding custom functionality. If
you are using additional Beaker documentation or examples, make sure that they
are current.*

To run an example app, execute it with Python, e.g. `python example_const.py`.
You should get an output like:
```
Loading config from "./.goracle"
Main app ID: 1004
Using local account ETKGKDOICCD7RQRX7TX24RAAM2WTHP7L4EGIORVLJEKZO7FWNY27RUTF3E
Deploying the app...
Done, txn ID: 3GH2465S6GPWRGHZQPHRQ7SHU7YOLXVPQVY64IJM2PVF4MSBM57A
App ID: 1280
App address: DPF45GKEB2H7P7HJNRHYNJXZTCSPWMLBIOFR5ZM6V2FJTPMNJ7C2VBQRHA
Token asset ID: 1003
Initializing app for GORA...
Setting up Algo deposit...
Setting up token deposit...
Calling the app
Confirmed in round: 16598
Top txn ID: USH3IB32OH5QQHGKHQGWLTW46QCOEKWQGCJ472G6FXG2VG2LLHPA
Running: "./goracle docker-status"
Background development Gora node not detected, running one temporarily
Running: "./goracle docker-start"
Goracle CLI tool, version N/A
goracle-nr-dev
2023-11-13T13:28:26.679Z DEBUG Applying GORACLE_CONFIG environment variable
2023-11-13T13:28:27.557Z INFO  Starting Goracle Node Runner
2023-11-13T13:28:27.909Z INFO  Version: "1.1.30"
2023-11-13T13:28:27.909Z INFO  Built on: "Sat, 11 Nov 2023 22:07:48 GMT"
2023-11-13T13:28:27.909Z INFO  Revision: "59652555bf372e85185d8cad47b99d3a8eb032ea"
2023-11-13T13:28:27.909Z INFO  Smart contracts revision: "1535e07cc84cdfea2ac8d0ec4bcb854c9f7d21ba"
2023-11-13T13:28:27.909Z INFO  Docker image: "107782235753.dkr.ecr.eu-central-1.amazonaws.com/goracle-nr:v1.1.30"
2023-11-13T13:28:27.910Z INFO  Docker image hash: "705d77c0330c8a1ddd07c1c2618e0ca5cf1debd583e4fa0b49d9f4fa2398a07b"
2023-11-13T13:28:27.986Z DEBUG Blockchain server host is local, changing it to "host.docker.internal" to make it work under Docker
2023-11-13T13:28:28.151Z INFO  Using Algorand API server: "http://host.docker.internal:4001/", port: "4001"
2023-11-13T13:28:28.191Z DEBUG Block seed is available
2023-11-13T13:28:28.195Z DEBUG Using network config override
2023-11-13T13:28:28.258Z INFO  Main address: "I5EY62R2X5PSONSKWEEXZAUC5WZ3XQZPUQOA2RQKLFNKKKM5BPXWN7EFEQ"
2023-11-13T13:28:28.258Z INFO  Participation address: "MA2XUHMW4F2HWJSXMX6GVFJSV4QDJLS4U2HDELEX75QQH2YE4LZSMVZIOE"
2023-11-13T13:28:28.259Z INFO  Main smart contract: "1004"
2023-11-13T13:28:28.259Z INFO  Voting smart contracts: "1010, 1014, 1018"
2023-11-13T13:28:28.259Z INFO  Token asset ID: "1003"
2023-11-13T13:28:28.261Z INFO  Last blockchain round: "16600"
2023-11-13T13:28:28.266Z INFO  Staked amount: 1000000000000 microGORA
2023-11-13T13:28:28.266Z INFO  Deposits: 70000 microALGO, 7000000000 microGORA
2023-11-13T13:28:28.324Z INFO  Oracle sources set up: 31
2023-11-13T13:28:28.401Z INFO  Processing round "16598" only
2023-11-13T13:28:28.419Z DEBUG Handling call "main#1004.request" from "DPF45GKEB2H7P7HJNRHYNJXZTCSPWMLBIOFR5ZM6V2FJTPMNJ7C2VBQRHA", round "16598"
2023-11-13T13:28:28.419Z DEBUG Using logged request ID, prefix: "req_id-"
2023-11-13T13:28:28.423Z INFO  Processing oracle request "2L7P3TYMSNBMBGMW2RFZESVXYB4W5NFH42KG5GBTU6UY53ZBIOIQ", destination: "1280.handle_oracle_const"
2023-11-13T13:28:28.424Z DEBUG Querying source #1, args:
2023-11-13T13:28:28.424Z DEBUG Result #0, source "1": 1, for "2L7P3TYMSNBMBGMW2RFZESVXYB4W5NFH42KG5GBTU6UY53ZBIOIQ"
2023-11-13T13:28:28.425Z DEBUG Result for "2L7P3TYMSNBMBGMW2RFZESVXYB4W5NFH42KG5GBTU6UY53ZBIOIQ": 1 (number, single)
2023-11-13T13:28:28.433Z DEBUG Using seed: "0x9d2b280c6aacbff4357c2f1fc0ba0e94f46160f4a2368f763a947944878abc86"
2023-11-13T13:28:28.438Z DEBUG Alloted "999982301" vote(s) for "2L7P3TYMSNBMBGMW2RFZESVXYB4W5NFH42KG5GBTU6UY53ZBIOIQ", zIndex: "4"
2023-11-13T13:28:28.456Z DEBUG Creating verify txn to vote on "2L7P3TYMSNBMBGMW2RFZESVXYB4W5NFH42KG5GBTU6UY53ZBIOIQ": { suggestedParams: { flatFee: true, fee: 0, firstRound: 16599, lastRound: 16608, genesisID: 'sandnet-v1', genesisHash: 'RXrzSgzbMh2FXnMJPwqL2UGeyIdbiks2G1oUvDS7fA8=', minFee: 1000 }, from: 'GBS6GNRJIOD3SFHQGCXT7QBUF2V6G7HHG7J3M3XYSAF57FIN4RN53DTRTU', appIndex: 1004, appArgs: [ '0x23fd2961', '0x46a261eaa8af75c2af39cc8232d849fb77def96e264a6fb02b14e5563a2e9ac5ff3513bc613405c6461898523280e17596543f4da7461910f4cb8662b6437d87', '0xf02acf8d37b7ae2d55be012bebbaab21322aea4ec214c5ba5b1def593906b29c1949842a74e904b7b7030ab6d003e6ccebab7efa7e7fa897a09e6bdc4cfac4eb9f11f6930761335de7b57f0643dd4108', '0x9d2b280c6aacbff4357c2f1fc0ba0e94f46160f4a2368f763a947944878abc86', '0x0000000000000001', '0x0000000000000002', '0x0000000000000003', '0x0000000000000001', '0x8ca52b2d1e080d74325852bf3d76bd6a8c4b335c198cab591e67df8e27476e6a', '0x3a66f2b5dba56c2aac3705641397a3aa5c8ee4f5c3ee84877e80346a9cb48bb58d6884389847ca9e3d115a7fdac390ac42b04ed8a1cb57c532181afe549ccebe000000003b9b31b5000000e8d4a51000000000000000000800000000000000009ddd285c2891cb74b21b2bbada87c4298459c3367a477eb3be6f00e5cb8eb2ae80', '0x0000000000000004' ], accounts: [ 'MA2XUHMW4F2HWJSXMX6GVFJSV4QDJLS4U2HDELEX75QQH2YE4LZSMVZIOE', 'I5EY62R2X5PSONSKWEEXZAUC5WZ3XQZPUQOA2RQKLFNKKKM5BPXWN7EFEQ', 'VSFZF5BRBVJY7P5QQN73JQ27DX3RP6PWSHW4I3SFFFZYFNTGCM3ZC2DHLE', 'TXOSQXBISHFXJMQ3FO5NVB6EFGCFTQZWPJDX5M56N4AOLS4OWKXAPCZFSY' ], foreignApps: [ 1010 ], boxes: [ { appIndex: 1004, name: '0x8ca52b2d1e080d74325852bf3d76bd6a8c4b335c198cab591e67df8e27476e6a' }, { appIndex: 1004, name: '0x3a66f2b5dba56c2aac3705641397a3aa5c8ee4f5c3ee84877e80346a9cb48bb5' }, { appIndex: 1010, name: '0x8d6884389847ca9e3d115a7fdac390ac42b04ed8a1cb57c532181afe549ccebe' } ], onComplete: 0 }
2023-11-13T13:28:28.463Z DEBUG Blockchain-voting on "2L7P3TYMSNBMBGMW2RFZESVXYB4W5NFH42KG5GBTU6UY53ZBIOIQ", seed: "0x9d2b280c6aacbff4357c2f1fc0ba0e94f46160f4a2368f763a947944878abc86" (real), VRF proof: "0xf02acf8d37b7ae2d55be012bebbaab21322aea4ec214c5ba5b1def593906b29c1949842a74e904b7b7030ab6d003e6ccebab7efa7e7fa897a09e6bdc4cfac4eb9f11f6930761335de7b57f0643dd4108", VRF result: "0x46a261eaa8af75c2af39cc8232d849fb77def96e264a6fb02b14e5563a2e9ac5ff3513bc613405c6461898523280e17596543f4da7461910f4cb8662b6437d87", request round: "16598", round window: "16599" - "16608"
2023-11-13T13:28:28.478Z DEBUG Calling "voting#1010.vote" by "MA2XUHMW4F2HWJSXMX6GVFJSV4QDJLS4U2HDELEX75QQH2YE4LZSMVZIOE", id: "23e1ed9b96248aff", args: { suggestedParams: { flatFee: true, fee: 2000, firstRound: 16599, lastRound: 16608, genesisID: 'sandnet-v1', genesisHash: 'RXrzSgzbMh2FXnMJPwqL2UGeyIdbiks2G1oUvDS7fA8=', minFee: 1000 }, method: 'vote', methodArgs: [ '0x46a261eaa8af75c2af39cc8232d849fb77def96e264a6fb02b14e5563a2e9ac5ff3513bc613405c6461898523280e17596543f4da7461910f4cb8662b6437d87', '0xf02acf8d37b7ae2d55be012bebbaab21322aea4ec214c5ba5b1def593906b29c1949842a74e904b7b7030ab6d003e6ccebab7efa7e7fa897a09e6bdc4cfac4eb9f11f6930761335de7b57f0643dd4108', '0x408f600000000000', '0x4094000000000000', '0xbbdd1de0', '0x1bcbce99440e8ff7fce96c4f86a6f998a4fb3161438b1ee59eae8a99bd8d4fc5', '0x4935455936325232583550534f4e534b574545585a41554335575a3358515a5055514f413252514b4c464e4b4b4b4d35425058574e3745464551', '0x3ff0000000000000', '0xd2fefdcf0c9342c09996d44b924ab7c0796eb4a7e6946e9833a7a98eef2143911bcbce99440e8ff7fce96c4f86a6f998a4fb3161438b1ee59eae8a99bd8d4fc500500063000000000000000000000000001101000000000000000100000000000000000000', '0x41cdcd426e800000', '0x4010000000000000', '0x00' ], note: '', appID: 1010, sender: 'MA2XUHMW4F2HWJSXMX6GVFJSV4QDJLS4U2HDELEX75QQH2YE4LZSMVZIOE', boxes: [ { appIndex: 1010, name: '0x47498f6a3abf5f27364ab1097c8282edb3bbc32fa41c0d460a595aa5299d0bef' }, { appIndex: 1010, name: '0x6e8e497a81d11786378b1419468bf2315758b0e1b6bfc4ecd4c8837bd48580f0' } ], appAccounts: [], appForeignApps: [], appForeignAssets: [], lease: '0xd2fefdcf0c9342c09996d44b924ab7c0796eb4a7e6946e9833a7a98eef214391' }
2023-11-13T13:28:34.589Z INFO  Submitted 999982301 vote(s) on request "2L7P3TYMSNBMBGMW2RFZESVXYB4W5NFH42KG5GBTU6UY53ZBIOIQ"
Waiting for for oracle return value (up to 10 seconds)
Received oracle value: 1.0
```
Note the last line: `Received oracle value: 1.0`. It shows the value returned by
the oracle which has been successfully processed and stored by the executed app.
If your Gora development node is already running, the date-prefixed log messages
above will be found in its output rather than in script's output above. Let us
now look at example apps in more detail.

### Basic example: `example_const.py`

[This app](https://github.com/GoraNetwork/developer-quick-start/blob/main/example_const.py "Example app on Github")
demonstrates the use of Gora in most simple and detailed possible way. It makes a
query to a special test source built into Gora that always returns the value of `1`.
To make the example more explicit, oracle request is built without using Gora
support libary. Since no external sources are queried, this example can even be run
offline.

### Classic example: `example_classic.py`

[This app](https://github.com/GoraNetwork/developer-quick-start/blob/main/example_classic.py "Example app on Github")
demonstrates the use of Gora with predefined data sources. These sources are
pre-configured under fixed numeric ID's, with more of them potentially being
added in future releases. This example uses Gora library to simplify oracle
request building which is recommended for production use.

### General URL example: `example_url.py`

[This app](https://github.com/GoraNetwork/developer-quick-start/blob/main/example_url.py "Example app on Github")
show how to use Gora for fetching data from arbitrary URLs. Data from URL
responses can be extracted with a variety of methods such as JSONPath, XPath,
regular expressions, or substring specifications.

Algorand [Dapp Flow](https://app.dappflow.org/explorer/home) web app can be used
to trace applicable transactions and confirm that the destination call has been
made and values updated.
**Warning!** *You may get an error message from Dapp Flow about "disabled
parameter: application-id". This is a minor issue and should not affect
operation.*
