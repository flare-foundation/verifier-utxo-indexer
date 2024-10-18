import logging
from unittest.mock import patch

from django.test import TestCase

from client.btc_client import BtcClient
from configuration.config import get_testing_config
from utxo_indexer.indexer.bitcoin import BtcIndexerClient
from utxo_indexer.models import (
    TipSyncState,
    TransactionInput,
    TransactionInputCoinbase,
    TransactionOutput,
    UtxoBlock,
    UtxoTransaction,
)
from utxo_indexer.tests.data_for_testing import block_ex

# DISABLE LOGGING
logging.disable(logging.CRITICAL)


class BtcIndexerClientTest(TestCase):
    def setUp(self):
        config = get_testing_config("TEST_BTC_V3", "btc")
        client = BtcClient(config.NODE_RPC_URL)
        self.indexer = BtcIndexerClient(client, 60, config)

    def test_default(self):
        """Test for default"""
        # Nothing to test, we have tested IndexerClient.new and BtcClient.default() already.
        pass

    @patch("utxo_indexer.indexer.indexer_client.IndexerClient._get_block_hash_from_height")
    @patch("utxo_indexer.indexer.indexer_client.IndexerClient._get_block_by_hash")
    def test_process_block(self, mock_get_block_by_hash, mock_get_block_hash_from_height):
        """Test for process_block method"""
        mock_get_block_by_hash.return_value = block_ex
        mock_get_block_hash_from_height.return_value = None
        self.indexer.process_block(33232)

        self.assertEqual(UtxoBlock.objects.count(), 1)
        self.assertEqual(UtxoTransaction.objects.count(), 2)
        self.assertEqual(TransactionInputCoinbase.objects.count(), 1)
        self.assertEqual(TransactionInput.objects.count(), 1)
        self.assertEqual(TransactionOutput.objects.count(), 5)
        tip_state = TipSyncState.instance()
        self.assertEqual(tip_state.latest_indexed_height, 33232)
        # Nothing else needs to be tested here,
        # object_from_node_response and update_tip_state_done_block_process
        # have been tested already.
