"use strict";

for (const event of [ "unhandledRejection", "uncaughtException" ]) {
  process.on(event, err => {
    console.log(err.stack ?? err);
    process.exit(1);
  });
}

const Fs = require("fs");
const ChildProcess = require("child_process");
const TimersPromises = require("timers/promises");
const Ethers = require("ethers");
const { deploy, loadContract } = require("./deploy.js");

const devGoraNodeDockerName = "gora-nr-dev";
const deflEvmApiUrl = "http://localhost:8546";

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

// Load Gora main contract, return its instance.
async function setupGoraContract(signer) {

  const addr = readContractAddr("main_default");
  const [ abi ] = loadContract("main");
  const res = new Ethers.Contract(addr, abi, signer);

  // Check that main contract is really at this address. It will not if
  // blockchain was restarted without contract redeployment and .addr file update.
  let goraName;
  try { goraName = await res.goraName() } catch (e) {};
  if (goraName != "main")
    throw "Saved gora main contract address is not current";

  await enableContractLogs(res, "main");
  return res;
}

// Return true if dev Gora node is running, false otherwise.
function isDevGoraNodeRunning() {

  const cmd = `docker ps --filter name=${devGoraNodeDockerName} --format Aha`;
  const output = ChildProcess.execSync(cmd)
  return Boolean(output.length);
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

  if (!isDevGoraNodeRunning())
    throw "No running development Gora node detected, cannot continue";

  let [ signer, provider ] = await connectToEvmNode(apiUrl);
  const goraContract = await setupGoraContract(signer);

  const solName = `example_${name}.sol`;
  const solArgs = [ ...solcOpts, solName ];
  console.log("Running:", solcCmd, solArgs.join(" "));

  const solRes = ChildProcess.spawnSync(solcCmd, solArgs);
  if (!solRes.stdout.length)
    throw solRes.stderr.toString();

  const compiled = JSON.parse(solRes.stdout.toString());
  const args = [ readContractAddr("main_default") ];
  if (name == "off_chain")
    args.push(Fs.readFileSync("off_chain_example.wasm"));

  const exampleContract = await deploy({
    signer, compiled, args,
    name: `example_${name}`,
  });
  await enableContractLogs(exampleContract, "example");

  let createdReqId;
  goraContract.on("CreateRequest", (_, reqId) => createdReqId = reqId);

  console.log("Making a Gora request");
  const txnReceipt = await (await exampleContract.makeGoraRequest(
    { gasLimit: 1000000, value: 1000000 }
  )).wait();
  console.log(`Gora request made in round "${txnReceipt.blockNumber}"`);
  await TimersPromises.setTimeout(1500);

  if (!createdReqId)
    throw "Failed to create Gora request or retrieve its ID";
  console.log(`Created Gora request ID: ${createdReqId}`);

  console.log("Checking received result");
  const lastReqId = await exampleContract.lastReqId();
  if (lastReqId == createdReqId)
    console.log("Success, response received by destination method");
  else
    console.log("Fail, response NOT received by destination method");

  const lastValueRaw = await exampleContract.lastValue();
  const lastValueStr = Buffer.from(lastValueRaw.slice(2), "hex").toString();
  console.log(`Response value: "${lastValueStr}"`);

  goraContract.removeAllListeners();
  exampleContract.removeAllListeners();
}

const exampleName = process.argv[2] ?? "basic";
console.log(`Running example: ${exampleName}`);

const apiUrl = process.env.GORA_EXAMPLE_EVM_API_URL || deflEvmApiUrl;
runExample(apiUrl, exampleName);