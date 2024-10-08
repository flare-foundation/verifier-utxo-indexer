import os

from configuration.types import Config

AVAILABLE_SOURCES = ["doge", "btc"]


def get_config() -> Config:
    # required env values
    source_name = os.environ["SOURCE_NAME"]
    node_rpc_url = os.environ["NODE_RPC_URL"]
    auth_username = os.environ["AUTH_USERNAME"]
    auth_password = os.environ["AUTH_PASSWORD"]

    # not required
    indexer_poll_interval = int(os.environ.get("INDEXER_POLL_INTERVAL", "10"))
    number_of_block_confirmations = int(os.environ.get("NUMBER_OF_BLOCK_CONFIRMATIONS", "60"))
    initial_block_height = int(os.environ.get("INITIAL_BLOCK_HEIGHT", "1"))
    number_of_workers = int(os.environ.get("NUMBER_OF_WORKERS", "10"))
    prune_keep_days = int(os.environ.get("PRUNE_KEEP_DAYS", "0"))
    prune_interval_seconds = int(os.environ.get("PRUNE_INTERVAL_SECONDS", "60"))

    # Health checks
    if source_name.lower() not in AVAILABLE_SOURCES:
        raise ValueError(f"Invalid source name. Available sources are {AVAILABLE_SOURCES}")

    return Config(
        SOURCE_NAME=source_name,
        NODE_RPC_URL=node_rpc_url,
        AUTH_USERNAME=auth_username,
        AUTH_PASSWORD=auth_password,
        INDEXER_POLL_INTERVAL=indexer_poll_interval,
        NUMBER_OF_BLOCK_CONFIRMATIONS=number_of_block_confirmations,
        INITIAL_BLOCK_HEIGHT=initial_block_height,
        NUMBER_OF_WORKERS=number_of_workers,
        PRUNE_KEEP_DAYS=prune_keep_days,
        PRUNE_INTERVAL_SECONDS=prune_interval_seconds,
    )


config = get_config()


def get_testing_config(source_prefix: str, source: str) -> Config:
    if source.lower() not in AVAILABLE_SOURCES:
        raise ValueError(f"Invalid source name. Available sources are {AVAILABLE_SOURCES}")

    node_rpc_url = os.getenv(f"{source_prefix}_NODE_RPC_URL")
    auth_username = os.getenv(f"{source_prefix}_AUTH_USERNAME")
    auth_password = os.getenv(f"{source_prefix}_AUTH_PASSWORD")
    if node_rpc_url is None or auth_username is None or auth_password is None:
        if node_rpc_url is None:
            raise ValueError(f"Missing configuration for testing {source_prefix} node rpc url")
        if auth_username is None:
            raise ValueError(f"Missing configuration for testing {source_prefix} auth username")
        if auth_password is None:
            raise ValueError(f"Missing configuration for testing {source_prefix} auth password")
        # raise ValueError(f"Missing configuration for testing {source_prefix} config")

    return Config(
        SOURCE_NAME=source,
        NODE_RPC_URL=node_rpc_url,
        AUTH_USERNAME=auth_username,
        AUTH_PASSWORD=auth_password,
        INDEXER_POLL_INTERVAL=10,
        NUMBER_OF_BLOCK_CONFIRMATIONS=60,
        INITIAL_BLOCK_HEIGHT=1,
        NUMBER_OF_WORKERS=10,
        PRUNE_KEEP_DAYS=0,
        PRUNE_INTERVAL_SECONDS=60,
    )
