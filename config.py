import os
import telebot
from dotenv import load_dotenv
load_dotenv()


BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)