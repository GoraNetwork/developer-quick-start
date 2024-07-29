"use strict";

const TimersPromises = require("timers/promises");
const Fs = require("fs");
const AxelarLocalDev = require("@axelar-network/axelar-local-dev");

// Network names to use for files with addresses of deployed contracts.
const netNames = [ "default", "slave" ];

async function main() {

  if (process.argv.length < 7) {
    console.log("Usage: axelar_relayer.js <interval ms> <master URL> <master key>"
                + " <slave URL> <slave key>");
    return;
  }

  const [ relayInterval, ...netConf ] = process.argv.slice(2);
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