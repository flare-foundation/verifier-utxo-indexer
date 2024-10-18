from typing import Any

"""Examples for tests."""

vin_ex1: Any = {
    "coinbase": "0344ba2f00",
    "txinwitness": ["0000000000000000000000000000000000000000000000000000000000000000"],
    "sequence": 4294967295,
}

vin_ex2: Any = {
    "txid": "18d99e54a50e48c58d462b41d1fcc8a45c9d881dc1f068edd0bb0445dfc3ee09",
    "vout": 1,
    "scriptSig": {"asm": "", "hex": ""},
    "txinwitness": [
        "8720085377a720c2e3b7eb758ef38df5dcc968564b07d3a065737a9c33b05d9ea1afb46523cb470588f94c8d64d64e2cda3fa65308fcc7353a2e80c1a1eeed99"
    ],
    "prevout": {
        "generated": "False",
        "height": 3127875,
        "value": "0.09738210",
        "scriptPubKey": {
            "asm": "1 585c29c7d63cb984442112bab5d80df72c0a643880c74c9b0f12e5ed13e14093",
            "desc": "rawtr(585c29c7d63cb984442112bab5d80df72c0a643880c74c9b0f12e5ed13e14093)#6a9hwaqx",
            "hex": "5120585c29c7d63cb984442112bab5d80df72c0a643880c74c9b0f12e5ed13e14093",
            "address": "tb1ptpwzn37k8jucg3ppz2attkqd7ukq5epcsrr5exc0ztj76ylpgzfsu46uaw",
            "type": "witness_v1_taproot",
        },
    },
    "sequence": 4294967293,
}


vout_ex1: Any = {
    "value": "1.13428769",
    "n": 0,
    "scriptPubKey": {
        "asm": "0 0508988e716ba1391175bc661e0115be5a88369a",
        "desc": "addr(tb1qq5yf3rn3dwsnjyt4h3npuqg4hedgsd56sc0jqz)#7yz9pn4p",
        "hex": "00140508988e716ba1391175bc661e0115be5a88369a",
        "address": "11tb1qq5yf3rn3dwsnjyt4h3npuqg4hedgsd56sc0jqz",
        "type": "witness_v0_keyhash",
        "reqSigs": 2,
    },
}

vout_ex2: Any = {
    "value": "1.13428769",
    "n": 0,
    "scriptPubKey": {
        "asm": "0 0508988e716ba1391175bc661e0115be5a88369a",
        "desc": "addr(tb1qq5yf3rn3dwsnjyt4h3npuqg4hedgsd56sc0jqz)#7yz9pn4p",
        "hex": "00140508988e716ba1391175bc661e0115be5a88369a",
        "addresses": ["22tb1qq5yf3rn3dwsnjyt4h3npuqg4hedgsd56sc0jqz", ""],
        "type": "witness_v0_keyhash",
        "reqSigs": 2,
    },
}

vout_ex3: Any = {
    "value": "1.13428769",
    "n": 0,
    "scriptPubKey": {
        "asm": "0 0508988e716ba1391175bc661e0115be5a88369a",
        "desc": "addr(tb1qq5yf3rn3dwsnjyt4h3npuqg4hedgsd56sc0jqz)#7yz9pn4p",
        "hex": "00140508988e716ba1391175bc661e0115be5a88369a",
        "type": "witness_v0_keyhash",
        "reqSigs": 2,
    },
}

