from dataclasses import dataclass
from enum import IntEnum

from eth_typing import ChecksumAddress
from web3 import Web3


class ChainId(IntEnum):
    ETH = 1
    UBIQ = 8
    OP = 10
    FLARE = 14
    SONGBIRD = 19
    ELASTOS = 20
    KARDIACHAIN = 24
    CRONOS = 25
    RSK = 30
    TELOS = 40
    XDC = 50
    CSC = 52
    ZYX = 55
    BSC = 56
    SYSCOIN = 57
    GOCHAIN = 60
    ETH_CLASSIC = 61
    OKEXCHAIN = 66
    HOO = 70
    METER = 82
    NOVA_NETWORK = 87
    VICTION = 88
    XDAI = 100
    VELAS = 106
    THUNDERCORE = 108
    FUSE = 122
    HECO = 128
    POLYGON = 137
    SHIMMER_EVM = 148
    MANTA = 169
    XDAIARB = 200
    OP_BNB = 204
    ENERGYWEB = 246
    OASYS = 248
    FANTOM = 250
    HPB = 269
    BOBA = 288
    OMAX = 311
    FILECOIN = 314
    KUCOIN = 321
    ERA = 324
    SHIDEN = 336
    THETA = 361
    PULSE = 369
    SX = 416
    AREON = 463
    CANDLE = 534
    ROLLUX = 570
    ASTAR = 592
    CALLISTO = 820
    WANCHAIN = 888
    CONFLUX = 1030
    METIS = 1088
    POLYGON_ZKEVM = 1101
    CORE = 1116
    ULTRON = 1231
    STEP = 1234
    MOONBEAM = 1284
    MOONRIVER = 1285
    LIVING_ASSETS_MAINNET = 1440
    TENET = 1559
    ONUS = 1975
    HUBBLENET = 1992
    DOGECHAIN = 2000
    KAVA = 2222
    SOMA = 2332
    BEAM = 4337
    IOTEX = 4689
    MANTLE = 5000
    XLC = 5050
    NAHMII = 5551
    TOMBCHAIN = 6969
    BITROCK = 7171
    CANTO = 7700
    KLAYTN = 8217
    BASE = 8453
    CHILIZ = 88888
    JBC = 8899
    EVMOS = 9001
    CARBON = 9790
    SMARTBCH = 10000
    LOOP = 15551
    EOS_EVM = 17777
    BLAST = 23888
    BITGERT = 32520
    FUSION = 32659
    ZILLIQA = 32769
    ARB = 42161
    ARB_NOVA = 42170
    CELO = 42220
    OASIS = 42262
    AVALANCHE = 43114
    REI = 47805
    REICHAIN = 55555
    LINEA = 59144
    GODWOKEN = 71402
    POLIS = 333999
    KEKCHAIN = 420420
    VISION = 888888
    NEON = 245022934
    AURORA = 1313161554
    HARMONY = 1666600000
    PALM = 11297108109
    CURIO = 836542336838601

    # testnets
    ETH_SEPOLIA = 11155111

    @classmethod
    def _missing_(cls, key):
        if isinstance(key, str):
            return ChainId[key.upper()]


@dataclass
class Chain:
    chain_id: ChainId
    name: str
    symbol: str
    native_token_name: str
    native_token_symbol: str
    weth: ChecksumAddress


CHAIN_INFO = {
    ChainId.ETH: Chain(
        chain_id=ChainId.ETH,
        name="Ethereum",
        symbol="ETH",
        native_token_name="Ether",
        native_token_symbol="ETH",
        weth=Web3.to_checksum_address("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"),
    ),
    ChainId.BSC: Chain(
        chain_id=ChainId.BSC,
        name="Binance Smart Chain",
        symbol="BSC",
        native_token_name="BNB",
        native_token_symbol="BNB",
        weth=Web3.to_checksum_address("0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c"),
    ),
}
