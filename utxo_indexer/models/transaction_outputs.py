from django.db import models

from utxo_indexer.models.model_utils import HexString32ByteField
from utxo_indexer.models.transaction import UtxoTransaction
from utxo_indexer.models.types import CoinbaseVinResponse, ScriptPubKeyResponse, VinResponse, VoutResponse


class AbstractTransactionOutput(models.Model):
    n = models.PositiveIntegerField()
    # currently total circulating supply fits in 20 digits
    value = models.CharField()

    script_key_asm = models.CharField()
    script_key_hex = models.CharField()
    # TODO: make this an integer
    script_key_req_sigs = models.CharField(blank=True, null=True)
    script_key_type = models.CharField()
    script_key_address = models.CharField(max_length=128)

    class Meta:
        abstract = True
        indexes = (models.Index(fields=["script_key_address"]),)

    def __str__(self) -> str:
        return super().__str__()


class TransactionOutput(AbstractTransactionOutput):
    transaction_link = models.ForeignKey("UtxoTransaction", on_delete=models.CASCADE)

    class Meta:
        unique_together = (("transaction_link", "n"),)

    def __str__(self) -> str:
        return super().__str__()

    @classmethod
    def object_from_node_response(cls, response: VoutResponse, transaction_link: UtxoTransaction):
        script_pub_key = response.scriptPubKey
        return cls(
            transaction_link=transaction_link,
            n=response.n,
            value=response.value,
            script_key_asm=script_pub_key.asm,
            script_key_hex=script_pub_key.hex,
            script_key_req_sigs=script_pub_key.reqSigs,
            script_key_type=script_pub_key.type,
            script_key_address=script_pub_key.address,
        )

    def to_vout_response(self) -> VoutResponse:
        return VoutResponse(
            n=self.n,
            value=self.value,
            scriptPubKey=ScriptPubKeyResponse(
                reqSigs=int(self.script_key_req_sigs) if self.script_key_req_sigs else None,
                address=self.script_key_address,
                type=self.script_key_type,
                asm=self.script_key_asm,
                hex=self.script_key_hex,
            ),
        )


class TransactionInputCoinbase(models.Model):
    transaction_link = models.ForeignKey("UtxoTransaction", on_delete=models.CASCADE)

    # Position in vin array of transaction (always 0 for coinbase)
    vin_n = models.PositiveIntegerField()

    vin_coinbase = models.CharField()
    vin_sequence = models.PositiveBigIntegerField()

    def __str__(self) -> str:
        return f"Coinbase vin for tx: {self.transaction_link.transaction_id}"

    @classmethod
    def object_from_node_response(
        cls, vin_n: int, vin_response: CoinbaseVinResponse, transaction_link: UtxoTransaction
    ):
        assert vin_n == 0, "Coinbase transaction should always be first in vin array"
        return cls(
            transaction_link=transaction_link,
            vin_n=vin_n,
            vin_coinbase=vin_response.coinbase,
            vin_sequence=vin_response.sequence,
        )


class TransactionInput(AbstractTransactionOutput):
    transaction_link = models.ForeignKey("UtxoTransaction", on_delete=models.CASCADE)

    # Position in vin array of transaction
    vin_n = models.PositiveIntegerField()

    vin_previous_txid = HexString32ByteField()
    vin_vout_index = models.PositiveIntegerField()

    # TODO: remove if not used
    vin_sequence = models.PositiveBigIntegerField()
    vin_script_sig_asm = models.CharField()
    vin_script_sig_hex = models.CharField()

    # TODO: Add witness data to db if needed

    class Meta:
        unique_together = (("transaction_link", "vin_n"),)
        # TODO: n and vin_vout_index should be the same

    def __str__(self) -> str:
        return f"Input {self.vin_n} for tx: {self.transaction_link.transaction_id}"

    @classmethod
    def object_from_node_response(
        cls,
        vin_n: int,
        vin_response: VinResponse,
        vout_response: VoutResponse,
        transaction_link: UtxoTransaction,
    ):
        vout_script_pub_key = vout_response.scriptPubKey
        return cls(
            transaction_link=transaction_link,
            vin_n=vin_n,
            # (pre)vout part
            n=vout_response.n,
            value=vout_response.value,
            script_key_asm=vout_script_pub_key.asm,
            script_key_hex=vout_script_pub_key.hex,
            script_key_req_sigs=vout_script_pub_key.reqSigs,
            script_key_type=vout_script_pub_key.type,
            script_key_address=vout_script_pub_key.address,
            # vin part
            vin_previous_txid=vin_response.txid,
            vin_vout_index=vin_response.vout,
            vin_sequence=vin_response.sequence,
            vin_script_sig_asm=vin_response.scriptSig.asm,
            vin_script_sig_hex=vin_response.scriptSig.hex,
        )
