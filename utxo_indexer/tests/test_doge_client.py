import logging
from unittest.mock import patch

from django.test import TestCase
from requests.models import HTTPBasicAuth
from requests.sessions import Session

from client.doge_client import DogeClient
from configuration.config import get_testing_config
from utxo_indexer.models.types import (
    BlockResponse,
    CoinbaseVinResponse,
    ScriptPubKeyResponse,
    ScriptSigResponse,
    TransactionResponse,
    VinResponse,
    VoutResponse,
)
from utxo_indexer.tests.data_for_testing.testing_addresses_data import tx_example_adress

# DISABLE LOGGING
logging.disable(logging.CRITICAL)


class DogeClientTest(TestCase):
    def setUp(self):
        self.config = get_testing_config("DOGE", "doge")
        self.clientDoge = DogeClient(self.config.NODE_RPC_URL)
        self.session = Session()
        self.session.auth = HTTPBasicAuth(self.config.AUTH_USERNAME, self.config.AUTH_PASSWORD)

    def test_init(self):
        """Test for initialisation of DogeClient"""
        rpc_url = "testing_rpc_url"
        client = DogeClient(rpc_url)
        self.assertEqual(client.url, rpc_url)

    def test_default(self):
        """Test for default method"""
        with patch("client.doge_client.config", new=self.config):
            client = DogeClient.default()
        self.assertEqual(isinstance(client, DogeClient), True)
        self.assertEqual(client.url, self.clientDoge.url)

    def test_post(self):
        """Test for _post method"""
        # Nothing to test here.

    def test_check_adress_reqSigs_prevout(self):
        """Test for address logic in  aget_block_by_hash method"""
        tx = self.clientDoge._check_adress_reqSigs_prevout(tx_example_adress)

        vouts = tx["vout"]
        self.assertEqual(vouts[0]["scriptPubKey"]["address"], "")
        self.assertEqual(vouts[0]["scriptPubKey"]["reqSigs"], 100)
        self.assertEqual(vouts[1]["scriptPubKey"]["address"], "address")
        self.assertEqual(vouts[1]["scriptPubKey"]["reqSigs"], None)
        self.assertEqual(vouts[2]["scriptPubKey"]["address"], "address1")
        self.assertEqual(vouts[3]["scriptPubKey"]["address"], "")

        vins = tx["vin"]
        self.assertEqual(vins[0]["prevout"], None)

    def test_get_transaction(self):
        """Test for get_block_by_hash method"""
        # Not coinbase
        txid = "5bb17cf0bd160b4d5f84dcf84a06cbf21b4fdcbe065a45407e15e2b4ed4512de"
        tx = self.clientDoge.get_transaction(self.session, txid)
        # Testing types
        self.assertEqual(isinstance(tx, TransactionResponse), True)
        self.assertEqual(isinstance(tx.vin[0], VinResponse), True)
        assert isinstance(tx.vin[0], VinResponse)
        self.assertEqual(isinstance(tx.vin[0].scriptSig, ScriptSigResponse), True)
        self.assertEqual(isinstance(tx.vout[0], VoutResponse), True)
        self.assertEqual(isinstance(tx.vout[0].scriptPubKey, ScriptPubKeyResponse), True)
        # We are testing only the attributes of the transaction that are later used.
        self.assertEqual(tx.txid, txid)
        self.assertEqual(len(tx.vout), 1)
        self.assertEqual(len(tx.vin), 5)
        self.assertEqual(tx.vin[0].txid, "fde8896126ed1f46fac9c6761e08fdcfb3455a7a6c474e6a3d147096e84bd705")
        self.assertEqual(tx.vin[0].sequence, 4294967295)
        self.assertEqual(tx.vin[0].vout, 1)
        self.assertEqual(tx.vin[0].prevout, None)
        self.assertEqual(
            tx.vin[0].scriptSig.asm,
            "3045022100afade3d747b83907f54208ca16621d08c6c3f1929122418b32fc1414cf3aef620220137f313a3bd61a59748837483329b7c15d627ed0a48ef50d03e847cf7fa39160[ALL] 029aef52532c0f5d1025ae033712e4c390194aec6253bce6c785a6b8fb10f22684",
        )
        self.assertEqual(
            tx.vin[0].scriptSig.hex,
            "483045022100afade3d747b83907f54208ca16621d08c6c3f1929122418b32fc1414cf3aef620220137f313a3bd61a59748837483329b7c15d627ed0a48ef50d03e847cf7fa391600121029aef52532c0f5d1025ae033712e4c390194aec6253bce6c785a6b8fb10f22684",
        )
        self.assertEqual(tx.vout[0].value, "399.52283620")
        self.assertEqual(tx.vout[0].n, 0)
        self.assertEqual(tx.vout[0].scriptPubKey.reqSigs, 1)
        self.assertEqual(
            tx.vout[0].scriptPubKey.asm,
            "OP_DUP OP_HASH160 cb5dc230e9c6de2ceeaf90cf5b536167de4930e8 OP_EQUALVERIFY OP_CHECKSIG",
        )
        self.assertEqual(tx.vout[0].scriptPubKey.hex, "76a914cb5dc230e9c6de2ceeaf90cf5b536167de4930e888ac")
        self.assertEqual(tx.vout[0].scriptPubKey.type, "pubkeyhash")
        self.assertEqual(tx.vout[0].scriptPubKey.address, "DPgQ2fAm2VGKHmFAWi1WiyitfNZMbwKbc6")

        # Coinbase
        txid = "c698548da58fecc05eae8df51350d114e406115b54c79e3a359f8d9178445b3c"
        tx = self.clientDoge.get_transaction(self.session, txid)
        # We are testing only the attributes of the transaction that are later used.
        self.assertEqual(isinstance(tx.vin[0], CoinbaseVinResponse), True)
        assert isinstance(tx.vin[0], CoinbaseVinResponse)
        self.assertEqual(
            tx.vin[0].coinbase,
            "038ed9520fe4b883e5bda9e7a59ee4bb99e9b1bc205b323032342d31302d32325430353a35323a35372e3036393433383539365a5d",
        )
        self.assertEqual(tx.vin[0].sequence, 4294967295)

    def test_get_block_by_hash(self):
        """Test for get_block_by_hash method"""
        hash = "f4128c693d2dfd0fb8d020c69831e45e9a8b68f58b3e7bf60d1deca12d0b1e60"
        block = self.clientDoge.get_block_by_hash(self.session, hash)
        # We are testing only the attributes of the block that are later used.
        self.assertEqual(block.hash, hash)
        self.assertEqual(block.height, 5424181)
        self.assertEqual(block.mediantime, 1729232830)
        prev_hash = "99dbd637870942c912235081b209102d2e34d8573330cf27a2e0a65a291b6cf0"
        self.assertEqual(block.previousblockhash, prev_hash)
        self.assertEqual(len(block.tx), 618)
        # Check in data is stored in the right classes
        self.assertEqual(isinstance(block, BlockResponse), True)
        self.assertEqual(isinstance(block.tx[0], TransactionResponse), True)
        self.assertEqual(isinstance(block.tx[0].vin[0], CoinbaseVinResponse), True)
        self.assertEqual(isinstance(block.tx[1].vin[0], VinResponse), True)
        assert isinstance(block.tx[1].vin[0], VinResponse)
        self.assertEqual(isinstance(block.tx[1].vin[0].scriptSig, ScriptSigResponse), True)
        self.assertEqual(block.tx[1].vin[0].prevout, None)
        self.assertEqual(isinstance(block.tx[1].vout[0], VoutResponse), True)
        self.assertEqual(isinstance(block.tx[1].vout[0].scriptPubKey, ScriptPubKeyResponse), True)

    def test_get_block_hash_from_height(self):
        """Test for get_block_hash_from_height method"""
        hash = self.clientDoge.get_block_hash_from_height(self.session, 5424181)
        real_hash = "f4128c693d2dfd0fb8d020c69831e45e9a8b68f58b3e7bf60d1deca12d0b1e60"
        self.assertEqual(hash, real_hash)

    def test_get_block_height(self):
        """Test for get_block_height method"""
        """This test is time sensitive and require your input"""

        # Change current_block_count to the height
        # of the most-work fully-validated chain
        current_block_count = None

        if current_block_count is not None:
            height = self.clientDoge.get_block_height(self.session)
            self.assertEqual(height, current_block_count)
