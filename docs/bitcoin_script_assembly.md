# Bitcoin Script Assembly: Syntax, Structure, and Encoding Guide

Bitcoin Script Assembly is the human-readable representation of Bitcoin scripts. It transforms obscure raw hexadecimal bytecodes into intuitive mnemonics, constant expressions, and data-pushing instructions, serving as a core tool for writing, debugging, and analyzing Bitcoin smart contracts (such as standard transactions, P2SH, SegWit, and Taproot script paths).

---

## I. Core Syntax Elements

In Bitcoin Script Assembly, scripts consist of a sequence of **tokens** separated by whitespace characters (spaces, newlines, etc.). They primarily fall into four basic types:

1. **Opcodes**:

- Mnemonics such as `OP_DUP`, `OP_HASH160`, `OP_EQUALVERIFY`, and `OP_CHECKSIG`.
- Supports abbreviations and aliases—for example, `OP_FALSE` is equivalent to `OP_0`, `OP_TRUE` to `OP_1`, and `OP_NOP2` corresponds to `OP_CHECKLOCKTIMEVERIFY`.
- Omitting the `OP_` prefix is often handled automatically by parsers (e.g., writing `DUP` is recognized as `OP_DUP`).

2. **Hex Data Literals**:

- Hexadecimal strings starting with `0x` or `0X`, such as `0x76a914`.
- **Note**: Hexadecimal digits must have an even length (byte-aligned), otherwise the parser will raise an error. They compile directly into their corresponding raw binary bytes.

3. **Decimal Numbers**:

- Standard integers such as `0`, `1`, `-1`, and `100`.
- **Optimization Mappings**:
- `-1` compiles to `OP_1NEGATE` (`0x4F`).
- Numbers from `0` to `16` typically compile directly to compact opcodes (e.g., `OP_0` through `OP_16`, i.e., `0x00` and `0x51 ~ 0x60`).
- Other values are converted into signed integers of minimal byte length on the stack using **ScriptNum** encoding rules.

4. **Quoted Strings**:

- Text enclosed in single quotes, such as `'Hello Bitcoin'`.
- During compilation, strings are converted into their UTF-8 encoded byte arrays, and an appropriate **`OP_PUSHDATA`** instruction is automatically chosen based on length.

---

## II. Data Pushing & Compilation Mechanics (PushData Operations)

Bitcoin's scripting system revolves around a stack-based calculation model. How are arbitrary-length binary data safely and efficiently pushed onto the stack? The Assembly compiler automatically selects four different underlying push mechanisms based on data length:

| Data Length Range                | Corresponding Instruction / Opcode | Bytecode Structure                                        |
| -------------------------------- | ---------------------------------- | --------------------------------------------------------- |
| **1 ~ 75 bytes**                 | Direct Push                        | `[Length Byte (1B)] + [Data Payload]`                     |
| **76 ~ 255 bytes**               | `OP_PUSHDATA1` (`0x4C`)            | `[0x4C] + [1-byte Length] + [Data Payload]`               |
| **256 ~ 65,535 bytes**           | `OP_PUSHDATA2` (`0x4D`)            | `[0x4D] + [2-byte Little-Endian Length] + [Data Payload]` |
| **65,536 ~ 4,294,967,295 bytes** | `OP_PUSHDATA4` (`0x4E`)            | `[0x4E] + [4-byte Little-Endian Length] + [Data Payload]` |
| **0 bytes (Empty Data)**         | `OP_0` (`0x00`)                    | `[0x00]`                                                  |

---

## III. Typical Script Assembly Examples

### 1. Standard P2PKH (Pay-to-Public-Key-Hash) Locking Script

```assembly
OP_DUP OP_HASH160 0x89abcdef0123456789abcdef0123456789abcdef OP_EQUALVERIFY OP_CHECKSIG

```

- **Meaning**: Duplicates the public key hash on top of the stack, hashes it (SHA256 followed by RIPEMD160), compares it with the given 20-byte public key hash, and verifies the digital signature upon a successful match.

### 2. Combination Script with Constants and Strings

```assembly
'SignHere' 100 OP_ADD 0xdeadbeef

```

- **Meaning**: Pushes the UTF-8 bytes of the string `'SignHere'` onto the stack, encodes and pushes the decimal `100`, executes addition, and finally pushes 4 bytes of hexadecimal data.

---

## IV. Development Best Practices & Common Pitfalls

1. **Minimal Encoding Rule (Minimaldata)**:
   Modern Bitcoin consensus rules (such as `SCRIPT_ERR_MINIMALDATA`) strictly require numbers and data pushes to use the shortest possible encoding format. For instance, the number `1` must use `OP_1` (`0x51`) or a single byte `0x01 0x01` rather than arbitrary multi-byte padding.
2. **Stack Size and Element Limits**:
   Under default consensus limits, a single script element (Push Data) generally cannot exceed **520 bytes** (excluding special upgrades like Taproot), and stack depth is strictly limited (typically to 1,000 items).
