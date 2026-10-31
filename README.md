# Bitcoin Sandbox

![fun](docs/assets/fun.jpeg)

**Bitcoin Sandbox** is a lightweight, pure-Python implementation of the Bitcoin protocol, built for education, research, and hands-on experimentation.

The project is an attempt to understand Bitcoin from the inside out by implementing its core mechanisms step by step. Rather than hiding those mechanisms behind a production node, Bitcoin Sandbox aims to provide a readable, cohesive, and hackable codebase for studying consensus rules, experimenting with custom networks, and exploring new ideas such as alternative signature schemes, VM opcodes, and AI integrations.

**Long-term goal:** build an interoperable Bitcoin node that can validate, mine, synchronize, and serve blockchain data on Mainnet, Testnet4, and isolated experimental networks, with an RPC interface and a browser-based wallet.

> **Development status:** Bitcoin Sandbox is an early-stage research project, **not yet a fully validating Bitcoin node**. It is not intended for production use or for securing real funds. Features described as goals below should not be mistaken for implemented functionality.

## Project Architecture

![overview](docs/assets/diagram-overview.svg)

The roadmap is organized around five main areas, with separately usable subcomponents for networking and RPC:

1. **Bitcoin Script VM** — script execution, transaction validation, and consensus compatibility.
2. **Miner** — proof-of-work verification and block mining.
3. **P2P** — **P2P Protocol** (shared binary data models, codecs, and transport), **P2P Server** (inbound connections), and **P2P Client** (outbound connections).
4. **RPC & Storage** — **RPC Protocol & API**, **RPC Server**, and **RPC Client**, backed by an independently designed **Storage Engine**.
5. **Web Wallet** — an experimental browser-based wallet that accesses node functions through a controlled RPC integration.

P2P inbound and outbound peers use the same Bitcoin protocol; the server/client distinction is an interface and connection-management choice, **not two different protocols**. Similarly, storage belongs to the node's shared infrastructure rather than to the RPC server alone.

## Current Development Status

The statuses below reflect features visible in the current code snapshot, not independently verified interoperability or the intended final feature set.

| Component                                    | Status                                       | Implemented so far                                                                                                                                                                                                   | Major work remaining                                                                                                                                              |
| -------------------------------------------- | -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Bitcoin Script VM**                        | In progress                                  | Script bytecode parser/compiler, assembly parser, stack and `ScriptNum` utilities, many opcode handlers, hashing and signature-verification helpers, verification-flag definitions, and a `script_tests.json` loader | Transaction-aware signature checks and complete transaction validation, full consensus/flag enforcement, and test-suite/chain-history parity                      |
| **Miner**                                    | PoW prototype (sequential + multiprocessing) | Compact target (`nBits`) utilities, block-header serialization, PoW checks, sequential nonce search, working multiprocessing miner, and experimental threading miner; basic block data models are also available     | Verify threaded behavior with free-threaded Python, coinbase/Merkle-root construction, difficulty-rule validation, and end-to-end mining on an experimental chain |
| **P2P Protocol / Server / Client**           | Binary-data codec foundations                | Byte-stream I/O, CompactSize, basic non-witness transaction and block serialization, network parameters, service flags, and DNS-seed discovery                                                                       | SegWit-aware serialization, P2P message framing and transport, inbound/outbound connections, peer management, synchronization, and relay                          |
| **RPC Protocol & API / Server / Client**     | Planned                                      | —                                                                                                                                                                                                                    | JSON-RPC request/response handling, method dispatch, authenticated HTTP server, and reusable RPC client                                                           |
| **Storage Engine** _(shared infrastructure)_ | Planned                                      | —                                                                                                                                                                                                                    | Persistent block/chainstate storage, indexing, efficient queries, and reorganization support                                                                      |
| **Web Wallet**                               | Planned                                      | —                                                                                                                                                                                                                    | Browser UI, RPC integration, key management, signing, and transaction workflows                                                                                   |

## Development Roadmap

### 1. Bitcoin Script VM

**Goal:** faithfully reproduce Bitcoin's script and transaction-validation behavior, including historical consensus rules. Validation correctness takes priority over feature breadth.

**Implemented foundations:**

