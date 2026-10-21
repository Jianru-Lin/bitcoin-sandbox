# Bitcoin Script Bytecode: Binary Layout, Execution Flow, and Parser Architecture

While Bitcoin Script Assembly provides a human-friendly interface, **Bitcoin Script Bytecode** is the raw binary stream actually transmitted across the network, stored in blocks, and executed by the Bitcoin consensus engine. Understanding bytecode layout and interpreter mechanics is essential for low-level protocol development, transaction analysis, and custom script interpreters.

---

## I. Binary Layout & Structure

A Bitcoin script bytecode stream is a sequence of bytes containing either instruction opcodes or embedded data payloads.

1. **Opcode Bytes**:

- Most operations are represented by a single byte ranging from `0x00` to `0xFF` (e.g., `OP_DUP` is `0x76`, `OP_EQUALVERIFY` is `0x88`, `OP_CHECKSIG` is `0xAC`).

2. **Data Push Mechanisms**:
   Unlike assembly where data sizes are implicit, bytecode uses specific prefix markers to define how many subsequent bytes constitute raw data to be pushed onto the stack:

- **Direct Push (`0x01` ~ `0x4B`)**: The byte value itself (1 to 75) indicates the exact number of payload bytes that immediately follow.
- **`OP_PUSHDATA1` (`0x4C`)**: Followed by 1 byte specifying a length up to 255 bytes, followed by the payload.
- **`OP_PUSHDATA2` (`0x4D`)**: Followed by a 2-byte little-endian unsigned integer specifying length up to 65,535 bytes, followed by the payload.
- **`OP_PUSHDATA4` (`0x4E`)**: Followed by a 4-byte little-endian unsigned integer specifying length up to 4,294,967,295 bytes, followed by the payload.

---

## II. Bytecode Parsing Architecture

To execute or analyze raw scripts, a parser (`BytecodeParser`) must scan the byte stream sequentially using a safe stream reader (`BytesReader`).

- **State Tracking (Program Counter / Offset)**: The parser maintains a position pointer (`pc`) to track the exact byte offset of each token.
- **Tokenization**: Each parsed chunk is converted into a structured `BytecodeToken` containing its original offset, resolved opcode, and optional payload data.
- **Error Safety**: Robust parsers guard against buffer overflows by verifying that remaining bytes match the expected length declared by push headers, raising validation errors if the stream ends unexpectedly.

---

## III. Interpreter Execution Flow & State Management

The **Script Interpreter** executes bytecode instructions sequentially while managing a complex execution context (`ScriptContext`). Key components include:

1. **The Primary Stack & Altstack**:

- The main stack holds data items (signatures, public keys, intermediate calculation results).
- An alternative stack (`altstack`) allows temporary storage using operations like `OP_TOALTSTACK` and `OP_FROMALTSTACK`.

2. **Branch Control (Conditional Execution)**:

- Opcodes like `OP_IF`, `OP_NOTIF`, `OP_ELSE`, and `OP_ENDIF` manage conditional execution blocks.
- A **branch stack** tracks nested execution states. If an outer branch evaluates to false, inner opcodes are skipped rather than executed, ensuring that only active branches modify the stack.

3. **Consensus Limits and Error Codes**:

- The interpreter enforces strict boundaries (e.g., maximum script size, maximum stack depth, and maximum operations per script) to prevent denial-of-service attacks.
- Execution terminates with a specific `ScriptError` (such as `SCRIPT_ERR_OK` on success, or `SCRIPT_ERR_BAD_OPCODE`, `SCRIPT_ERR_STACK_SIZE`, and `SCRIPT_ERR_EVAL_FALSE` on failure).

---

## IV. Assembly-to-Bytecode Translation Example

Consider a standard 20-byte public key hash push in a P2PKH script:

- **Assembly Representation**:
  `0x76a91489abcdef0123456789abcdef0123456789abcdef88ac` (written as hex string)
- **Bytecode Breakdown**:
- `0x76` (`OP_DUP`)
- `0xa9` (`OP_HASH160`)
- `0x14` (Direct push header: length 20 bytes / 0x14)
- `89abcdef0123456789abcdef0123456789abcdef` (20 bytes of payload data)
- `0x88` (`OP_EQUALVERIFY`)
- `0xac` (`OP_CHECKSIG`)
