import logging

from django.test import TestCase
from requests.models import HTTPBasicAuth
from requests.sessions import Session

from configuration.config import get_testing_config
from utxo_indexer.indexer.decorators import retry
from utxo_indexer.indexer.doge import DogeClient
from utxo_indexer.indexer.indexer_client import IndexerClient, new_session
from utxo_indexer.indexer.types import PostProcessingMemoryElement
from utxo_indexer.models import (
    TransactionInput,
    TransactionInputCoinbase,
    UtxoTransaction,
)
from utxo_indexer.tests.data_for_testing.testing_models_data import (
    tx_example1,
    vin_example,
    vin_example_coinbase,
    vout_example,
)
from utxo_indexer.utils import merkle_tree_from_address_strings

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

    """Most tests are made seperately for bitcoin and doge"""
    """in test_doge.py and test_bitcoin.py"""

    def setUp(self):
        configDoge = get_testing_config("DOGE", "doge")
        clientDoge = DogeClient(configDoge.NODE_RPC_URL)
        self.indexerDoge = IndexerClient(clientDoge, 60, configDoge)
        configBTC = get_testing_config("TEST_BTC_V3", "btc")
        clientBTC = DogeClient(configBTC.NODE_RPC_URL)
        self.indexerBTC = IndexerClient(clientBTC, 60, configBTC)

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

    def test_process_block(self):
        """Test for process_block"""
        try:
            self.indexerBTC.process_block(6)
        except NotImplementedError:
            AssertionError("proces_block method in BtcIndexerClient is undefined")
        try:
            self.indexerDoge.process_block(6)
        except NotImplementedError:
            AssertionError("proces_block method in DogeIndexerClient is undefined")

    def test_update_source_addresses_root_from_tx_data(self):
        tx = UtxoTransaction.object_from_node_response(tx_example1, 3127876, 1728884507)
        cbi = TransactionInputCoinbase.object_from_node_response(0, vin_example_coinbase, tx)
        inp = TransactionInput.object_from_node_response(0, vin_example, vout_example, tx)
        t1 = PostProcessingMemoryElement(obj=tx, cbi=[], inp=[])
        try:
            self.indexerDoge.update_source_addresses_root_from_tx_data(t1)
        except Exception:
            pass
        else:
            raise AssertionError()

        t2 = PostProcessingMemoryElement(obj=tx, cbi=[cbi], inp=[inp])
        try:
            self.indexerDoge.update_source_addresses_root_from_tx_data(t2)
        except Exception:
            pass
        else:
            raise AssertionError()

        t3 = PostProcessingMemoryElement(obj=tx, cbi=[cbi], inp=[])
        self.indexerDoge.update_source_addresses_root_from_tx_data(t3)
        self.assertEqual(tx.source_addresses_root, "0000000000000000000000000000000000000000000000000000000000000000")

        t3 = PostProcessingMemoryElement(obj=tx, cbi=[cbi], inp=[])
        self.indexerBTC.update_source_addresses_root_from_tx_data(t3)
        self.assertEqual(tx.source_addresses_root, "0000000000000000000000000000000000000000000000000000000000000000")

        t4 = PostProcessingMemoryElement(obj=tx, cbi=[], inp=[inp])
        self.indexerDoge.update_source_addresses_root_from_tx_data(t4)
        root = merkle_tree_from_address_strings(["11tb1qq5yf3rn3dwsnjyt4h3npuqg4hedgsd56sc0jqz"]).root
        assert root is not None
        self.assertEqual(tx.source_addresses_root, root[2:])

        t4 = PostProcessingMemoryElement(obj=tx, cbi=[], inp=[inp])
        self.indexerBTC.update_source_addresses_root_from_tx_data(t4)
        root = merkle_tree_from_address_strings(["11tb1qq5yf3rn3dwsnjyt4h3npuqg4hedgsd56sc0jqz"]).root
        assert root is not None
        self.assertEqual(tx.source_addresses_root, root[2:])
