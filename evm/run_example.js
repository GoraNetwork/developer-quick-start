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
const { deploy, loadContract } = require("./deploy.js");

const testStake = 10_000;
const devGoraNodeDockerName = "gora-nr-dev";

// Solidity compilation command and options.
const solcCmd = "./solc";
const solcOpts = [ "--no-color", "--combined-json", "abi,bin" ];

// Read a smart contract address file.
function readAddr(name) {

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

// Return true if Gora main contract is available, false otherwise.
async function checkGoraContract(signer) {

  const addr = readAddr("main");
  if (!addr)
    return;

  const [ abi ] = loadContract("main");
  const contract = new Ethers.Contract(addr, abi, signer);
  await enableContractLogs(contract, "main");

  let hasFailed;
  try {
    console.log(`Checking for Gora contract at "${addr}"`);
    await (await contract.testLog()).wait();
  }
  catch (e) {
    hasFailed = true;
  }

  return hasFailed ? false : contract;
}

// Deploy Gora smart contracts if they aren't already.
async function deployGoraMaybe(signer) {

  const contract = await checkGoraContract(signer);
  if (contract)
    return contract;

  console.log(`No Gora main contract detected, deploying anew`);
  return await deploy({ signer, name: "main" });
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

async function connectToApi(url) {

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

  let [ signer, provider ] = await connectToApi(apiUrl);
  const goraContract = await deployGoraMaybe(signer);

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
    args: [ readAddr("main") ],
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

  const hardhatUrl = process.env.GORA_DEV_HARDHAT_URL || "http://127.0.0.1:8545/";
  const privKey = process.env.GORA_DEV_HARDHAT_PRIV_KEY;
  const evmCfg = {
    networks: {
      hardhat: {
        privKey,
        mainContract: goraContract.target,
        server: hardhatUrl
      }
    }
  };

  // Shut down the connection, or ECONNRESET (socket hang up) errors may occur
  // with Hardhat after Gora node has executed.
  exampleContract.removeAllListeners(); // otherwise destroy() will break
  goraContract.removeAllListeners();
  await TimersPromises.setTimeout(500); // only way to ensure the above worked
  provider.destroy();

  if (!createdReqId)
    throw `Failed to create request or retrieve its ID`;
  console.log("Created request ID:", createdReqId);

  startGoraNodeMaybe(txnReceipt.blockNumber, evmCfg);
  console.log("Checking received result");

  // Reconnect.
  [ signer, provider ] = await connectToApi(apiUrl);
  Object.defineProperties(exampleContract, { // silly read-only properties
    runner: { value: signer, writable: true }
  });

  const lastReqId = await exampleContract.lastReqId();
  if (lastReqId == createdReqId)
    console.log("Success: response received by destination method.");
  else
    console.log("Fail: response NOT received by destination method");

  const lastValue = await exampleContract.lastValue();
  console.log("Response value:", lastValue);
}

const apiUrl = process.env.GORA_EXAMPLE_EVM_API_URL || "http://127.0.0.1:8545/";
runExample(apiUrl, "basic");