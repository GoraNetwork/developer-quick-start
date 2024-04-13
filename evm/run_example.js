"use strict";

const fatalErrHandler = err => {
  console.log(err ?? err.stack);
  process.exit(1);
};
process.on("unhandledRejection", fatalErrHandler);
process.on("uncaughtException", fatalErrHandler);

const Ethers = require("ethers");
const Fs = require("fs");
const ChildProcess = require("child_process");
const TimersPromises = require("timers/promises");
const Events = require("events");
const { deploy, loadContract } = require("./deploy.js");

const testStake = 10_000;
const devGoraNodeDockerName = "gora-nr-dev";

// Solidity compilation command and options.
const solcCmd = "./solc";
const solcOpts = [ "--no-color", "--combined-json", "abi,bin" ];

// Read a smart contract address file.
function readContractAddr(name) {

  const file = name + ".addr";
  return Fs.existsSync(file) ? Fs.readFileSync(file, "ascii") : null;
}

// Enable logging of a contracts log messages via console.
async function enableContractLogs(contract, name) {

  const lastRound = await contract.runner.provider.getBlockNumber();
  console.log(`Enabling logs for contract "${name}" at "${contract.target}"`
              + ` from round "${lastRound}"`);
  contract.on("LogMsg", (str, num, bin, info) => {
    if (info.log.blockNumber > lastRound) // ignore older events
      console.log(`CONTRACT ${name} @${info.log.blockNumber} ${str} ${num} ${bin}`);
  });
}

// Load/deploy Gora main contract and return its instance.
async function setupGoraContract(signer) {

  let res;
  const addr = readContractAddr("main");

  if (addr) {
    const [ abi ] = loadContract("main");
    res = new Ethers.Contract(addr, abi, signer);

    // Check that main contract is really at this address. That will not be
    // the case if Hardhat has been restarted.
    console.log(`Checking for Gora contract at "${addr}"`);
    let goraName;
    try { goraName = await res.goraName() } catch (e) {};
    if (goraName != "main")
      res = undefined;
  }

  if (!res)
    res = await deploy({ signer, name: "main" });

  await enableContractLogs(res, "main");
  return res;
}

// Return true if dev Gora node is running, false otherwise.
function isDevGoraNodeRunning() {

  const cmd = `docker ps --filter name=${devGoraNodeDockerName} --format Aha`;
  const output = ChildProcess.execSync(cmd)
  return Boolean(output.length);
}

// Start one-time Gora node if necessary.
async function startGoraNodeMaybe(reqRound, evmCfg) {

  if (isDevGoraNodeRunning()) {
    console.log("Detected development Gora node running in the background");
    return;
  }
  console.log("Background development Gora node not detected, starting a"
              + " temporary one")

  const customCfg = JSON.parse(process.env.GORA_CONFIG || "{}");
  customCfg.blockchain ||= {};
  customCfg.blockchain.evm = {
    ...(customCfg.blockchain.evm || {}),
    ...evmCfg
  };

  const args = [ "docker-start" ];
  let cmd = process.env.GORA_DEV_CLI_TOOL ?? "../gora_cli";
  if (cmd.endsWith(".js")) {
    args.unshift(cmd);
    cmd = "node";
  }
  console.log("Running:", cmd, ...args);

  const opts = {
    encoding: "utf-8",
    stdio: "inherit",
    env: {
      ...process.env,
      GORA_CONFIG: JSON.stringify(customCfg),
      GORA_CONFIG_FILE: process.env.GORA_DEV_CONFIG_FILE ?? "../.gora",
      GORA_DEV_EVM_ONLY_NETWORK_ROUND: `hardhat:${reqRound}`,
    }
  };
  ChildProcess.execFileSync(cmd, args, opts);
}

// Start local EVM node for execution of this example.
async function startEvmNode() {

  const checkCmd = "npx --no --no-color hardhat check";
  const checkOutput = ChildProcess.execSync(checkCmd, { encoding: "utf-8" });
  if (checkOutput) {
    throw "Hardhat is required, make sure it is installed and operational."
          + " npx output: " + checkOutput;
  }

  const streams = [ "out", "err" ].map(x => Fs.createWriteStream(`evm_${x}.log`));
  await Promise.all(streams.map(x => Events.once(x, "open")));

  console.log('Starting temporary Hardhat node, see "evm_*.log" files for its output');
  const evmNodeProcess = ChildProcess.spawn("npx", [ "hardhat", "node" ], {
    stdio: [ "ignore", ...streams ],
  });

  await TimersPromises.setTimeout(1000);
  return [ evmNodeProcess, "http://localhost:8545/" ];
}

