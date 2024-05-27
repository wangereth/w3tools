from enum import Enum

from w3tools.chain import ChainId


class RPC_PROVIDER(Enum):
    LOCAL = "local"
    INFURA = "infura"
    ALCHEMY = "alchemy"
    CHAINBASE = "chainbase"
    DEFAULT = "default"
    QUICKNODE = "quicknode"

    def __missing__(cls, key):
        if isinstance(key, str):
            return RPC_PROVIDER[key.upper()]


HTTP_PROVIDERS = {
    ChainId.ETH: {
        RPC_PROVIDER.LOCAL: "http://localhost:8545",
        RPC_PROVIDER.DEFAULT: "https://eth.llamarpc.com",
        RPC_PROVIDER.INFURA: "https://mainnet.infura.io/v3/{}",
        RPC_PROVIDER.ALCHEMY: "https://eth-mainnet.alchemyapi.io/v2/{}",
        RPC_PROVIDER.CHAINBASE: "https://ethereum-mainnet.s.chainbase.online/v1/{}",
        RPC_PROVIDER.QUICKNODE: "https://fittest-summer-pool.quiknode.pro/{}",
    },
    ChainId.BSC: {
        RPC_PROVIDER.DEFAULT: "https://bsc.llamarpc.com",
        RPC_PROVIDER.CHAINBASE: "https://bsc-mainnet.s.chainbase.online/v1/{}",
    },
    ChainId.ARB: {
        RPC_PROVIDER.DEFAULT: "https://arbitrum.llamarpc.com",
        RPC_PROVIDER.CHAINBASE: "https://arbitrum-mainnet.s.chainbase.online/v1/{}",
    },
    ChainId.ETH_SEPOLIA: {
        RPC_PROVIDER.DEFAULT: "https://rpc.sepolia.org",
        RPC_PROVIDER.INFURA: "https://sepolia.infura.io/v3/{}",
        RPC_PROVIDER.ALCHEMY: "https://eth-sepolia.g.alchemy.com/v2/{}",
    },
}

WS_PROVIDERS = {
    ChainId.ETH: {
        RPC_PROVIDER.LOCAL: "ws://localhost:8546",
        RPC_PROVIDER.DEFAULT: "wss://eth.llamarpc.com",
        RPC_PROVIDER.INFURA: "wss://mainnet.infura.io/ws/v3/{}",
        RPC_PROVIDER.ALCHEMY: "wss://eth-mainnet.ws.alchemyapi.io/v2/{}",
        RPC_PROVIDER.CHAINBASE: "wss://ethereum-mainnet.s.chainbase.online/ws/v1/{}",
        RPC_PROVIDER.QUICKNODE: "wss://fittest-summer-pool.quiknode.pro/{}",
    },
    ChainId.BSC: {
        RPC_PROVIDER.DEFAULT: "wss://bsc.llamarpc.com",
        RPC_PROVIDER.CHAINBASE: "wss://bsc-mainnet.s.chainbase.online/ws/v1/{}",
    },
    ChainId.ARB: {
        RPC_PROVIDER.DEFAULT: "wss://arbitrum.llamarpc.com",
        RPC_PROVIDER.CHAINBASE: "wss://arbitrum-mainnet.s.chainbase.online/ws/v1/{}",
    },
    ChainId.ETH_SEPOLIA: {
        RPC_PROVIDER.DEFAULT: "wss://rpc.sepolia.org",
        RPC_PROVIDER.INFURA: "wss://sepolia.infura.io/ws/v3/{}",
        RPC_PROVIDER.ALCHEMY: "wss://eth-sepolia.g.alchemy.com/v2/{}",
    },
}