- [x] Parse and compile Bitcoin Script bytecode, including push-data operations.
- [x] Parse script assembly into bytecode.
- [x] Implement stack utilities, Script number encoding/decoding, and a script execution framework.
- [x] Implement handlers for many stack, control-flow, arithmetic, hash, and signature-related opcodes. These handlers are still subject to consensus testing and refinement.
- [x] Add ECDSA and Schnorr verification helpers using `btclib`.
- [x] Define script verification flags, signature-version contexts, and a loader for Bitcoin Core's `script_tests.json` cases.

**Next milestones:**

- [ ] Connect script execution to the new transaction data models, real signature hashing, and signature verification. The current interpreter still uses a dummy signature checker.
- [ ] Enforce the applicable consensus rules and verification flags for each script context and historical activation period.
- [ ] Complete transaction validation across the original Bitcoin rules, P2SH (BIP16), SegWit (BIP141/143), and Taproot/Tapscript (BIP340/341/342).
- [ ] Pass **all** applicable Bitcoin Core `script_tests.json` cases, including expected failure behavior.
- [ ] Replay and validate transactions from Mainnet and Testnet4 block histories, comparing results against Bitcoin Core under the rules applicable at each block height.

**Acceptance criteria:** the official script test suite passes, and historical transaction-validation results agree with Bitcoin Core. Broader block- and chain-level consensus validation is also required before the node can be considered safe from consensus divergence.

### 2. Miner

**Goal:** understand and implement the full proof-of-work lifecycle, from target encoding to constructing, mining, and validating blocks.

**Implemented foundations:**

- [x] Encode/decode the compact difficulty target (`nBits`) and calculate target values.
- [x] Encode/decode Bitcoin's 80-byte block header; typed block and transaction data models now provide basic binary serialization.
- [x] Check a block-header hash against a supplied PoW target.
- [x] Search a nonce range for a header satisfying a target with the sequential `Miner`.
- [x] Implement `MultiProcessMiner`, splitting the nonce range across worker processes. **Confirmed working in local tests.**
- [x] Implement an experimental `MultiThreadMiner` with chunked nonce ranges and a shared stop event. **Not yet successfully validated in tests.**

**Next milestones:**

- [ ] Test `MultiThreadMiner` under a free-threaded (GIL-disabled) Python build and verify correctness and parallel speedup.
- [ ] Benchmark sequential, multithreaded, and multiprocessing mining implementations.
- [ ] Construct valid mining candidates using the existing block/transaction data models, including coinbase transactions, Merkle roots, and witness commitments where applicable.
- [ ] Validate difficulty targets and contextual difficulty-adjustment rules.
- [ ] Implement full block validation, including transactions and consensus limits.
- [ ] Mine and validate blocks end to end on Regtest or a custom private network.

**Parallelism note:** On standard GIL-enabled CPython, threads are not expected to provide effective CPU parallelism for this small-hash mining workload. The multiprocessing implementation uses separate processes and has been tested successfully. The threading version is experimental and needs testing on free-threaded Python; it is not currently a verified speedup.

The current miner supports **PoW verification and nonce searching**, including a working multiprocessing approach, but is not yet a complete block-mining subsystem.

### 3. P2P Networking & Synchronization

**Goal:** provide reusable P2P building blocks for protocol experiments while ultimately operating as an interoperable Bitcoin peer that can download, validate, and relay blockchain data on Mainnet and Testnet4.

The public-facing design has three components. **P2P Server** accepts inbound connections; **P2P Client** initiates outbound connections. Both rely on the same protocol codecs, transports, peer-session logic, and message handlers. Once connected, peers can both send and receive application messages regardless of who initiated the connection.

#### 3.1 P2P Protocol — Encoding, Decoding & Transport

**Responsibility:** provide shared Bitcoin binary data structures and encoding/decoding primitives, then build P2P message formats and transports on top. The data codecs are useful beyond networking, including block validation, mining, and storage. They do not depend on whether a peer connection is inbound or outbound.

**Implemented foundations:**

- [x] Define network parameters for Mainnet, Testnet4, and Regtest and selected peer service flags. The `NODE_P2P_V2` capability bit is defined, but v2 transport is **not** implemented.
- [x] Implement `BytesReader` / `BytesWriter`, including little-endian 8-, 16-, 32-, and 64-bit integer operations, with stream-position and remaining-byte helpers.
- [x] Implement `CompactSize` integer encoding/decoding.
- [x] Define binary data models for `OutPoint`, `TxIn`, `TxOut`, and `Transaction`, with serialization/deserialization of the **legacy (non-witness) transaction format**.
- [x] Define `BlockHeader`, `BlockBody`, and `Block` and support encoding/decoding complete blocks composed of legacy-format transactions.
- [x] Provide stream-oriented `encode` / `decode` methods and convenient `encode_to_bytes` / `decode_from_bytes` helpers for these structures, including trailing-byte checks in standalone decoders.

