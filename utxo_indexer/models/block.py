from django.db import models

from utxo_indexer.models.model_utils import HexString32ByteField
from utxo_indexer.models.types import BlockResponse


class UtxoBlock(models.Model):
    block_hash = HexString32ByteField(primary_key=True, db_column="blockHash")

    block_number = models.PositiveIntegerField(db_column="blockNumber")
    timestamp = models.PositiveBigIntegerField(db_column="timestamp")
    previous_block_hash = HexString32ByteField(db_column="previousBlockHash")

    # Number of transactions in block
    transactions = models.PositiveIntegerField(db_column="transactions")

    confirmed = models.BooleanField(default=False, db_column="confirmed")

    class Meta:
        indexes = (
            models.Index(fields=["block_number"]),
            models.Index(fields=["timestamp"]),
            models.Index(fields=["previous_block_hash"]),
        )

    def __str__(self) -> str:
        return f"Block {self.block_number} : {self.block_hash}"

    @classmethod
    def object_from_node_response(cls, response: BlockResponse):
        return cls(
            block_number=response.height,
            timestamp=response.mediantime,
            block_hash=response.hash,
            previous_block_hash=response.previousblockhash,
            transactions=len(response.tx),
            confirmed=True,
        )
