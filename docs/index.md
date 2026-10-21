# Bitcoin Script VM & Protocol Knowledge Base

Welcome to the documentation and technical notes for **bitcoin-script-vm**. This project is a Python-based implementation of a Bitcoin Script virtual machine, P2P networking components, and bytecode parsers, designed to bridge low-level protocol mechanics with a comprehensive understanding of Bitcoin architecture.

---

## 📚 Table of Contents

### Part I: Introduction & History

- [History and Milestones](./01-introduction/history_and_milestones.md) - Key events and the evolution of Bitcoin.
- [Satoshi's Vision & Whitepaper](./01-introduction/satoshi_vision.md) - Core concepts and design choices.

### Part II: Core Architecture & Consensus

- [P2P Network & Node Discovery](./02-architecture/p2p_network.md) - DNS seeds, magic bytes, and peer handshake (implemented in our codebase).
- [Chain Structure, PoW & UTXO](./02-architecture/chain_and_utxo.md) - Block validation and state management.
- [Transaction Lifecycle](./02-architecture/transaction_lifecycle.md) - From mempool to inclusion.

### Part III: Bitcoin Script & Virtual Machine (Core Tech)

- [Script Assembly Syntax](./03-script-vm/bitcoin_script_assembly.md) - Opcodes, decimal/hex literals, and string push rules.
- [Script Bytecode & Parsers](./03-script-vm/bitcoin_script_bytecode.md) - Binary layouts and stream reading.
- [VM Execution Flow & Stack](./03-script-vm/script_evaluation_flow.md) - Interpreter architecture, main stack, and altstack.
- [Script Upgrades](./03-script-vm/script_upgrades.md) - Evolution from P2PKH, P2SH, SegWit, to Taproot.
- [Miniscript & Policies](./03-script-vm/bitcoin_miniscript.md) - Structured script analysis and compilation.

### Part IV: Ecosystem & Layer 2

- [The Lightning Network](./04-ecosystem-and-l2/lightning_network.md) - Payment channels and HTLCs.
- [Sidechains & Modern L2s](./04-ecosystem-and-l2/sidechains_and_l2.md) - Liquid, Rootstock, and Ark.
- [Exchanges & Infrastructure](./04-ecosystem-and-l2/exchange_and_infra.md) - Custody and API integrations.

### Part V: Security, Bugs & Historical CVEs

- [Historical CVE Analysis](./05-security-and-cve/historical_cves.md) - Recreating and analyzing famous bugs (e.g., Value Overflow / CVE-2010-5139).
- [Consensus Pitfalls](./05-security-and-cve/script_pitfalls.md) - Strict encoding, minimaldata, and signature rules.
- [Testing Framework](./05-security-and-cve/testing_framework.md) - Working with `script_tests.json`.

### Part VI: Limitations & Future Evolution

- [Scalability & State Bloat](./06-limitations-and-future/scalability_limits.md) - Block size debates and throughput bottlenecks.
- [Privacy & Censorship Resistance](./06-limitations-and-future/privacy_and_censorship.md) - CoinJoin, Schnorr, and taproot privacy.
- [Post-Quantum Cryptography](./06-limitations-and-future/post_quantum_crypto.md) - Transitioning away from Secp256k1.
