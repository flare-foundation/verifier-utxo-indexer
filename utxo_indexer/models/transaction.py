from typing import TYPE_CHECKING, List, Sequence

from django.db import models

from utxo_indexer.models.model_utils import HexString32ByteField
from utxo_indexer.models.types import CoinbaseVinResponse, TransactionResponse, VoutResponse
from utxo_indexer.utils import (
    ZERO_BYTES_32,
    WordToOpcode,
    is_valid_bytes_32_hex,
    merkle_tree_from_address_strings,
    un_prefix_0x,
)

if TYPE_CHECKING:
    from utxo_indexer.models import (
        TransactionInput,
        TransactionInputCoinbase,
        TransactionOutput,
    )

ZERO_REFERENCE = ZERO_BYTES_32
ZERO_SOURCE_ADDRESS_ROOT = ZERO_BYTES_32


class UtxoTransaction(models.Model):
    transactioninput_set: models.Manager["TransactionInput"]
    transactioninputcoinbase_set: models.Manager["TransactionInputCoinbase"]
    transactionoutput_set: models.Manager["TransactionOutput"]

    transaction_id = HexString32ByteField(primary_key=True)

    block_number = models.PositiveIntegerField()
    timestamp = models.PositiveBigIntegerField()

    # Precalculated field to enable quick search for transactions to support attestation types
    payment_reference = HexString32ByteField(null=True)
    source_addresses_root = HexString32ByteField()

    # All transactions but coinbase are native payment transactions
    is_native_payment = models.BooleanField(default=False)

    # TODO: consider update to enum field
    transaction_type = models.CharField()

    # response = models.BinaryField(db_column="response")

    class Meta:
        indexes = (
            models.Index(fields=["block_number"]),
            models.Index(fields=["timestamp"]),
            models.Index(fields=["payment_reference"]),
            models.Index(fields=["transaction_type"]),
            models.Index(fields=["source_addresses_root"]),
        )

    def __str__(self) -> str:
        return f"Transaction {self.transaction_id} in block : {self.block_number}"

    def update_source_addresses_root(self, inputs: List["TransactionInput"]):
        addresses = []
        for input in inputs:
            if input.script_key_address != "":
                addresses.append(input.script_key_address)
            else:
                addresses.append(None)
        self.source_addresses_root = self._construct_address_root(addresses)

    def update_source_addresses_root_cb(self, inputs: List["TransactionInputCoinbase"]):
        addresses = [None]
        self.source_addresses_root = self._construct_address_root(addresses)

    def _construct_address_root(self, addresses: Sequence[str | None]) -> str:
        tree = merkle_tree_from_address_strings(addresses)
        if tree.root is None:
            return ZERO_SOURCE_ADDRESS_ROOT
        return un_prefix_0x(tree.root).lower()

    @classmethod
    def object_from_node_response(cls, response: TransactionResponse, block_number: int, timestamp: int):
        ref = cls._extract_payment_reference(response)
        is_coinbase = cls._is_coinbase_transaction(response)
        if is_coinbase:
            return cls(
                block_number=block_number,
                timestamp=timestamp,
                transaction_id=response.txid.lower(),
                payment_reference=None,
                is_native_payment=False,
                transaction_type="coinbase",
                source_addresses_root=ZERO_SOURCE_ADDRESS_ROOT,
            )
        return cls(
            block_number=block_number,
            timestamp=timestamp,
            transaction_id=response.txid.lower(),
            payment_reference=ref,
            is_native_payment=True,
            transaction_type="full_payment",
            source_addresses_root=ZERO_SOURCE_ADDRESS_ROOT,
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
            return std_references[0].lower()
        return None
