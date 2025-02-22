import string
from enum import Enum
from typing import Sequence

from py_flare_common.merkle import MerkleTree, single_hash

ZERO_BYTES_32 = "0000000000000000000000000000000000000000000000000000000000000000"


def un_prefix_0x(s: str) -> str:
    return s.removeprefix("0x")


def is_valid_bytes_32_hex(maybe_hex_string: str):
    maybe_hex_string = un_prefix_0x(maybe_hex_string)
    return len(maybe_hex_string) == 64 and all(c in string.hexdigits for c in maybe_hex_string)


def string_to_ascii_hex(input_string: str) -> str:
    return "".join(format(ord(char), "02x") for char in input_string)


def merkle_tree_from_address_strings(addresses: Sequence[str | None]):
    hashedAddresses = []
    for address in addresses:
        if address is None:
            hashedAddresses.append(ZERO_BYTES_32)
        else:
            hashadd = un_prefix_0x(single_hash(un_prefix_0x(single_hash(string_to_ascii_hex(address)))))
            hashedAddresses.append(hashadd)
    return MerkleTree(hashedAddresses)


class WordToOpcode(Enum):
    # push value
    OP_0 = 0x00
    OP_FALSE = OP_0
    OP_PUSHDATA1 = 0x4C
    OP_PUSHDATA2 = 0x4D
    OP_PUSHDATA4 = 0x4E
    OP_1NEGATE = 0x4F
    OP_RESERVED = 0x50
    OP_1 = 0x51
    OP_TRUE = OP_1
    OP_2 = 0x52
    OP_3 = 0x53
    OP_4 = 0x54
    OP_5 = 0x55
    OP_6 = 0x56
    OP_7 = 0x57
    OP_8 = 0x58
    OP_9 = 0x59
    OP_10 = 0x5A
    OP_11 = 0x5B
    OP_12 = 0x5C
    OP_13 = 0x5D
    OP_14 = 0x5E
    OP_15 = 0x5F
    OP_16 = 0x60

    # control
    OP_NOP = 0x61
    OP_VER = 0x62
    OP_IF = 0x63
    OP_NOTIF = 0x64
    OP_VERIF = 0x65
    OP_VERNOTIF = 0x66
    OP_ELSE = 0x67
    OP_ENDIF = 0x68
    OP_VERIFY = 0x69
    OP_RETURN = 0x6A

    # stack ops
    OP_TOALTSTACK = 0x6B
    OP_FROMALTSTACK = 0x6C
    OP_2DROP = 0x6D
    OP_2DUP = 0x6E
    OP_3DUP = 0x6F
    OP_2OVER = 0x70
    OP_2ROT = 0x71
    OP_2SWAP = 0x72
    OP_IFDUP = 0x73
    OP_DEPTH = 0x74
    OP_DROP = 0x75
    OP_DUP = 0x76
    OP_NIP = 0x77
    OP_OVER = 0x78
    OP_PICK = 0x79
    OP_ROLL = 0x7A
    OP_ROT = 0x7B
    OP_SWAP = 0x7C
    OP_TUCK = 0x7D

    # splice ops
    OP_CAT = 0x7E
    OP_SUBSTR = 0x7F
    OP_LEFT = 0x80
    OP_RIGHT = 0x81
    OP_SIZE = 0x82

    # bit logic
    OP_INVERT = 0x83
    OP_AND = 0x84
    OP_OR = 0x85
    OP_XOR = 0x86
    OP_EQUAL = 0x87
    OP_EQUALVERIFY = 0x88
    OP_RESERVED1 = 0x89
    OP_RESERVED2 = 0x8A

    # numeric
    OP_1ADD = 0x8B
    OP_1SUB = 0x8C
    OP_2MUL = 0x8D
    OP_2DIV = 0x8E
    OP_NEGATE = 0x8F
    OP_ABS = 0x90
    OP_NOT = 0x91
    OP_0NOTEQUAL = 0x92

    OP_ADD = 0x93
    OP_SUB = 0x94
    OP_MUL = 0x95
    OP_DIV = 0x96
    OP_MOD = 0x97
    OP_LSHIFT = 0x98
    OP_RSHIFT = 0x99

    OP_BOOLAND = 0x9A
    OP_BOOLOR = 0x9B
    OP_NUMEQUAL = 0x9C
    OP_NUMEQUALVERIFY = 0x9D
    OP_NUMNOTEQUAL = 0x9E
    OP_LESSTHAN = 0x9F
    OP_GREATERTHAN = 0xA0
    OP_LESSTHANOREQUAL = 0xA1
    OP_GREATERTHANOREQUAL = 0xA2
    OP_MIN = 0xA3
    OP_MAX = 0xA4

    OP_WITHIN = 0xA5

    # crypto
    OP_RIPEMD160 = 0xA6
    OP_SHA1 = 0xA7
    OP_SHA256 = 0xA8
    OP_HASH160 = 0xA9
    OP_HASH256 = 0xAA
    OP_CODESEPARATOR = 0xAB
    OP_CHECKSIG = 0xAC
    OP_CHECKSIGVERIFY = 0xAD
    OP_CHECKMULTISIG = 0xAE
    OP_CHECKMULTISIGVERIFY = 0xAF

    # expansion
    OP_NOP1 = 0xB0
    OP_CHECKLOCKTIMEVERIFY = 0xB1
    OP_NOP2 = OP_CHECKLOCKTIMEVERIFY
    OP_CHECKSEQUENCEVERIFY = 0xB2
    OP_NOP3 = OP_CHECKSEQUENCEVERIFY
    OP_NOP4 = 0xB3
    OP_NOP5 = 0xB4
    OP_NOP6 = 0xB5
    OP_NOP7 = 0xB6
    OP_NOP8 = 0xB7
    OP_NOP9 = 0xB8
    OP_NOP10 = 0xB9

    # Opcode added by BIP 342 (Tapscript)
    OP_CHECKSIGADD = 0xBA

    OP_INVALIDOPCODE = 0xFF
