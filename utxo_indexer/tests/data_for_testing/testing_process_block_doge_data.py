import cattrs

from utxo_indexer.models.types import BlockResponse, TransactionResponse

# Data for tests:
# test_doge.test_process_block

block_example_doge_dict = {
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
                        "reqSigs": 4,
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
                        "reqSigs": 12,
                    },
                },
            ],
        },
        {
            "txid": "cb09112278043f486e0e1b649d58c08e962958f2115d210f82f1ca9a13484ea2",
            "vin": [
                {
                    "txid": "279ea599e880def81e3c15f3aee904fae7d90abcfd73470b581efa192b62c5f6",
                    "vout": 0,
                    "scriptSig": {"asm": "", "hex": ""},
                    "prevout": None,
                    "sequence": 4294967293,
                },
                {
                    "txid": "432423423435gfdgbdrgdgdg97dg9d8g7dgudvg98dfgddg9u80808078bbz988d",
                    "vout": 0,
                    "scriptSig": {"asm": "", "hex": ""},
                    "prevout": None,
                    "sequence": 4294967293,
                },
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
                        "reqSigs": 3,
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
                        "reqSigs": 12,
                    },
                },
            ],
        },
    ],
}
block_example_doge = cattrs.structure(block_example_doge_dict, BlockResponse)


tx_example1_doge_dict = {
    "txid": "279ea599e880def81e3c15f3aee904fae7d90abcfd73470b581efa192b62c5f6",
    "vin": [
        {
            "txid": "fde8896126ed1f46fac9c6761e08fdcfb3455a7a6c474e6a3d147096e84bd705",
            "vout": 1,
            "scriptSig": {
                "asm": "3045022100afade3d747b83907f54208ca16621d08c6c3f1929122418b32fc1414cf3aef620220137f313a3bd61a59748837483329b7c15d627ed0a48ef50d03e847cf7fa39160[ALL] 029aef52532c0f5d1025ae033712e4c390194aec6253bce6c785a6b8fb10f22684",
                "hex": "483045022100afade3d747b83907f54208ca16621d08c6c3f1929122418b32fc1414cf3aef620220137f313a3bd61a59748837483329b7c15d627ed0a48ef50d03e847cf7fa391600121029aef52532c0f5d1025ae033712e4c390194aec6253bce6c785a6b8fb10f22684",
            },
            "sequence": 4294967295,
            "prevout": None,
        },
        {
            "txid": "9a446bc375f9292e825763d9ff26805de3adc292b0e756ca542328586171a174",
            "vout": 0,
            "scriptSig": {
                "asm": "3045022100fd6156cc34b31e8050bde7a73532d608d0a410a8bc8178c0436bd25b76b8d23d02204711ba37a65eb038fefb59b10bd41fd0280b5500ff4fe8100d9ea0b8c9c5224e[ALL] 029aef52532c0f5d1025ae033712e4c390194aec6253bce6c785a6b8fb10f22684",
                "hex": "483045022100fd6156cc34b31e8050bde7a73532d608d0a410a8bc8178c0436bd25b76b8d23d02204711ba37a65eb038fefb59b10bd41fd0280b5500ff4fe8100d9ea0b8c9c5224e0121029aef52532c0f5d1025ae033712e4c390194aec6253bce6c785a6b8fb10f22684",
            },
            "sequence": 4294967295,
            "prevout": None,
        },
        {
            "txid": "c09621cd726681bf7d859776fad16aef573e5113e5e4e686e710f39dac0f5297",
            "vout": 0,
            "scriptSig": {
                "asm": "3045022100fa0711cc0e9761230211515a01e87399290e7977a0f98a349d683937c5c0f338022042d32a4b418f690c49d983c48ed9cb9c070f7f6e29009f6b1a3221ee40ec64d9[ALL] 029aef52532c0f5d1025ae033712e4c390194aec6253bce6c785a6b8fb10f22684",
                "hex": "483045022100fa0711cc0e9761230211515a01e87399290e7977a0f98a349d683937c5c0f338022042d32a4b418f690c49d983c48ed9cb9c070f7f6e29009f6b1a3221ee40ec64d90121029aef52532c0f5d1025ae033712e4c390194aec6253bce6c785a6b8fb10f22684",
            },
            "sequence": 4294967295,
            "prevout": None,
        },
        {
            "txid": "c1fa81c99a0148e3de48cf8f4bac24bedd8f790fff2f6b5e94da5d3a5eb5368b",
            "vout": 0,
            "scriptSig": {
                "asm": "30440220071588405c349bcd3ab6159f87f220172ea2297574630d75a4e15e6fcc7811da02207d180457b3ef4c2c4220d33ccb31a73a5ed3f9f497fea659e6a451e2712b5e0f[ALL] 029aef52532c0f5d1025ae033712e4c390194aec6253bce6c785a6b8fb10f22684",
                "hex": "4730440220071588405c349bcd3ab6159f87f220172ea2297574630d75a4e15e6fcc7811da02207d180457b3ef4c2c4220d33ccb31a73a5ed3f9f497fea659e6a451e2712b5e0f0121029aef52532c0f5d1025ae033712e4c390194aec6253bce6c785a6b8fb10f22684",
            },
            "sequence": 4294967295,
            "prevout": None,
        },
        {
            "txid": "cca822ce467a041fd8f4979f21eba91a0156a463589ccda1c87d80a4577fbaa8",
            "vout": 0,
            "scriptSig": {
                "asm": "3045022100ce1f26b03ca268f947791eff6427b377ef907b100844154fea1e64e61cf1710f022024c49f85fede3d692a4d0761c81343626d98b263b8508ac67cd10a8f7c8ce81e[ALL] 029aef52532c0f5d1025ae033712e4c390194aec6253bce6c785a6b8fb10f22684",
                "hex": "483045022100ce1f26b03ca268f947791eff6427b377ef907b100844154fea1e64e61cf1710f022024c49f85fede3d692a4d0761c81343626d98b263b8508ac67cd10a8f7c8ce81e0121029aef52532c0f5d1025ae033712e4c390194aec6253bce6c785a6b8fb10f22684",
            },
            "sequence": 4294967295,
            "prevout": None,
        },
    ],
    "vout": [
        {
            "value": "399.52283620",
            "n": 0,
            "scriptPubKey": {
                "asm": "OP_DUP OP_HASH160 cb5dc230e9c6de2ceeaf90cf5b536167de4930e8 OP_EQUALVERIFY OP_CHECKSIG",
                "hex": "76a914cb5dc230e9c6de2ceeaf90cf5b536167de4930e888ac",
                "reqSigs": 1,
                "type": "pubkeyhash",
                "address": "DPgQ2fAm2VGKHmFAWi1WiyitfNZMbwKbc6",
            },
        }
    ],
}
tx_example1_doge = cattrs.structure(tx_example1_doge_dict, TransactionResponse)


