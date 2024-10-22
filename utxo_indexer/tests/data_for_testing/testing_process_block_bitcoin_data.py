import cattrs

from utxo_indexer.models.types import BlockResponse

# Data for tests:
# test_bitcoin.test_process_block

block_example_bitcoin_dict = {
    "hash": "000000000d84e3cb8f5d1ad8508d0d038a2b0c84e66a29de2773750cb8f6e55a",
    "height": 3193793,
    "mediantime": 1729575626,
    "previousblockhash": "000000000000000f36e2d285c4c510f598f34fd0f41d6291cb54ed1964b90bc1",
    "tx": [
        {
            "txid": "ea57078c1ec6f4670fa3eb49c6486257ba36f9c49a0ad94d3b6cf631a2e92ae5",
            "vin": [
                {
                    "coinbase": "03c1bb3000fe50a90300fe52590b000963676d696e6572343208230000000000000000",
                    "sequence": 4294967295,
                }
            ],
            "vout": [
                {
                    "value": "8.61238437",
                    "n": 0,
                    "scriptPubKey": {
                        "asm": "OP_DUP OP_HASH160 33fbd6484bdeccc064407780ee7dd15fa4ae2536 OP_EQUALVERIFY OP_CHECKSIG",
                        "hex": "76a91433fbd6484bdeccc064407780ee7dd15fa4ae253688ac",
                        "address": "mkFpSnHwyKaoe3PoTeABYjrfeNLha9cJX5",
                        "type": "pubkeyhash",
                        "reqSigs": None,
                    },
                },
                {
                    "value": "0.00000000",
                    "n": 1,
                    "scriptPubKey": {
                        "asm": "OP_RETURN aa21a9edc5c01d953a4723b82cee76ac85a47239e819b8ee7672e2562db2bc927dda6958",
                        "hex": "6a24aa21a9edc5c01d953a4723b82cee76ac85a47239e819b8ee7672e2562db2bc927dda6958",
                        "type": "nulldata",
                        "address": "",
                        "reqSigs": None,
                    },
                },
            ],
        },
        {
            "txid": "cb09112278043f486e0e1b649d58c08e962958f2115d210f82f1ca9a13484ea2",
            "vin": [
                {
                    "txid": "279ea599e880def81e3c15f3aee904fae7d90abcfd73470b581efa192b62c5f6",
                    "vout": 1,
                    "scriptSig": {"asm": "", "hex": ""},
                    "prevout": {
                        "value": "0.83860072",
                        "scriptPubKey": {
                            "asm": "0 fc785d6b5794d47dbd8a1f3fd02dcc0223973695",
                            "hex": "0014fc785d6b5794d47dbd8a1f3fd02dcc0223973695",
                            "address": "tb1ql3u9666hjn28m0v2rulaqtwvqg3ewd543y66dy",
                            "type": "witness_v0_keyhash",
                            "reqSigs": None,
                        },
                    },
                    "sequence": 4294967293,
                }
            ],
            "vout": [
                {
                    "value": "0.82838301",
                    "n": 0,
                    "scriptPubKey": {
                        "asm": "1 a69d33343e6e4e04a2aa6008c45054c06d999b862be0cf63b80a3802a0ae6492",
                        "hex": "5120a69d33343e6e4e04a2aa6008c45054c06d999b862be0cf63b80a3802a0ae6492",
                        "address": "tb1p56wnxdp7de8qfg42vqyvg5z5cpkenxux90sv7cacpguq9g9wvjfqtxshlj",
                        "type": "witness_v1_taproot",
                        "reqSigs": None,
                    },
                },
                {
                    "value": "0.00001000",
                    "n": 1,
                    "scriptPubKey": {
                        "asm": "1 b0a65b220b43d3efc03350cbc1bb8376ef5d6ad482dfaa3e20cedab366902af7",
                        "hex": "5120b0a65b220b43d3efc03350cbc1bb8376ef5d6ad482dfaa3e20cedab366902af7",
                        "address": "tb1pkzn9kgstg0f7lspn2r9urwurwmh466k5st06503qemdtxe5s9tms3afumx",
                        "type": "witness_v1_taproot",
                        "reqSigs": None,
                    },
                },
            ],
        },
    ],
}
block_example_bitcoin = cattrs.structure(block_example_bitcoin_dict, BlockResponse)
