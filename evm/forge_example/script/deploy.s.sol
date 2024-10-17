// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "../lib/forge-std/src/Script.sol";
import "../src/example_basic.sol";

contract DeployGoraExample is Script {
    function run() external returns (address) {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        
        address goraAddress = vm.envAddress("GORA_ADDRESS");

        vm.startBroadcast(deployerPrivateKey);

        GoraExample goraExample = new GoraExample(goraAddress);

        vm.stopBroadcast();

        console.log("GoraExample deployed at:", address(goraExample));
        return address(goraExample);
    }
}