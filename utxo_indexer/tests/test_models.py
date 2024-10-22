import logging

from django.db.utils import DataError
from django.test import TestCase

from utxo_indexer.models.block import UtxoBlock
from utxo_indexer.models.sync_state import PruneSyncState, TipSyncState, TipSyncStateChoices
from utxo_indexer.models.transaction import UtxoTransaction
from utxo_indexer.models.transaction_outputs import TransactionInput, TransactionInputCoinbase, TransactionOutput
from utxo_indexer.tests.data_for_testing.testing_models_data import (
    block_example,
    tx_example1,
    tx_example2,
    tx_example_coinbase,
    vin_example,
    vin_example_coinbase,
    vout_example,
)

logging.disable(logging.CRITICAL)


class BlockTest(TestCase):
    def test_object_from_node_response(self):
        block = UtxoBlock.object_from_node_response(block_example)
        self.assertEqual(isinstance(block, UtxoBlock), True)
        self.assertEqual(block_example.height, block.block_number)
        self.assertEqual(block_example.mediantime, block.timestamp)
        self.assertEqual(block_example.hash, block.block_hash)
        self.assertEqual(block_example.previousblockhash, block.previous_block_hash)
        self.assertEqual(len(block_example.tx), block.transactions)

    def test_HexString32ByteField(self):
        block_long_hash = UtxoBlock(
            block_hash="12345678901234567890123456789012345678901234567890123456789012345",
            block_number=1,
            timestamp=0,
            previous_block_hash="",
            transactions=0,
            confirmed=True,
        )
        block_normal_hash = UtxoBlock(
            block_hash="1234567890123456789012345678901234567890123456789012345678901234",
            block_number=1,
            timestamp=0,
            previous_block_hash="",
            transactions=0,
            confirmed=True,
        )
        block_normal_hash.save()
        try:
            block_long_hash.save()
        except DataError:
            pass
        else:
            raise ValueError("block_hash of block_long_hash is too long")


class UtxoTransactionTest(TestCase):
    def test__is_coinbase_transaction(self):
        boolean_ex1 = UtxoTransaction._is_coinbase_transaction(tx_example_coinbase)
        boolean_ex2 = UtxoTransaction._is_coinbase_transaction(tx_example1)
        self.assertEqual(boolean_ex1, True)
        self.assertEqual(boolean_ex2, False)

    def test__extract_payment_reference(self):
        reference_ex1 = UtxoTransaction._extract_payment_reference(tx_example1)
        reference_ex2 = UtxoTransaction._extract_payment_reference(tx_example2)
        self.assertEqual(reference_ex1, "0000000000000000000000000000000000000000000000000000000000000000")
        self.assertEqual(reference_ex2, "aa21a9ed6c401b737bf1cd54a846760c3050908b77ef20c5e85880848fb3d1c8")

    def test_object_from_node_response(self):
        tx_examle_model = UtxoTransaction.object_from_node_response(tx_example1, 3127876, 1728884507)
        self.assertEqual(isinstance(tx_examle_model, UtxoTransaction), True)
        self.assertEqual(
            tx_examle_model.transaction_id, "279ea599e880def81e3c15f3aee904fae7d90abcfd73470b581efa192b62c5f6"
        )
        self.assertEqual(tx_examle_model.block_number, 3127876)
        self.assertEqual(tx_examle_model.timestamp, 1728884507)
        self.assertEqual(
            tx_examle_model.payment_reference, "0000000000000000000000000000000000000000000000000000000000000000"
        )
        self.assertEqual(tx_examle_model.is_native_payment, True)
        self.assertEqual(tx_examle_model.transaction_type, "full_payment")

        tx_example_coinbase_model = UtxoTransaction.object_from_node_response(tx_example_coinbase, 3127876, 1728884507)
        self.assertEqual(isinstance(tx_example_coinbase_model, UtxoTransaction), True)
        self.assertEqual(
            tx_example_coinbase_model.transaction_id, "279ea599e880def81e3c15f3aee904fae7d90abcfd73470b581efa192b62c5f6"
        )
        self.assertEqual(tx_example_coinbase_model.block_number, 3127876)
        self.assertEqual(tx_example_coinbase_model.timestamp, 1728884507)
        self.assertEqual(
            tx_example_coinbase_model.payment_reference,
            "0000000000000000000000000000000000000000000000000000000000000000",
        )
        self.assertEqual(tx_example_coinbase_model.is_native_payment, False)
        self.assertEqual(tx_example_coinbase_model.transaction_type, "coinbase")


