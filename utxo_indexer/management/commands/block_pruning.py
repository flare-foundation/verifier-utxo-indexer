import logging
import time

from django.core.management.base import BaseCommand
from django.db import transaction

from configuration.config import config
from utxo_indexer.models import (
    TransactionInput,
    TransactionInputCoinbase,
    TransactionOutput,
    UtxoBlock,
    UtxoTransaction,
)
from utxo_indexer.models.sync_state import PruneSyncState

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        prune_state = PruneSyncState.instance()
        while True:
            if not config.PRUNE_KEEP_DAYS or config.PRUNE_KEEP_DAYS <= 0:
                logger.warn("Running a pruning task without PRUNE_KEEP_DAYS set, skipping")
                return

            now_ts = int(time.time())

            cutoff = now_ts - config.PRUNE_KEEP_DAYS * 24 * 60 * 60

            logger.info(f"Pruning at: {now_ts} all transactions and block before cutoff: {cutoff}")

            latest_block = UtxoBlock.objects.order_by("block_number").last()
            if latest_block is None or latest_block.timestamp <= cutoff:
                logger.info(
                    "Not pruning when the latest block height is older than PRUNE_KEEP_DAYS (%s days)",
                    config.PRUNE_KEEP_DAYS,
                )
            else:
                with transaction.atomic():
                    # objects with fk to transaction first
                    TransactionInput.objects.filter(transaction_link__timestamp__lt=cutoff).delete()
                    TransactionInputCoinbase.objects.filter(transaction_link__timestamp__lt=cutoff).delete()
                    TransactionOutput.objects.filter(transaction_link__timestamp__lt=cutoff).delete()

                    # then others
                    UtxoBlock.objects.filter(timestamp__lt=cutoff).delete()
                    UtxoTransaction.objects.filter(timestamp__lt=cutoff).delete()

                    bottom_block = UtxoBlock.objects.order_by("block_number").first()
                    bottom_block_transaction = UtxoTransaction.objects.order_by("block_number").first()

                    if bottom_block is not None and bottom_block_transaction is not None:
                        if bottom_block.block_number != bottom_block_transaction.block_number:
                            raise Exception("Bottom block and bottom transaction block number mismatch while pruning")

                        prune_state.latest_indexed_tail_height = bottom_block.block_number
                        prune_state.timestamp = now_ts
                        prune_state.save()

                logger.info("Prune finished, sleeping for %s sec", config.PRUNE_INTERVAL_SECONDS)

            time.sleep(config.PRUNE_INTERVAL_SECONDS)
