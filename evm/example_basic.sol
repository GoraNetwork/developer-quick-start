pragma solidity >=0.6.12;
pragma experimental ABIEncoderV2;

// Example smart contract making use of Gora on EVM.
contract GoraExample {

  // URL from which to fetch oracle data.
  string constant exampleUrl = "http://echo.jsontest.com/testfield/testvalue";

  // Expression to extract oracle value from the response.
  string constant exampleValueExpr = "json:$.testfield";

  // Destination smart contract method name to call with the response.
  string constant exampleDestMethod = "receiveResponse";

  // Arbitrary piece of data to pass to the destination method.
  string constant exampleUserData = "my user data";

  address goraAddr; // Gora smart contract address
  bytes public lastValue; // last value received from Gora
  bytes32 public lastReqId; // Gora request ID for the last value received
  
  // Initialize, setting Gora smart contract address that must be passed by
  // the deploying application.
  constructor(address initGoraAddr) public {
    goraAddr = initGoraAddr;
  }

  // Make a request to Gora using the above configuration.
  function makeGoraRequest() public {

    // Call this same contract as the destination one.
    address exampleDestAddr = address(this);

    bytes memory reqSig = abi.encodeWithSignature(
      "request(string, string, address, string, bytes)",
      exampleUrl, exampleValueExpr, exampleDestAddr, exampleDestMethod,
      exampleUserData
    );

    (bool isOk,) = goraAddr.call(reqSig);
    if (!isOk)
      revert("Unable to make a Gora request");
  }

  // Receive a response from Gora to the above request.
  function receiveGoraResponse(bytes32 reqId, uint256 reqRound, address requester,
                               bytes calldata value, bytes calldata userData,
                               uint256 srcErrors) public {

    // Save received variables for further inspection.
    lastValue = value;
    lastReqId = reqId;
  }
}