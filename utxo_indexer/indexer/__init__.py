from configuration.config import config
from utxo_indexer.indexer.bitcoin import BtcIndexerClient
from utxo_indexer.indexer.doge import DogeIndexerClient


def get_indexer_client():
    source = config.SOURCE_NAME
    match source:
        case "doge":
            return DogeIndexerClient.default()
        case "btc":
            return BtcIndexerClient.default()
        case _:
            raise ValueError(f"Invalid source name. Available sources are {config}")
