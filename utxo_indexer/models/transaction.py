from typing import TYPE_CHECKING

from django.db import models

from utxo_indexer.models.model_utils import HexString32ByteField
from utxo_indexer.models.types import CoinbaseVinResponse, TransactionResponse, VoutResponse
from utxo_indexer.utils import WordToOpcode, is_valid_bytes_32_hex

if TYPE_CHECKING:
    from utxo_indexer.models import (
        TransactionInput,
        TransactionInputCoinbase,
        TransactionOutput,
    )

ZERO_REFERENCE = "0000000000000000000000000000000000000000000000000000000000000000"


class UtxoTransaction(models.Model):
    transactioninput_set: models.Manager["TransactionInput"]
    transactioninputcoinbase_set: models.Manager["TransactionInputCoinbase"]
    transactionoutput_set: models.Manager["TransactionOutput"]

    transaction_id = HexString32ByteField(primary_key=True, db_column="transactionId")

    block_number = models.PositiveIntegerField(db_column="blockNumber")
    timestamp = models.PositiveBigIntegerField(db_column="timestamp")

    payment_reference = HexString32ByteField(db_column="paymentReference")

    # All transactions but coinbase are native payment transactions
    is_native_payment = models.BooleanField(default=False, db_column="isNativePayment")

    # TODO: update to enum field
    transaction_type = models.CharField(db_column="transactionType")

    # response = models.BinaryField(db_column="response")

    class Meta:
        indexes = (
            models.Index(fields=["block_number"]),
            models.Index(fields=["timestamp"]),
            models.Index(fields=["payment_reference"]),
            models.Index(fields=["transaction_type"]),
        )

    def __str__(self) -> str:
        return f"Transaction {self.transaction_id} in block : {self.block_number}"

    @classmethod
    def object_from_node_response(cls, response: TransactionResponse, block_number: int, timestamp: int):
        ref = cls._extract_payment_reference(response)
        is_coinbase = cls._is_coinbase_transaction(response)
        if is_coinbase:
            return cls(
                block_number=block_number,
                timestamp=timestamp,
                transaction_id=response.txid,
                payment_reference=ZERO_REFERENCE,
                is_native_payment=False,
                transaction_type="coinbase",
            )
        return cls(
            block_number=block_number,
            timestamp=timestamp,
            transaction_id=response.txid,
            payment_reference=ref,
            is_native_payment=True,
            transaction_type="full_payment",
        )

    @staticmethod
    def _is_coinbase_transaction(response: TransactionResponse):
        for vin in response.vin:
            if isinstance(vin, CoinbaseVinResponse):
                return True
        return False

    @staticmethod
    def _extract_payment_reference(response: TransactionResponse):
        def is_op_return(vout: VoutResponse):
            return vout.scriptPubKey.asm.startswith("OP_RETURN")

        std_references = []
        op_return_id = hex(WordToOpcode.OP_RETURN.value)[2:]

        for vout in response.vout:
            if is_op_return(vout):
                data = vout.scriptPubKey.hex
                if len(data) < 2:
                    continue
                if data[:2] == op_return_id:
                    if len(data) < 4:
                        continue
                    # TODO: test if len can be more than 2**32 (4 bytes)
                    message = data[4:]
                    if is_valid_bytes_32_hex(message):
                        std_references.append(message)

        if len(std_references) == 1:
            return std_references[0]
        return ZERO_REFERENCE
