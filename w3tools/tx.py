import time
from functools import cached_property

from eth_typing import ChecksumAddress
from loguru import logger
from web3.types import TxData, TxReceipt

from w3tools.chain import ChainId
from w3tools.w3 import make_w3

DUMMY_TXHASH = "0x" + "0" * 64


class TX:
    def __init__(
        self,
        chain: ChainId,
        txhash: str,
        w3=None,
        txdata: TxData = None,
        receipt: TxReceipt = None,
        trace=None,
    ):
        self._chain = chain
        if isinstance(txhash, bytes):
            self._txhash = txhash.hex()
        else:
            self._txhash = txhash

        if w3 is None:
            w3 = make_w3(chain)
        self.w3 = w3

        self._txdata = txdata

        self._receipt = receipt

        self._trace = trace

    def __hash__(self):
        return int(self.txhash, 16)

    @property
    def is_pending(self):
        return self.block_number == None

    @property
    def chain(self):
        return self._chain

    @property
    def txhash(self) -> str:
        return self._txhash

    ## txdata
    @property
    def txdata(self):
        try:
            if self._txdata is None:
                self._txdata = self.w3.eth.get_transaction(self.txhash)
        except Exception as e:
            logger.error(f"get txdata failed: {e}, txhash: {self.txhash}")
        return self._txdata

    ## receipt
    @property
    def receipt(self):
        if self._receipt is None:
            if self.is_pending:
                self._receipt = self._logs_from_trace()
            else:
                self._receipt = self.w3.eth.get_transaction_receipt(self.txhash)
        return self._receipt

    ## trace
    @cached_property
    def trace(self):
        if self._trace:
            return self._trace
        for i in range(1):
            try:
                res = self.w3.provider.make_request(
                    "debug_traceTransaction",
                    [
                        self.txhash,
                        {"tracer": "callTracer", "tracerConfig": {"withLog": True}},
                    ],
                )
                assert res["result"] != None
                return res
            except Exception as e:
                logger.error(
                    f"get calls from debug_traceTransaction failed: {e}, the {i+1} time, res: {res}"
                )
                time.sleep(0.5)
        return {"result": {"calls": []}}

    ## basic properties from txdata
    @property
    def tx_type(self):
        return self.txdata["type"]

    @property
    def nonce(self):
        return self.txdata["nonce"]

    @property
    def value(self):
        return self.txdata["value"]

    @property
    def block_number(self):
        return self.txdata.get("blockNumber", None)

    @property
    def to(self):
        if self.txdata["to"] == None:
            return ""
        return self.txdata["to"]

    @property
    def sender(self) -> ChecksumAddress:
        return self.txdata["from"]

    ### gas related
    @property
    def gas_limit(self) -> int:
        return self.txdata["gas"]

    @property
    def gas_price(self) -> int:
        return self.txdata["gasPrice"]

    @property
    def max_gas_price(self) -> int:
        return self.txdata.get("maxFeePerGas", 0)

    @property
    def priority_gas_price(self) -> int:
        return self.txdata.get("maxPriorityFeePerGas", 0)

    ### input related
    @property
    def input(self) -> bytes:
        return self.txdata["input"]

    @property
    def input_hex(self) -> str:
        return self.txdata["input"].hex()

    @property
    def input_len(self) -> int:
        return len(self.input)

    @property
    def method_sig(self) -> str:
        if self.input == "0x":
            return ""
        return self.input[:4].hex()

    ## basic properties from receipt
    @property
    def tx_index(self):
        return self.receipt["transactionIndex"]

    @property
    def status(self):
        return self.receipt["status"]

    @cached_property
    def logs(self):
        if self.is_pending:
            # parse logs from trace
            return self._logs_from_trace()

        return self.receipt["logs"]

    @property
    def logs_num(self):
        return len(self.logs)

    @property
    def receiver(self) -> ChecksumAddress:
        if self.to:
            return self.to
        elif self.receipt and self.receipt["contractAddress"]:
            return self.receipt["contractAddress"]
        else:
            raise ValueError(
                "receiver not found, tx may be failed, txhash: {self.txhash}"
            )

    ### fee related
    @property
    def gas_used(self):
        return self.receipt["gasUsed"]

    @property
    def fee(self) -> int:
        return self.gas_price * self.gas_used

    ## basic properties from trace
    @cached_property
    def internal_txs(self):
        return self._internal_txs_from_trace()

    @property
    def internal_txs_num(self):
        return len(self.internal_txs)

    ## basic properties from block

    @cached_property
    def timestamp(self):
        return self.w3.eth.get_block(self.block_number)["timestamp"]

    @property
    def is_native_transfer(self) -> bool:
        return self.txdata["input"] == "0x"

    @property
    def is_transfer_gas_used(self) -> bool:
        """
        eoa to eoa = 21000
        eoa to contract = 21033
        """
        return self.gas_used == 21000 or self.gas_used == 21033

    #### contract and create calls related
    @property
    def contract_created(self) -> bool:
        """
        check if tx is contract created, including create, create2 and contract deployed
        """
        return self.has_create_call or self.contract_deployed

    @property
    def contract_deployed(self) -> bool:
        """
        check if tx is contract deployed
        """
        if self.receipt and self.receipt["contractAddress"]:
            return True
        else:
            return False

    @cached_property
    def has_create_call(self) -> bool:
        """
        check if tx has create and create2 call
        """
        return len(self.create_calls) > 0

    @cached_property
    def create_calls(self) -> list:
        """
        get create and create2 calls
        """
        calls = []
        for tx in self.internal_txs:
            if tx["type"].lower() == "create" or tx["type"] == "create2":
                calls.append(tx)
        return calls

    def debug_trace(self, tracer=None, withlog=False):
        if tracer is None:
            return self.w3.provider.make_request(
                "debug_traceTransaction", [self.txhash]
            )
        assert tracer in ["callTracer", "prestateTracer"]
        return self.w3.provider.make_request(
            "debug_traceTransaction",
            [self.txhash, {"tracer": tracer, "tracerConfig": {"withlog": withlog}}],
        )

    def simulate_call(
        self, from_address=None, to_address=None, value=None, gas=None, gas_price=None
    ):
        if from_address is None:
            from_address = self.sender
        if to_address is None:
            to_address = self.to
        if value is None:
            value = self.value
        if gas is None:
            gas = self.gas_limit
        if gas_price is None:
            gas_price = self.gas_price
        return self.w3.eth.call(
            {
                "from": from_address,
                "to": self.to,
                "value": value,
                "data": self.input,
                "gas": gas,
                "gasPrice": gas_price,
            }
        )

    def simulate_debug_trace_call(
        self,
        from_address=None,
        to_address=None,
        value=None,
        gas=None,
        gas_price=None,
        block_number="latest",
    ):
        if from_address is None:
            from_address = self.sender
        if to_address is None:
            to_address = self.to
        if value is None:
            value = self.value
        value = int(value)
        if gas is None:
            gas = self.gas_limit
        if gas_price is None:
            gas_price = self.gas_price

        if block_number == "last":
            block_number = hex(self.block_number - 1)

        txdata = {
            "from": from_address,
            "to": to_address,
            "value": value,
            "data": self.input,
            "gas": gas,
            "gasPrice": gas_price,
        }

        payload = {
            "from": from_address,
            "to": self.to,
            "value": hex(value),
            "data": self.input_hex,
            "gas": hex(gas),
            "gasPrice": hex(gas_price),
        }
        trace = self.w3.provider.make_request(
            "debug_traceCall",
            [
                payload,
                "latest",
                {"tracer": "callTracer", "tracerConfig": {"withLog": True}},
            ],
        )

        # check trace error
        if trace.get("result", {}).get("error", None) != None:
            logger.debug(
                f"trace error: {trace['result']['error']}, txhash: {self.txhash}"
            )
            return None

        tx = TX(self.chain, DUMMY_TXHASH, w3=self.w3, txdata=txdata, trace=trace)
        return tx

    @cached_property
    def max_call_depth(self):

        def parse_calls(calls, depth=0):
            if len(calls) == 0:
                return depth
            max_depth = depth
            for call in calls:
                max_depth = max(
                    max_depth, parse_calls(call.get("calls", []), depth + 1)
                )
            return max_depth

        return parse_calls(self.trace["result"].get("calls", []))

    def _internal_txs_from_trace(self):
        txs = []

        def parse_calls(calls):
            if len(calls) == 0:
                return
            for call in calls:
                call = dict(call)
                call["value"] = int(call.get("value", "0x0"), 16)
                txs.append(call)
                parse_calls(call.get("calls", []))

        # recursive get internal txs
        try:
            if self.trace["result"].get("calls", None) != None:
                parse_calls(self.trace["result"]["calls"])
        except Exception as e:
            logger.error(f"get internal txs from trace failed: {e}")
        return txs

    def _logs_from_trace(self):
        logs = []

        def parse_calls(calls):
            if len(calls) == 0:
                return
            for call in calls:
                logs.extend(call.get("logs", []))
                parse_calls(call.get("calls", []))

        try:
            if self.trace["result"].get("calls", None) != None:
                parse_calls(self.trace["result"]["calls"])
        except Exception as e:
            logger.error(f"get logs from trace failed: {e}")
        return logs
