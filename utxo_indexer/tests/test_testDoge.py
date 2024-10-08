import logging
from typing import Any

from django.test import TestCase

from client import DogeClient
from configuration.config import get_testing_config
from utxo_indexer.indexer import DogeIndexerClient
from utxo_indexer.models import UtxoTransaction

# DISABLE LOGGING
logging.disable(logging.CRITICAL)


class TransactionReferenceTest(TestCase):
    """Doge testnet reference transaction test"""

    def setUp(self, **kwargs: Any) -> Any:
        config = get_testing_config("TEST_DOGE", "doge")
        client = DogeClient(config.NODE_RPC_URL)
        self.indexer = DogeIndexerClient(client, 60, config)
        self.indexer.process_block(6319658)

    def test_payment_reference_extracted(self):
        """Testing payment reference extraction"""
        tx_id = "e0cc82dc9606efb224f1ecb5c06cdbc6cf511ad487089080f1edd18a61d342d6"
        tx = UtxoTransaction.objects.get(transaction_id=tx_id)

        self.assertEqual(
            tx.payment_reference,
            "10000000000000000000000000000000000000000beefbeaddeafdeaddeedcab",
        )
