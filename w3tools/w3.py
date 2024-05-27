import asyncio
import json
import logging
import time

from eth_utils.toolz import compose
from loguru import logger
from pyrate_limiter import Duration, Limiter, Rate
from web3 import Web3
from web3._utils.method_formatters import (
    apply_list_to_array_formatter,
    receipt_formatter,
)
from web3._utils.rpc_abi import RPC
from web3.method import Method, default_root_munger
from web3.middleware import geth_poa_middleware, simple_cache_middleware, validation
from websockets import connect

from w3tools.chain import ChainId
from w3tools.rpc import HTTP_PROVIDERS, RPC_PROVIDER, WS_PROVIDERS

# disable rate limiter logger
logging.getLogger("pyrate_limiter").setLevel(logging.WARNING)


def debug_middle(make_request, w3):
    # do one-time setup operations here

    def middleware(method, params):

        if method == "eth_getBlockReceipts":
            logger.debug(f"{method}, {params}")
        # perform the RPC request, getting the response
        response = make_request(method, params)
        if method == "eth_getBlockReceipts":
            # print(len(response["result"]), response["result"][0])
            logger.debug(f"{method}, {response}")
        # print(response)

        # finally return the response
        return response

    return middleware


def make_w3(
    chain: ChainId,
    provider: RPC_PROVIDER | str = "default",
    endpoint=None,
    api_key="",
    rate_limit=None,
    debug=False,
    skip_validation=False,
    cache=True,
):
    """
    :param chain:
    :param provider: if provider is custom, endpoint and api_key must be provided
    :param endpoint: provider endpoint when provider is custom
    :param api_key: provider api key when needed
    :param rate_limit: rate_limit every second. Ref: https://github.com/vutran1710/PyrateLimiter
    :param debug:
    :param skip_validation: skip validation for certain methods to reduce rpc call count
    :return:
    """
    if provider == "custom":
        if not endpoint:
            raise ValueError("endpoint must be provided when provider is custom")
    else:
        if isinstance(provider, str):
            provider = RPC_PROVIDER(provider)
        endpoint = HTTP_PROVIDERS[chain][provider].format(api_key)
    w3 = Web3(Web3.HTTPProvider(endpoint))
    # add poa middleware for bsc
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    if skip_validation:
        # whatever methods you want to not validate
        _METHODS_TO_VALIDATE = validation.METHODS_TO_VALIDATE
        validation.METHODS_TO_VALIDATE = [
            i
            for i in _METHODS_TO_VALIDATE
            if i not in [RPC.eth_call, RPC.eth_estimateGas]
        ]
    if debug:
        w3.middleware_onion.inject(debug_middle, layer=0)
    if cache:
        w3.middleware_onion.add(simple_cache_middleware)
    if rate_limit:
        rates = [Rate(rate_limit, Duration.SECOND * 1)]
        limiter = Limiter(rates, raise_when_fail=False, max_delay=Duration.SECOND * 1)

        def rate_limit_middleware(make_request, w3):
            def middleware(method, params):
                ok = limiter.try_acquire("default")
                if not ok:
                    logger.warning(f"rate limit, sleep 0.5s")
                    time.sleep(0.5)
                response = make_request(method, params)
                return response

            return middleware

        w3.middleware_onion.inject(rate_limit_middleware, layer=0)

    # add custom method
    def result_formatter(method, module):
        def formatter(res):
            return apply_list_to_array_formatter(receipt_formatter)(res)

        return compose(formatter)

    def request_formatter(params):
        def formatter(param):
            if type(param[0]) == int:
                return [hex(param[0])]
            return param

        return compose(formatter)

    _get_block_receipts = Method(
        "eth_getBlockReceipts",
        mungers=[default_root_munger],
        request_formatters=request_formatter,
        result_formatters=result_formatter,
    )
    w3.eth.attach_methods({"get_block_receipts": _get_block_receipts})

    _trace_block = Method(
        "debug_traceBlockByNumber",
        mungers=[default_root_munger],
    )
    w3.eth.attach_methods({"trace_block": _trace_block})

    return w3


def make_w3_ws(
    chain: ChainId,
    provider: RPC_PROVIDER | str = "default",
    endpoint=None,
    api_key="",
    timeout=10,
):
    if provider == "custom":
        if not endpoint:
            raise ValueError("endpoint must be provided when provider is custom")
    if isinstance(provider, str):
        provider = RPC_PROVIDER(provider)
    endpoint = WS_PROVIDERS[chain][provider].format(api_key)
    return WSClient(chain, endpoint, timeout)


class WSClient:
    def __init__(self, chain: ChainId, w3_ws_endpoint, timeout=10):
        self.chain = chain
        self.w3_ws = w3_ws_endpoint
        self.timeout = timeout

    async def subscribe_new_pending_transactions(self, callback):
        while True:
            await self.subscribe("newPendingTransactions", callback)

    async def subscribe_new_blocks(self, callback):
        while True:
            await self.subscribe("newHeads", callback)

    async def subscribe_logs(self, callback):
        while True:
            await self.subscribe("logs", callback)

    async def subscribe(self, subscribe_type, callback):
        async with connect(self.w3_ws) as ws:
            await ws.send(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "method": "eth_subscribe",
                        "params": [subscribe_type],
                        "id": 1,
                    }
                )
            )
            _ = await ws.recv()
            while True:
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=self.timeout)
                    # time.sleep(0.5)
                    callback(response)

                except Exception as e:
                    logger.error(f"ws error: {e}")
                    return
