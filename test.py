import unittest
from pathlib import Path

from main import (
    AssemblyParser,
    AssemblyTokenBytes,
    AssemblyTokenInteger,
    AssemblyTokenOpcode,
    AssemblyTokenString,
    Bits,
    BlockHeader,
    BytecodeCompiler,
    BytecodeParser,
    BytecodeToken,
    CompactSize,
    Miner,
    MultiProcessMiner,
    MultiThreadMiner,
    Opcode,
    OpcodeAliases,
    ScriptCrypto,
    ScriptNumDecoder,
    ScriptNumEncoder,
    ScriptStack,
    ScriptTestsLoader,
    ScriptVerifyFlags,
    ScriptVerifyFlagsParser,
)

script_tests_json_file_path = Path(__file__).parent / "script_tests.json"
cases = ScriptTestsLoader.load(script_tests_json_file_path)


class TestOpcode(unittest.TestCase):
    def test_all_opcode_names_are_uppercase(self):
        for name, member in Opcode.__members__.items():
            with self.subTest(opcode_name=name, member=member):
                self.assertTrue(
                    name.isupper(),
                    f"Opcode name '{name}' is not fully uppercase",
                )

    def test_all_opcode_names_start_with_op_prefix(self):
        for name, member in Opcode.__members__.items():
            with self.subTest(opcode_name=name, member=member):
                self.assertTrue(
                    name.startswith("OP_"),
                    f"Opcode name '{name}' does not start with 'OP_'",
                )


class TestOpcodeAlias(unittest.TestCase):
    def test_resolve_name(self):
        self.assertEqual(OpcodeAliases.resolve_name("OP_TRUE"), Opcode.OP_1)
        self.assertEqual(OpcodeAliases.resolve_name("op_true"), Opcode.OP_1)
        self.assertEqual(OpcodeAliases.resolve_name("OP_FALSE"), Opcode.OP_0)
        self.assertEqual(OpcodeAliases.resolve_name("op_false"), Opcode.OP_0)
        self.assertEqual(
            OpcodeAliases.resolve_name("OP_NOP2"), Opcode.OP_CHECKLOCKTIMEVERIFY
        )
        self.assertEqual(
            OpcodeAliases.resolve_name("op_nop2"), Opcode.OP_CHECKLOCKTIMEVERIFY
        )
        self.assertEqual(
            OpcodeAliases.resolve_name("OP_NOP3"), Opcode.OP_CHECKSEQUENCEVERIFY
        )
        self.assertEqual(
            OpcodeAliases.resolve_name("op_nop3"), Opcode.OP_CHECKSEQUENCEVERIFY
        )

    def test_get_alias(self):
        self.assertEqual(OpcodeAliases.get_alias(Opcode.OP_0), "OP_FALSE")
        self.assertEqual(OpcodeAliases.get_alias(Opcode.OP_1), "OP_TRUE")
        self.assertEqual(OpcodeAliases.get_alias(Opcode.OP_2), None)
        self.assertEqual(OpcodeAliases.get_alias(Opcode.OP_3), None)
        self.assertEqual(
            OpcodeAliases.get_alias(Opcode.OP_CHECKLOCKTIMEVERIFY), "OP_NOP2"
        )
        self.assertEqual(
            OpcodeAliases.get_alias(Opcode.OP_CHECKSEQUENCEVERIFY), "OP_NOP3"
        )


class TestBytecodeParser(unittest.TestCase):
    def test_empty_script(self):
        self.assertEqual(BytecodeParser.parse(b""), [])

    def test_single_and_combined_opcodes(self):
        raw = bytes(
            [
                Opcode.OP_DUP,
                Opcode.OP_HASH160,
                Opcode.OP_EQUALVERIFY,
                Opcode.OP_CHECKSIG,
            ]
        )
        expected = [
            BytecodeToken(0, Opcode.OP_DUP),
            BytecodeToken(1, Opcode.OP_HASH160),
            BytecodeToken(2, Opcode.OP_EQUALVERIFY),
            BytecodeToken(3, Opcode.OP_CHECKSIG),
        ]
        self.assertEqual(BytecodeParser.parse(raw), expected)

    def test_direct_pushdata_direct(self):
        raw_4bytes = b"\x04\xde\xad\xbe\xef"
        self.assertEqual(
            BytecodeParser.parse(raw_4bytes),
            [BytecodeToken(0, Opcode.OP_PUSHDATA_DIRECT, b"\xde\xad\xbe\xef")],
        )

        # 75 bytes data
        data_75 = b"A" * 75
        raw_75bytes = b"\x4b" + data_75
        self.assertEqual(
            BytecodeParser.parse(raw_75bytes),
            [BytecodeToken(0, Opcode.OP_PUSHDATA_DIRECT, data_75)],
        )

    def test_pushdata1(self):
        data_80 = b"B" * 80
        raw = b"\x4c\x50" + data_80
        self.assertEqual(
            BytecodeParser.parse(raw), [BytecodeToken(0, Opcode.OP_PUSHDATA1, data_80)]
        )

    # def test_unknown_opcode_raises_error(self):
    #     raw = bytes([0x76, 0xA9, 0xFF, 0x88])
    #     with self.assertRaises(ValueError) as ctx:
    #         _ = parse(raw)

    #     self.assertIn("0xFF", str(ctx.exception))
    #     self.assertIn("offset 2", str(ctx.exception))


