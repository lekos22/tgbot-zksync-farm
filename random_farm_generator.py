import os
import random
from web3 import Web3
from dotenv import load_dotenv
load_dotenv()
import random
import requests



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



def suggest_tx(eth_balance, weth_balance, usdc_balance):
    # Check eth_balance
    if eth_balance <= 0.005*1e18:
        return {'insufficient ETH balance'}

    WETH_ADDRESS = '0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91'
    USDC_ADDRESS = '0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4'

    # Get WETH price

    weth_price = get_eth_price()

    # Convert balances to real value
    weth_real_value = weth_balance / (10**18)
    usdc_real_value = usdc_balance / (10**6)

    # Convert WETH balance to USD value
    weth_usd_value = weth_real_value * weth_price

    # Determine which token has higher % of USD balance
    total_usd_value = weth_usd_value + usdc_real_value
    weth_percentage = (weth_usd_value / total_usd_value) * 100
    usdc_percentage = 100 - weth_percentage

    if weth_percentage > usdc_percentage:
        token_in = WETH_ADDRESS
        max_amount = weth_real_value
    else:
        token_in = USDC_ADDRESS
        max_amount = usdc_real_value

        # Randomly select an amount_in
    while True:
        random_percentage = random.uniform(0.75, 1)  # Assuming you want to choose between 10% and 100%
        amount_in = random_percentage * max_amount

        # Convert amount_in to USD value
        amount_in_usd_value = amount_in * (weth_price if token_in == WETH_ADDRESS else 1)

        # Check if amount_in_usd_value is greater than $10
        if amount_in_usd_value > 10:
            break

    return {
        'token_in': token_in,
        'token_out': WETH_ADDRESS if token_in == USDC_ADDRESS else USDC_ADDRESS,
        'amount_in': amount_in,
        'tx_value': amount_in_usd_value
    }


def divide_length(total_length, N):
    # Step 1: Generate N-1 random numbers
    random_points = [random.randint(1, total_length - 1) for _ in range(N - 1)]

    # Step 2: Add 0 at the start and total_length at the end
    random_points.append(0)
    random_points.append(total_length)

    # Step 3: Sort the list
    random_points.sort()

    # Step 4: Compute the differences
    segments = [random_points[i + 1] - random_points[i] for i in range(N)]

    return segments