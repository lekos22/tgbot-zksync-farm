import json
from eth_keys import keys
from eth_utils import to_checksum_address
from datetime import datetime
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


# Let's assume keys range from rabby1 to rabby12 (you can adjust this range)

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



def save_users_balances():
    user_balances = {}
    overall_total_balance_usd = 0
    users = load_accounts()
    eth_price = get_eth_price()
    overall_total_balance_eth_usd = 0
    overall_total_balance_weth_usd = 0
    overall_total_balance_usdc_usd = 0
    for i in users:
        eth_bal_usd = users[i]['eth_balance'] * eth_price / 1e18
        weth_bal_usd = users[i]['weth_balance'] * eth_price / 1e18
        usdc_bal_usd = users[i]['usdc_balance'] / 1e6

        account_total_balance_usd = eth_bal_usd + weth_bal_usd + usdc_bal_usd

        user_balances[i] = {
            'total_balance_usd': account_total_balance_usd,
            'eth_bal_usd': eth_bal_usd,
            'weth_bal_usd': weth_bal_usd,
            'usdc_bal_usd': usdc_bal_usd,
            'eth_bal_wei': users[i]['eth_balance'],
            'weth_bal_wei': users[i]['weth_balance'],
            'usdc_bal_wei': users[i]['usdc_balance'],
        }
        overall_total_balance_usd += account_total_balance_usd
        overall_total_balance_eth_usd += eth_bal_usd
        overall_total_balance_weth_usd += weth_bal_usd
        overall_total_balance_usdc_usd += usdc_bal_usd

    users_usd_balances = {'overall_usd': {'usdc+eth+weth':overall_total_balance_usd,
                                      'eth': overall_total_balance_eth_usd,
                                      'weth': overall_total_balance_weth_usd,
                                      'usdc': overall_total_balance_usdc_usd}}
    users_usd_balances.update(user_balances)

    date_str = datetime.today().strftime('%Y_%m_%d')
    filename = f'users_data/{date_str}_users_usd_balances.json'

    with open(filename, 'w') as file:
        json.dump(users_usd_balances, file, indent=2)



