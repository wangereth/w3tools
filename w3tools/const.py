from web3 import Web3

NATIVE_ETH = Web3.to_checksum_address("0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
ZERO_ADDRESS = Web3.to_checksum_address("0x0000000000000000000000000000000000000000")

BLACKHOLE_ADDRESSES = {
    ZERO_ADDRESS,
    Web3.to_checksum_address("0x000000000000000000000000000000000000dead"),
}