class TestAssemblyParser(unittest.TestCase):
    def test_tokenize_empty(self):
        self.assertEqual(AssemblyParser.tokenize(""), [])

    def test_tokenize_integer(self):
        self.assertEqual(
            AssemblyParser.tokenize("1"),
            [
                AssemblyTokenInteger(raw_text="1", value=1),
            ],
        )
        self.assertEqual(
            AssemblyParser.tokenize("-1"),
            [
                AssemblyTokenInteger(raw_text="-1", value=-1),
            ],
        )
        self.assertEqual(
            AssemblyParser.tokenize("+1"),
            [
                AssemblyTokenInteger(raw_text="+1", value=1),
            ],
        )

    def test_tokenize_bytes(self):
        self.assertEqual(
            AssemblyParser.tokenize("0x"),
            [
                AssemblyTokenBytes(raw_text="0x", data=b""),
            ],
        )
        self.assertEqual(
            AssemblyParser.tokenize("0xff"),
            [
                AssemblyTokenBytes(raw_text="0xff", data=bytes.fromhex("ff")),
            ],
        )

    def test_tokenize_string(self):
        self.assertEqual(
            AssemblyParser.tokenize("'hello world'"),
            [
                AssemblyTokenString(raw_text="'hello world'", data=b"hello world"),
            ],
        )

    def test_tokenize_opcode(self):
        self.assertEqual(
            AssemblyParser.tokenize("OP_DUP"),
            [
                AssemblyTokenOpcode(raw_text="OP_DUP", opcode=Opcode.OP_DUP),
            ],
        )
        self.assertEqual(
            AssemblyParser.tokenize("op_dup"),
            [
                AssemblyTokenOpcode(raw_text="op_dup", opcode=Opcode.OP_DUP),
            ],
        )
        self.assertEqual(
            AssemblyParser.tokenize("DUP"),
            [
                AssemblyTokenOpcode(raw_text="DUP", opcode=Opcode.OP_DUP),
            ],
        )
        self.assertEqual(
            AssemblyParser.tokenize("dup"),
            [
                AssemblyTokenOpcode(raw_text="dup", opcode=Opcode.OP_DUP),
            ],
        )

    def test_tokenize_opcode_alias(self):
        self.assertEqual(
            AssemblyParser.tokenize("OP_TRUE"),
            [
                AssemblyTokenOpcode(raw_text="OP_TRUE", opcode=Opcode.OP_1),
            ],
        )
        self.assertEqual(
            AssemblyParser.tokenize("OP_FALSE"),
            [
                AssemblyTokenOpcode(raw_text="OP_FALSE", opcode=Opcode.OP_0),
            ],
        )
        self.assertEqual(
            AssemblyParser.tokenize("OP_NOP2"),
            [
                AssemblyTokenOpcode(
                    raw_text="OP_NOP2", opcode=Opcode.OP_CHECKLOCKTIMEVERIFY
                ),
            ],
        )
        self.assertEqual(
            AssemblyParser.tokenize("OP_NOP3"),
            [
                AssemblyTokenOpcode(
                    raw_text="OP_NOP3", opcode=Opcode.OP_CHECKSEQUENCEVERIFY
                ),
            ],
        )

    def test_tokenize_unknown(self):
        with self.assertRaises(ValueError):
            _ = AssemblyParser.tokenize("OP_")

        with self.assertRaises(ValueError):
            _ = AssemblyParser.tokenize("OP_XXX")

        with self.assertRaises(ValueError):
            _ = AssemblyParser.tokenize("XXX")

    def test_tokenize_opcode_blacklist(self):
        with self.assertRaises(ValueError):
            _ = AssemblyParser.tokenize("OP_PUSHDATA_DIRECT")

    def test_parse_empty(self):
        self.assertEqual(AssemblyParser.parse(""), b"")
        self.assertEqual(AssemblyParser.parse("0x"), b"")
        self.assertEqual(AssemblyParser.parse("0x 0x"), b"")

    def test_parse_string(self):
        self.assertEqual(AssemblyParser.parse("''"), b"\x00")
        self.assertEqual(AssemblyParser.parse("'a'"), b"\x01" + b"a")
        self.assertEqual(AssemblyParser.parse("'😄'"), b"\x04" + "😄".encode())

    def test_parse_decimal(self):
        self.assertEqual(AssemblyParser.parse("0"), b"\x00")

    def test_parse_hex(self):
        self.assertEqual(AssemblyParser.parse("0x"), b"")
        self.assertEqual(AssemblyParser.parse("0x00"), b"\x00")
        self.assertEqual(AssemblyParser.parse("0x00 0x01"), b"\x00\x01")
        self.assertEqual(AssemblyParser.parse("0x0001"), b"\x00\x01")

    def test_parse_opcode(self):
        self.assertEqual(AssemblyParser.parse("OP_DUP"), bytes([Opcode.OP_DUP.value]))
        self.assertEqual(AssemblyParser.parse("DUP"), bytes([Opcode.OP_DUP.value]))

    def test_parse_simple(self):
        self.assertEqual(
            AssemblyParser.parse("1 1 OP_ADD"),
            b"\x51\x51\x93",
        )
        self.assertEqual(
            AssemblyParser.parse("1 1 OP_ADD"),
            BytecodeCompiler.compile(
                [
                    BytecodeToken(offset=0, opcode=Opcode.OP_1),
                    BytecodeToken(offset=1, opcode=Opcode.OP_1),
                    BytecodeToken(offset=2, opcode=Opcode.OP_ADD),
                ]
            ),
        )


