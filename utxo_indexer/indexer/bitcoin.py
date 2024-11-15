import logging

from django.db import transaction

from client.btc_client import BtcClient
from utxo_indexer.models import (
    TransactionInput,
    TransactionInputCoinbase,
    TransactionOutput,
    UtxoBlock,
    UtxoTransaction,
)
from utxo_indexer.models.types import CoinbaseVinResponse, PrevoutResponse, VoutResponse

from .indexer_client import IndexerClient
from .types import BlockInformationPassing, BlockProcessorMemory

logger = logging.getLogger(__name__)


class BtcIndexerClient(IndexerClient):
    _client = BtcClient

    @classmethod
    def default(cls):
        return cls.new(BtcClient.default(), 600)

    # Block processing part
    def process_block(self, block_height: int):
        # NOTE: we always assume that block processing is for blocks that are for sure on main branch of the blockchain

        processed_blocks = BlockProcessorMemory()

        block_hash = self._get_block_hash_from_height(block_height, self.toplevel_worker)
        res_block = self._get_block_by_hash(block_hash, self.toplevel_worker)

        block_db = UtxoBlock.object_from_node_response(res_block)

        block_info = BlockInformationPassing(
            block_num=res_block.height,
            block_ts=res_block.mediantime,
        )
        for tx in res_block.tx:
            tx_link = UtxoTransaction.object_from_node_response(tx, block_info.block_num, block_info.block_ts)
            processed_blocks.tx.append(tx_link)
            for vin_n, vin in enumerate(tx.vin):
                if isinstance(vin, CoinbaseVinResponse):
                    cb_input = TransactionInputCoinbase.object_from_node_response(vin_n, vin, tx_link)
                    processed_blocks.vins_cb.append(cb_input)
                else:
                    assert isinstance(
                        vin.prevout, PrevoutResponse
                    ), "PrevoutResponse sholdn't be None for BitcoinClient"
                    vout = VoutResponse(n=vin.vout, value=vin.prevout.value, scriptPubKey=vin.prevout.scriptPubKey)
                    tx_input = TransactionInput.object_from_node_response(vin_n, vin, vout, tx_link)
                    processed_blocks.vins.append(tx_input)

            for vout in tx.vout:
                processed_blocks.vouts.append(TransactionOutput.object_from_node_response(vout, tx_link))

        self.post_process_block_data(processed_blocks)

        with transaction.atomic():
            UtxoTransaction.objects.bulk_create(processed_blocks.tx, batch_size=999)
            TransactionInputCoinbase.objects.bulk_create(processed_blocks.vins_cb, batch_size=999)
            TransactionInput.objects.bulk_create(processed_blocks.vins, batch_size=999)
            TransactionOutput.objects.bulk_create(processed_blocks.vouts, batch_size=999)
            UtxoBlock.objects.bulk_create([block_db])
            self.update_tip_state_done_block_process(block_height)
