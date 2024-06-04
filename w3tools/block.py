import time
from collections import Counter
from dataclasses import dataclass
from functools import cached_property
from typing import List

from cacheout import LFUCache
from loguru import logger
from web3.types import BlockIdentifier, TxData, TxReceipt

from w3tools.chain import ChainId as Chain
from w3tools.tx import TX
from w3tools.w3 import make_w3

cache = LFUCache(maxsize=10)


@dataclass
class Block:
    chain: Chain
    hash: str

    sender_counts: Counter
    receiver_counts: Counter

    def __init__(
        self,
        chain: Chain,
        hash: str,
        timestamp: int,
        txhashes: list,
        w3=None,
        txdatas: List[TxData] = None,
        receipts: List[dict] = None,
        traces: List[dict] = None,
    ) -> None:
        self.chain = chain
        self.hash = hash
        if w3 is None:
            w3 = make_w3(chain)
        self.w3 = w3

        self.txs = [
            TX(
                chain,
                txhash,
                w3=self.w3,
                txdata=txdata,
                receipt=receipt,
                trace=trace,
            )
            for txhash, txdata, receipt, trace in zip(
                txhashes, txdatas, receipts, traces
            )
        ]

        self.timestamp = timestamp

    @classmethod
    def from_w3(
        cls,
        chain: Chain,
        block_identifier: str,  # hex
        w3=None,
        need_txdatas=True,
        need_receipts=True,
        need_traces=True,
    ):

        key = f"{chain}_{block_identifier}_{need_txdatas}_{need_receipts}_{need_traces}"
        if cache.has(key):
            return cache.get(key)

        if w3 is None:
            w3 = make_w3(chain)

        if need_txdatas:
            data = w3.eth.get_block(
                block_identifier,
                full_transactions=True,
            )
            txhashes = [tx["hash"] for tx in data["transactions"]]
            txdatas = data["transactions"]
        else:
            data = w3.eth.get_block(
                block_identifier,
                full_transactions=False,
            )
            txhashes = [tx for tx in data["transactions"]]
            txdatas = len(txhashes) * [None]

        if type(block_identifier) == int:
            block_identifier = hex(block_identifier)

        receipts = len(txhashes) * [None]
        if need_receipts:
            for i in range(5):  # retry 3 times
                try:
                    receipts = w3.eth.get_block_receipts(block_identifier)
                    break
                except Exception as e:
                    logger.error(
                        f"get block receipts error: {block_identifier}, {e}, the {i+1} time"
                    )
                    time.sleep(0.5)
                    continue

        traces = len(txhashes) * [None]

        if need_traces:
            for i in range(5):  # retry 3 times
                try:
                    traces = w3.eth.trace_block(
                        block_identifier, {"tracer": "callTracer"}
                    )
                    break
                except Exception as e:
                    logger.error(
                        f"trace block error: {block_identifier}, {e}, the {i+1} time"
                    )
                    time.sleep(0.5)
                    continue

        b = cls(
            chain,
            data["hash"],
            data["timestamp"],
            txhashes,
            w3=w3,
            txdatas=txdatas,
            receipts=receipts,
            traces=traces,
        )

        cache.set(key, b)
        return b

    @property
    def sender_counts(self):
        return Counter([tx.sender for tx in self.txs])

    @property
    def receiver_counts(self):
        return Counter([tx.receiver for tx in self.txs])

    @property
    def from_to_counts(self):
        return Counter([tx.sender + tx.to for tx in self.txs])

    @cached_property
    def sandwich_txs(self):
        """TODO: not ok, some sandwich tx order is not continuous
        only backrun tx can be sandwich tx"""
        txs = set()

        for idx, tx in enumerate(self.txs):
            # check second previous tx
            if idx < 2:
                continue

            if not tx.to or not self.txs[idx - 2].to:
                continue

            if tx.sender + tx.to == self.txs[idx - 2].sender + self.txs[idx - 2].to:
                txs.add(tx.txhash)
                txs.add(self.txs[idx - 2].txhash)

        return txs


if __name__ == "__main__":
    for i in range(35578786, 35578786 + 10):
        w3 = make_w3(Chain.BSC, "chainbase")
        block = Block.from_w3(Chain.BSC, hex(i), w3=w3)
        print(block.hash, block.timestamp, len(block.txs))
        print(id(block))

        block = Block.from_w3(Chain.BSC, hex(i))
        print(id(block))

        break
