import logging
from unittest.mock import patch

from django.test import TestCase
from requests.models import HTTPBasicAuth
from requests.sessions import Session

from client.btc_client import BtcClient
from configuration.config import get_testing_config

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
        _response = self.clientBTC.get_block_by_hash(self.session, hash)
        response = _response.json(parse_float=str)
        self.assertEqual(response["error"], None)
        self.assertEqual(response["id"], "rpc")
        # We are testing only the attributes of the block that are later used.
        self.assertEqual(response["result"]["hash"], hash)
        self.assertEqual(response["result"]["height"], 3127876)
        self.assertEqual(response["result"]["mediantime"], 1728884507)
        prev_hash = "00000000000000b7e2bb4f563bebf3a9c815ba3012de250fa0e8048ae064604b"
        self.assertEqual(response["result"]["previousblockhash"], prev_hash)
        self.assertEqual(len(response["result"]["tx"]), 3524)

    def test_get_block_hash_from_height(self):
        """Test for get_block_hash_from_height method"""
        _response = self.clientBTC.get_block_hash_from_height(self.session, 3127876)
        response = _response.json(parse_float=str)
        self.assertEqual(response["error"], None)
        self.assertEqual(response["id"], "rpc")
        real_hash = "00000000bda648a1f6336a8126ba84dfb4f3dde9aba3ccbae7b7a44dc15b8926"
        self.assertEqual(response["result"], real_hash)

    def test_get_block_height(self):
        """Test for get_block_height method"""
        """This test is time sensitive and require your input"""

        # Change current_block_count to the height
        # of the most-work fully-validated chain
        current_block_count = None

        if current_block_count is not None:
            _response = self.clientBTC.get_block_height(self.session)
            response = _response.json(parse_float=str)
            self.assertEqual(response["error"], None)
            self.assertEqual(response["id"], "rpc")
            self.assertEqual(response["result"], current_block_count)
