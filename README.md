# Blockchain Pet Project

This pet project is inspired by the **Blockchain A-Z** course and the [blockchain-demo](https://github.com/anders94/blockchain-demo/tree/master) by [anders94](https://github.com/anders94).

Technologies used: Python, Flask, OOP, peer-to-peer system, blockchain, Solidity.

The main idea is to replicate the structure of a real Blockchain network by creating multiple node servers. These nodes interact with each other using defined rules, proof-of-work, and consensus mechanisms.

Each server-node is able to mine block, send transactions and more.

## How to Test the Project

To test the project, follow these steps:

1. **Set up the virtual environment (venv):**
   - Create and activate a virtual environment.
   - Install the required dependencies.

2. **Run each node as a Flask server:**
   - Navigate to the `\user_node_servers` directory.
   - Start each node by running the Flask server.

3. **Send API requests to the nodes:**
   - Use Postman or a REST Client to send API requests to the nodes.
   - Sample requests can be found in the `blockchain requests.http` file.

## Smart Contract

I also attempted to write a smart contract using Solidity. To run it, you will need additional software like Remix or a similar Solidity development environment.

