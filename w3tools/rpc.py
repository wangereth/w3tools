from enum import Enum

from w3tools.chain import ChainId


class RPC_PROVIDER(Enum):
    INFURA = "infura"
    ALCHEMY = "alchemy"
    CHAINBASE = "chainbase"
    DEFAULT = "default"

    def __missing__(cls, key):
        if isinstance(key, str):
            return RPC_PROVIDER[key.upper()]


HTTP_PROVIDERS = {
    ChainId.ETH: {
        RPC_PROVIDER.DEFAULT: "https://eth.llamarpc.com",
        RPC_PROVIDER.INFURA: "https://mainnet.infura.io/v3/{}",
        RPC_PROVIDER.ALCHEMY: "https://eth-mainnet.alchemyapi.io/v2/{}",
        RPC_PROVIDER.CHAINBASE: "https://ethereum-mainnet.s.chainbase.online/v1/{}",
    },
    ChainId.BSC: {
        RPC_PROVIDER.DEFAULT: "https://bsc.llamarpc.com",
        RPC_PROVIDER.CHAINBASE: "https://bsc-mainnet.s.chainbase.online/v1/{}",
    },
}