class TestAssemblyParserWithTestCases(unittest.TestCase):
    def test_parse_all_script_cases(self) -> None:
        self.assertGreater(len(cases), 0, "No test cases loaded.")

        for idx, case in enumerate(cases):
            # TODO skip
            if (
                "#TAPROOTOUTPUT#" in case.script_sig
                or "#TAPROOTOUTPUT#" in case.script_pubkey
            ):
                continue

            with self.subTest(
                index=idx,
                field="script_sig",
                script=case.script_sig,
                comment=case.comments,
            ):
                compiled_sig = AssemblyParser.parse(case.script_sig)
                self.assertIsInstance(compiled_sig, bytes)

            with self.subTest(
                index=idx,
                field="script_pubkey",
                script=case.script_pubkey,
                comment=case.comments,
            ):
                compiled_pk = AssemblyParser.parse(case.script_pubkey)
                self.assertIsInstance(compiled_pk, bytes)


class TestScriptNumDecoder(unittest.TestCase):
    def test_decode(self):
        cases = [
            (bytes([]), 0),
            (bytes([0b0000_0001]), 1),
            (bytes([0b1000_0001]), -1),
            (bytes([0b0000_0010]), 2),
            (bytes([0b1000_0010]), -2),
            (bytes([0b1000_0000, 0b0000_0000]), 128),
            (bytes([0b1000_0000, 0b1000_0000]), -128),  # failed here
        ]
        for raw_bytes, expected_val in cases:
            with self.subTest(raw_bytes=raw_bytes, expected_val=expected_val):
                self.assertEqual(
                    ScriptNumDecoder.decode(
                        raw_bytes, require_minimal=True, max_size=4
                    ),
                    expected_val,
                )

    def test_is_minimal(self):
        cases = [
            (bytes([]), True),  # +0 (correct)
            (bytes([0b0000_0000]), False),  # +0 (incorrect)
            (bytes([0b1000_0000]), False),  # -0 (incorrect)
            (bytes([0b0000_0001]), True),  # 1 (correct)
            (bytes([0b0000_0001, 0b0000_0000]), False),  # 1 (incorrect)
            (bytes([0b1000_0001]), True),  # -1 (correct)
            (bytes([0b1000_0001, 0b0000_0000]), True),  # 129 (correct)
            (bytes([0b0111_1111]), True),
        ]
        for raw_bytes, expected_valid in cases:
            with self.subTest(raw_bytes=raw_bytes, expected_valid=expected_valid):
                self.assertIs(ScriptNumDecoder.is_minimal(raw_bytes), expected_valid)


