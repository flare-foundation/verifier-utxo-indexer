import logging

from django.test import TestCase

from client.btc_client import BtcClient
from configuration.config import get_testing_config
from utxo_indexer.indexer.bitcoin import BtcIndexerClient
from utxo_indexer.models.block import UtxoBlock

# DISABLE LOGGING
logging.disable(logging.CRITICAL)


class IndexingBlockWorkingTest(TestCase):
    def setUp(self):
        config = get_testing_config("TEST_BTC_V3", "btc")
        client = BtcClient(config.NODE_RPC_URL)
        self.indexer = BtcIndexerClient(client, 600, config)

    def test_should_process_block(self):
        """Testing indexing for block 2904561"""
        block_num = 2904561
        self.indexer.process_block(block_num)

        block = UtxoBlock.objects.get(block_number=block_num)

        self.assertEqual(block.block_number, block_num)
        self.assertEqual(block.transactions, 3556)
