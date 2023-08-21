
import json
import os
import requests
from web3 import Web3
from dotenv import load_dotenv
load_dotenv()
import web3
from web3_functions import *

w3 = Web3(Web3.HTTPProvider('https://mainnet.era.zksync.io'))

odos_router_address = '0x4bBa932E9792A2b917D47830C93a9BC79320E4f7'





def odos_transaction(token_in_address, token_out_address, token_in_amount, user, simulate=True):

    decimals_in = get_token_decimals(token_in_address)
    decimals_out = get_token_decimals(token_out_address)

    allowance = get_allowance(token_in_address, user, odos_router_address)
    if allowance < token_in_amount*10**decimals_in:
        approve_token(token_in_address, odos_router_address, int(token_in_amount*100), user)
    else:

        request_body = {
          "chainId": 324,
          "compact": True,
          "disableRFQs": False,
          "gasPrice": w3.eth.gas_price/1e9,
          "inputTokens": [
            {
              "amount": str(int(token_in_amount*10**decimals_in)),
              "tokenAddress": Web3.toChecksumAddress(token_in_address)
            }
          ],
          "outputTokens": [
            {
              "proportion": 1,
              "tokenAddress": Web3.toChecksumAddress(token_out_address)
            }
          ],
          "referralCode": 0,
          "slippageLimitPercent": 0.3,
          "sourceBlacklist": [],
          "sourceWhitelist": [],
          "userAddr": Web3.toChecksumAddress(user['address'])
        }

        response = requests.post(
              "https://api.odos.xyz/sor/quote/v2",
              headers={"Content-Type": "application/json"},
              json=request_body
            )
        if response.status_code == 200:
            quote = response.json()
            # handle quote response data
        else:
            print(f"Error in Quote: {response.json()}")
            return None

        assemble_url = "https://api.odos.xyz/sor/assemble"

        assemble_request_body = {
            "userAddr": Web3.toChecksumAddress(user['address']),  # the checksummed address used to generate the quote
            "pathId": quote["pathId"],  # Replace with the pathId from quote response in step 1
            "simulate": simulate,
            # this can be set to true if the user isn't doing their own estimate gas call for the transaction
        }

        response = requests.post(
            assemble_url,
            headers={"Content-Type": "application/json"},
            json=assemble_request_body
        )

        if response.status_code == 200:
            assembled_transaction = response.json()
            transaction = assembled_transaction["transaction"]
            transaction["chainId"] = 324
            transaction["value"] = int(transaction["value"])
        else:
            print(f"Error in Transaction Assembly: {response.json()}")
            # handle transaction assembly failure cases
            return None

        return quote, transaction






# gas price of ok tx: 1_150_338, but on rabby also 2_800_000


def execute_tx(transaction, user):


    signed_tx = w3.eth.account.signTransaction(transaction, user['private_key'])
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)


    return tx_hash





# print(json.dumps(transaction, indent=2))