class TestScriptStack(unittest.TestCase):
    def test_len(self):
        self.assertEqual(len(ScriptStack()), 0)
        self.assertEqual(len(ScriptStack([])), 0)
        self.assertEqual(len(ScriptStack([b""])), 1)
        self.assertEqual(len(ScriptStack([b"\x00"])), 1)
        self.assertEqual(len(ScriptStack([b"\x00", b"\x00"])), 2)

    def test_bool(self):
        self.assertEqual(bool(ScriptStack()), False)
        self.assertEqual(bool(ScriptStack([])), False)
        self.assertEqual(bool(ScriptStack([b""])), True)
        self.assertEqual(bool(ScriptStack([b"\x00"])), True)
        self.assertEqual(bool(ScriptStack([b"\x00", b"\x00"])), True)

    def test_repr(self):
        self.assertEqual(repr(ScriptStack()), r"ScriptStack([])")
        self.assertEqual(repr(ScriptStack([])), r"ScriptStack([])")
        self.assertEqual(repr(ScriptStack([b""])), r"ScriptStack([b''])")
        self.assertEqual(repr(ScriptStack([b"\x00"])), r"ScriptStack([b'\x00'])")
        self.assertEqual(
            repr(ScriptStack([b"\x00", b"\x01"])), r"ScriptStack([b'\x00', b'\x01'])"
        )

    def test_push(self):
        stack = ScriptStack()
        self.assertEqual(len(stack), 0)
        stack.push(b"")
        self.assertEqual(len(stack), 1)
        stack.push(b"")
        self.assertEqual(len(stack), 2)

    def test_pop_empty(self):
        stack = ScriptStack()
        with self.assertRaises(ValueError):
            _ = stack.pop()

    def test_push_pop(self):
        stack = ScriptStack()
        self.assertEqual(len(stack), 0)
        stack.push(b"\x01")
        self.assertEqual(len(stack), 1)
        stack.push(b"\x02")
        self.assertEqual(len(stack), 2)
        self.assertEqual(stack.pop(), b"\x02")
        self.assertEqual(len(stack), 1)
        self.assertEqual(stack.pop(), b"\x01")
        self.assertEqual(len(stack), 0)

    def test_peek_empty(self):
        stack = ScriptStack()
        with self.assertRaises(ValueError):
            _ = stack.peek(0)

    def test_push_peek(self):
        stack = ScriptStack()
        self.assertEqual(len(stack), 0)
        stack.push(b"\x01")
        self.assertEqual(len(stack), 1)
        stack.push(b"\x02")
        self.assertEqual(len(stack), 2)
        self.assertEqual(stack.peek(0), b"\x02")
        self.assertEqual(stack.peek(1), b"\x01")

    def test_clone_empty(self):
        stack1 = ScriptStack()
        stack2 = stack1.clone()
        self.assertIsNot(stack1, stack2)

    def test_clone(self):
        stack1 = ScriptStack()
        stack1.push(b"\x01")
        stack2 = stack1.clone()
        stack2.push(b"\x02")
        self.assertIsNot(stack1, stack2)
        self.assertEqual(len(stack1), 1)
        self.assertEqual(len(stack2), 2)
        self.assertEqual(stack1.peek(0), b"\x01")
        self.assertEqual(stack2.peek(0), b"\x02")

    def test_remove_at_empty(self):
        stack = ScriptStack()
        with self.assertRaises(ValueError):
            _ = stack.remove_at(0)

    def test_remove_at_0(self):
        stack = ScriptStack()
        stack.push(b"\x01")
        stack.push(b"\x02")
        stack.push(b"\x03")
        self.assertEqual(len(stack), 3)
        self.assertEqual(stack.remove_at(0), b"\x03")
        self.assertEqual(len(stack), 2)
        self.assertEqual(stack.remove_at(0), b"\x02")
        self.assertEqual(len(stack), 1)
        self.assertEqual(stack.remove_at(0), b"\x01")
        self.assertEqual(len(stack), 0)

    def test_remove_at_1(self):
        stack = ScriptStack()
        stack.push(b"\x01")
        stack.push(b"\x02")
        stack.push(b"\x03")
        self.assertEqual(len(stack), 3)
        self.assertEqual(stack.remove_at(1), b"\x02")
        self.assertEqual(stack.peek(0), b"\x03")
        self.assertEqual(stack.peek(1), b"\x01")

    def test_remove_at_2(self):
        stack = ScriptStack()
        stack.push(b"\x01")
        stack.push(b"\x02")
        stack.push(b"\x03")
        self.assertEqual(len(stack), 3)
        self.assertEqual(stack.remove_at(2), b"\x01")
        self.assertEqual(stack.peek(0), b"\x03")
        self.assertEqual(stack.peek(1), b"\x02")

    def test_insert_at_empty(self):
        stack = ScriptStack()
        stack.insert_at(0, b"\x00")
        self.assertEqual(len(stack), 1)
        self.assertEqual(stack.peek(0), b"\x00")

    def test_insert_at_0(self):
        stack = ScriptStack()
        stack.push(b"\x01")
        stack.push(b"\x02")
        stack.push(b"\x03")
        self.assertEqual(len(stack), 3)
        stack.insert_at(0, b"\x04")
        self.assertEqual(len(stack), 4)
        self.assertEqual(stack.peek(0), b"\x04")
        self.assertEqual(stack.peek(1), b"\x03")
        self.assertEqual(stack.peek(2), b"\x02")
        self.assertEqual(stack.peek(3), b"\x01")

    def test_insert_at_1(self):
        stack = ScriptStack()
        stack.push(b"\x01")
        stack.push(b"\x02")
        stack.push(b"\x03")
        self.assertEqual(len(stack), 3)
        stack.insert_at(1, b"\x04")
        self.assertEqual(len(stack), 4)
        self.assertEqual(stack.peek(0), b"\x03")
        self.assertEqual(stack.peek(1), b"\x04")
        self.assertEqual(stack.peek(2), b"\x02")
        self.assertEqual(stack.peek(3), b"\x01")

    def test_insert_at_2(self):
        stack = ScriptStack()
        stack.push(b"\x01")
        stack.push(b"\x02")
        stack.push(b"\x03")
        self.assertEqual(len(stack), 3)
        stack.insert_at(2, b"\x04")
        self.assertEqual(len(stack), 4)
        self.assertEqual(stack.peek(0), b"\x03")
        self.assertEqual(stack.peek(1), b"\x02")
        self.assertEqual(stack.peek(2), b"\x04")
        self.assertEqual(stack.peek(3), b"\x01")

    def test_insert_at_3(self):
        stack = ScriptStack()
        stack.push(b"\x01")
        stack.push(b"\x02")
        stack.push(b"\x03")
        self.assertEqual(len(stack), 3)
        stack.insert_at(3, b"\x04")
        self.assertEqual(len(stack), 4)
        self.assertEqual(stack.peek(0), b"\x03")
        self.assertEqual(stack.peek(1), b"\x02")
        self.assertEqual(stack.peek(2), b"\x01")
        self.assertEqual(stack.peek(3), b"\x04")

    def test_push_bool_pop_bool(self):
        stack = ScriptStack()
        stack.push_bool(True)
        self.assertEqual(len(stack), 1)
        self.assertEqual(stack.pop_bool(), True)
        self.assertEqual(len(stack), 0)
        stack.push_bool(False)
        self.assertEqual(len(stack), 1)
        self.assertEqual(stack.pop_bool(), False)
        self.assertEqual(len(stack), 0)

    def test_push_num_pop_num(self):
        stack = ScriptStack()
        stack.push_num(0)
        self.assertEqual(len(stack), 1)
        self.assertEqual(stack.pop_num(require_minimal=True, max_size=4), 0)
        self.assertEqual(len(stack), 0)
        stack.push_num(1)
        self.assertEqual(len(stack), 1)
        self.assertEqual(stack.pop_num(require_minimal=True, max_size=4), 1)
        self.assertEqual(len(stack), 0)


