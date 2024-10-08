from requests.sessions import Session

from configuration.config import config

# TODO: Add type hints


class DogeClient:
    """
    Implements Doge
    """

    @classmethod
    def default(cls):
        return cls(config.NODE_RPC_URL)

    def __init__(self, rpc_url) -> None:
        self.url = rpc_url

    def _post(self, session: Session, json=None):
        return session.post(self.url, json=json, timeout=20)

    def get_transaction(self, session: Session, txid: str):
        return self._post(
            session,
            {
                "jsonrpc": "1.0",
                "id": "rpc",
                "method": "getrawtransaction",
                "params": [txid, True],
            },
        )

    def get_block_by_hash(self, session: Session, block_hash: str):
        return self._post(
            session,
            {
                "jsonrpc": "1.0",
                "id": "rpc",
                "method": "getblock",
                "params": [block_hash, True],
            },
        )

    def get_block_hash_from_height(self, session: Session, block_height: int):
        return self._post(
            session,
            {
                "jsonrpc": "1.0",
                "id": "rpc",
                "method": "getblockhash",
                "params": [block_height],
            },
        )

    def get_block_height(
        self,
        session: Session,
    ):
        return self._post(
            session,
            {
                "jsonrpc": "1.0",
                "id": "rpc",
                "method": "getblockcount",
                "params": [],
            },
        )