// Return private key to use for signing txn's.
function getEvmPrivKey() {

  let res = process.env.GORA_DEV_HARDHAT_PRIV_KEY;
  if (res)
    return res;

  let hardhatCfg;
  try { hardhatCfg = require("./hardhat.config.js") } catch(e) {};
  res = hardhatCfg?.networks?.hardhat?.accounts?.[0]?.privateKey;
  if (!res)
    throw "Test EVM account private key not configured";

  return res;
}

async function connectToEvmNode(url) {

  console.log(`Using EVM API at: ${url}`);
  const provider = new Ethers.JsonRpcProvider(url, null, {
    batchMaxCount: 1,
    batchStallTime: 0,
    staticNetwork: true,
  });
  const signer = await provider.getSigner();

  let round
  try { round = await provider.getBlockNumber(); } catch (e) {};
  if (!(round >= 0))
    throw `EVM API endpoint at "${url}" is unavailable`;

  return [ signer, provider ];
}

// Run an EVM example by name.
async function runExample(apiUrl, name) {

  let evmNodeProcess;
  if (!apiUrl)
    [ evmNodeProcess, apiUrl ] = await startEvmNode();

  let [ signer, provider ] = await connectToEvmNode(apiUrl);
  const goraContract = await setupGoraContract(signer);

  const solName = `example_${name}.sol`;
  const solArgs = [ ...solcOpts, solName ];
  console.log("Running:", solcCmd, solArgs.join(" "));

  const solRes = ChildProcess.spawnSync(solcCmd, solArgs);
  if (!solRes.stdout.length)
    throw solRes.stderr.toString();

  const compiled = JSON.parse(solRes.stdout.toString());
  const exampleContract = await deploy({
    signer, compiled,
    name: `example_${name}`,
    args: [ readContractAddr("main") ],
  });
  await enableContractLogs(exampleContract, "example");

  let createdReqId;
  goraContract.on("CreateRequest", (_, reqId) => createdReqId = reqId);

  console.log("Making a Gora request");
  const txnResp = await exampleContract.makeGoraRequest();
  const txnReceipt = await txnResp.wait();
  console.log(`Gora request made in round "${txnReceipt.blockNumber}"`);

  console.log("Setting signer's stake to:", testStake);
  const signerAddr = await signer.getAddress();
  await (await goraContract.testSetStakes([ signerAddr ], [ testStake ])).wait();

  const evmCfg = {
    networks: {
      hardhat: {
        privKey: getEvmPrivKey(),
        mainContract: goraContract.target,
        server: apiUrl
      }
    }
  };

  // Shut down EVM API the connection. Otherwise ECONNRESET (socket hang up)
  // errors may occur with Hardhat after Gora node has executed.
  exampleContract.removeAllListeners(); // otherwise destroy() will break
  goraContract.removeAllListeners();
  await TimersPromises.setTimeout(500); // ensure the above worked
  provider.destroy();

  if (!createdReqId)
    throw "Failed to create Gora request or retrieve its ID";
  console.log("Created Gora request ID:", createdReqId);

  startGoraNodeMaybe(txnReceipt.blockNumber, evmCfg);
  console.log("Checking received result");

  // Reconnect.
  [ signer, provider ] = await connectToEvmNode(apiUrl);
  Object.defineProperties(exampleContract, { // silly read-only properties
    runner: { value: signer, writable: true }
  });

  const lastReqId = await exampleContract.lastReqId();
  if (lastReqId == createdReqId)
    console.log("Success, response received by destination method");
  else
    console.log("Fail, response NOT received by destination method");

  const lastValueRaw = await exampleContract.lastValue();
  const lastValueStr = Buffer.from(lastValueRaw.slice(2), "hex").toString();
  console.log("Response value:", lastValueStr);

  if (evmNodeProcess) {
    console.log("Stopping temporary Hardhat node");
    evmNodeProcess.kill("SIGKILL"); // SIGTERM not enough due to subprocesses
  }
}

runExample(process.env.GORA_EXAMPLE_EVM_API_URL, "basic");