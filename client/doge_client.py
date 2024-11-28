import cattrs
from requests.sessions import Session

from configuration.config import config
from utxo_indexer.models.types import (
    BlockResponse,
    CoinbaseVinResponse,
    ScriptPubKeyResponse,
    ScriptSigResponse,
    TransactionResponse,
    VinResponse,
    VoutResponse,
)


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

        vout_list = []
        for _vout in tx["vout"]:
            _spk = _vout["scriptPubKey"]
            script_pub_key = ScriptPubKeyResponse(
                reqSigs=_spk["reqSigs"],
                address=_spk["address"],
                type=_spk["type"],
                asm=_spk["asm"],
                hex=_spk["hex"],
            )
            vout = VoutResponse(
                n=_vout["n"],
                value=_vout["value"],
                scriptPubKey=script_pub_key,
            )
            vout_list.append(vout)

        vin_list = []
        for _vin in tx["vin"]:
            if "coinbase" in _vin:
                coinb = CoinbaseVinResponse(
                    coinbase=_vin["coinbase"],
                    sequence=_vin["sequence"],
                )
                vin_list.append(coinb)

            _ss = _vin["scriptSig"]
            script_sig = ScriptSigResponse(
                asm=_ss["asm"],
                hex=_ss["hex"],
            )
            vin = VinResponse(
                txid=_vin["txid"],
                sequence=_vin["sequence"],
                vout=_vin["vout"],
                prevout=_vin["prevout"],
                scriptSig=script_sig,
            )
            vout_list.append(vin)

        return TransactionResponse(txid=tx["txid"], vout=vout_list, vin=vin_list)

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