class TestScriptVerifyFlagsParser(unittest.TestCase):
    def test_parse_empty(self):
        self.assertEqual(ScriptVerifyFlagsParser.parse(""), ScriptVerifyFlags.NONE)

    def test_parse_none(self):
        self.assertEqual(ScriptVerifyFlagsParser.parse("NONE"), ScriptVerifyFlags.NONE)
        self.assertEqual(ScriptVerifyFlagsParser.parse("NONE,"), ScriptVerifyFlags.NONE)

    def test_parse_flags(self):
        for flag in ScriptVerifyFlags:
            assert flag.name is not None
            self.assertEqual(
                ScriptVerifyFlagsParser.parse(flag.name), ScriptVerifyFlags[flag.name]
            )
            self.assertEqual(
                ScriptVerifyFlagsParser.parse(f"{flag.name},"),
                ScriptVerifyFlags[flag.name],
            )
            self.assertEqual(
                ScriptVerifyFlagsParser.parse(f",{flag.name}"),
                ScriptVerifyFlags[flag.name],
            )


class TestScriptTestsLoader(unittest.TestCase):
    def test_load(self):
        _ = ScriptTestsLoader.load(script_tests_json_file_path)


class TestScriptCrypto(unittest.TestCase):
    def test_sha1(self):
        data = b""
        expected = bytes.fromhex("da39a3ee5e6b4b0d3255bfef95601890afd80709")
        self.assertEqual(ScriptCrypto.sha1(data), expected)

    def test_sha256(self):
        data = b""
        expected = bytes.fromhex(
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        )
        self.assertEqual(ScriptCrypto.sha256(data), expected)

    def test_hash256(self):
        data = b""
        expected = bytes.fromhex(
            "5df6e0e2761359d30a8275058e299fcc0381534545f55cf43e41983f5d4c9456"
        )
        self.assertEqual(ScriptCrypto.hash256(data), expected)

    def test_ripemd160(self):
        data = b""
        expected = bytes.fromhex("9c1185a5c5e9fc54612808977ee8f548b2258d31")
        self.assertEqual(ScriptCrypto.ripemd160(data), expected)

    def test_hash160(self):
        data = b""
        expected = bytes.fromhex("b472a266d0bd89c13706a4132ccfb16f7c3b9fcb")
        self.assertEqual(ScriptCrypto.hash160(data), expected)


