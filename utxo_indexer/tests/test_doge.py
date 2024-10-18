import logging

from django.test import TestCase

from client.doge_client import DogeClient
from configuration.config import get_testing_config
from utxo_indexer.indexer.doge import DogeIndexerClient

# DISABLE LOGGING
logging.disable(logging.CRITICAL)


class DogeIndexerClientTest(TestCase):
    def setUp(self):
        config = get_testing_config("DOGE", "doge")
        client = DogeClient(config.NODE_RPC_URL)
        self.indexer = DogeIndexerClient(client, 60, config)

    def test_default(self):
        """Nothing to test, we have tested IndexerClient.new and DogeClient.default() already."""
        pass

    # @patch("utxo_indexer.indexer.indexer_client.IndexerClient._get_block_hash_from_height")
    # @patch("utxo_indexer.indexer.indexer_client.IndexerClient._get_block_by_hash")
    # def test_process_block(self, mock_get_block_by_hash, mock_get_block_hash_from_height):
    #     mock_get_block_by_hash.return_value = block_ex
    #     mock_get_block_hash_from_height.return_value = None
    #     self.indexer.process_block(33232)

    #     self.assertEqual(UtxoBlock.objects.count(),1)
    #     self.assertEqual(UtxoTransaction.objects.count(),2)
    #     self.assertEqual(TransactionInputCoinbase.objects.count(),1)
    #     self.assertEqual(TransactionInput.objects.count(),1)
    #     self.assertEqual(TransactionOutput.objects.count(),5)
    #     tip_state = TipSyncState.instance()
    #     self.assertEqual(tip_state.latest_indexed_height, 33232)
    #     """Nothing else needs to be tested here,"""
    #     """object_from_node_response and update_tip_state_done_block_process"""
    #     """have been tested already."""
