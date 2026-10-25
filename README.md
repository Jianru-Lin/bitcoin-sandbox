# Bitcoin Sandbox

![fun](docs/assets/fun.jpeg)

**Bitcoin Sandbox** is a lightweight, pure-Python implementation of the Bitcoin protocol designed for education, research, and rapid experimentation.

Unlike production node software, Bitcoin Sandbox packages everything into a single, cohesive codebase. Whether you want to study Bitcoin’s underlying mechanisms, spin up an isolated custom network for teaching, or prototype cutting-edge features (such as alternative signature schemes, new VM opcodes, or AI integrations), this sandbox provides a complete, hackable environment.

## Key Features

![overview](docs/assets/diagram-overview.svg)

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

## AI Usage & Philosophy

Every line of code in this repository is written by hand.

The primary motivation behind Bitcoin Sandbox is **deep, uncompromising technical comprehension**. Bitcoin does not strictly need a Python re-implementation, Bitcoin Core remains the gold standard. Instead, building this sandbox from scratch is an exercise in mastering Bitcoin's underlying mechanics. While an AI agent could theoretically generate a project like this, copy-pasting AI-generated code would completely defeat that purpose.

Here is how AI is—and isn't—used in this project:

1. **Codebase Navigation & Explanation:** I use AI as a companion to help read, navigate, and explain complex C++ implementation details and design patterns from Bitcoin Core.
2. **Design Sparring & Reference Snippets:** AI helps brainstorm architecture alternatives or draft reference Python snippets based on high-level descriptions. However, **I never copy-paste this code directly.** I study it, understand the logic, and hand-write the implementation myself. _(If I didn't write it myself, it's not my code.)_
3. **Documentation & Writing:** Due to language barriers, AI assists in drafting documentation and text assets like this `README.md`. I provide the requirements, review the drafts, and manually refine the content. If parts of the prose feel a bit too "AI-polished," I appreciate your understanding!

## References

- [bitcoin/src/script/script.h](https://github.com/bitcoin/bitcoin/blob/master/src/script/script.h)
- [bitcoin/src/script/script.cpp](https://github.com/bitcoin/bitcoin/blob/master/src/script/script.cpp)
- [bitcoin/src/script/interpreter.h](https://github.com/bitcoin/bitcoin/blob/master/src/script/interpreter.h)
- [bitcoin/src/script/interpreter.cpp](https://github.com/bitcoin/bitcoin/blob/master/src/script/interpreter.cpp)
- [bitcoin/src/test/data/script_tests.json](https://github.com/bitcoin/bitcoin/blob/master/src/test/data/script_tests.json)
- [btclib](https://btclib.org/)
- [A from-scratch tour of Bitcoin in Python](https://karpathy.github.io/2021/06/21/blockchain/)
- [Programming Bitcoin](https://github.com/jimmysong/programmingbitcoin)
