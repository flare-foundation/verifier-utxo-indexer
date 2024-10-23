import cattrs
from requests.sessions import Session

from configuration.config import config
from utxo_indexer.models.types import BlockResponse


class BtcClient:
    """
    Implements BTC
    """

    @classmethod
    def default(cls):
        return cls(config.NODE_RPC_URL)

    def __init__(self, rpc_url) -> None:
        self.url = rpc_url

    def _post(self, session: Session, json=None):
        return session.post(self.url, json=json, timeout=20)

    def _check_address_reqSigs(self, tx):
        """Makes sure that address, reqSigs are correct"""
        for vin in tx["vin"]:
            if "prevout" in vin:
                scriptPubKey = vin["prevout"]["scriptPubKey"]
                scriptPubKey.setdefault("reqSigs")
                if "addresses" in scriptPubKey and len(scriptPubKey["addresses"]) > 0:
                    scriptPubKey["address"] = scriptPubKey["addresses"][0]
                else:
                    scriptPubKey.setdefault("address", "")
        for vout in tx["vout"]:
            scriptPubKey = vout["scriptPubKey"]
            scriptPubKey.setdefault("reqSigs")
            if "addresses" in scriptPubKey and len(scriptPubKey["addresses"]) > 0:
                scriptPubKey["address"] = scriptPubKey["addresses"][0]
            else:
                scriptPubKey.setdefault("address", "")
        return tx

    def get_block_by_hash(self, session: Session, block_hash: str) -> BlockResponse:
        """Returns a block presented with class types."""
        block = self._post(
            session,
            {
                "jsonrpc": "1.0",
                "id": "rpc",
                "method": "getblock",
                "params": [block_hash, 3],
            },
        ).json(parse_float=str)["result"]

        # Handle address and reqSigs
        for tx in block["tx"]:
            tx = self._check_address_reqSigs(tx)
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
