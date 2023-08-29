from config import *
from accounts_info import *
from odos_router import *
from telebot import types
import time
from suggest_tx import divide_length
user_state = {}

@bot.message_handler(commands=['swap_to_weth'])
def swap_to_weth(message):
    bot.send_message(message.chat.id, f"Loading wallets...🕐\n"
                                      f"ETA: 3s per wallet", parse_mode='Markdown')
    users = load_accounts()


    total_time = 15 * 60
    sleep_times = divide_length(total_time, len(users))
    # load the users keys and balances
    total_swaps = 0
    txs = {}
    full_message = "You're swapping these amounts of USDC to WETH: \n"
    for n, i in enumerate(users):
        if round(users[i]['usdc_balance']/1e6, 2) < 10:
            full_message += f"{i}: balance < 10$, no need to swap \n"
        else:
            full_message += f"{i}: ${round(users[i]['usdc_balance']/1e6, 2)} \n"
            txs[i] = {
                "token_in": USDC_ADDRESS,
                "token_out": WETH_ADDRESS,
                "amount_in": users[i]['usdc_balance']/1e6,
                "tx_value": users[i]['usdc_balance']/1e6,
                "sleep_time": sleep_times[n]
            }
            total_swaps += users[i]['usdc_balance']/1e6
    full_message += f"*\nTotal volume: ${round(total_swaps,2)}*"
    full_message += f"\nTotal time: {total_time // 60}min"
    full_message += "\n\nPlease confirm the action..."

    send_tx = types.InlineKeyboardMarkup(row_width=2)
    send_tx_button = types.InlineKeyboardButton("✅Execute TXs", callback_data=f"Execute")
    cancel_tx = types.InlineKeyboardButton("❌Cancel TXs", callback_data=f"Cancel")
    send_tx.add(send_tx_button, cancel_tx)

    with open('current_txs_prepared.json', 'w') as file:
        json.dump(txs, file, indent=2)
    bot.send_message(message.chat.id, full_message, reply_markup=send_tx, parse_mode='Markdown')


@bot.message_handler(commands=['swap_to_usdc'])
def swap_to_usdc(message):
    bot.send_message(message.chat.id, f"Loading wallets...🕐\n"
                                      f"ETA: 3s per wallet", parse_mode='Markdown')
    users = load_accounts()


    total_time = 15 * 60
    sleep_times = divide_length(total_time, len(users))
    # load the users keys and balances
    total_swaps = 0
    txs = {}
    full_message = "You're swapping these amounts of WETH to USDC: \n"
    for n, i in enumerate(users):
        if round(users[i]['weth_balance'] / 1e18, 2) < 0.005:
            full_message += f"{i}: balance < 0.005 WETH, no need to swap \n"
        else:
            full_message += f"{i}: ${round(users[i]['weth_balance']/1e18, 2)} \n"
            txs[i] = {
                "token_in": WETH_ADDRESS,
                "token_out": USDC_ADDRESS,
                "amount_in": users[i]['weth_balance']/1e18,
                "tx_value": users[i]['weth_balance']/1e18,
                "sleep_time": sleep_times[n]
            }
            total_swaps += users[i]['weth_balance']/1e18
    full_message += f"\n*Total volume: {round(total_swaps,2)} WETH*"
    full_message += f"\nTotal time: {total_time//60}min"
    full_message += "\n\nPlease confirm the action..."

    send_tx = types.InlineKeyboardMarkup(row_width=2)
    send_tx_button = types.InlineKeyboardButton("✅Execute TXs", callback_data=f"Execute")
    cancel_tx = types.InlineKeyboardButton("❌Cancel TXs", callback_data=f"Cancel")
    send_tx.add(send_tx_button, cancel_tx)

    with open('current_txs_prepared.json', 'w') as file:
        json.dump(txs, file, indent=2)
    bot.send_message(message.chat.id, full_message, reply_markup=send_tx, parse_mode='Markdown')

