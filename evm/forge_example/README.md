# Gora Example Project

This project demonstrates how to deploy a smart contract using Foundry Forge and interact with the Gora protocol.

## Addresses

| Contract      | Address                                    |
| ------------- | -------------------------------------------|
| Base Sepolia  | 0xcb201275cb25a589f3877912815d5f17f66d4f13 |
| Base Mainnet  | 0xd4c99f88095f32df993030d9a6080e3be723f617 |

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/GoraNetwork/developer-quick-start
   cd developer-quick-start/evm/forge_example
   ```

2. Install Foundry:
   ```
   curl -L https://foundry.paradigm.xyz | bash
   ```
    After installation you need to open new terminal and run:
    ```
    foundryup
    ``` 

3. Install project dependencies:
   ```
   forge install
   ```
###### For more information about installation see [Foundry Installation Guide](https://book.getfoundry.sh/getting-started/installation)

## Building the Project

Compile the smart contracts:

```
forge build
```
## Deployment

To deploy the `GoraExample` contract:

1. Set up environment variables:
   Change .env.example to .env and set your private key
   ```
   mv .env.example .env
   ```


2. Run the deployment script:
   ```
   forge script script/deploy.s.sol:DeployGoraExample --rpc-url your_rpc_url --broadcast
   ```

   Replace `your_rpc_url` with the appropriate RPC URL for your target network. You may use [Alchemy](https://www.alchemy.com/) for this.

## Additional Information

- Make sure you have sufficient funds in the account associated with the private key for deployment.
- The deployment script will output the address of the deployed `GoraExample` contract.
- You can also find contract address in the file `broadcast/deploy.s.sol/84532/run-latest.json`
```
"contractAddress": "address"
```