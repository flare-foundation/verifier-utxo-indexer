from attrs import define, field

from utxo_indexer.models import (
    TransactionInput,
    TransactionInputCoinbase,
    TransactionOutput,
    UtxoTransaction,
)


@define
class BlockProcessorMemory:
    tx: list[UtxoTransaction] = field(factory=list)
    vins: list[TransactionInput] = field(factory=list)
    vins_cb: list[TransactionInputCoinbase] = field(factory=list)
    vouts: list[TransactionOutput] = field(factory=list)
    # exceptions raised by worker threads; checked by process_block after the queue is drained
    errors: list[Exception] = field(factory=list)


@define
class PostProcessingMemoryElement:
    obj: UtxoTransaction
    inp: list[TransactionInput] = field(factory=list)
    cbi: list[TransactionInputCoinbase] = field(factory=list)


@define
class BlockInformationPassing:
    block_num: int
    block_ts: int
