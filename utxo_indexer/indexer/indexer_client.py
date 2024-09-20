import logging
import time
from typing import Any

from requests.models import HTTPBasicAuth
from requests.sessions import Session

from configuration.config import config
from utxo_indexer.models import (
    TipSyncState,
    TipSyncStateChoices,
    UtxoBlock,
)

from .decorators import retry

logger = logging.getLogger(__name__)


def new_session():
    session = Session()
    session.auth = HTTPBasicAuth(config.AUTH_USERNAME, config.AUTH_PASSWORD)
    return session


class IndexerClient:
    """
    Base class for indexer clients
    - Client: client for interacting with the node (DogeClient or BtcClient)
    - Expected production: expected time for block production of the chain (60 for DOGE, 600 for BTC)
    """

    def __init__(self, client, expected_production) -> None:
        self._client = client

        self.workers = [new_session() for _ in range(config.NUMBER_OF_WORKERS)]
        self.toplevel_worker = self.workers[0]

        assert expected_production > 0, "Expected block production time should be positive"
        self.expected_block_production_time = expected_production

        # Determining starting block height for indexing
        self.latest_indexed_block_height = self.extract_initial_block_height()
        self.latest_tip_block_height = 0

    def extract_initial_block_height(self) -> int:
        """
        Extracts the initial block height from the config
        """

        logger.info("Extracting initial block height")

        latest_block = UtxoBlock.objects.order_by("block_number").last()
        if latest_block is not None:
            if latest_block.block_number < config.INITIAL_BLOCK_HEIGHT:
                raise Exception(
                    f"Starting processing from block {config.INITIAL_BLOCK_HEIGHT}"
                    f" with latest block in db: {latest_block.block_number} would"
                    " create holes in the transaction history"
                )
            return latest_block.block_number

        logger.info("No blocks in the database, starting from the initial block height")

        height = self._get_current_block_height(self.toplevel_worker)

        if config.PRUNE_KEEP_DAYS <= 0:
            logger.info(
                f"Pruning is disabled, starting from the initial block height set in config {config.INITIAL_BLOCK_HEIGHT}"
            )
            return config.INITIAL_BLOCK_HEIGHT

        safety_factor = 1.5
        blocks_since_pruning = int(
            config.PRUNE_KEEP_DAYS * 24 * 60 * 60 * safety_factor / self.expected_block_production_time
        )

        if config.INITIAL_BLOCK_HEIGHT < height - blocks_since_pruning:
            logger.info(
                f"Initial block is much older than pruning setting, starting from block {height - blocks_since_pruning} \n"
                f"Initial block height set: {config.INITIAL_BLOCK_HEIGHT}, pruning setting: {config.PRUNE_KEEP_DAYS} days with factor: {safety_factor}"
            )
            return height - blocks_since_pruning

        logger.info(f"Starting from the initial block height set in config {config.INITIAL_BLOCK_HEIGHT}")
        return config.INITIAL_BLOCK_HEIGHT

    def run(self) -> None:
        """
        Runs the indexing process in a endless loop
        """
        logger.info("Starting the indexer")
        while True:
            height = self._get_current_block_height(self.toplevel_worker)

            if self.latest_tip_block_height < height:
                # We need to update the tip state and process new blocks
                self.update_tip_state_indexing(height)
                self.latest_tip_block_height = height
                for i in range(self.latest_indexed_block_height + 1, height - config.NUMBER_OF_BLOCK_CONFIRMATIONS + 1):
                    start = time.time()
                    self.process_block(i)
                    logger.info("Processed block: %s in: %s", i, time.time() - start)
                    self.latest_indexed_block_height = i

                # TODO save all blocks up to tip height
            else:
                logger.info(
                    f"No new blocks to process, indexed/latest: {self.latest_indexed_block_height}/{height} sleeping for {config.INDEXER_POLL_INTERVAL} seconds"
                )
                self.update_tip_state_idle()
                time.sleep(config.INDEXER_POLL_INTERVAL)

    # Base methods for interacting with node directly

    # TODO:(matej) retry only on possible exceptions
    @retry(5)
    def _get_current_block_height(self, worker: Session) -> int:
        return self._client.get_block_height(worker).json(parse_float=str)["result"]

    # TODO:(matej) retry only on possible exceptions
    @retry(5)
    def _get_block_hash_from_height(self, block_height: int, worker: Session) -> str:
        return self._client.get_block_hash_from_height(worker, block_height).json(parse_float=str)["result"]

    # TODO:(matej) retry only on possible exceptions
    # TODO: type hint (IBlockResponse)
    @retry(5)
    def _get_block_by_hash(self, block_hash: str, worker: Session) -> Any:
        return self._client.get_block_by_hash(worker, block_hash).json(parse_float=str)["result"]

    # TODO:(matej) retry only on possible exceptions
    # TODO: type hint (ITransactionResponse)
    @retry(5)
    def _get_transaction(self, txid: str, worker: Session) -> Any:
        return self._client.get_transaction(worker, txid).json(parse_float=str)["result"]

    # Tip state management
    def update_tip_state_indexing(self, block_tip_height: int):
        """
        Update the tip state when indexing is in progress

        Args:
            block_tip_height (int): latest seen block height
        """
        tip_state = TipSyncState.instance()
        assert tip_state.latest_tip_height <= block_tip_height, "New block height should be higher than the current one"
        if tip_state.latest_tip_height < block_tip_height:
            tip_state.latest_tip_height = block_tip_height
        # Always update the state with latest timestamp
        tip_state.sync_state = TipSyncStateChoices.syncing
        tip_state.timestamp = int(time.time())
        tip_state.save()

    def update_tip_state_idle(self):
        """
        Update the tip state when we see no new blocks to process
        """
        tip_state = TipSyncState.instance()
        tip_state.sync_state = TipSyncStateChoices.up_to_date
        tip_state.timestamp = int(time.time())
        tip_state.save()

    def update_tip_state_done_block_process(self, indexed_block_height: int):
        """
        Update the tip state when we processed the block and saved it to db

        Args:
            indexed_block_height (int): _description_
        """
        tip_state = TipSyncState.instance()
        assert tip_state.latest_indexed_height < indexed_block_height, "Process block was already indexed"
        if tip_state.latest_indexed_height < indexed_block_height:
            tip_state.latest_indexed_height = indexed_block_height
        tip_state.sync_state = TipSyncStateChoices.syncing
        tip_state.timestamp = int(time.time())
        tip_state.save()

    def process_block(self, block_height: int):
        """
        Process the block with given height

        Args:
            block_height (int): height of the block to process
        """
        raise NotImplementedError("Implement the block processing method")