class TestBits(unittest.TestCase):
    def test_decode(self):
        self.assertEqual(
            Bits.decode(bytes.fromhex("ffff001d")),
            Bits(base=0x00FFFF, scale=0x1D),
        )

    def test_parse(self):
        self.assertEqual(
            Bits.decode_from_bytes_string("ffff001d"),
            Bits(base=0x00FFFF, scale=0x1D),
        )
        self.assertEqual(
            Bits.decode_from_int(0x1D00FFFF),
            Bits(base=0x00FFFF, scale=0x1D),
        )

    def test_parse_bytes_string(self):
        self.assertEqual(
            Bits.decode_from_bytes_string("ffff001d"),
            Bits(base=0x00FFFF, scale=0x1D),
        )

    def test_parse_int(self):
        self.assertEqual(
            Bits.decode_from_int(0x1D00FFFF),
            Bits(base=0x00FFFF, scale=0x1D),
        )

    def test_to_target_bytes(self):
        self.assertEqual(
            Bits(base=0x000001, scale=0x03).to_target_bytes(),
            bytes.fromhex(
                "0100000000000000000000000000000000000000000000000000000000000000"
            ),
        )

    def test_to_target_hex_big_endian(self):
        self.assertEqual(
            Bits(base=0x000001, scale=0x03).to_target_hex_big_endian(),
            "0000000000000000000000000000000000000000000000000000000000000001",
        )

    def test_to_difficulty(self):
        mainnet_genesis_bits = Bits.decode_from_int(0x1D00FFFF)

        self.assertEqual(
            Bits.decode(bytes.fromhex("ffff001d")).to_difficulty(
                reference_target=mainnet_genesis_bits.to_target()
            ),
            1,
        )
        self.assertEqual(
            Bits.decode_from_int(0x1C2A1115).to_difficulty(
                reference_target=mainnet_genesis_bits.to_target()
            ),
            6.085476906000794,
        )


class TestMiner(unittest.TestCase):
    def test_validate_genesis_block_header(self):
        genesis_header_hex = "0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a29ab5f49ffff001d1dac2b7c"
        genesis_header_bytes = bytes.fromhex(genesis_header_hex)
        genesis_header = BlockHeader.decode_from_bytes(genesis_header_bytes)
        self.assertTrue(
            Miner.validate(
                header_without_nonce=genesis_header.encode_without_nonce_to_bytes(),
                nonce=genesis_header.nonce,
                target=genesis_header.bits.to_target(),
            )
        )

    def test_validate_block_header_1(self):
        block_header_1_hex = "010000006fe28c0ab6f1b372c1a6a246ae63f74f931e8365e15a089c68d6190000000000982051fd1e4ba744bbbe680e1fee14677ba1a3c3540bf7b1cdb606e857233e0e61bc6649ffff001d01e36299"
        block_header_1_bytes = bytes.fromhex(block_header_1_hex)
        block_header_1 = BlockHeader.decode_from_bytes(block_header_1_bytes)
        self.assertTrue(
            Miner.validate(
                header_without_nonce=block_header_1.encode_without_nonce_to_bytes(),
                nonce=block_header_1.nonce,
                target=block_header_1.bits.to_target(),
            )
        )

    def test_mine_genesis_block_next(self):
        genesis_header_hex = "0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a29ab5f49ffff001d1dac2b7c"
        genesis_header_bytes = bytes.fromhex(genesis_header_hex)
        genesis_header = BlockHeader.decode_from_bytes(genesis_header_bytes)
        mined_nonce = Miner.mine(
            header_without_nonce=genesis_header.encode_without_nonce_to_bytes(),
            target=genesis_header.bits.to_target(),
            start_nonce=2083236800,
            end_nonce=2083237000,
        )
        self.assertIsNotNone(mined_nonce)
        assert mined_nonce is not None
        self.assertTrue(
            Miner.validate(
                header_without_nonce=genesis_header.encode_without_nonce_to_bytes(),
                nonce=mined_nonce,
                target=genesis_header.bits.to_target(),
            )
        )


class TestMultiThreadMiner(unittest.TestCase):
    def test_mine_genesis_block_next_num_threads_0(self):
        genesis_header_hex = "0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a29ab5f49ffff001d1dac2b7c"
        genesis_header_bytes = bytes.fromhex(genesis_header_hex)
        genesis_header = BlockHeader.decode_from_bytes(genesis_header_bytes)
        mined_nonce = MultiThreadMiner.mine(
            header_without_nonce=genesis_header.encode_without_nonce_to_bytes(),
            target=genesis_header.bits.to_target(),
            start_nonce=2083236800,
            end_nonce=2083237000,
            num_threads=0,
        )
        self.assertIsNone(mined_nonce)

    def test_mine_genesis_block_next_num_threads_1(self):
        genesis_header_hex = "0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a29ab5f49ffff001d1dac2b7c"
        genesis_header_bytes = bytes.fromhex(genesis_header_hex)
        genesis_header = BlockHeader.decode_from_bytes(genesis_header_bytes)
        mined_nonce = MultiThreadMiner.mine(
            header_without_nonce=genesis_header.encode_without_nonce_to_bytes(),
            target=genesis_header.bits.to_target(),
            start_nonce=2083236800,
            end_nonce=2083237000,
            num_threads=1,
        )
        self.assertIsNotNone(mined_nonce)
        assert mined_nonce is not None
        self.assertTrue(
            Miner.validate(
                header_without_nonce=genesis_header.encode_without_nonce_to_bytes(),
                nonce=mined_nonce,
                target=genesis_header.bits.to_target(),
            )
        )

    def test_mine_genesis_block_next_num_threads_2(self):
        genesis_header_hex = "0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a29ab5f49ffff001d1dac2b7c"
        genesis_header_bytes = bytes.fromhex(genesis_header_hex)
        genesis_header = BlockHeader.decode_from_bytes(genesis_header_bytes)
        mined_nonce = MultiThreadMiner.mine(
            header_without_nonce=genesis_header.encode_without_nonce_to_bytes(),
            target=genesis_header.bits.to_target(),
            start_nonce=2083236800,
            end_nonce=2083237000,
            num_threads=2,
        )
        self.assertIsNotNone(mined_nonce)
        assert mined_nonce is not None
        self.assertTrue(
            Miner.validate(
                header_without_nonce=genesis_header.encode_without_nonce_to_bytes(),
                nonce=mined_nonce,
                target=genesis_header.bits.to_target(),
            )
        )


