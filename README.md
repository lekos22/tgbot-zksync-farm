# tgbot-zksync-farm
Welcome my dear shareholders to my guide on how to build a telegram bot to automate the boring process of airdrop farming.

To use this tool, you have to follow these steps

## Prerequisites

In this first alpha stage, this application is still not able to swap ETH but just WETH <-> USDC, so be sure to
1. Fund a wallet from a CEX to Ethereum mainnet
2. Do at least 1 tx on Ethereum
3. Bridge the funds to ZKSync (I suggest Orbiter Bridge)
4. Swap all the ETH to WETH or USDC, except for like $25 for gas fees

Now let's move to Telegram Bot setup

## Telegram Instructions
1. Search for @BotFather on Telegram
2. /newbot -> give it a name and a handle

You will get a token like this, save it

![image](https://github.com/lekos22/tgbot-zksync-farm/assets/140423090/8349d976-4130-4a88-97d3-4cb3208ef21b)

3. /mybots -> select your bot -> edit bot -> edit commands
4. digit this `generate_farm_paths - Generate swap paths for all wallets`

You're done with telegram, let's move to Python

## Python Instructions
1. Download all files of this repository
2. Create a new python project with a development environments (I use PyCharm)
3. Install the packages in the requirements.txt:
   - Go to the project folder > right click > terminal
   - `pip install -r requirements.txt`

  
4. Create in the same folder a file called `.env`, populate it with the telegram bot token, the etherscan api key and your wallets. You should have something like this (I censored everything ofc)

![image](https://github.com/lekos22/tgbot-zksync-farm/assets/140423090/28b7fbea-bca8-49fa-b2c8-e60fc67f380c)

5. Run the main.py file with python, let it run until you're done with the farming

(ATTENTION, THE BOT WON'T WORK IF PYTHON IS NOT RUNNING)



# How it works

## main.py
This file basically just run the bot in 'polling' mode (waiting for commands)

## config.py
Load the bot info from .env

## accounts_info.py
Load accounts info starting from the private keys (address, current balances of eth/weth/usdc)

## web3_functions.py
Defines the functions to get the allowance of a token, set approval and get balances (allowance/approval will help with future updates)

## odos_router.py
Defines the functions to setup and execute a swap function on Odos (using their official API)

## random_farm_generator.py
Contains a function called suggest_tx(). Starting from WETH and USDC, takes the one with higher balance and generates a random transaction with volume > 75% of the balance (to maximize volume). 
With future updates you will have more granularity on this.

## generate_paths.py
Define the `generate_farm_paths` telegram command, invoke the suggest_tx() to generate transactions for every user, divided randomly in a 30 minutes window (you can edit time editind the variable `sleep_times`)











