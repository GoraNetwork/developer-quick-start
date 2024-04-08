pragma solidity >=0.6.12;
pragma experimental ABIEncoderV2;

// Example smart contract making use of Gora on EVM.
contract GoraExample {

  // Gora request method signature.
  string constant goraRequestSigSrc = "request(string,string,address,string,bytes)";

  // URL from which to fetch oracle data.
  string constant exampleUrl = "http://echo.jsontest.com/testfield/testvalue";

  // Expression to extract oracle value from the response.
  string constant exampleValueExpr = "jsonpath:$.testfield";

  // Destination smart contract method name to call with the response.
  string constant exampleDestMethod = "receiveGoraResponse";

  // Arbitrary piece of data to pass to the destination method.
  string constant exampleUserData = "my user data";

  address goraAddr; // Gora smart contract address
  bytes public lastValue; // last value received from Gora
  bytes32 public lastReqId; // Gora request ID for the last value received
  

  // Emit debug log message event.
  function DEBUG(string memory str, uint num, bytes memory bin) internal {
    emit LogMsg(str, num, bin); // COMMENT OUT to disable debug logging
  }

  event LogMsg(string message, uint num, bytes bin);
  event ReceiveResponse(bytes32 reqId, bytes value);

  // Initialize, setting Gora smart contract address that must be passed by
  // the deploying application.
  constructor(address initGoraAddr) {
    goraAddr = initGoraAddr;
  }

  // Make a request to Gora using the above configuration.
  function makeGoraRequest() public {

    DEBUG("Using Gora address", 0, abi.encodePacked(goraAddr));

    // Call this same contract as the destination one.
    address exampleDestAddr = address(this);

    bytes memory reqSig = abi.encodeWithSignature(goraRequestSigSrc,
      exampleUrl, exampleValueExpr, exampleDestAddr, exampleDestMethod,
      exampleUserData
    );
    (bool isOk, bytes memory res) = goraAddr.call(reqSig);
    if (!isOk)
      revert("Unable to make Gora request");

    DEBUG("Gora request made", 0, res);
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

    DEBUG("Gora response received", 0, bytes32ToBytes(reqId));
    // Save received variables for further inspection.
    lastValue = value;
    lastReqId = reqId;
    emit ReceiveResponse(reqId, value);
 }
}