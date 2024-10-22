import logging
from unittest.mock import patch

from django.test import TestCase
from requests.models import HTTPBasicAuth
from requests.sessions import Session

from client.doge_client import DogeClient
from configuration.config import get_testing_config
from configuration.types import Config
from utxo_indexer.indexer.doge import DogeIndexerClient
from utxo_indexer.indexer.indexer_client import IndexerClient
from utxo_indexer.models import (
    TipSyncState,
    TipSyncStateChoices,
    TransactionInput,
    TransactionInputCoinbase,
    TransactionOutput,
    UtxoBlock,
    UtxoTransaction,
)
from utxo_indexer.tests.data_for_testing.testing_process_block_doge_data import (
    block_example_doge,
    tx_example1_doge,
    tx_example2_doge,
)

# DISABLE LOGGING
logging.disable(logging.CRITICAL)


class DogeIndexerClientTest(TestCase):
    def setUp(self):
        self.configDoge = get_testing_config("DOGE", "doge")
        self.clientDoge = DogeClient(self.configDoge.NODE_RPC_URL)

    @patch("utxo_indexer.indexer.indexer_client.IndexerClient.extract_initial_block_height")
    def test_init(self, mock_extract_initial_block_height):
        """Test for initialisation of Bitcoin IndexerClient"""
        mock_extract_initial_block_height.return_value = 10
        try:
            indexerDoge = IndexerClient(self.clientDoge, 0, self.configDoge)
        except AssertionError:
            pass
        else:
            raise AssertionError("expected_production must be a positive integer")

        indexerDoge = IndexerClient(self.clientDoge, 9, self.configDoge)
        self.assertEqual(indexerDoge._client, self.clientDoge)
        self.assertEqual(indexerDoge.instance_config, self.configDoge)
        self.assertEqual(len(indexerDoge.workers), self.configDoge.NUMBER_OF_WORKERS)
        auth = HTTPBasicAuth(self.configDoge.AUTH_USERNAME, self.configDoge.AUTH_PASSWORD)
        for worker in indexerDoge.workers:
            self.assertEqual(isinstance(worker, Session), True)
            self.assertEqual(worker.auth, auth)
        self.assertEqual(indexerDoge.toplevel_worker, indexerDoge.workers[0])
        self.assertEqual(indexerDoge.expected_block_production_time, 9)
        self.assertEqual(indexerDoge.latest_indexed_block_height, 10)
        self.assertEqual(indexerDoge.latest_tip_block_height, 0)

    @patch("utxo_indexer.indexer.indexer_client.IndexerClient.extract_initial_block_height")
    def test_new(self, mock_extract_initial_block_height):
        """Test for new method for Bitcoin"""
        mock_extract_initial_block_height.return_value = 7
        with patch("utxo_indexer.indexer.indexer_client.config", new=self.configDoge):
            indexerDoge = IndexerClient.new(self.clientDoge, 9)
        self.assertEqual(indexerDoge._client, self.clientDoge)
        self.assertEqual(indexerDoge.instance_config, self.configDoge)
        self.assertEqual(len(indexerDoge.workers), self.configDoge.NUMBER_OF_WORKERS)
        auth = HTTPBasicAuth(self.configDoge.AUTH_USERNAME, self.configDoge.AUTH_PASSWORD)
        for worker in indexerDoge.workers:
            self.assertEqual(isinstance(worker, Session), True)
            self.assertEqual(worker.auth, auth)
        self.assertEqual(indexerDoge.toplevel_worker, indexerDoge.workers[0])
        self.assertEqual(indexerDoge.expected_block_production_time, 9)
        self.assertEqual(indexerDoge.latest_indexed_block_height, 7)
        self.assertEqual(indexerDoge.latest_tip_block_height, 0)

    def test_default(self):
        """Test for default"""
        # Nothing to test, we have tested IndexerClient.new and DogeClient.default() already.
        pass

    def test_extract_initial_block_height_some_blocks(self):
        """Test for extract_initial_block_height method, when there are some blocks in db"""
        block = UtxoBlock(
            block_hash="", block_number=72, timestamp=0, previous_block_hash="", transactions=0, confirmed=True
        )
        block.save()

        # Case1: block_number < INITIAL_BLOCK_HEIGHT
        config1 = Config(
            SOURCE_NAME=self.configDoge.SOURCE_NAME,
            NODE_RPC_URL=self.configDoge.NODE_RPC_URL,
            AUTH_USERNAME=self.configDoge.AUTH_USERNAME,
            AUTH_PASSWORD=self.configDoge.AUTH_PASSWORD,
            INDEXER_POLL_INTERVAL=10,
            NUMBER_OF_BLOCK_CONFIRMATIONS=60,
            INITIAL_BLOCK_HEIGHT=73,
            NUMBER_OF_WORKERS=10,
            PRUNE_KEEP_DAYS=0,
            PRUNE_INTERVAL_SECONDS=60,
        )
        clientDoge1 = DogeClient(config1.NODE_RPC_URL)

        try:
            IndexerClient(clientDoge1, 1, config1)
        except Exception:
            pass
        else:
            raise AssertionError("block_number can't be smaller than INITIAL_BLOCK_HEIGHT")

        # Case2: block_number >= INITIAL_BLOCK_HEIGHT
        config2 = Config(
            SOURCE_NAME=self.configDoge.SOURCE_NAME,
            NODE_RPC_URL=self.configDoge.NODE_RPC_URL,
            AUTH_USERNAME=self.configDoge.AUTH_USERNAME,
            AUTH_PASSWORD=self.configDoge.AUTH_PASSWORD,
            INDEXER_POLL_INTERVAL=10,
            NUMBER_OF_BLOCK_CONFIRMATIONS=60,
            INITIAL_BLOCK_HEIGHT=72,
            NUMBER_OF_WORKERS=10,
            PRUNE_KEEP_DAYS=0,
            PRUNE_INTERVAL_SECONDS=60,
        )
        clientDoge2 = DogeClient(config2.NODE_RPC_URL)
        indexerDoge2 = IndexerClient(clientDoge2, 1, config2)
        self.assertEqual(indexerDoge2.latest_indexed_block_height, 72)

    @patch("utxo_indexer.indexer.indexer_client.IndexerClient._get_current_block_height")
    def test_extract_initial_block_height_no_blocks(self, mock_get_current_block_height):
        """Test for extract_initial_block_height method, when there are no blocks in db"""
        # During testing the db is emtpy by default, so latest_block variable in
        # extract_initial_block_height is None
        assert UtxoBlock.objects.order_by("block_number").last() is None

        # Case1: PRUNE_KEEP_DAYS <= 0
        config1 = Config(
            SOURCE_NAME=self.configDoge.SOURCE_NAME,
            NODE_RPC_URL=self.configDoge.NODE_RPC_URL,
            AUTH_USERNAME=self.configDoge.AUTH_USERNAME,
            AUTH_PASSWORD=self.configDoge.AUTH_PASSWORD,
            INDEXER_POLL_INTERVAL=10,
            NUMBER_OF_BLOCK_CONFIRMATIONS=60,
            INITIAL_BLOCK_HEIGHT=1,
            NUMBER_OF_WORKERS=10,
            PRUNE_KEEP_DAYS=0,
            PRUNE_INTERVAL_SECONDS=60,
        )
        clientDoge1 = DogeClient(config1.NODE_RPC_URL)
        indexerDoge1 = IndexerClient(clientDoge1, 1, config1)
        self.assertEqual(indexerDoge1.latest_indexed_block_height, config1.INITIAL_BLOCK_HEIGHT)

        # Case2: PRUNE_KEEP_DAYS > 0
        mock_get_current_block_height.return_value = 9
        # Subcase1: INITIAL_BLOCK_HEIGHT < height - blocks_since_pruning
        config2 = Config(
            SOURCE_NAME=self.configDoge.SOURCE_NAME,
            NODE_RPC_URL=self.configDoge.NODE_RPC_URL,
            AUTH_USERNAME=self.configDoge.AUTH_USERNAME,
            AUTH_PASSWORD=self.configDoge.AUTH_PASSWORD,
            INDEXER_POLL_INTERVAL=10,
            NUMBER_OF_BLOCK_CONFIRMATIONS=60,
            INITIAL_BLOCK_HEIGHT=1,
            NUMBER_OF_WORKERS=10,
            PRUNE_KEEP_DAYS=2,
            PRUNE_INTERVAL_SECONDS=60,
        )
        clientDoge2 = DogeClient(config2.NODE_RPC_URL)
        indexerDoge2 = IndexerClient(clientDoge2, 24 * 60 * 60, config2)
        self.assertEqual(indexerDoge2.latest_indexed_block_height, 6)

        # Subcase2: INITIAL_BLOCK_HEIGHT >= height - blocks_since_pruning
        config2 = Config(
            SOURCE_NAME=self.configDoge.SOURCE_NAME,
            NODE_RPC_URL=self.configDoge.NODE_RPC_URL,
            AUTH_USERNAME=self.configDoge.AUTH_USERNAME,
            AUTH_PASSWORD=self.configDoge.AUTH_PASSWORD,
            INDEXER_POLL_INTERVAL=10,
            NUMBER_OF_BLOCK_CONFIRMATIONS=60,
            INITIAL_BLOCK_HEIGHT=1,
            NUMBER_OF_WORKERS=10,
            PRUNE_KEEP_DAYS=6,
            PRUNE_INTERVAL_SECONDS=60,
        )
        clientDoge2 = DogeClient(config2.NODE_RPC_URL)
        indexerDoge2 = IndexerClient(clientDoge2, 24 * 60 * 60, config2)
        self.assertEqual(indexerDoge2.latest_indexed_block_height, 1)

    def test_get_transaction(self):
        """Test for _get_transaction"""
        # Nothing to test, we have tested retry and client.get_transaction already.
        pass

    def test_update_tip_state_indexing(self):
        """Test for update_tip_state_indexing"""
        """Test that take some time to run is in comments"""
        indexerDoge = IndexerClient(self.clientDoge, 60, self.configDoge)
        TipSyncState.instance().delete()
        tip_state = TipSyncState.instance()
        tip_state.latest_tip_height = 400
        # timestamp_0 = tip_state.timestamp
        # time.sleep(2)
        tip_state.save()
        try:
            indexerDoge.update_tip_state_indexing(block_tip_height=399)
        except AssertionError:
            pass
        else:
            error = "block_tip_height must be bigger than tip_state.latest_tip_height"
            raise AssertionError(error)

        indexerDoge.update_tip_state_indexing(block_tip_height=402)
        tip_state = TipSyncState.instance()
        self.assertEqual(tip_state.latest_tip_height, 402)
        self.assertEqual(tip_state.sync_state, TipSyncStateChoices.syncing)
        # self.assertGreater(tip_state.timestamp, timestamp_0)

    def test_update_tip_state_idle(self):
        """Test for update_tip_state_idle"""
        """Test that take some time to run is in comments"""
        indexerDoge = IndexerClient(self.clientDoge, 60, self.configDoge)
        TipSyncState.instance().delete()
        # tip_state = TipSyncState.instance()
        # timestamp_0 = tip_state.timestamp
        # time.sleep(2)

        indexerDoge.update_tip_state_idle()
        tip_state = TipSyncState.instance()
        self.assertEqual(tip_state.sync_state, TipSyncStateChoices.up_to_date)
        # self.assertGreater(tip_state.timestamp, timestamp_0)

    def test_update_tip_state_done_block_process(self):
        """Test for update_tip_state_done_block_process"""
        """Test that take some time to run is in comments"""
        indexerDoge = IndexerClient(self.clientDoge, 60, self.configDoge)
        TipSyncState.instance().delete()
        tip_state = TipSyncState.instance()
        tip_state.latest_indexed_height = 400
        # timestamp_0 = tip_state.timestamp
        # time.sleep(2)
        tip_state.save()
        try:
            indexerDoge.update_tip_state_done_block_process(indexed_block_height=400)
        except AssertionError:
            pass
        else:
            error = "indexed_block_height must be bigger than tip_state.latest_indexed_height"
            raise AssertionError(error)

        indexerDoge.update_tip_state_done_block_process(indexed_block_height=402)
        tip_state = TipSyncState.instance()
        self.assertEqual(tip_state.latest_indexed_height, 402)
        self.assertEqual(tip_state.sync_state, TipSyncStateChoices.syncing)
        # self.assertGreater(tip_state.timestamp, timestamp_0)

    @patch("utxo_indexer.indexer.indexer_client.IndexerClient._get_block_hash_from_height")
    @patch("utxo_indexer.indexer.indexer_client.IndexerClient._get_block_by_hash")
    @patch("utxo_indexer.indexer.doge.DogeIndexerClient._get_transaction")
    def test_process_block(self, mock_get_transaction, mock_get_block_by_hash, mock_get_block_hash_from_height):
        mock_get_block_by_hash.return_value = block_example_doge
        mock_get_block_hash_from_height.return_value = None
        mock_get_transaction.side_effect = [tx_example1_doge, tx_example2_doge]
        TipSyncState.instance().delete()
        indexerDoge = DogeIndexerClient(self.clientDoge, 60, self.configDoge)
        indexerDoge.process_block(33232)

        self.assertEqual(UtxoBlock.objects.count(), 1)
        self.assertEqual(UtxoTransaction.objects.count(), 2)
        self.assertEqual(TransactionInputCoinbase.objects.count(), 1)
        self.assertEqual(TransactionInput.objects.count(), 2)
        self.assertEqual(TransactionOutput.objects.count(), 4)
        tip_state = TipSyncState.instance()
        self.assertEqual(tip_state.latest_indexed_height, 33232)
        # Nothing else needs to be tested here,
        # object_from_node_response and update_tip_state_done_block_process
        # have been tested already.

    def test_process_block_real_example(self):
        """Test for process_block method"""
        """This time we use real block and no mock functions"""
        TipSyncState.instance().delete()
        indexerDoge = DogeIndexerClient(self.clientDoge, 60, self.configDoge)
        indexerDoge.process_block(5000000)

        self.assertEqual(UtxoBlock.objects.count(), 1)
        self.assertEqual(UtxoTransaction.objects.count(), 2749)
        self.assertEqual(TransactionInputCoinbase.objects.count(), 1)
        self.assertEqual(TransactionOutput.objects.count(), 5665)
        self.assertEqual(TransactionInput.objects.count(), 3305)
        tip_state = TipSyncState.instance()
        self.assertEqual(tip_state.latest_indexed_height, 5000000)
        # Nothing else needs to be tested here,
        # object_from_node_response and update_tip_state_done_block_process
        # have been tested already.
