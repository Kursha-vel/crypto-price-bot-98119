import os
import asyncio
from python_telegram_bot.telegram import Update
from python_telegram_bot.telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from python_telegram_bot.telegram.ext import job

import requests

TOKEN = os.environ.get("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Этот бот показывает курс Bitcoin и Ethereum каждые 12 часов. Нажмите /price, чтобы получить текущий курс.")

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = requests.get('https://min-api.cryptocompare.com/data/price?fsym=USD&tsyms=BTC,ETH')
    data = response.json()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Курс Bitcoin: {data["BTC"]}\nКурс Ethereum: {data["ETH"]}')

async def send_price(context: ContextTypes.DEFAULT_TYPE):
    response = requests.get('https://min-api.cryptocompare.com/data/price?fsym=USD&tsyms=BTC,ETH')
    data = response.json()
    for chat_id in context.job.chat_data:
        await context.bot.send_message(chat_id=chat_id, text=f'Курс Bitcoin: {data["BTC"]}\nКурс Ethereum: {data["ETH"]}')

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))
    job_queue = app.job_queue
    job_queue.run_repeating(send_price, interval=43200, first=0) # 12 часов
    job_queue.run_once(lambda context: job_queue.run_repeating(send_price, interval=43200, first=0))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()