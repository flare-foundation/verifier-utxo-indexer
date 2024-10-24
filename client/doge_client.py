import cattrs
from requests.sessions import Session

from configuration.config import config
from utxo_indexer.models.types import BlockResponse, TransactionResponse


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

    def _check_address_reqSigs_prevout(self, tx):
        """Makes sure that address, reqSigs and prevout are correct"""
        for vin in tx["vin"]:
            if "coinbase" not in vin:
                vin["prevout"] = None
        for vout in tx["vout"]:
            scriptPubKey = vout["scriptPubKey"]
            scriptPubKey.setdefault("reqSigs")
            if "addresses" in scriptPubKey and len(scriptPubKey["addresses"]) > 0:
                scriptPubKey["address"] = scriptPubKey["addresses"][0]
            else:
                scriptPubKey.setdefault("address", "")
        return tx

    def get_transaction(self, session: Session, txid: str) -> TransactionResponse:
        """Returns a transaction presented with class types."""
        tx = self._post(
            session,
            {
                "jsonrpc": "1.0",
                "id": "rpc",
                "method": "getrawtransaction",
                "params": [txid, True],
            },
        ).json(parse_float=str)["result"]

        # Handle address, reqSigs and prevout
        tx = self._check_address_reqSigs_prevout(tx)
        return cattrs.structure(tx, TransactionResponse)

    def get_block_by_hash(self, session: Session, block_hash: str) -> BlockResponse:
        """Returns a block presented with class types."""
        block = self._post(
            session,
            {
                "jsonrpc": "1.0",
                "id": "rpc",
                "method": "getblock",
                "params": [block_hash, 2],
            },
        ).json(parse_float=str)["result"]

        # Handle address, reqSigs and prevout
        for tx in block["tx"]:
            tx = self._check_address_reqSigs_prevout(tx)
        return cattrs.structure(block, BlockResponse)

    def get_block_hash_from_height(self, session: Session, block_height: int) -> str:
        hash = self._post(
            session,
            {
                "jsonrpc": "1.0",
                "id": "rpc",
                "method": "getblockhash",
                "params": [block_height],
            },
        ).json(parse_float=str)["result"]
        return hash

    def get_block_height(self, session: Session) -> int:
        height = self._post(
            session,
            {
                "jsonrpc": "1.0",
                "id": "rpc",
                "method": "getblockcount",
                "params": [],
            },
        ).json(parse_float=str)["result"]
        return height