class TransactionOutputTest(TestCase):
    def setUp(self):
        self.transaction = UtxoTransaction(
            transaction_id="63c25bcfcce2d2e830dec089d84653c678e6841cf375cdcc5518590cba5b2008",
            block_number=1,
            timestamp=1,
            payment_reference="0000000000000000000000000000000000000000000000000000000000000000",
            is_native_payment=True,
            transaction_type="",
        )
        self.transaction.save()

    def test_object_from_node_response(self):
        tx_out1 = TransactionOutput.object_from_node_response(
            vout_example, "63c25bcfcce2d2e830dec089d84653c678e6841cf375cdcc5518590cba5b2008"
        )
        self.assertEqual(isinstance(tx_out1, TransactionOutput), True)
        self.assertEqual(tx_out1.n, 0)
        self.assertEqual(tx_out1.value, "1.13428769")
        self.assertEqual(tx_out1.script_key_asm, "0 0508988e716ba1391175bc661e0115be5a88369a")
        self.assertEqual(tx_out1.script_key_hex, "00140508988e716ba1391175bc661e0115be5a88369a")
        self.assertEqual(tx_out1.script_key_req_sigs, 2)
        self.assertEqual(tx_out1.script_key_type, "witness_v0_keyhash")
        self.assertEqual(tx_out1.script_key_address, "11tb1qq5yf3rn3dwsnjyt4h3npuqg4hedgsd56sc0jqz")
        self.assertEqual(tx_out1.transaction_link, self.transaction)


class TransactionInputCoinbaseTest(TestCase):
    def setUp(self):
        self.transaction = UtxoTransaction(
            transaction_id="45f91bcfcce2d2e830dec089d84653c678e6841cf375cdcc5518590cba5b2008",
            block_number=1,
            timestamp=1,
            payment_reference="0000000000000000000000000000000000000000000000000000000000000000",
            is_native_payment=True,
            transaction_type="",
        )
        self.transaction.save()

    def test_object_from_node_response(self):
        try:
            TransactionInputCoinbase.object_from_node_response(
                1, vin_example_coinbase, "45f91bcfcce2d2e830dec089d84653c678e6841cf375cdcc5518590cba5b2008"
            )
        except AssertionError:
            pass
        else:
            raise ValueError("vin_n=1 is not 0")

        tx_in = TransactionInputCoinbase.object_from_node_response(
            0, vin_example_coinbase, "45f91bcfcce2d2e830dec089d84653c678e6841cf375cdcc5518590cba5b2008"
        )
        self.assertEqual(isinstance(tx_in, TransactionInputCoinbase), True)
        self.assertEqual(tx_in.vin_n, 0)
        self.assertEqual(tx_in.vin_coinbase, "0344ba2f00")
        self.assertEqual(tx_in.vin_sequence, 4294967295)
        self.assertEqual(tx_in.transaction_link, self.transaction)


class TransactionInputTest(TestCase):
    def setUp(self):
        self.transaction = UtxoTransaction(
            transaction_id="73f91bcfcce2d2e830dec089d84653c678e6841cf375cdcc5518590cba5b2008",
            block_number=1,
            timestamp=1,
            payment_reference="0000000000000000000000000000000000000000000000000000000000000000",
            is_native_payment=True,
            transaction_type="",
        )
        self.transaction.save()

    def test_object_from_node_response(self):
        tx_in1 = TransactionInput.object_from_node_response(
            1, vin_example, vout_example, "73f91bcfcce2d2e830dec089d84653c678e6841cf375cdcc5518590cba5b2008"
        )
        self.assertEqual(isinstance(tx_in1, TransactionInput), True)
        self.assertEqual(tx_in1.n, 0)
        self.assertEqual(tx_in1.value, "1.13428769")
        self.assertEqual(tx_in1.script_key_asm, "0 0508988e716ba1391175bc661e0115be5a88369a")
        self.assertEqual(tx_in1.script_key_hex, "00140508988e716ba1391175bc661e0115be5a88369a")
        self.assertEqual(tx_in1.script_key_req_sigs, 2)
        self.assertEqual(tx_in1.script_key_type, "witness_v0_keyhash")
        self.assertEqual(tx_in1.script_key_address, "11tb1qq5yf3rn3dwsnjyt4h3npuqg4hedgsd56sc0jqz")

        self.assertEqual(tx_in1.vin_previous_txid, "18d99e54a50e48c58d462b41d1fcc8a45c9d881dc1f068edd0bb0445dfc3ee09")
        self.assertEqual(tx_in1.vin_vout_index, 1)
        self.assertEqual(tx_in1.vin_sequence, 4294967293)
        self.assertEqual(tx_in1.vin_script_sig_asm, "")
        self.assertEqual(tx_in1.vin_script_sig_hex, "")

        self.assertEqual(tx_in1.vin_n, 1)
        self.assertEqual(tx_in1.transaction_link, self.transaction)


class TipSyncStateTest(TestCase):
    def test_instance(self):
        instance1 = TipSyncState.instance()
        self.assertEqual(isinstance(instance1, TipSyncState), True)
        self.assertEqual(instance1.sync_state, TipSyncStateChoices.created)
        self.assertEqual(instance1.latest_tip_height, 0)
        self.assertEqual(instance1.latest_indexed_height, 0)

        instance2 = TipSyncState.instance()
        self.assertEqual(instance1, instance2)


class PruneSyncStateTest(TestCase):
    def test_instance(self):
        instance1 = PruneSyncState.instance()
        self.assertEqual(isinstance(instance1, PruneSyncState), True)
        self.assertEqual(instance1.latest_indexed_tail_height, 0)

        instance2 = PruneSyncState.instance()
        self.assertEqual(instance1, instance2)