tx_example2_doge_dict = {
    "txid": "432423423435gfdgbdrgdgdg97dg9d8g7dgudvg98dfgddg9u80808078bbz988d",
    "vin": [
        {
            "txid": "fde8896126ed1f46fac9c6761e08fdcfb3455a7a6c474e6a3d147096e84bd705",
            "vout": 1,
            "scriptSig": {
                "asm": "3045022100afade3d747b83907f54208ca16621d08c6c3f1929122418b32fc1414cf3aef620220137f313a3bd61a59748837483329b7c15d627ed0a48ef50d03e847cf7fa39160[ALL] 029aef52532c0f5d1025ae033712e4c390194aec6253bce6c785a6b8fb10f22684",
                "hex": "483045022100afade3d747b83907f54208ca16621d08c6c3f1929122418b32fc1414cf3aef620220137f313a3bd61a59748837483329b7c15d627ed0a48ef50d03e847cf7fa391600121029aef52532c0f5d1025ae033712e4c390194aec6253bce6c785a6b8fb10f22684",
            },
            "sequence": 4294967295,
            "prevout": None,
        },
        {
            "txid": "9a446bc375f9292e825763d9ff26805de3adc292b0e756ca542328586171a174",
            "vout": 0,
            "scriptSig": {
                "asm": "3045022100fd6156cc34b31e8050bde7a73532d608d0a410a8bc8178c0436bd25b76b8d23d02204711ba37a65eb038fefb59b10bd41fd0280b5500ff4fe8100d9ea0b8c9c5224e[ALL] 029aef52532c0f5d1025ae033712e4c390194aec6253bce6c785a6b8fb10f22684",
                "hex": "483045022100fd6156cc34b31e8050bde7a73532d608d0a410a8bc8178c0436bd25b76b8d23d02204711ba37a65eb038fefb59b10bd41fd0280b5500ff4fe8100d9ea0b8c9c5224e0121029aef52532c0f5d1025ae033712e4c390194aec6253bce6c785a6b8fb10f22684",
            },
            "sequence": 4294967295,
            "prevout": None,
        },
        {
            "txid": "c09621cd726681bf7d859776fad16aef573e5113e5e4e686e710f39dac0f5297",
            "vout": 0,
            "scriptSig": {
                "asm": "3045022100fa0711cc0e9761230211515a01e87399290e7977a0f98a349d683937c5c0f338022042d32a4b418f690c49d983c48ed9cb9c070f7f6e29009f6b1a3221ee40ec64d9[ALL] 029aef52532c0f5d1025ae033712e4c390194aec6253bce6c785a6b8fb10f22684",
                "hex": "483045022100fa0711cc0e9761230211515a01e87399290e7977a0f98a349d683937c5c0f338022042d32a4b418f690c49d983c48ed9cb9c070f7f6e29009f6b1a3221ee40ec64d90121029aef52532c0f5d1025ae033712e4c390194aec6253bce6c785a6b8fb10f22684",
            },
            "sequence": 4294967295,
            "prevout": None,
        },
        {
            "txid": "c1fa81c99a0148e3de48cf8f4bac24bedd8f790fff2f6b5e94da5d3a5eb5368b",
            "vout": 0,
            "scriptSig": {
                "asm": "30440220071588405c349bcd3ab6159f87f220172ea2297574630d75a4e15e6fcc7811da02207d180457b3ef4c2c4220d33ccb31a73a5ed3f9f497fea659e6a451e2712b5e0f[ALL] 029aef52532c0f5d1025ae033712e4c390194aec6253bce6c785a6b8fb10f22684",
                "hex": "4730440220071588405c349bcd3ab6159f87f220172ea2297574630d75a4e15e6fcc7811da02207d180457b3ef4c2c4220d33ccb31a73a5ed3f9f497fea659e6a451e2712b5e0f0121029aef52532c0f5d1025ae033712e4c390194aec6253bce6c785a6b8fb10f22684",
            },
            "sequence": 4294967295,
            "prevout": None,
        },
        {
            "txid": "cca822ce467a041fd8f4979f21eba91a0156a463589ccda1c87d80a4577fbaa8",
            "vout": 0,
            "scriptSig": {
                "asm": "3045022100ce1f26b03ca268f947791eff6427b377ef907b100844154fea1e64e61cf1710f022024c49f85fede3d692a4d0761c81343626d98b263b8508ac67cd10a8f7c8ce81e[ALL] 029aef52532c0f5d1025ae033712e4c390194aec6253bce6c785a6b8fb10f22684",
                "hex": "483045022100ce1f26b03ca268f947791eff6427b377ef907b100844154fea1e64e61cf1710f022024c49f85fede3d692a4d0761c81343626d98b263b8508ac67cd10a8f7c8ce81e0121029aef52532c0f5d1025ae033712e4c390194aec6253bce6c785a6b8fb10f22684",
            },
            "sequence": 4294967295,
            "prevout": None,
        },
    ],
    "vout": [
        {
            "value": "399.52283620",
            "n": 0,
            "scriptPubKey": {
                "asm": "OP_DUP OP_HASH160 cb5dc230e9c6de2ceeaf90cf5b536167de4930e8 OP_EQUALVERIFY OP_CHECKSIG",
                "hex": "76a914cb5dc230e9c6de2ceeaf90cf5b536167de4930e888ac",
                "reqSigs": 1,
                "type": "pubkeyhash",
                "address": "DPgQ2fAm2VGKHmFAWi1WiyitfNZMbwKbc6",
            },
        }
    ],
}
tx_example2_doge = cattrs.structure(tx_example2_doge_dict, TransactionResponse)
