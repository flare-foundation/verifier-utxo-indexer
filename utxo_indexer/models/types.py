from typing import List

from attrs import frozen


@frozen
class ScriptSigResponse:
    asm: str
    hex: str


@frozen
class ScriptPubKeyResponse:
    reqSigs: int | None
    address: str
    type: str
    asm: str
    hex: str


@frozen
class PrevoutResponse:
    value: str
    scriptPubKey: ScriptPubKeyResponse


@frozen
class VoutResponse:
    n: int
    value: str
    scriptPubKey: ScriptPubKeyResponse


@frozen
class CoinbaseVinResponse:
    coinbase: str
    sequence: int


# Definition of VinResponse class
@frozen
class VinResponse:
    txid: str
    sequence: int
    scriptSig: ScriptSigResponse
    vout: int
    prevout: PrevoutResponse | None


# Definition of TransactionResponse class
@frozen
class TransactionResponse:
    txid: str
    vout: List[VoutResponse]
    vin: List[VinResponse | CoinbaseVinResponse]


# Definition of BlockResponse class
@frozen
class BlockResponse:
    hash: str
    height: int
    mediantime: int
    previousblockhash: str
    tx: List[TransactionResponse]
