"use strict";

const TimersPromises = require("timers/promises");
const Fs = require("fs");
const AxelarLocalDev = require("@axelar-network/axelar-local-dev");

// Network names to use for files with addresses of deployed contracts.
const netNames = [ "default", "slave" ];

// Default command-line arguments
const defaultArgs = [
  500, // relay interval in ms.
  "http://127.0.0.1:8546/", // master RPC endpoint
  "0xcf154564c745ba11a8f4de1c0ca2e70739eb7683680c6f97d8baf605f9e5a57d", // master owner
  "http://127.0.0.1:8547/", // slave RPC endpoint
  "0xcf154564c745ba11a8f4de1c0ca2e70739eb7683680c6f97d8baf605f9e5a57d", // slave address
];


async function main() {

  // Apply CLI argument defaults.
  const args = [];
  for (const [ i, defaultVal ] of defaultArgs.entries())
    args[i] = process.argv[2 + i] ?? defaultVal;

  const [ relayInterval, ...netConf ] = args;
  const networks = [];

  // Deploy Axelar contracts.
  for (let i = 0; i < netConf.length / 2; i++) {
    console.log(`Setting up smart contracts on network #${i}`);
    networks.push(
      await AxelarLocalDev.setupNetwork(
        netConf[i*2], // RPC URL
        {
          name: "chain_" + i, // numbered names required by our contracts
          ownerKey: netConf[i*2+1],
        },
      )
    );
  }

  // Save contract addresses for reference by other tools.
  for (let i = 0; i < netNames.length; i++) {
    const save = (x,y) => {
      const file = `./axelar_${x}_${netNames[i]}.addr`;
      console.log(`Writing ${netNames[i]} ${y} contract address to "${file}"`);
      Fs.writeFileSync(file, networks[i][y].address);
    }
    save("gw", "gateway");
    save("gas", "gasService");
  }

  // Start the perpetual relay loop.
  console.log("Relaying, interval (ms):", relayInterval);
  while (true) {
    await TimersPromises.setTimeout(relayInterval);
    try {
      await AxelarLocalDev.relay();
    }
    catch (e) {
      console.log(e.stack ?? e);
    }
  }
}

console.log("Starting Gora local Axelar relayer");
main();