**Next milestones:**

- [ ] Add SegWit transaction marker/flag and witness-stack serialization, and implement `txid` / `wtxid` calculations.
- [ ] Harden binary decoders for canonical CompactSize encodings, size/count limits, and malformed or adversarial data. Existing decoding support is **not** a claim of full consensus-safe parsing.
- [ ] Add network-address and additional P2P payload data structures.
- [ ] Encode/decode Bitcoin P2P messages (e.g., `version`, `verack`, `ping`, `pong`, `inv`, `getdata`, `headers`, `block`, and `tx`).
- [ ] Implement legacy v1 message framing, payload-size handling, and checksum verification.
- [ ] Implement BIP324 v2 transport as a separate transport implementation, including key exchange, encrypted packet framing, and application-message mapping.

**Scope note:** transaction/block **binary serialization** is now implemented in its basic legacy form; transaction and block **consensus validation** are separate unfinished tasks. No P2P message exchange, peer connection, or chain synchronization is implemented yet.

**Design principle:** separate _typed Bitcoin data models_, _P2P application-message codecs_, and _transport framing_. In particular, BIP324 is more than an alternative message serializer; it changes how peer connections are established and protected.

#### 3.2 P2P Server — Inbound Connections

**Responsibility:** make the sandbox node accessible to other Bitcoin peers and to nodes on custom experimental networks.

- [ ] Listen for inbound TCP connections on the configured network.
- [ ] Accept, negotiate, and maintain peer sessions with connection limits, timeouts, and clean shutdown.
- [ ] Process incoming peer messages using the shared protocol implementation.
- [ ] Serve requested headers, blocks, and transactions when data is available and appropriate to relay.
- [ ] Integrate inbound peers into peer management, chain synchronization, and transaction/block propagation.

**Status:** planned; inbound peer connections have not yet been implemented.

#### 3.3 P2P Client — Outbound Connections

**Responsibility:** connect to Bitcoin peers, discover the network, and obtain and relay blockchain data.

- [x] Discover candidate peers from DNS seeds, including service-flag-prefixed queries.
- [ ] Establish outgoing TCP connections and complete Bitcoin version handshakes.
- [ ] Maintain peer connections, handle liveness checks, disconnects, and reconnection.
- [ ] Exchange inventories, request headers and blocks, and propagate transactions.
- [ ] Implement initial block download and chain synchronization in cooperation with shared validation and storage services.

**Status:** peer discovery is implemented; outbound peer connections and synchronization are not yet implemented.

**Shared internal infrastructure:** peer sessions, handshake/message dispatch, synchronization coordination, and chain selection should be reusable by both inbound and outbound peers. Chain selection, reorganization, and consensus validation remain node-wide responsibilities rather than features exclusive to the P2P Client.

**Acceptance criteria:** exchange messages with real Bitcoin peers, synchronize and validate chain data independently, handle reorganizations, and participate in Mainnet/Testnet4 as an interoperable validating peer.

### 4. RPC Interface & Storage Engine

**Goal:** offer a reusable JSON-RPC API for controlling and inspecting the sandbox node, together with storage designed for persistent validation, synchronization, and efficient queries.

RPC is split into three components. **RPC Protocol & API** defines the method surface and request/response behavior; **RPC Server** hosts it; **RPC Client** calls it. The **Storage Engine** is designed as a separate shared subsystem because P2P, validation, mining, and RPC all need access to blockchain state.

#### 4.1 RPC Protocol & API

**Responsibility:** define the JSON-RPC contract and translate method calls into node services without coupling method implementations to HTTP connections.

- [ ] Define request/response and error models, parameter validation, method registration, and dispatch.
- [ ] Support the JSON-RPC behaviors needed for compatibility with Bitcoin Core, including supported protocol versions and batch requests.
- [ ] Expose node, blockchain, network, raw-transaction, and mining operations through consistent method interfaces.
- [ ] Expand toward comprehensive Bitcoin Core-compatible RPC method coverage, documenting any intentionally sandbox-specific methods or differences.

