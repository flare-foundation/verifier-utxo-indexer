import logging
from unittest.mock import patch

from django.test import TestCase
from requests.models import HTTPBasicAuth
from requests.sessions import Session

from client.btc_client import BtcClient
from configuration.config import get_testing_config
from utxo_indexer.models.types import (
    BlockResponse,
    CoinbaseVinResponse,
    PrevoutResponse,
    ScriptPubKeyResponse,
    ScriptSigResponse,
    TransactionResponse,
    VinResponse,
    VoutResponse,
)
from utxo_indexer.tests.data_for_testing.testing_addresses_data import tx_example_adress

# DISABLE LOGGING
logging.disable(logging.CRITICAL)


class BtcClientTest(TestCase):
    def setUp(self):
        self.config = get_testing_config("TEST_BTC_V3", "btc")
        self.clientBTC = BtcClient(self.config.NODE_RPC_URL)
        self.session = Session()
        self.session.auth = HTTPBasicAuth(self.config.AUTH_USERNAME, self.config.AUTH_PASSWORD)

    def test_init(self):
        """Test for initialisation of BtcClient"""
        rpc_url = "testing_rpc_url"
        client = BtcClient(rpc_url)
        self.assertEqual(client.url, rpc_url)

    def test_default(self):
        """Test for default method"""
        with patch("client.btc_client.config", new=self.config):
            client = BtcClient.default()
        self.assertEqual(isinstance(client, BtcClient), True)
        self.assertEqual(client.url, self.clientBTC.url)

    def test_post(self):
        """Test for _post method"""
        # Nothing to test here.

    def test_get_block_by_hash(self):
        """Test for get_block_by_hash method"""
        hash = "00000000bda648a1f6336a8126ba84dfb4f3dde9aba3ccbae7b7a44dc15b8926"
        block = self.clientBTC.get_block_by_hash(self.session, hash)
        # We are testing only the attributes of the block that are later used.
        self.assertEqual(block.hash, hash)
        self.assertEqual(block.height, 3127876)
        self.assertEqual(block.mediantime, 1728884507)
        prev_hash = "00000000000000b7e2bb4f563bebf3a9c815ba3012de250fa0e8048ae064604b"
        self.assertEqual(block.previousblockhash, prev_hash)
        self.assertEqual(len(block.tx), 3524)
        # Check in data is stored in the right classes
        self.assertEqual(isinstance(block, BlockResponse), True)
        self.assertEqual(isinstance(block.tx[0], TransactionResponse), True)
        self.assertEqual(isinstance(block.tx[0].vin[0], CoinbaseVinResponse), True)
        self.assertEqual(isinstance(block.tx[1].vin[0], VinResponse), True)
        assert isinstance(block.tx[1].vin[0], VinResponse)
        self.assertEqual(isinstance(block.tx[1].vin[0].scriptSig, ScriptSigResponse), True)
        self.assertEqual(isinstance(block.tx[1].vin[0].prevout, PrevoutResponse), True)
        assert isinstance(block.tx[1].vin[0].prevout, PrevoutResponse)
        self.assertEqual(isinstance(block.tx[1].vin[0].prevout.scriptPubKey, ScriptPubKeyResponse), True)
        self.assertEqual(isinstance(block.tx[1].vout[0], VoutResponse), True)
        self.assertEqual(isinstance(block.tx[1].vout[0].scriptPubKey, ScriptPubKeyResponse), True)

    def test_check_adress_reqSigs(self):
        """Test for address logic in  aget_block_by_hash method"""
        tx = self.clientBTC._check_address_reqSigs(tx_example_adress)

        vouts = tx["vout"]
        self.assertEqual(vouts[0]["scriptPubKey"]["address"], "")
        self.assertEqual(vouts[0]["scriptPubKey"]["reqSigs"], 100)
        self.assertEqual(vouts[1]["scriptPubKey"]["address"], "address")
        self.assertEqual(vouts[1]["scriptPubKey"]["reqSigs"], None)
        self.assertEqual(vouts[2]["scriptPubKey"]["address"], "address1")
        self.assertEqual(vouts[3]["scriptPubKey"]["address"], "")

        vins = tx["vin"]
        self.assertEqual(vins[0]["prevout"]["scriptPubKey"]["address"], "")
        self.assertEqual(vins[0]["prevout"]["scriptPubKey"]["reqSigs"], 100)
        self.assertEqual(vins[1]["prevout"]["scriptPubKey"]["address"], "address")
        self.assertEqual(vins[1]["prevout"]["scriptPubKey"]["reqSigs"], None)
        self.assertEqual(vins[2]["prevout"]["scriptPubKey"]["address"], "address1")
        self.assertEqual(vins[3]["prevout"]["scriptPubKey"]["address"], "")

    def test_get_block_hash_from_height(self):
        """Test for get_block_hash_from_height method"""
        response = self.clientBTC.get_block_hash_from_height(self.session, 3127876)
        real_hash = "00000000bda648a1f6336a8126ba84dfb4f3dde9aba3ccbae7b7a44dc15b8926"
        self.assertEqual(response, real_hash)

    def test_get_block_height(self):
        """Test for get_block_height method"""
        """This test is time sensitive and require your input"""

        # Change current_block_count to the height
        # of the most-work fully-validated chain
        current_block_count = None

        if current_block_count is not None:
            response = self.clientBTC.get_block_height(self.session)
            self.assertEqual(response, current_block_count)
