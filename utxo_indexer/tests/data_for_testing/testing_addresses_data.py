# Data for tests:
# test_doge_client.test_check_adress_reqSigs_prevout
# test_btc_client.test_check_adress_reqSigs

tx_example_adress = {
    "txid": "",
    "hash": "",
    "version": 1,
    "size": 1,
    "vsize": 1,
    "weight": 1,
    "locktime": 1,
    "vin": [
        {
            "txid": "",
            "vout": 1,
            "scriptSig": {"asm": "", "hex": ""},
            "prevout": {
                "height": 1,
                "value": "",
                "scriptPubKey": {"asm": "", "desc": "", "hex": "", "type": "", "reqSigs": 100},
            },
            "sequence": 1,
        },
        {
            "txid": "",
            "vout": 1,
            "scriptSig": {"asm": "", "hex": ""},
            "prevout": {
                "height": 1,
                "value": "",
                "scriptPubKey": {
                    "asm": "",
                    "desc": "",
                    "hex": "",
                    "address": "address",
                    "type": "",
                },
            },
            "sequence": 1,
        },
        {
            "txid": "",
            "vout": 1,
            "scriptSig": {"asm": "", "hex": ""},
            "prevout": {
                "height": 1,
                "value": "",
                "scriptPubKey": {
                    "asm": "",
                    "desc": "",
                    "hex": "",
                    "addresses": ["address1", "address2"],
                    "type": "",
                },
            },
            "sequence": 1,
        },
        {
            "txid": "",
            "vout": 1,
            "scriptSig": {"asm": "", "hex": ""},
            "prevout": {
                "height": 1,
                "value": "",
                "scriptPubKey": {
                    "asm": "",
                    "desc": "",
                    "hex": "",
                    "addresses": [],
                    "type": "",
                },
            },
            "sequence": 1,
        },
    ],
    "vout": [
        {
            "value": "0.",
            "n": 0,
            "scriptPubKey": {"asm": "", "desc": "", "hex": "", "type": "", "reqSigs": 100},
        },
        {
            "value": "0.",
            "n": 1,
            "scriptPubKey": {
                "asm": "",
                "desc": "",
                "hex": "",
                "address": "address",
                "type": "",
            },
        },
        {
            "value": "0.",
            "n": 2,
            "scriptPubKey": {
                "asm": "",
                "desc": "",
                "hex": "",
                "addresses": ["address1", "address2"],
                "type": "",
            },
        },
        {
            "value": "0.",
            "n": 3,
            "scriptPubKey": {
                "asm": "",
                "desc": "",
                "hex": "",
                "addresses": [],
                "type": "",
            },
        },
    ],
    "fee": "",
    "hex": "",
}
