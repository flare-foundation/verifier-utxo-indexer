from django.db import models

from utxo_indexer.models.model_utils import HexString32ByteField
from utxo_indexer.models.types import BlockResponse


class UtxoBlock(models.Model):
    block_hash = HexString32ByteField(primary_key=True)

    block_number = models.PositiveIntegerField()
    timestamp = models.PositiveBigIntegerField()
    previous_block_hash = HexString32ByteField()

    # Number of transactions in block
    transactions = models.PositiveIntegerField()

    confirmed = models.BooleanField(default=False)

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
            block_hash=response.hash.lower(),
            previous_block_hash=response.previousblockhash.lower(),
            transactions=len(response.tx),
            confirmed=True,
        )
