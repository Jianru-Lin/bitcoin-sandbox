# Miniscript: Structure, Analysis, and Policy Compilation in Bitcoin

While raw Bitcoin Script provides Turing-incomplete programmability, writing complex spending conditions manually is notoriously error-prone, hard to analyze, and difficult to compose securely (especially for multisig, time-locks, and threshold logic). **Miniscript** is a language designed to represent Bitcoin scripts in a structured, mathematically sound way, enabling automated analysis, optimal script compilation, and seamless wallet composition.

---

## I. Core Philosophy & Motivation

Before Miniscript, creating a policy involving complex conditions (e.g., _"Spendable by Alice, or by Bob and Charlie after 30 days"_ or _"2-of-3 multisig where any key can be replaced by a recovery key after 90 days"_) required writing raw scripts or relying on ad-hoc script generators. This introduced major risks:

- **Inability to analyze**: Wallets couldn't easily verify if a script was valid, safely spendable, or free from consensus/standardness traps.
- **Composition limits**: Combining two separate scripts securely was nearly impossible without breaking fee estimation or signature correctness.

Miniscript solves this by acting as an intermediate layer between high-level **Policies** and low-level **Bitcoin Scripts**.

---

## II. Miniscript Architecture & Node Types

Miniscript expressions are represented as a tree of typed nodes. Every fragment in Miniscript is assigned a strict type system based on how it behaves during execution:

1. **Type Qualifiers**:

- **`B` (Base)**: Produces a nonzero stack element on success (e.g., `checksig`).
- **`V` (Verify)**: Consumes input and fails on error, leaving nothing on the stack (e.g., `checksigverify`).
- **`K` (Key)**: Pushes a public key onto the stack.
- **`W` (Wrapped)**: Pushes a witness program or operates within specific wrapper contexts.
- **`Z` (Zero-arg / Base)**: Takes no arguments from the stack.

2. **Common Miniscript Operators**:

- **`pk_k(KEY)`**: A public key expression (type `K`).
- **`c:NODE`**: Converts a `K` node into a `B` node using `OP_CHECKSIG`.
- **`and_v(X, Y)`**: Executes `X` (which must be type `V`) and then `Y`.
- **`and_b(X, Y)`**: Combines two `B` expressions using `OP_BOOLAND`.
- **`or_b(X, Y)`**: Logical OR for `B` expressions.
- **`older(TICKS)`**: Relative time-lock using `OP_CHECKSEQUENCEVERIFY`.
- **`after(TIME)`**: Absolute time-lock using `OP_CHECKLOCKTIMEVERIFY`.
- **`thresh(k, [X1, X2, ...])`**: Threshold logic (like multi-signature or conditional paths).

---

## III. Policy to Miniscript Compilation

Users rarely write raw Miniscript syntax directly; instead, they write human-readable **Policies** (similar to logical expressions), which a compiler translates into optimized Miniscript.

- **High-Level Policy Example**:

```text
or(pk(Alice), and(pk(Bob), older(144)))

```

_(Meaning: Alice can spend immediately, or Bob can spend after 144 blocks)._

- **Miniscript Compilation**:
  The compiler analyzes the execution costs, signature requirements, and script size limits to produce the most efficient Miniscript structure, which then compiles directly into standard Bitcoin Script (often natively deployed via SegWit or Taproot).

---

## IV. Key Benefits in Production

1. **Correctness & Soundness**: Miniscript guarantees that a script is free from malleability bugs, invalid branch paths, and stack overflow risks.
2. **Optimal Fee Estimation & Signing**: Because the structure is fully transparent, wallets can precisely calculate the exact witness size and signature weight _before_ broadcasting transactions.
3. **Hardware Wallet Compatibility**: Hardware signers can parse Miniscript descriptors to independently verify the exact spending conditions they are signing, preventing blind-signing attacks.
