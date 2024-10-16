// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "../lib/forge-std/src/Script.sol";
import "../src/example_basic.sol";

contract DeployGoraExample is Script {
    function run() external returns (address) {
        // Загрузка приватного ключа из переменной среды
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        
        // Загрузка адреса Gora из переменной среды
        address goraAddress = vm.envAddress("GORA_ADDRESS");

        // Начало широковещательной транзакции
        vm.startBroadcast(deployerPrivateKey);

        // Создание и развертывание контракта GoraExample
        GoraExample goraExample = new GoraExample(goraAddress);

        // Завершение широковещательной транзакции
        vm.stopBroadcast();

        // Возвращаем адрес развернутого контракта
        console.log("GoraExample deployed at:", address(goraExample));
        return address(goraExample);
    }
}