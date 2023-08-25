import os
from web3 import Web3
from dotenv import load_dotenv
import requests
load_dotenv()






w3 = Web3(Web3.HTTPProvider('https://mainnet.era.zksync.io'))

odos_router_address = Web3.toChecksumAddress('0x4bBa932E9792A2b917D47830C93a9BC79320E4f7')


def get_allowance(token_address, user, spender_address):
    # Standard ERC20 Allowance function signature
    function_signature = w3.eth.contract(abi=[{
        'constant': True,
        'inputs': [
            {'name': '_owner', 'type': 'address'},
            {'name': '_spender', 'type': 'address'}
        ],
        'name': 'allowance',
        'outputs': [{'name': 'remaining', 'type': 'uint256'}],
        'type': 'function'
    }])

    contract = function_signature(Web3.toChecksumAddress(token_address))
    return contract.functions.allowance(Web3.toChecksumAddress(user['address']),
                                        Web3.toChecksumAddress(spender_address)).call()









def approve_token(token_address, spender_address, amount, user):
    # Standard ERC20 Approve function signature
    function_signature = w3.eth.contract(abi=[{
        'constant': False,
        'inputs': [
            {'name': '_spender', 'type': 'address'},
            {'name': '_value', 'type': 'uint256'}
        ],
        'name': 'approve',
        'outputs': [{'name': 'success', 'type': 'bool'}],
        'type': 'function'
    }])

    contract = function_signature(token_address)

    # Build the transaction
    tx = contract.functions.approve(Web3.toChecksumAddress(spender_address), int(amount)).buildTransaction({
        'chainId': 324,  # This is for mainnet. Adjust accordingly for other networks.
        'gas': 1000000,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.getTransactionCount(Web3.toChecksumAddress(user['address'])),
    })

    # Sign the transaction
    signed_tx = w3.eth.account.signTransaction(tx, user['private_key'])

    # Send the transaction
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    return tx_hash



def get_eth_balance(wallet):
    balance_wei = w3.eth.getBalance(Web3.toChecksumAddress(wallet))
    return balance_wei



def get_token_balance(token_address, wallet):
    # Standard ERC20 balanceOf function signature
    function_signature = w3.eth.contract(abi=[{
        'constant': True,
        'inputs': [
            {'name': '_owner', 'type': 'address'}
        ],
        'name': 'balanceOf',
        'outputs': [{'name': 'balance', 'type': 'uint256'}],
        'type': 'function'
    }])

    decimals = get_token_decimals(token_address)

    contract = function_signature(Web3.toChecksumAddress(token_address))
    balance = contract.functions.balanceOf(Web3.toChecksumAddress(wallet)).call()
    return balance



def get_token_decimals(token_address):

    # Standard ERC20 decimals function signature
    decimals_abi = {
        'constant': True,
        'inputs': [],
        'name': 'decimals',
        'outputs': [{'name': '', 'type': 'uint8'}],
        'type': 'function'
    }

    contract = w3.eth.contract(address=Web3.toChecksumAddress(token_address), abi=[decimals_abi])
    decimals = contract.functions.decimals().call()
    return decimals



def get_eth_price():
    # Define the base URL and parameters
    url = "https://api.etherscan.io/api"
    parameters = {
        'module': 'stats',
        'action': 'ethprice',
        'apikey': os.getenv('ETHERSCAN_API')
    }
    # Make the GET request
    response = requests.get(url, params=parameters)

    # Ensure the response is successful
    response.raise_for_status()

    # Parse the JSON response
    data = response.json()

    # Check if the result is successful
    if data['status'] == '1':
        return float(data['result']['ethusd'])
    else:
        raise ValueError(f"API Error: {data['message']}")