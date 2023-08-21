import os
import json
from eth_keys import keys
from eth_utils import to_checksum_address

from dotenv import load_dotenv
load_dotenv()

from web3_functions import *


WETH_ADDRESS = '0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91'
USDC_ADDRESS = '0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4'


###  import private keys ###
def derive_ethereum_address(private_key_hex):
    private_key = keys.PrivateKey(bytes.fromhex(private_key_hex))
    return to_checksum_address(private_key.public_key.to_address())


users = {}


# Let's assume keys range from rabby1 to rabby99 (you can adjust this range)

def load_accounts():
    for i in range(1, 12):
        private_key_name = f'private_key_rabby{i}'
        private_key_value = os.getenv(private_key_name)

        if private_key_value:
            address = derive_ethereum_address(private_key_value)
            eth_balance = get_eth_balance(address)
            weth_balance = get_token_balance(WETH_ADDRESS, address)
            usdc_balance = get_token_balance(USDC_ADDRESS, address)

            users[f'rabby{i}'] = {
                'private_key': private_key_value,
                'address': address,
                'eth_balance': eth_balance,
                'weth_balance': weth_balance,
                'usdc_balance': usdc_balance
        }

    return users
