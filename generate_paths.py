import time
import os
from config import *
from odos_router import *
from accounts_info import *
from suggest_tx import *
from telebot import types
import random

WETH_ADDRESS = '0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91'


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to Plow, the farming bot.")


@bot.message_handler(commands=['generate_farm_paths'])
def generate_farm_paths(message):
    # send the message
    bot.send_message(message.chat.id, f"Loading wallets...🕐\n"
                                      f"ETA: 3s per wallet", parse_mode='Markdown')

    # load the users keys and balances
    users = load_accounts()

    # send the message to inform the user
    bot.send_message(message.chat.id, f"Wallets loaded ✅", parse_mode='Markdown')
    bot.send_message(message.chat.id, f"Calculating paths...🕐", parse_mode='Markdown')
    print(json.dumps(users, indent=2))

    # set sleep times
    total_time = 45 * 60
    sleep_times = list(divide_length(total_time, len(users)))

    n = 0
    total_volume = 0
    full_message = ""
    txs = {}

    for n, i in enumerate(users):

        # generate a suggested tx
        suggested_tx = suggest_tx(users[i]['eth_balance'], users[i]['weth_balance'], users[i]['usdc_balance'])

        # check if possible to proceed
        if suggested_tx == 'insufficient ETH balance':
            bot.send_message(message.chat.id, "🔴 Not enough ETH to send transactions!", parse_mode='Markdown')
            return
        elif suggested_tx == 'insufficient WETH and USDC balance':
            bot.send_message(message.chat.id, "🔴 Not enough WETH or USDC to send transactions!", parse_mode='Markdown')
            return
        else:
            # txs details will be written into a json
            txs[i] = suggested_tx
            txs[i]['sleep_time'] = sleep_times[n]

            if users[i]['eth_balance'] < 0.01:
                full_message += generate_message_for_user(i, users[i], suggested_tx, sleep_times[n], low_eth=True)
            else:
                full_message += generate_message_for_user(i, users[i], suggested_tx, sleep_times[n])

            # build the message to send

            total_volume += suggested_tx['tx_value']


    # gas estimation is a bit simplified, but gas fees are incredibly low on zksync so it's ok
    gas_estimate = round((w3.eth.gas_price * 2_000_000 / 1e18) * 0.7 * get_eth_price(), 3)

    # add the summary to the message
    full_message += f'\n*Summary* \n' \
                    f'Total Volume: *${round(total_volume, 2)}* \n' \
                    f'LP fees ~ *${round(total_volume * 0.0007, 2)}* \n' \
                    f'Gas fees ~ *${round(gas_estimate * len(users), 2)}* \n' \
                    f'\nTransactions will execute at random times within a {total_time // 60}-minute window.'

    with open('current_txs_prepared.json', 'w') as file:
        json.dump(txs, file, indent=2)

    # insert execute/cancel buttons
    send_or_cancel_tx = types.InlineKeyboardMarkup(row_width=2)
    send_tx = types.InlineKeyboardButton("✅Execute TXs", callback_data=f"Execute")
    cancel_tx = types.InlineKeyboardButton("❌Cancel TXs", callback_data=f"Cancel")
    send_or_cancel_tx.add(send_tx, cancel_tx)

    # send the message
    bot.send_message(message.chat.id, full_message, reply_markup=send_or_cancel_tx, parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: call.data.startswith('Execute'))
def Execute_prepared_txs(call):
    users = load_accounts()

    with open('current_txs_prepared.json', 'r') as file:
        txs = json.load(file)

    for i in txs:
        token_in_address = txs[i]['token_in']
        token_out_address = txs[i]['token_out']
        token_in_amount = txs[i]['amount_in']
        transaction = odos_transaction(token_in_address, token_out_address, token_in_amount, users[i], simulate=True)
        if int(transaction['gas']) > 0 and int(transaction['gas']) < 7_000_000:

            tx_hash, initial_gas_spent = execute_tx(transaction, users[i])

            bot.send_message(call.message.chat.id,
                             f"✅ *{i}*:  TX executed @ `{tx_hash.hex()}`",
                             parse_mode='Markdown')
            bot.send_message(call.message.chat.id,
                             f"🕐 Waiting *{txs[i]['sleep_time']}s* to execute the next tx",
                             parse_mode='Markdown')
            time.sleep(txs[i]['sleep_time'])


        elif int(transaction['gas']) < 0:
            bot.send_message(call.message.chat.id,
                             f"❌ *{i}*:  ODOS failed to create the transaction",
                             parse_mode='Markdown')
        elif int(transaction['gas']) > 7_000_000:
            bot.send_message(call.message.chat.id,
                             f"⛽️💰 *{i}*:  Gas too high, tx interrupted!",
                             parse_mode='Markdown')

    bot.send_message(call.message.chat.id, "✅ All Transactions Executed", parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: call.data.startswith('Cancel'))
def Cancel_prepared_txs(call):
    file_name = "current_txs_prepared.json"

    if os.path.exists(file_name):
        try:
            os.remove(file_name)
            print(f"'{file_name}' has been deleted successfully.")
        except Exception as e:
            print(f"Error occurred while deleting '{file_name}': {e}")
    else:
        print(f"'{file_name}' does not exist.")


def tx_total_expenses():
    weth_price = get_eth_price()

    balance_before = 0

    for i in users:
        balance_before += (users[i]['eth_balance'] + users[i]['weth_balance']) / 1e18 * weth_price \
                          + users[i]['usdc_balance'] / 1e6


def generate_message_for_user(account_name, user, suggested_tx, sleep_time, low_eth=False):
    token_in = 'WETH' if suggested_tx['token_in'] == WETH_ADDRESS else 'USDC'
    token_out = 'USDC' if token_in == 'WETH' else 'WETH'

    decimals_in = 18 if token_in == 'WETH' else 6
    decimals_out = 18 if token_out == 'WETH' else 6

    low_eth_warning = "" if low_eth == False else "(⚠️ Low ETH)"

    return (f"🟢 Account: *{account_name}*\n"
            f"ETH balance: {round(user['eth_balance'] / 1e18, 4)} {low_eth_warning}\n"
            f"WETH balance: {round(user[f'weth_balance'] / 1e18, 4)}\n"
            f"USDC balance: {round(user[f'usdc_balance'] / 1e6, 4)}\n"
            f"Suggested TX: {round(suggested_tx['amount_in'], 3)} {token_in} -> {token_out} (*${round(suggested_tx['tx_value'], 2)}*)\n"
            f"Sleep time: {sleep_time // 60}m\n\n")
