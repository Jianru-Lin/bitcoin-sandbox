# Bitcoin Sandbox

**Bitcoin Sandbox** is a lightweight, pure-Python implementation of the Bitcoin protocol designed for education, research, and rapid experimentation.

Unlike production node software, Bitcoin Sandbox packages everything into a single, cohesive codebase. Whether you want to study Bitcoin’s underlying mechanisms, spin up an isolated custom network for teaching, or prototype cutting-edge features (such as alternative signature schemes, new VM opcodes, or AI integrations), this sandbox provides a complete, hackable environment.

## Key Features

- **Complete Bitcoin Node Stack:** Encompasses the Bitcoin Script VM, P2P networking layer, RPC interface, mining framework, and wallet functionalities.
- **Custom Networks & DNS Seeding:** Easily launch private custom networks for academic or classroom experiments, including support for custom DNSSeeder servers and local block mining.
- **Pure Python & Extensible:** Built using modern Python (`btclib` for elliptic curve cryptography), making it readable, highly extensible, and easy to modify for advanced research (e.g., post-quantum cryptography, novel VM instructions).
- **Robust Script Engine:** Implements bytecode parsing, assembly compilation, script evaluation, and validation flags mirroring Bitcoin Core.

## Current Development Progress & Roadmap

We are building the core components incrementally, starting from the foundation up:

1. **Bitcoin Script VM & Compliance:**

- **Current Milestone:** Passing **all** official Bitcoin Core script compliance tests (`script_tests.json`).
- Implement full validation flags, stack rules, and cryptographic verification checks.

2. **Transaction & Block Validation:**

- Implementing historic and modern validation rules across Satoshi-era, P2SH (BIP16), SegWit (BIP141/143), and Taproot (BIP340/341/342).

3. **P2P Networking & Node Synchronization:**

- Handshaking, inventory management, block downloading, and transaction propagation across Mainnet, Testnet, and custom networks.

4. **RPC Interface & Wallet:**

- Exposing standard JSON-RPC endpoints for local development and wallet management (key generation, signing, and broadcasting).

## Getting Started

_(Quick start instructions and usage examples coming soon as core modules are finalized.)_

## References

- [bitcoin/src/script/script.h](https://github.com/bitcoin/bitcoin/blob/master/src/script/script.h)
- [bitcoin/src/script/script.cpp](https://github.com/bitcoin/bitcoin/blob/master/src/script/script.cpp)
- [bitcoin/src/script/interpreter.h](https://github.com/bitcoin/bitcoin/blob/master/src/script/interpreter.h)
- [bitcoin/src/script/interpreter.cpp](https://github.com/bitcoin/bitcoin/blob/master/src/script/interpreter.cpp)
- [bitcoin/src/test/data/script_tests.json](https://github.com/bitcoin/bitcoin/blob/master/src/test/data/script_tests.json)
