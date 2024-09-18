from attrs import frozen


@frozen
class Config:
    SOURCE_NAME: str
    NODE_RPC_URL: str
    AUTH_USERNAME: str
    AUTH_PASSWORD: str
    INDEXER_POLL_INTERVAL: int
    INITIAL_BLOCK_HEIGHT: int
    NUMBER_OF_BLOCK_CONFIRMATIONS: int
    NUMBER_OF_WORKERS: int
    PRUNE_KEEP_DAYS: int
    PRUNE_INTERVAL_SECONDS: int