#
#     def test_mine_genesis_block_next_num_threads_8(self):
#         genesis_header_hex = "0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a29ab5f49ffff001d1dac2b7c"
#         genesis_header_bytes = bytes.fromhex(genesis_header_hex)
#         genesis_header = BlockHeader.decode(genesis_header_bytes)
#         mined_nonce = MultiThreadMiner.mine(
#             header_without_nonce=genesis_header.encode_without_nonce(),
#             target=genesis_header.bits.to_target(),
#             start_nonce=0,
#             end_nonce=2**32,
#             num_threads=8,
#         )
#         self.assertIsNotNone(mined_nonce)
#         assert mined_nonce is not None
#         self.assertTrue(
#             Miner.validate(
#                 header_without_nonce=genesis_header.encode_without_nonce(),
#                 nonce=mined_nonce,
#                 target=genesis_header.bits.to_target(),
#             )
#         )


class TestMultiProcessMiner(unittest.TestCase):
    def test_mine_genesis_block_next_num_processes_0(self):
        genesis_header_hex = "0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a29ab5f49ffff001d1dac2b7c"
        genesis_header_bytes = bytes.fromhex(genesis_header_hex)
        genesis_header = BlockHeader.decode_from_bytes(genesis_header_bytes)
        mined_nonce = MultiProcessMiner.mine(
            header_without_nonce=genesis_header.encode_without_nonce_to_bytes(),
            target=genesis_header.bits.to_target(),
            start_nonce=2083236800,
            end_nonce=2083237000,
            num_processes=0,
        )
        self.assertIsNone(mined_nonce)

    def test_mine_genesis_block_next_num_processes_1(self):
        genesis_header_hex = "0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a29ab5f49ffff001d1dac2b7c"
        genesis_header_bytes = bytes.fromhex(genesis_header_hex)
        genesis_header = BlockHeader.decode_from_bytes(genesis_header_bytes)
        mined_nonce = MultiProcessMiner.mine(
            header_without_nonce=genesis_header.encode_without_nonce_to_bytes(),
            target=genesis_header.bits.to_target(),
            start_nonce=2083236800,
            end_nonce=2083237000,
            num_processes=1,
        )
        self.assertIsNotNone(mined_nonce)
        assert mined_nonce is not None
        self.assertTrue(
            Miner.validate(
                header_without_nonce=genesis_header.encode_without_nonce_to_bytes(),
                nonce=mined_nonce,
                target=genesis_header.bits.to_target(),
            )
        )

    def test_mine_genesis_block_next_num_processes_2(self):
        genesis_header_hex = "0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a29ab5f49ffff001d1dac2b7c"
        genesis_header_bytes = bytes.fromhex(genesis_header_hex)
        genesis_header = BlockHeader.decode_from_bytes(genesis_header_bytes)
        mined_nonce = MultiProcessMiner.mine(
            header_without_nonce=genesis_header.encode_without_nonce_to_bytes(),
            target=genesis_header.bits.to_target(),
            start_nonce=2083236800,
            end_nonce=2083237000,
            num_processes=2,
        )
        self.assertIsNotNone(mined_nonce)
        assert mined_nonce is not None
        self.assertTrue(
            Miner.validate(
                header_without_nonce=genesis_header.encode_without_nonce_to_bytes(),
                nonce=mined_nonce,
                target=genesis_header.bits.to_target(),
            )
        )

    def test_mine_genesis_block_next_num_processes_8(self):
        genesis_header_hex = "0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a29ab5f49ffff001d1dac2b7c"
        genesis_header_bytes = bytes.fromhex(genesis_header_hex)
        genesis_header = BlockHeader.decode_from_bytes(genesis_header_bytes)
        mined_nonce = MultiProcessMiner.mine(
            header_without_nonce=genesis_header.encode_without_nonce_to_bytes(),
            target=genesis_header.bits.to_target(),
            start_nonce=2083236800,
            end_nonce=2083237000,
            # start_nonce=0,
            # end_nonce=2**32,
            num_processes=8,
        )
        self.assertIsNotNone(mined_nonce)
        assert mined_nonce is not None
        self.assertTrue(
            Miner.validate(
                header_without_nonce=genesis_header.encode_without_nonce_to_bytes(),
                nonce=mined_nonce,
                target=genesis_header.bits.to_target(),
            )
        )


