import logging
import threading
from queue import Empty, Queue
from typing import Callable

from django.db import transaction
from requests.sessions import Session

from client import DogeClient
from utxo_indexer.models import (
    TransactionInput,
    TransactionInputCoinbase,
    TransactionOutput,
    UtxoBlock,
    UtxoTransaction,
)
from utxo_indexer.models.types import CoinbaseVinResponse, TransactionResponse, VinResponse

from .decorators import retry
from .indexer_client import IndexerClient
from .types import BlockInformationPassing, BlockProcessorMemory, PostProcessingMemoryElement

logger = logging.getLogger(__name__)


def thread_worker(session: Session, process_queue: Queue, processed_block: BlockProcessorMemory):
    while True:
        try:
            item = process_queue.get_nowait()
            item(session, processed_block)
            process_queue.task_done()
        except Empty:
            return


def process_pre_vout_transaction(
    vin: VinResponse,
    vin_n: int,
    tx_link: UtxoTransaction,
    transaction_getter: Callable[[str, Session], TransactionResponse],
):
    """Return the function that processes the transaction prevouts and link it to the spending transaction

    Args:
        vin (VinResponse): vin object from spending transaction
        vin_n (int): index of vin in spending transaction
        tx_link (UtxoTransaction): transaction object of spending transaction
        transaction_getter (Callable): function to retrieve transaction details
    """

    def _process_pre_vout_transaction(session: Session, processed_block: BlockProcessorMemory):
        txid, vout_n = vin.txid, vin.vout
        # Memo:
        vout = TransactionOutput.objects.filter(transaction_link__transaction_id=txid, n=vout_n).first()
        if vout is not None:
            prevout_res = vout.to_vout_response()
        else:
            res = transaction_getter(txid, session)
            prevout_res = res.vout[vout_n]
        input_object = TransactionInput.object_from_node_response(vin_n, vin, prevout_res, tx_link)
        processed_block.vins.append(TransactionInput.object_from_node_response(vin_n, vin, prevout_res, tx_link))
        return input_object

    return _process_pre_vout_transaction


class DogeIndexerClient(IndexerClient):
    _client: DogeClient

    @classmethod
    def default(cls):
        return cls.new(DogeClient.default(), 60)

    @retry(5)
    def _get_transaction(self, txid: str, worker: Session) -> TransactionResponse:
        return self._client.get_transaction(worker, txid)

    # Block processing part
    def process_block(self, block_height: int):
        # NOTICE: we always assume that block processing is for blocks that are for sure on main branch of the blockchain

        processed_block = BlockProcessorMemory()
        process_queue: Queue[Callable[[Session, BlockProcessorMemory], TransactionInput]] = Queue()

        assert self.toplevel_worker is not None, "Toplevel worker is not set"
        block_hash = self._get_block_hash_from_height(block_height, self.toplevel_worker)
        res_block = self._get_block_by_hash(block_hash, self.toplevel_worker)

        # Update the block info in DB, indicating it has processed transactions once we proceeded them
        # do it within transaction atomic update
        block_db = UtxoBlock.object_from_node_response(res_block)

        block_info = BlockInformationPassing(
            block_num=res_block.height,
            block_ts=res_block.mediantime,
        )

        # Put all of the transaction in block on the processing queue
        for tx in res_block.tx:
            tx_link = UtxoTransaction.object_from_node_response(tx, block_info.block_num, block_info.block_ts)
            processed_block.tx.append(tx_link)
            for vin_n, vin in enumerate(tx.vin):
                if isinstance(vin, CoinbaseVinResponse):
                    processed_block.vins_cb.append(
                        TransactionInputCoinbase.object_from_node_response(vin_n, vin, tx_link)
                    )
                else:
                    # CONSIDER: consider adding memeo here to not fill the queue
                    process_queue.put(process_pre_vout_transaction(vin, vin_n, tx_link, self._get_transaction))
            for vout in tx.vout:
                processed_block.vouts.append(TransactionOutput.object_from_node_response(vout, tx_link))

        # Multithreading part of the processing
        # Launch worker threads
        workers: list[threading.Thread] = []
        for worker_index in range(len(self.workers)):
            t = threading.Thread(
                target=thread_worker, args=(self.workers[worker_index], process_queue, processed_block)
            )
            workers.append(t)
            t.start()

        # Wait for all tasks to be processed and for workers to finnish.
        process_queue.join()
        [t.join() for t in workers]

        if not process_queue.empty():
            raise Exception("Queue should be empty after processing")

        # Adding source_addresses_root to UtxoTransaction
        postprocess_obj: dict[str, PostProcessingMemoryElement] = {}
        for tx in processed_block.tx:
            postprocess_obj[tx.transaction_id] = PostProcessingMemoryElement(obj=tx, cbi=[], inp=[])

        for cbi in processed_block.vins_cb:
            txid = cbi.transaction_link.transaction_id
            if txid not in postprocess_obj:
                raise Exception("Post processing fail in coinbase inputs loop")
            postprocess_obj[txid].cbi.append(cbi)

        for tinp in processed_block.vins:
            txid = tinp.transaction_link.transaction_id
            if txid not in postprocess_obj:
                raise Exception("Post processing fail in regular inputs loop")
            postprocess_obj[txid].inp.append(tinp)

        for processed_transaction in postprocess_obj.values():
            self.update_source_addresses_root_from_tx_data(processed_transaction)

        with transaction.atomic():
            UtxoTransaction.objects.bulk_create(processed_block.tx, batch_size=999)
            TransactionInputCoinbase.objects.bulk_create(processed_block.vins_cb, batch_size=999)
            TransactionInput.objects.bulk_create(processed_block.vins, batch_size=999)
            TransactionOutput.objects.bulk_create(processed_block.vouts, batch_size=999)
            UtxoBlock.objects.bulk_create([block_db])
            self.update_tip_state_done_block_process(block_height)
