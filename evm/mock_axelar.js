"use strict";

const TimersPromises = require("timers/promises");
const Fs = require("fs");
const AxelarLocalDev = require("@axelar-network/axelar-local-dev");

// How often to check for messages to relay.
const defaultRelayInterval = 500;

const defaultAddrs = [ "0x69aeb7dc4f2a86873dae8d753de89326cf90a77a",
                       "0x783e7717fd4592814614afc47ee92568a495ce0b" ];

async function setupAndRunInternal(args) {

  let [ port, relayInterval, ...addrs ] = args;
  port ||= 8500;
  relayInterval ||= defaultRelayInterval;
  if (!addrs.length)
    addrs = defaultAddrs;

  console.log("Setting up Axelar multi-chain dev environment");
  const chains = [];
  AxelarLocalDev.createAndExport({
    port, relayInterval,
    chains: [ ...addrs.keys() ].map(x => `chain_${x}`),
    callback: x => chains.push(x),
    relayers: { evm: new AxelarLocalDev.EvmRelayer() },
  });

  // Wait until all chains are created.
  while (chains.length != addrs.length)
    await TimersPromises.setTimeout(100);

  // Fund master addresses. "accountsToFund" argument to createAndExport() throws.
  for (let i = 0; i < chains.length; i++) {
    console.log(`Funding address "${addrs[i]}"`);
    await (await chains[i].userWallets[0].sendTransaction({
      to: chains[i].userWallets[1].address, value: 1000,
    })).wait();
  }

}

async function setupExternal(args) {

  if (!args.length) {
    args = [
      "http://127.0.0.1:8546/",
      "0xcf154564c745ba11a8f4de1c0ca2e70739eb7683680c6f97d8baf605f9e5a57d",
      "http://127.0.0.1:8547/",
      "0xcf154564c745ba11a8f4de1c0ca2e70739eb7683680c6f97d8baf605f9e5a57d",
    ];
  }

  const networks = [];
  for (let i = 0; i < args.length / 2; i++) {
    networks.push(
      await AxelarLocalDev.setupNetwork(
        args[i*2],
        { name: "chain_" + i, ownerKey: args[i*2+1], },
      )
    );
  }

  const names = [ "default", "slave" ];
  for (let i = 0; i < names.length; i++) {
    Fs.writeFileSync(`axelar_gw_${names[i]}.addr`, networks[i].gateway.address);
    Fs.writeFileSync(`axelar_gas_${names[i]}.addr`, networks[i].gasService.address);
  }

  console.log("Relaying, interval:", defaultRelayInterval);
  while (true) {
    await TimersPromises.setTimeout(defaultRelayInterval);
    try {
      await AxelarLocalDev.relay();
    }
    catch (e) {
      console.log(e.stack ?? e);
    }
  }
}

async function main() {

  if (process.argv[2] == "-i")
    await setupAndRunInternal(process.argv.slice(3));
  else
    await setupExternal(process.argv.slice(2));
}

main();