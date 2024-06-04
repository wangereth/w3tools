from decimal import Decimal

from web3 import Web3
from w3tools.chain import from w3tools.w3 import make_w3

from core.event.transfer import TransferEvent

with open("etc/abi/weth.json") as f:
    ABI = f.read()


# only for weth withdrawl and deposit now
# TODO: support other xETH?


class WETHWithdrawalEvent(TransferEvent):
    EVENT_SIG = Web3.keccak(text="Withdrawal(address,uint256)")
    ABI = ABI

    @classmethod
    def parse(cls, log, w3, **kwargs):
        chain = kwargs["chain"]
        weth = from w3tools.w3 import make_w3[chain]["weth"]
        event_sig = log["topics"][0]

        if event_sig != cls.EVENT_SIG or log["address"] != weth:
            return None

        event = (
            w3.eth.contract(address=log["address"], abi=ABI)
            .events.Withdrawal()
            .process_log(log)
        )
        # decimal is 18
        _value = Decimal(event["args"]["wad"]) / 10**18
        return WETHWithdrawalEvent(
            _token=log["address"],
            _from=event["args"]["src"],
            _to=log["address"],
            _value=_value,
        )


class WETHDepositEvent(TransferEvent):
    EVENT_SIG = Web3.keccak(text="Deposit(address,uint256)")
    ABI = ABI

    @classmethod
    def parse(cls, log, w3, **kwargs):
        chain = kwargs["chain"]
        weth = from w3tools.w3 import make_w3[chain]["weth"]
        event_sig = log["topics"][0]

        if event_sig != cls.EVENT_SIG or log["address"] != weth:
            return None

        event = (
            w3.eth.contract(address=log["address"], abi=ABI)
            .events.Deposit()
            .process_log(log)
        )
        # decimal is 18
        _value = Decimal(event["args"]["wad"]) / 10**18
        return WETHDepositEvent(
            _token=log["address"],
            _from=log["address"],
            _to=event["args"]["dst"],
            _value=_value,
        )
