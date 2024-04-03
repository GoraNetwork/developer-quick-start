"use strict";

const Ethers = require("ethers");
const Fs = require("fs");

async function deploy({ apiUrl, name, addrFile, compiled, args }) {

  if (!compiled) {
    const file = name + ".compiled";
    console.log("Reading compiled contract (combined JSON):", file);
    compiled = JSON.parse(Fs.readFileSync(file));
  }

  console.log("EVM API endpoint:", apiUrl);
  const provider = new Ethers.JsonRpcProvider(apiUrl);
  console.log("At block:", await provider.getBlockNumber());

  let signer;
  const keyFile = "deploy_key.txt";
  if (Fs.existsSync(keyFile)) {
    console.log(`Reading signer's private key from "${keyFile}"`);
    const privKeyHex = Fs.readFileSync(keyFile, "utf8");
    signer = new Ethers.Wallet(privKeyHex, provider);
  }
  else {
    console.log("No key file, getting a signer automatically");
    signer = await provider.getSigner();
  }

  const signerAddr = await signer.getAddress();
  console.log("Signer:", signerAddr);

  const solName = name + ".sol";
  const nameKey = Object.keys(compiled.contracts)
                        .find(x => x.startsWith(`${solName}:`));
  if (!nameKey)
    throw `Smart contract "${solName}" not found in the JSON file`;

  const contractInfo = compiled.contracts[nameKey];
  const abi = typeof contractInfo.abi == "string"
              ? JSON.parse(contractInfo.abi) : contractInfo.abi;
  const bin = Buffer.from(contractInfo.bin, "hex");

  const constrArgs = args || [];
  for (const varName in process.env) {
    const prefix = "EVM_DEPLOY_CONSTR_ARG_";
    if (varName.startsWith(prefix))
      constrArgs[Number(varName.substr(prefix.length))] = process.env[varName];
  }

  console.log(`Deploying "${solName}" with ${constrArgs.length || 'no'} argument(s)`);
  const factory = new Ethers.ContractFactory(abi, bin, signer);
  const contract = await factory.deploy(...constrArgs);
  await contract.waitForDeployment();

  const addr = await contract.getAddress();
  console.log("Deployed to:", addr);

  addrFile ||= name + ".addr";
  console.log("Writing address to:", addrFile);
  Fs.writeFileSync(addrFile, addr);
}

if (module.parent)
  Object.assign(exports, { deploy });
else {
  if (process.argv.length > 3)
    deploy(...process.argv);
  else
    console.log("Usage: node deploy.js <node URL> <contract JSON file> [address output file]");
}
