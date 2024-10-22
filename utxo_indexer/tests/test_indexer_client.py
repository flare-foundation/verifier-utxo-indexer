import logging

from django.test import TestCase
from requests.models import HTTPBasicAuth
from requests.sessions import Session

from configuration.config import get_testing_config
from utxo_indexer.indexer.decorators import retry
from utxo_indexer.indexer.doge import DogeClient
from utxo_indexer.indexer.indexer_client import IndexerClient, new_session

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
