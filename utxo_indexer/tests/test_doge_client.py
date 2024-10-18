# import logging
# from unittest.mock import patch

# from django.test import TestCase
# from requests.models import HTTPBasicAuth
# from requests.sessions import Session

# from client.doge_client import DogeClient
# from configuration.config import get_testing_config

# # DISABLE LOGGING
# logging.disable(logging.CRITICAL)


# class BtcClientTest(TestCase):
#     def setUp(self):
#         self.config = get_testing_config("DOGE", "doge")
#         self.clientDoge = DogeClient(self.config.NODE_RPC_URL)
#         self.session = Session()
#         self.session.auth = HTTPBasicAuth(self.config.AUTH_USERNAME, self.config.AUTH_PASSWORD)

#     def test_init(self):
#         rpc_url = "testing_rpc_url"
#         client = DogeClient(rpc_url)
#         self.assertEqual(client.url, rpc_url)

#     def test_default(self):
#         with patch("client.doge_client.config", new=self.config):
#             client = DogeClient.default()
#         self.assertEqual(type(client), DogeClient)
#         self.assertEqual(client.url, self.clientDoge.url)

#     def test_post(self):
#         """Nothing to test here."""

#     def test_get_block_by_hash(self):
#         hash = "7713122ec467e9c5f6aec70acfbe66c5378b6294b63caa9fbb6ccba3c055f874"
#         _response = self.clientDoge.get_block_by_hash(self.session, hash)
#         response = _response.json(parse_float=str)
#         self.assertEqual(response["error"], None)
#         self.assertEqual(response["id"], "rpc")
#         # We are testing only for attributes of the block that are later used.
#         self.assertEqual(response["result"]["hash"],"00000000bda648a1f6336a8126ba84dfb4f3dde9aba3ccbae7b7a44dc15b8926")
#         self.assertEqual(response["result"]["height"],3127876)
#         self.assertEqual(response["result"]["mediantime"],1728884507)
#         self.assertEqual(response["result"]["previousblockhash"],"00000000000000b7e2bb4f563bebf3a9c815ba3012de250fa0e8048ae064604b")
#         self.assertEqual(len(response["result"]["tx"]),3524)

#     def test_get_block_hash_from_height(self):
#         _response = self.clientDoge.get_block_hash_from_height(self.session, 3127876)
#         response = _response.json(parse_float=str)
#         self.assertEqual(response["error"], None)
#         self.assertEqual(response["id"], "rpc")
#         self.assertEqual(response["result"], "00000000bda648a1f6336a8126ba84dfb4f3dde9aba3ccbae7b7a44dc15b8926")

#     # This test is time sensitive.
#     def test_get_block_height(self):
#         "Change current_block_count to the height of the most-work fully-validated chain."
#         current_block_count = None

#         if current_block_count != None:
#             _response = self.clientDoge.get_block_height(self.session)
#             response = _response.json(parse_float=str)
#             self.assertEqual(response["error"], None)
#             self.assertEqual(response["id"], "rpc")
#             self.assertEqual(response["result"], current_block_count)
