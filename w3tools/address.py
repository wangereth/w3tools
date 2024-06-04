from cacheout import LRUCache
from loguru import logger
from web3 import Web3

from w3tools.w3 import make_w3

ERC20_METHODS = [
    Web3.keccak(text="name()")[0:4],
    Web3.keccak(text="symbol()")[0:4],
    Web3.keccak(text="decimals()")[0:4],
    Web3.keccak(text="totalSupply()")[0:4],
    Web3.keccak(text="balanceOf(address)")[0:4],
    Web3.keccak(text="transfer(address,uint256)")[0:4],
    Web3.keccak(text="transferFrom(address,address,uint256)")[0:4],
    Web3.keccak(text="approve(address,uint256)")[0:4],
    Web3.keccak(text="allowance(address,address)")[0:4],
]

LPV2_METHODS = [
    Web3.keccak(text="reverse0()")[0:4],
    Web3.keccak(text="reverse1()")[0:4],
    Web3.keccak(text="getReserves()")[0:4],
]

LPV3_METHODS = [
    Web3.keccak(text="slot0()")[0:4],
    Web3.keccak(text="token0()")[0:4],
    Web3.keccak(text="token1()")[0:4],
    Web3.keccak(text="tickSpacing()")[0:4],
]

cache_eoa = LRUCache(maxsize=10000)
cache_erc20 = LRUCache(maxsize=10000)
cache_lpv2 = LRUCache(maxsize=10000)
cache_lpv3 = LRUCache(maxsize=10000)


@cache_eoa.memoize()
def is_eoa(address, w3=None, chain=None):
    """check if address is EOA"""
    if w3 is None:
        w3 = make_w3(chain)

    code = w3.eth.get_code(address)
    if code == b"":
        return True
    else:
        return False


def _helper(address, chain, w3, methods):
    if w3 is None:
        w3 = make_w3(chain)
    try:
        code = w3.eth.get_code(address)
        for method in methods:
            if method not in code:
                return False
        return True
    except Exception as e:
        logger.warning(f"Failed to check {address}: {e}")
        return False


@cache_erc20.memoize()
def is_erc20(address, chain, w3=None):
    """check if address is ERC20 contract"""
    return _helper(address, chain, w3, ERC20_METHODS)


@cache_lpv2.memoize()
def is_lpv2(address, chain, w3=None):
    """check if address is LPV2 contract"""
    return _helper(address, chain, w3, LPV2_METHODS)


@cache_lpv3.memoize()
def is_lpv3(address, chain, w3=None):
    """check if address is LPV3 contract"""
    return _helper(address, chain, w3, LPV3_METHODS)


if __name__ == "__main__":
    print(is_erc20("0x0f3284bFEbc5f55B849c8CF792D39cC0f729e0BC"))
