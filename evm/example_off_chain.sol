// Demonstrate Gora's arbitrary off-chain computation capability. Public JSON
// APIs are used to query required data, so an Internet connection is necessary
// to run this example.

pragma solidity >=0.6.12;
pragma experimental ABIEncoderV2;

// Example smart contract making use of Gora on EVM.
contract GoraExampleOffChain {

  address goraAddr;
  bytes wasmBody;
  bytes public lastValue;
  bytes32 public lastReqId;

  // Emit debug log message event.
  function DEBUG(string memory str, uint num, bytes memory bin) internal {
    emit LogMsg(str, num, bin); // COMMENT OUT to disable debug logging
  }

  event LogMsg(string message, uint num, bytes bin);
  event ReceiveResponse(bytes32 reqId, bytes value);

  // Initialize, setting Gora smart contract address that must be passed by
  // the deploying application.
  constructor(address initGoraAddr, bytes memory initWasmBody) {
    goraAddr = initGoraAddr;
    wasmBody = initWasmBody;
  }

  // Make a request to Gora using the above configuration.
  function makeGoraRequest() payable public {

    bytes[] memory args = new bytes[](1);
    args[0]= "sm14hp"; // UK postcode of the area queried

    uint16 apiVer = 1;
    uint16 specType = 0; // 1 - in-place binary WASM

    bytes memory srcArg = abi.encode(apiVer, specType, wasmBody, args);
    bytes memory reqSig = abi.encodeWithSignature(
      "request(uint8,bytes,bytes,address,string,bytes,uint256)", 3,
      "gora://offchain/inline", srcArg, address(this), "receiveGoraResponse",
      "", 0
    );

    (bool isOk, bytes memory res) = goraAddr.call(reqSig);
    if (!isOk)
      revert("Unable to make Gora request");

    DEBUG("Gora request made", block.number, res);
  }

  function bytes32ToBytes(bytes32 src) internal pure returns (bytes memory) {
    bytes memory res = new bytes(32);
    assembly { mstore(add(res, 32), src) }
    return res;
  }

  // Receive a response from Gora to the above request.
  function receiveGoraResponse(bytes32 reqId, uint256 reqRound, address requester,
                               bytes calldata value, bytes calldata userData,
                               uint256 srcErrors) public {

    require(msg.sender == goraAddr, "sender is not Gora main contract");
    DEBUG("Gora response received", 0, bytes32ToBytes(reqId));

    // Save received variables for further inspection.
    lastValue = value;
    lastReqId = reqId;
    emit ReceiveResponse(reqId, value);
 }
}