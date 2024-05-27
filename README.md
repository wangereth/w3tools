# w3tools: Enhanced Web3 Development Toolkit for Python

w3tools is a Python library that provides a set of tools to enhance the development of Web3 applications, including:

1. Web3 RPC client for popular EVM-based blockchains supporting:
   - popular RPC providers, like Infura, Alchemy, etc.
   - multiple EVM-based blockchains, like Ethereum, Binance Smart Chain, etc.
   - Websocket and HTTP RPC
   - rate limiting and retrying
   - skip validation of RPC method parameters
   - debug mode
   - cache
   - custom RPC method
2. Get token price from Uniswap and other DEXs
3. Get Uniswap liquidity pool information
4. more...

## Installation

```bash
pip install w3tools
```

## Usage

```python
from w3tools.chain import ChainId
from w3tools.w3 import make_w3

w3 = make_w3(
    ChainId.ETH,
    "quicknode",
    api_key="your key",
)

print(w3.eth.block_number)
```

## Credits

- [Web3.py](https://github.com/ethereum/web3.py)

## Development

The project is still under development. Please feel free to contribute or report any issues and feature requests.
