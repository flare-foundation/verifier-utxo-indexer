import logging
from unittest.mock import patch

from django.test import TestCase
from requests.models import HTTPBasicAuth
from requests.sessions import Session

from client.btc_client import BtcClient
from client.doge_client import DogeClient
from configuration.config import get_testing_config
from configuration.types import Config
from utxo_indexer.indexer.decorators import retry
from utxo_indexer.indexer.indexer_client import IndexerClient, new_session
from utxo_indexer.models import UtxoBlock
from utxo_indexer.models.sync_state import TipSyncState, TipSyncStateChoices

# DISABLE LOGGING
logging.disable(logging.CRITICAL)


class DecoratorRetryTest(TestCase):
    """Tests for decorators.py file"""

    def test_get_current_block_height(self):
        """Test for decorator retry"""

        def error_until(n):
            call_count = 0

            def inner_function():
                nonlocal call_count
                call_count += 1
                if call_count <= n:
                    raise Exception
                return "All good!"

            return inner_function

        error_function1 = error_until(4)
        error_function2 = error_until(5)

        self.assertEqual(retry(5)(error_function1)(), "All good!")
        try:
            retry(5)(error_function2)()
        except Exception:
            pass
        else:
            raise AssertionError("retry should return exception, because" "error_until returns Exception 5 times")


class IndexerClientAuxiliaryFunctionTest(TestCase):
    """Tests for auxuliary functions in indexer_client.py"""

    def test_new_session(self):
        """Test for new_session function"""
        # Case Bitcoin
        configBTC = get_testing_config("TEST_BTC_V3", "btc")
        sesionBTC = new_session(configBTC)
        self.assertEqual(isinstance(sesionBTC, Session), True)
        authBTC = HTTPBasicAuth(configBTC.AUTH_USERNAME, configBTC.AUTH_PASSWORD)
        self.assertEqual(sesionBTC.auth, authBTC)
        # Case Doge
        configDoge = get_testing_config("DOGE", "doge")
        sesionDoge = new_session(configDoge)
        self.assertEqual(isinstance(sesionDoge, Session), True)
        authDoge = HTTPBasicAuth(configDoge.AUTH_USERNAME, configDoge.AUTH_PASSWORD)
        self.assertEqual(sesionDoge.auth, authDoge)


class IndexerClientTest(TestCase):
    """Tests for IndexerClient class"""

    def setUp(self):
        self.configBTC = get_testing_config("TEST_BTC_V3", "btc")
        self.clientBTC = BtcClient(self.configBTC.NODE_RPC_URL)
        self.configDoge = get_testing_config("DOGE", "doge")
        self.clientDoge = DogeClient(self.configDoge.NODE_RPC_URL)

    @patch("utxo_indexer.indexer.indexer_client.IndexerClient.extract_initial_block_height")
    def test_init_BTC(self, mock_extract_initial_block_height):
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
        self.assertEqual(len(indexerBTC.workers), self.configBTC.NUMBER_OF_WORKERS)
        auth = HTTPBasicAuth(self.configBTC.AUTH_USERNAME, self.configBTC.AUTH_PASSWORD)
        for worker in indexerBTC.workers:
            self.assertEqual(isinstance(worker, Session), True)
            self.assertEqual(worker.auth, auth)
        self.assertEqual(indexerBTC.toplevel_worker, indexerBTC.workers[0])
        self.assertEqual(indexerBTC.expected_block_production_time, 9)
        self.assertEqual(indexerBTC.latest_indexed_block_height, 10)
        self.assertEqual(indexerBTC.latest_tip_block_height, 0)

    @patch("utxo_indexer.indexer.indexer_client.IndexerClient.extract_initial_block_height")
    def test_init_Doge(self, mock_extract_initial_block_height):
        """Test for initialisation of Doge IndexerClient"""
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
    def test_new_BTC(self, mock_extract_initial_block_height):
        """Test for new method for Bitcoin"""
        mock_extract_initial_block_height.return_value = 7
        with patch("utxo_indexer.indexer.indexer_client.config", new=self.configBTC):
            indexerBTC = IndexerClient.new(self.clientBTC, 9)
        self.assertEqual(indexerBTC._client, self.clientBTC)
        self.assertEqual(indexerBTC.instance_config, self.configBTC)
        self.assertEqual(len(indexerBTC.workers), self.configBTC.NUMBER_OF_WORKERS)
        auth = HTTPBasicAuth(self.configBTC.AUTH_USERNAME, self.configBTC.AUTH_PASSWORD)
        for worker in indexerBTC.workers:
            self.assertEqual(isinstance(worker, Session), True)
            self.assertEqual(worker.auth, auth)
        self.assertEqual(indexerBTC.toplevel_worker, indexerBTC.workers[0])
        self.assertEqual(indexerBTC.expected_block_production_time, 9)
        self.assertEqual(indexerBTC.latest_indexed_block_height, 7)
        self.assertEqual(indexerBTC.latest_tip_block_height, 0)

    @patch("utxo_indexer.indexer.indexer_client.IndexerClient.extract_initial_block_height")
    def test_new_Doge(self, mock_extract_initial_block_height):
        """Test for new method for Doge"""
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

    def test_run(self):
        pass

    def test_get_current_block_height(self):
        """Test for _get_current_block_height"""
        # Nothing to test, we have tested retry and client.get_block_height already.
        pass

    def test_get_block_hash_from_height(self):
        """Test for _get_block_hash_from_height"""
        # Nothing to test, we have tested retry and client.get_block_hash_from_height already.
        pass

    def test_get_block_by_hash(self):
        """Test for _get_block_by_hash"""
        # Nothing to test, we have tested retry and client.get_block_by_hash already.
        pass

    def test_get_transaction(self):
        """Test for _get_transaction"""
        # Nothing to test, we have tested retry and client.get_transaction already.
        pass

    def test_update_tip_state_indexing(self):
        """Test for update_tip_state_indexing"""
        """Test that take some time to run is in comments"""
        indexerBTC = IndexerClient(self.clientBTC, 60, self.configBTC)
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

    def test_process_block(self):
        """Test for process_block"""
        indexerBTC = IndexerClient(self.clientBTC, 60, self.configBTC)
        indexerDoge = IndexerClient(self.clientDoge, 60, self.configDoge)
        try:
            indexerBTC.process_block(6)
        except NotImplementedError:
            AssertionError("proces_block method in BtcIndexerClient is undefined")
        try:
            indexerDoge.process_block(6)
        except NotImplementedError:
            AssertionError("proces_block method in DogeIndexerClient is undefined")
