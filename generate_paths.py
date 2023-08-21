import time
import os
from config import *
from odos_router import *
from accounts_info import *
from random_farm_generator import *
from telebot import types
import random



@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to Plow, the farming bot.")




@bot.message_handler(commands=['generate_farm_paths'])
def generate_farm_paths(message):
    bot.send_message(message.chat.id, f"Loading wallets...🕐\n"
                                      f"ETA: 3s per wallet", parse_mode='Markdown')

    users = load_accounts()

    bot.send_message(message.chat.id, f"Wallets loaded ✅", parse_mode='Markdown')
    bot.send_message(message.chat.id, f"Calculating paths...🕐", parse_mode='Markdown')
    print(json.dumps(users, indent=2))

    full_message = ""
    txs = {}
    total_time = 30 * 60
    sleep_times = divide_length(1800, len(users))
    n=0


    for i in users:



        suggested_tx = suggest_tx(users[i]['eth_balance'], users[i]['weth_balance'], users[i]['usdc_balance'])

        if suggested_tx['token_in'] == '0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91':
            suggested_tx_readable = f"{round(suggested_tx['amount_in'], 3)} WETH -> USDC " \
                                    f"(*${round(suggested_tx['tx_value'], 2)}*)"
            decimals_in = 1e18
            decimals_out = 1e6

        else:
            suggested_tx_readable = f"{round(suggested_tx['amount_in'], 2)} USDC -> WETH " \
                                    f"(*${round(suggested_tx['tx_value'], 2)}*)"
            decimals_in = 1e6
            decimals_out = 1e18

        full_message += f"Account: *{i}*\n"
        full_message += f"ETH balance: {round(users[i]['eth_balance']/1e18,4)}\n"
        full_message += f"WETH balance: {round(users[i]['weth_balance']/1e18,4)}\n"
        full_message += f"USDC balance: {round(users[i]['usdc_balance']/1e6,2)}\n"

        full_message += f"{suggested_tx_readable}\n\n"


        txs[i] = suggested_tx
        txs[i]['sleep_time'] = sleep_times[n]
        n+=1

    with open('current_txs_prepared.json', 'w') as file:
        json.dump(txs, file, indent=2)


        # buttons
    send_or_cancel_tx = types.InlineKeyboardMarkup(row_width=2)
    send_tx = types.InlineKeyboardButton("✅Execute TXs", callback_data=f"Execute")
    cancel_tx = types.InlineKeyboardButton("❌Cancel TXs", callback_data=f"Cancel")
    send_or_cancel_tx.add(send_tx, cancel_tx)


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
        odos_transaction(token_in_address, token_out_address, token_in_amount, users[i], simulate=True)
        execute_tx(odos_transaction, users[i])

        time.sleep()


    bot.send_message(call.message.chat.id, "Transactions Executed", parse_mode='Markdown')


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

