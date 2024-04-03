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
const { deploy } = require("./deploy.js");

const devGoraNodeDockerName = "gora-nr-dev";

// Solidity compilation command and options.
const solcCmd = "./solc";
const solcOpts = [ "--no-color", "--combined-json", "abi,bin" ];

// Return provider and signer objects for given API URL.
async function getProviderSigner(apiUrl) {

  const provider = new Ethers.JsonRpcProvider(apiUrl);
  const signer = await provider.getSigner();
  return [ provider, signer ];
}

// Read a smart contract address file.
function readAddr(name) {

  const file = name + ".addr";
  return Fs.existsSync(file) ? Fs.readFileSync(file, "ascii") : null;
}

// Check EVM API availability at given URL, throw on failure.
async function checkEvmApi(url) {

  const [ provider ] = await getProviderSigner();
  try {
    await provider.getBlockNumber();
  }
  catch (e) {
    throw `EVM API endpoint at "${url}" is unavailable`;
  }
}

// Return true if Gora main contract is available, false otherwise.
async function checkGoraContract() {

  const addr = readAddr("main");
  if (!addr)
    return;

  const testAbi = "function testVrfExample() pure external";
  const [ , signer ] = await getProviderSigner();
  const contract = new Ethers.Contract(addr, [ testAbi ], signer);

  let hasFailed;
  try {
    await contract.testVrfExample();
  }
  catch (e) {
    hasFailed = true;
  }

  return !hasFailed;
}

// Deploy Gora smart contracts if they aren't already.
async function deployGoraMaybe(apiUrl) {

  if (await checkGoraContract())
    return;

  console.log(`No Gora main contract detected, deploying anew`);
  await deploy({ apiUrl, name: "main" });
}

// Return true if dev Gora node is running, false otherwise.
function isDevGoraNodeRunning() {

  return Boolean(
    ChildProcess.execSync(`docker ps --filter name=${devGoraNodeDockerName}`
                          + " --format Aha", dockerArgs)
  );
}

// Start one-time Gora node if necessary.
async function startGoraNodeMaybe(reqRound) {

  if (isDevGoraNodeRunning()) {
    console.log("Detected development Gora node running in the background");
    return;
  }
  console.log("Background development Gora node not detected, starting a"
              + " temporary one")

  const cliTool = process.env.GORA_DEV_CLI_TOOL ?? "../gora_cli";
  const opts = {
    encoding: "utf-8",
    stdio: "inherit",
    env: {
      ...process.env,
      GORA_CONFIG_FILE: process.env.GORA_DEV_CONFIG_FILE ?? "../.gora",
      GORA_DEV_ONLY_ROUND_EVM: reqRound,
    }
  };
  ChildProcess.execFileSync(cliTool, [ "docker-start" ], opts);
}

// Run an EVM example by name.
async function runExample(apiUrl, name) {

  console.log(`Using EVM API at: ${apiUrl}`);
  await checkEvmApi(apiUrl);
  await deployGoraMaybe(apiUrl);

  const solName = `example_${name}.sol`;
  const solArgs = [ ...solcOpts, solName ];
  console.log("Running:", solcCmd, solArgs.join(" "));

  const solRes = ChildProcess.spawnSync(solcCmd, solArgs);
  if (!solRes.stdout.length)
    throw solRes.stderr.toString();

  const compiled = JSON.parse(solRes.stdout.toString());
  await deploy({
    apiUrl, compiled,
    name: `example_${name}`,
    args: [ readAddr("main") ],
  });
}

const apiUrl = process.env.GORA_EXAMPLE_EVM_API_URL || "http://127.0.0.1:8545/";
runExample(apiUrl, "basic");