transaction_ex1: Any = {  # Coinbase
    "txid": "63c25bcfcce2d2e830dec089d84653c678e6841cf375cdcc5518590cba5b2008",
    "hash": "3a0f72c4996295fa0db8b3ccaa90c73f6d67c426a8cb025db9f0ac6ed687bd95",
    "version": 2,
    "size": 170,
    "vsize": 143,
    "weight": 572,
    "locktime": 0,
    "vin": [vin_ex1],
    "vout": [
        {
            "value": "1.13428769",
            "n": 0,
            "scriptPubKey": {
                "asm": "0 0508988e716ba1391175bc661e0115be5a88369a",
                "desc": "addr(tb1qq5yf3rn3dwsnjyt4h3npuqg4hedgsd56sc0jqz)#7yz9pn4p",
                "hex": "00140508988e716ba1391175bc661e0115be5a88369a",
                "address": "tb1qq5yf3rn3dwsnjyt4h3npuqg4hedgsd56sc0jqz",
                "type": "witness_v0_keyhash",
            },
        },
        {
            "value": "0.00000000",
            "n": 1,
            "scriptPubKey": {
                "asm": "OP_RETURN aa21a9ed6c401b737bf1cd54a846760c3050908b77ef20c5e85880848fb3d1c8be697430",
                "desc": "raw(6a24aa21a9ed6c401b737bf1cd54a846760c3050908b77ef20c5e85880848fb3d1c8be697430)#5vyaratw",
                "hex": "6a24aa21a9ed6c401b737bf1cd54a846760c3050908b77ef20c5e85880848fb3d1c8",  # be697430",
                "type": "nulldata",
            },
        },
    ],
    "hex": "020000000001010000000000000000000000000000000000000000000000000000000000000000ffffffff050344ba2f00ffffffff0221c9c206000000001600140508988e716ba1391175bc661e0115be5a88369a0000000000000000266a24aa21a9ed6c401b737bf1cd54a846760c3050908b77ef20c5e85880848fb3d1c8be6974300120000000000000000000000000000000000000000000000000000000000000000000000000",
}

transaction_ex2: Any = {  # Not coinbase
    "txid": "5153f4f21aa01a19d7929292906a751967b045143a499e26abc93b7c2d4b98fe",
    "hash": "c9e58b7e66a5287cab0740735a7c7a559a588169764306c7cb3f76a025189c54",
    "version": 2,
    "size": 212,
    "vsize": 161,
    "weight": 644,
    "locktime": 3127875,
    "vin": [vin_ex2],
    "vout": [
        {
            "value": "0.09230786",
            "n": 0,
            "scriptPubKey": {
                "asm": "0 80a22adbcf11afce9277349e44457aaeb3496047",
                "desc": "addr(tb1qsz3z4k70zxhuaynhxj0yg3t646e5jcz8ljymz4)#dp2jja7n",
                "hex": "001480a22adbcf11afce9277349e44457aaeb3496047",
                "address": "tb1qsz3z4k70zxhuaynhxj0yg3t646e5jcz8ljymz4",
                "type": "witness_v0_keyhash",
            },
        },
        {
            "value": "0.00004900",
            "n": 1,
            "scriptPubKey": {
                "asm": "0 87a1b14d2e61c0e820ae9833b112cdc70b039238",
                "desc": "addr(tb1qs7smznfwv8qwsg9wnqemzykdcu9s8y3cptky7e)#f2wgdxq9",
                "hex": "001487a1b14d2e61c0e820ae9833b112cdc70b039238",
                "address": "tb1qs7smznfwv8qwsg9wnqemzykdcu9s8y3cptky7e",
                "type": "witness_v0_keyhash",
            },
        },
        {
            "value": "0.00004900",
            "n": 2,
            "scriptPubKey": {
                "asm": "0 0ac036c52ad9c4404cac51f20d004ff834c036a6",
                "desc": "addr(tb1qptqrd3f2m8zyqn9v28eq6qz0lq6vqd4x0urvl6)#sfyg34dr",
                "hex": "00140ac036c52ad9c4404cac51f20d004ff834c036a6",
                "address": "tb1qptqrd3f2m8zyqn9v28eq6qz0lq6vqd4x0urvl6",
                "type": "witness_v0_keyhash",
            },
        },
    ],
    "fee": "0.00497624",
    "hex": "0200000000010109eec3df4504bbd0ed68f0c11d889d5ca4c8fcd1412b468dc5480ea5549ed9180100000000fdffffff03c2d98c000000000016001480a22adbcf11afce9277349e44457aaeb3496047241300000000000016001487a1b14d2e61c0e820ae9833b112cdc70b03923824130000000000001600140ac036c52ad9c4404cac51f20d004ff834c036a601408720085377a720c2e3b7eb758ef38df5dcc968564b07d3a065737a9c33b05d9ea1afb46523cb470588f94c8d64d64e2cda3fa65308fcc7353a2e80c1a1eeed9943ba2f00",
}


block_ex: Any = {
    "size": 0,
    "hash": "ehafbuegfzu3gbrfui3wgrz3ubfzuwrirhiw",
    "height": 33232,
    "mediantime": 1,
    "previousblockhash": "dghdrgd564t43tfe3t3vbtv3bt3",
    "tx": [
        transaction_ex1,
        transaction_ex2,
    ],
}
