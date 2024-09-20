import logging
import queue
import threading
from typing import Callable

from django.db import transaction
from requests.sessions import Session

from client import DogeClient
from configuration.config import config
from utxo_indexer.models import (
    TransactionInput,
    TransactionInputCoinbase,
    TransactionOutput,
    UtxoBlock,
    UtxoTransaction,
)
from utxo_indexer.models.types import IUtxoVinTransaction

from .indexer_client import IndexerClient
from .types import BlockInformationPassing, BlockProcessorMemory

logger = logging.getLogger(__name__)


def thread_worker(session: Session, process_queue: queue.Queue, processed_block: BlockProcessorMemory):
    while not process_queue.empty():
        item = process_queue.get()
        if callable(item):
            item(session, processed_block)
        else:
            raise Exception("Item in queue is not callable")


def process_toplevel_transaction(
    process_queue: queue.Queue,
    txid: str,
    block_info: BlockInformationPassing,
    transaction_getter: Callable,
):
    """Return the function that processes each individual transaction and fills the processing queue with all necessary additional tasks this creates

    Args:
        process_queue (queue.Queue): a queue that is shared between all workers and contains all the tasks that need to be processed
        txid (str): transaction id to process
        block_num (int): information about block number this transaction is a part of
        block_ts (int): information about block timestamp this transaction is a part of
    """

    def _process_toplevel_transaction(session: Session, processed_block: BlockProcessorMemory):
        res = transaction_getter(txid, session)

        tx_link = UtxoTransaction.object_from_node_response(res, block_info.block_num, block_info.block_ts)
        processed_block.tx.append(tx_link)

        for ind, vin in enumerate(res["vin"]):
            process_queue.put(process_pre_vout_transaction(vin, ind, tx_link.transaction_id, transaction_getter))

        for vout in res["vout"]:
            processed_block.vouts.append(TransactionOutput.object_from_node_response(vout, tx_link.transaction_id))

        return True

    return _process_toplevel_transaction


def process_pre_vout_transaction(
    vin: IUtxoVinTransaction,
    vin_n: int,
    tx_link: str,
    transaction_getter: Callable,
):
    """Return the function that processes the transaction prevouts and link it to the spending transaction

    Args:
        vin (IUtxoVinTransaction): vin object from spending transaction
        vin_n (int): index of vin in spending transaction
        tx_link (str): transaction id of spending transaction
    """

    def _process_pre_vout_transaction(session: Session, processed_block: BlockProcessorMemory):
        if "txid" not in vin or "vout" not in vin:
            # Only coinbase transactions have no txid
            processed_block.vins_cb.append(TransactionInputCoinbase.object_from_node_response(vin_n, vin, tx_link))
            return True
        txid, vout_n = vin["txid"], vin["vout"]
        res = transaction_getter(txid, session)
        prevout_res = res["vout"][vout_n]
        processed_block.vins.append(TransactionInput.object_from_node_response(vin_n, vin, prevout_res, tx_link))
        return True

    return _process_pre_vout_transaction


class DogeIndexerClient(IndexerClient):
    @classmethod
    def default(cls):
        return cls(DogeClient(), 60)

    # Block processing part
    def process_block(self, block_height: int):
        # NOTICE: we always assume that block processing is for blocks that are for sure on main branch of the blockchain

        processed_blocks = BlockProcessorMemory()
        process_queue: queue.Queue = queue.Queue()

        block_hash = self._get_block_hash_from_height(block_height, self.toplevel_worker)
        res_block = self._get_block_by_hash(block_hash, self.toplevel_worker)

        tx_ids = res_block["tx"]
        block_info = BlockInformationPassing(
            block_num=res_block["height"],
            block_ts=res_block["mediantime"],
        )

        # Update the block info in DB, indicating it has processed transactions once we proceeded them
        # do it within transaction atomic update
        block_db = UtxoBlock.object_from_node_response(res_block)

        # Put all of the transaction in block on the processing queue
        for tx in tx_ids:
            process_queue.put(process_toplevel_transaction(process_queue, tx, block_info, self._get_transaction))

        # multithreading part of the processing
        workers = []

        for worker_index in range(config.NUMBER_OF_WORKERS):
            t = threading.Thread(
                target=thread_worker, args=(self.workers[worker_index], process_queue, processed_blocks)
            )
            workers.append(t)
            t.start()

        [t.join() for t in workers]

        if not process_queue.empty():
            raise Exception("Queue should be empty after processing")

        with transaction.atomic():
            UtxoTransaction.objects.bulk_create(processed_blocks.tx, batch_size=999)
            TransactionInputCoinbase.objects.bulk_create(processed_blocks.vins_cb, batch_size=999)
            TransactionInput.objects.bulk_create(processed_blocks.vins, batch_size=999)
            TransactionOutput.objects.bulk_create(processed_blocks.vouts, batch_size=999)
            UtxoBlock.objects.bulk_create([block_db])
            self.update_tip_state_done_block_process(block_height)
