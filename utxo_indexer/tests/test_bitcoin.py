import logging
from unittest.mock import patch

from django.test import TestCase
from requests.models import HTTPBasicAuth
from requests.sessions import Session

from client.btc_client import BtcClient
from configuration.config import get_testing_config
from configuration.types import Config
from utxo_indexer.indexer.bitcoin import BtcIndexerClient
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
from utxo_indexer.tests.data_for_testing.testing_process_block_bitcoin_data import block_example_bitcoin
from utxo_indexer.utils import merkle_tree_from_address_strings

# DISABLE LOGGING
logging.disable(logging.CRITICAL)


class BtcIndexerClientTest(TestCase):
    def setUp(self):
        self.configBTC = get_testing_config("TEST_BTC_V3", "btc")
        self.clientBTC = BtcClient(self.configBTC.NODE_RPC_URL)

    @patch("utxo_indexer.indexer.indexer_client.IndexerClient.extract_initial_block_height")
    def test_init(self, mock_extract_initial_block_height):
        """Test for initialisation of Bitcoin IndexerClient"""
        mock_extract_initial_block_height.return_value = 10
        try:
            indexerBTC = IndexerClient(self.clientBTC, 0, self.configBTC)
        except AssertionError:
            pass
        else:
            raise AssertionError("expected_production must be a positive integer")

        indexerBTC = IndexerClient(self.clientBTC, 9, self.configBTC)
        self.assertEqual(indexerBTC._client, self.clientBTC)
        self.assertEqual(indexerBTC.instance_config, self.configBTC)
        self.assertEqual(len(indexerBTC.workers), 1)
        self.assertEqual(indexerBTC.toplevel_worker, indexerBTC.workers[0])
        self.assertEqual(isinstance(indexerBTC.toplevel_worker, Session), True)
        auth = HTTPBasicAuth(self.configBTC.AUTH_USERNAME, self.configBTC.AUTH_PASSWORD)
        self.assertEqual(indexerBTC.toplevel_worker.auth, auth)
        self.assertEqual(indexerBTC.expected_block_production_time, 9)
        self.assertEqual(indexerBTC.latest_indexed_block_height, 10)
        self.assertEqual(indexerBTC.latest_tip_block_height, 0)

    @patch("utxo_indexer.indexer.indexer_client.IndexerClient.extract_initial_block_height")
    def test_new(self, mock_extract_initial_block_height):
        """Test for new method for Bitcoin"""
        mock_extract_initial_block_height.return_value = 7
        with patch("utxo_indexer.indexer.indexer_client.config", new=self.configBTC):
            indexerBTC = IndexerClient.new(self.clientBTC, 9)
        self.assertEqual(indexerBTC._client, self.clientBTC)
        self.assertEqual(indexerBTC.instance_config, self.configBTC)
        self.assertEqual(len(indexerBTC.workers), 1)
        self.assertEqual(indexerBTC.toplevel_worker, indexerBTC.workers[0])
        self.assertEqual(isinstance(indexerBTC.toplevel_worker, Session), True)
        auth = HTTPBasicAuth(self.configBTC.AUTH_USERNAME, self.configBTC.AUTH_PASSWORD)
        self.assertEqual(indexerBTC.toplevel_worker.auth, auth)
        self.assertEqual(indexerBTC.expected_block_production_time, 9)
        self.assertEqual(indexerBTC.latest_indexed_block_height, 7)
        self.assertEqual(indexerBTC.latest_tip_block_height, 0)

    def test_default(self):
        """Test for default"""
        # Nothing to test, we have tested IndexerClient.new and BtcClient.default() already.
        pass

    def test_extract_initial_block_height_some_blocks(self):
        """Test for extract_initial_block_height method, when there are some blocks in db"""
        block = UtxoBlock(
            block_hash="", block_number=72, timestamp=0, previous_block_hash="", transactions=0, confirmed=True
        )
        block.save()

        # Case1: block_number < INITIAL_BLOCK_HEIGHT
        config1 = Config(
            SOURCE_NAME=self.configBTC.SOURCE_NAME,
            NODE_RPC_URL=self.configBTC.NODE_RPC_URL,
            AUTH_USERNAME=self.configBTC.AUTH_USERNAME,
            AUTH_PASSWORD=self.configBTC.AUTH_PASSWORD,
            INDEXER_POLL_INTERVAL=10,
            NUMBER_OF_BLOCK_CONFIRMATIONS=60,
            INITIAL_BLOCK_HEIGHT=73,
            NUMBER_OF_WORKERS=10,
            PRUNE_KEEP_DAYS=0,
            PRUNE_INTERVAL_SECONDS=60,
        )
        clientBTC1 = BtcClient(config1.NODE_RPC_URL)

        try:
            IndexerClient(clientBTC1, 1, config1)
        except Exception:
            pass
        else:
            raise AssertionError("block_number can't be smaller than INITIAL_BLOCK_HEIGHT")

        # Case2: block_number >= INITIAL_BLOCK_HEIGHT
        config2 = Config(
            SOURCE_NAME=self.configBTC.SOURCE_NAME,
            NODE_RPC_URL=self.configBTC.NODE_RPC_URL,
            AUTH_USERNAME=self.configBTC.AUTH_USERNAME,
            AUTH_PASSWORD=self.configBTC.AUTH_PASSWORD,
            INDEXER_POLL_INTERVAL=10,
            NUMBER_OF_BLOCK_CONFIRMATIONS=60,
            INITIAL_BLOCK_HEIGHT=72,
            NUMBER_OF_WORKERS=10,
            PRUNE_KEEP_DAYS=0,
            PRUNE_INTERVAL_SECONDS=60,
        )
        clientBTC2 = BtcClient(config2.NODE_RPC_URL)
        indexerBTC2 = IndexerClient(clientBTC2, 1, config2)
        self.assertEqual(indexerBTC2.latest_indexed_block_height, 72)

    @patch("utxo_indexer.indexer.indexer_client.IndexerClient._get_current_block_height")
    def test_extract_initial_block_height_no_blocks(self, mock_get_current_block_height):
        """Test for extract_initial_block_height method, when there are no blocks in db"""
        # During testing the db is emtpy by default, so latest_block variable in
        # extract_initial_block_height is None
        assert UtxoBlock.objects.order_by("block_number").last() is None

        # Case1: PRUNE_KEEP_DAYS <= 0
        config1 = Config(
            SOURCE_NAME=self.configBTC.SOURCE_NAME,
            NODE_RPC_URL=self.configBTC.NODE_RPC_URL,
            AUTH_USERNAME=self.configBTC.AUTH_USERNAME,
            AUTH_PASSWORD=self.configBTC.AUTH_PASSWORD,
            INDEXER_POLL_INTERVAL=10,
            NUMBER_OF_BLOCK_CONFIRMATIONS=60,
            INITIAL_BLOCK_HEIGHT=1,
            NUMBER_OF_WORKERS=10,
            PRUNE_KEEP_DAYS=0,
            PRUNE_INTERVAL_SECONDS=60,
        )
        clientBTC1 = BtcClient(config1.NODE_RPC_URL)
        indexerBTC1 = IndexerClient(clientBTC1, 1, config1)
        self.assertEqual(indexerBTC1.latest_indexed_block_height, config1.INITIAL_BLOCK_HEIGHT)

        # Case2: PRUNE_KEEP_DAYS > 0
        mock_get_current_block_height.return_value = 9
        # Subcase1: INITIAL_BLOCK_HEIGHT < height - blocks_since_pruning
        config2 = Config(
            SOURCE_NAME=self.configBTC.SOURCE_NAME,
            NODE_RPC_URL=self.configBTC.NODE_RPC_URL,
            AUTH_USERNAME=self.configBTC.AUTH_USERNAME,
            AUTH_PASSWORD=self.configBTC.AUTH_PASSWORD,
            INDEXER_POLL_INTERVAL=10,
            NUMBER_OF_BLOCK_CONFIRMATIONS=60,
            INITIAL_BLOCK_HEIGHT=1,
            NUMBER_OF_WORKERS=10,
            PRUNE_KEEP_DAYS=2,
            PRUNE_INTERVAL_SECONDS=60,
        )
        clientBTC2 = BtcClient(config2.NODE_RPC_URL)
        indexerBTC2 = IndexerClient(clientBTC2, 24 * 60 * 60, config2)
        self.assertEqual(indexerBTC2.latest_indexed_block_height, 6)

        # Subcase2: INITIAL_BLOCK_HEIGHT >= height - blocks_since_pruning
        config2 = Config(
            SOURCE_NAME=self.configBTC.SOURCE_NAME,
            NODE_RPC_URL=self.configBTC.NODE_RPC_URL,
            AUTH_USERNAME=self.configBTC.AUTH_USERNAME,
            AUTH_PASSWORD=self.configBTC.AUTH_PASSWORD,
            INDEXER_POLL_INTERVAL=10,
            NUMBER_OF_BLOCK_CONFIRMATIONS=60,
            INITIAL_BLOCK_HEIGHT=1,
            NUMBER_OF_WORKERS=10,
            PRUNE_KEEP_DAYS=6,
            PRUNE_INTERVAL_SECONDS=60,
        )
        clientBTC2 = BtcClient(config2.NODE_RPC_URL)
        indexerBTC2 = IndexerClient(clientBTC2, 24 * 60 * 60, config2)
        self.assertEqual(indexerBTC2.latest_indexed_block_height, 1)

    def test_update_tip_state_indexing(self):
        """Test for update_tip_state_indexing"""
        """Test that take some time to run is in comments"""
        indexerBTC = IndexerClient(self.clientBTC, 60, self.configBTC)
        TipSyncState.instance().delete()
        tip_state = TipSyncState.instance()
        tip_state.latest_tip_height = 400
        # timestamp_0 = tip_state.timestamp
        # time.sleep(2)
        tip_state.save()
        try:
            indexerBTC.update_tip_state_indexing(block_tip_height=399)
        except AssertionError:
            pass
        else:
            error = "block_tip_height must be bigger than tip_state.latest_tip_height"
            raise AssertionError(error)

        indexerBTC.update_tip_state_indexing(block_tip_height=402)
        tip_state = TipSyncState.instance()
        self.assertEqual(tip_state.latest_tip_height, 402)
        self.assertEqual(tip_state.sync_state, TipSyncStateChoices.syncing)
        # self.assertGreater(tip_state.timestamp, timestamp_0)

    def test_update_tip_state_idle(self):
        """Test for update_tip_state_idle"""
        """Test that take some time to run is in comments"""
        indexerBTC = IndexerClient(self.clientBTC, 60, self.configBTC)
        TipSyncState.instance().delete()
        # tip_state = TipSyncState.instance()
        # timestamp_0 = tip_state.timestamp
        # time.sleep(2)

        indexerBTC.update_tip_state_idle()
        tip_state = TipSyncState.instance()
        self.assertEqual(tip_state.sync_state, TipSyncStateChoices.up_to_date)
        # self.assertGreater(tip_state.timestamp, timestamp_0)

    def test_update_tip_state_done_block_process(self):
        """Test for update_tip_state_done_block_process"""
        """Test that take some time to run is in comments"""
        indexerBTC = IndexerClient(self.clientBTC, 60, self.configBTC)
        TipSyncState.instance().delete()
        tip_state = TipSyncState.instance()
        tip_state.latest_indexed_height = 400
        # timestamp_0 = tip_state.timestamp
        # time.sleep(2)
        tip_state.save()
        try:
            indexerBTC.update_tip_state_done_block_process(indexed_block_height=400)
        except AssertionError:
            pass
        else:
            error = "indexed_block_height must be bigger than tip_state.latest_indexed_height"
            raise AssertionError(error)

        indexerBTC.update_tip_state_done_block_process(indexed_block_height=402)
        tip_state = TipSyncState.instance()
        self.assertEqual(tip_state.latest_indexed_height, 402)
        self.assertEqual(tip_state.sync_state, TipSyncStateChoices.syncing)
        # self.assertGreater(tip_state.timestamp, timestamp_0)

    @patch("utxo_indexer.indexer.indexer_client.IndexerClient._get_block_hash_from_height")
    @patch("utxo_indexer.indexer.indexer_client.IndexerClient._get_block_by_hash")
    def test_process_block(self, mock_get_block_by_hash, mock_get_block_hash_from_height):
        """Test for process_block method"""
        mock_get_block_by_hash.return_value = block_example_bitcoin
        mock_get_block_hash_from_height.return_value = None
        TipSyncState.instance().delete()
        indexerBTC = BtcIndexerClient(self.clientBTC, 60, self.configBTC)
        indexerBTC.process_block(33232)

        self.assertEqual(UtxoBlock.objects.count(), 1)
        self.assertEqual(UtxoTransaction.objects.count(), 2)
        self.assertEqual(TransactionInputCoinbase.objects.count(), 1)
        self.assertEqual(TransactionInput.objects.count(), 1)
        self.assertEqual(TransactionOutput.objects.count(), 4)
        tip_state = TipSyncState.instance()
        self.assertEqual(tip_state.latest_indexed_height, 33232)

        tx1 = UtxoTransaction.objects.get(pk="ea57078c1ec6f4670fa3eb49c6486257ba36f9c49a0ad94d3b6cf631a2e92ae5")
        assert tx1 is not None
        self.assertEqual(tx1.source_addresses_root, "0000000000000000000000000000000000000000000000000000000000000000")

        tx2 = UtxoTransaction.objects.get(pk="cb09112278043f486e0e1b649d58c08e962958f2115d210f82f1ca9a13484ea2")
        assert tx2 is not None
        root = merkle_tree_from_address_strings(["tb1ql3u9666hjn28m0v2rulaqtwvqg3ewd543y66dy"]).root
        assert root is not None
        self.assertEqual(tx2.source_addresses_root, root[2:])

        # Nothing else needs to be tested here,
        # object_from_node_response and update_tip_state_done_block_process
        # have been tested already.

    def test_process_block_real_example(self):
        """Test for process_block method"""
        """This time we use real block and no mock functions"""
        TipSyncState.instance().delete()
        indexerBTC = BtcIndexerClient(self.clientBTC, 60, self.configBTC)
        indexerBTC.process_block(3127792)

        self.assertEqual(UtxoBlock.objects.count(), 1)
        self.assertEqual(UtxoTransaction.objects.count(), 3503)
        self.assertEqual(TransactionInputCoinbase.objects.count(), 1)
        self.assertEqual(TransactionOutput.objects.count(), 7083)
        self.assertEqual(TransactionInput.objects.count(), 3533)
        tip_state = TipSyncState.instance()
        self.assertEqual(tip_state.latest_indexed_height, 3127792)
        # Nothing else needs to be tested here,
        # object_from_node_response and update_tip_state_done_block_process
        # have been tested already.

    def test_run(self):
        """Test for run method"""
        pass


class BtcIndexerClientRealBTCTest(TestCase):
    def setUp(self):
        self.configBTC = get_testing_config("BTC", "btc")
        self.clientBTC = BtcClient(self.configBTC.NODE_RPC_URL)

    def test_source_addresses_root(self):
        """Test for source_addresses_root"""
        """The results are compared with same tests in mcc library"""
        TipSyncState.instance().delete()
        indexerBTC = BtcIndexerClient(self.clientBTC, 60, self.configBTC)
        indexerBTC.process_block(871299)
        self.assertEqual(UtxoTransaction.objects.count(), 1747)

        tx_cb = UtxoTransaction.objects.get(pk="203a8c661a241d25b1ea1da6fa36732118f39e169c22e227c68199ab729ab1ec")
        self.assertEqual(
            tx_cb.source_addresses_root, "0000000000000000000000000000000000000000000000000000000000000000"
        )

        tx = UtxoTransaction.objects.get(pk="f5d78b32b1684f040c5142bd6a814f391a216dc39848c4c3e4cfd3f02336b1c9")
        self.assertEqual(tx.source_addresses_root, "23699dbbba39d81c44489afe2da832f67038c710fbfb04a2be5a1a0e663da6be")