class TestBlockHeader(unittest.TestCase):
    def test_decode_genesis_block_header(self):
        genesis_header_hex = "0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a29ab5f49ffff001d1dac2b7c"
        genesis_header_bytes = bytes.fromhex(genesis_header_hex)
        header = BlockHeader.decode_from_bytes(genesis_header_bytes)
        self.assertEqual(header.version, 1)
        self.assertEqual(header.prev_block_hash, b"\x00" * 32)
        self.assertEqual(
            header.merkle_root,
            (
                0x4A5E1E4BAAB89F3A32518A88C31BC87F618F76673E2CC77AB2127B7AFDEDA33B
            ).to_bytes(32, byteorder="little"),
        )
        self.assertEqual(header.timestamp, 1231006505)
        self.assertEqual(header.bits, Bits.decode_from_int(0x1D00FFFF))
        self.assertEqual(header.nonce, 0x7C2BAC1D)


class TestCompactSize(unittest.TestCase):
    def test_encode_underflow(self):
        with self.assertRaises(ValueError):
            _ = CompactSize.encode_to_bytes(-1)

    def test_encode_overflow(self):
        with self.assertRaises(ValueError):
            _ = CompactSize.encode_to_bytes(0xFFFF_FFFF_FFFF_FFFF + 1)

    def test_encode(self):
        self.assertEqual(CompactSize.encode_to_bytes(0), b"\x00")
        self.assertEqual(CompactSize.encode_to_bytes(1), b"\x01")
        self.assertEqual(CompactSize.encode_to_bytes(0xFC), b"\xfc")
        self.assertEqual(CompactSize.encode_to_bytes(0xFD), b"\xfd\xfd\x00")
        self.assertEqual(CompactSize.encode_to_bytes(0xFFFE), b"\xfd\xfe\xff")
        self.assertEqual(CompactSize.encode_to_bytes(0xFFFF), b"\xfd\xff\xff")
        self.assertEqual(
            CompactSize.encode_to_bytes(0x0001_0000), b"\xfe\x00\x00\x01\x00"
        )
        self.assertEqual(
            CompactSize.encode_to_bytes(0xFFFF_FFFE), b"\xfe\xfe\xff\xff\xff"
        )
        self.assertEqual(
            CompactSize.encode_to_bytes(0xFFFF_FFFF), b"\xfe\xff\xff\xff\xff"
        )
        self.assertEqual(
            CompactSize.encode_to_bytes(0x0000_0001_0000_0000),
            b"\xff\x00\x00\x00\x00\x01\x00\x00\x00",
        )
        self.assertEqual(
            CompactSize.encode_to_bytes(0xFFFF_FFFF_FFFF_FFFE),
            b"\xff\xfe\xff\xff\xff\xff\xff\xff\xff",
        )
        self.assertEqual(
            CompactSize.encode_to_bytes(0xFFFF_FFFF_FFFF_FFFF),
            b"\xff\xff\xff\xff\xff\xff\xff\xff\xff",
        )

    def test_decode(self):
        self.assertEqual(CompactSize.decode_from_bytes(b"\x00"), 0)
        self.assertEqual(CompactSize.decode_from_bytes(b"\x01"), 1)
        self.assertEqual(CompactSize.decode_from_bytes(b"\xfc"), 0xFC)
        self.assertEqual(CompactSize.decode_from_bytes(b"\xfd\xfd\x00"), 0xFD)
        self.assertEqual(CompactSize.decode_from_bytes(b"\xfd\xfe\xff"), 0xFFFE)
        self.assertEqual(CompactSize.decode_from_bytes(b"\xfd\xff\xff"), 0xFFFF)
        self.assertEqual(
            CompactSize.decode_from_bytes(b"\xfe\x00\x00\x01\x00"), 0x0001_0000
        )
        self.assertEqual(
            CompactSize.decode_from_bytes(b"\xfe\xfe\xff\xff\xff"), 0xFFFF_FFFE
        )
        self.assertEqual(
            CompactSize.decode_from_bytes(b"\xfe\xff\xff\xff\xff"), 0xFFFF_FFFF
        )
        self.assertEqual(
            CompactSize.decode_from_bytes(b"\xff\x00\x00\x00\x00\x01\x00\x00\x00"),
            0x0000_0001_0000_0000,
        )
        self.assertEqual(
            CompactSize.decode_from_bytes(b"\xff\xfe\xff\xff\xff\xff\xff\xff\xff"),
            0xFFFF_FFFF_FFFF_FFFE,
        )
        self.assertEqual(
            CompactSize.decode_from_bytes(b"\xff\xff\xff\xff\xff\xff\xff\xff\xff"),
            0xFFFF_FFFF_FFFF_FFFF,
        )


if __name__ == "__main__":
    _ = unittest.main(verbosity=2)