#### 4.2 RPC Server

**Responsibility:** expose RPC methods over HTTP for local tools, automated tests, and authorized applications.

- [ ] Implement an HTTP JSON-RPC endpoint backed by the shared method dispatcher.
- [ ] Add authentication, access restrictions, request handling, and robust error responses.
- [ ] Integrate with running P2P, mining, validation, and storage services.

#### 4.3 RPC Client

**Responsibility:** provide a Python API for calling RPC methods, usable independently of the server implementation.

- [ ] Implement HTTP JSON-RPC requests, responses, errors, and authentication handling.
- [ ] Add convenient wrappers for supported Bitcoin Sandbox and compatible Bitcoin Core methods.
- [ ] Use the client in tests, scripts, and the backend serving the experimental web wallet.

#### Shared Storage Engine

**Responsibility:** store and retrieve node data efficiently and consistently; this is **not** an implementation detail of the RPC Server.

- [ ] Design persistence for raw blocks, block headers, chain metadata, and UTXO/chainstate data.
- [ ] Support indexes for efficient queries, validation, and transaction lookup where indexed data is available.
- [ ] Handle chain updates and reorganizations consistently across P2P, validation, mining, and RPC.

**Status:** the RPC components and persistent storage engine are planned; they are not yet implemented.

### 5. Web Wallet

**Goal:** provide a browser-based wallet for learning and experimenting with Bitcoin using the sandbox node's RPC services.

**Planned work:**

- [ ] Build a simple web UI that accesses sandbox node services through a controlled RPC backend/gateway, without exposing privileged node RPC credentials in the browser.
- [ ] Support key generation, address management, and transaction construction and signing.
- [ ] Display balances and transaction history using node data.
- [ ] Broadcast transactions and inspect their status.
- [ ] Support safe experimentation on Regtest and other controlled networks.

**Status:** not yet implemented.

## Getting Started

Quick-start instructions and runnable examples will be added as the core modules become usable together.

For now, this repository is primarily a work-in-progress implementation and a record of the development process.

## AI Usage & Philosophy

Every line of implementation code in this repository is written by hand.

The primary motivation behind Bitcoin Sandbox is **deep, uncompromising technical comprehension**. Bitcoin does not strictly need another Python implementation; Bitcoin Core remains the gold standard. Rebuilding these mechanisms from scratch is a way to understand how they work, why they exist, and where their edge cases lie.

AI is used as a learning and writing companion, not as a substitute for implementing the protocol myself:

1. **Codebase navigation & explanation:** AI helps me read and understand complex C++ implementations and design patterns in Bitcoin Core.
2. **Design sparring & reference snippets:** AI helps explore architectural alternatives and illustrative Python examples. I study the ideas, then write the implementation myself rather than copying generated code. _(If I didn't write it myself, it's not my code.)_
3. **Documentation & writing:** Due to language barriers, AI helps draft English documentation such as this `README.md`. I review and refine the text manually. If some wording feels a little too AI-polished, I appreciate your understanding.

## References

- [Bitcoin Core — script.h](https://github.com/bitcoin/bitcoin/blob/master/src/script/script.h)
- [Bitcoin Core — script.cpp](https://github.com/bitcoin/bitcoin/blob/master/src/script/script.cpp)
- [Bitcoin Core — interpreter.h](https://github.com/bitcoin/bitcoin/blob/master/src/script/interpreter.h)
- [Bitcoin Core — interpreter.cpp](https://github.com/bitcoin/bitcoin/blob/master/src/script/interpreter.cpp)
- [Bitcoin Core — script_tests.json](https://github.com/bitcoin/bitcoin/blob/master/src/test/data/script_tests.json)
- [Bitcoin P2P Network Reference](https://developer.bitcoin.org/reference/p2p_networking.html)
- [Bitcoin Core — JSON-RPC Interface](https://github.com/bitcoin/bitcoin/blob/master/doc/JSON-RPC-interface.md)
- [BIP324 — Version 2 P2P Encrypted Transport Protocol](https://github.com/bitcoin/bips/blob/master/bip-0324.mediawiki)
- [btclib](https://btclib.org/)
- [A from-scratch tour of Bitcoin in Python](https://karpathy.github.io/2021/06/21/blockchain/)
- [Programming Bitcoin](https://github.com/jimmysong/programmingbitcoin)
