import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
import logging

# Enable logging
logging.basicConfig(level=logging.DEBUG)

# Environment variables
TOKEN = os.getenv("TELEGRAM_API_KEY")

# Fetch stock data function
def fetch_stock_data_by_symbol(symbol):
    url = "https://www.nepalstock.com/today-price"
    try:
        response = requests.get(url, timeout=10, verify=False)
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")
        return None

    if response.status_code != 200:
        logging.error(f"Error: Unable to fetch data. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'class': 'table'})
    if not table:
        logging.error("Error: No table found in the response.")
        return None

    rows = table.find_all('tr')[1:]
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 10:
            continue

        row_symbol = cols[1].text.strip()
        if row_symbol.upper() == symbol.upper():
            ltp = cols[9].text.strip()
            return {'Symbol': symbol, 'LTP': ltp}

    logging.info(f"Symbol '{symbol}' not found.")
    return None

# Command handler: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to NEPSE📊BOT!\nकृपया स्टकको सिम्बोल दिनुहोस्।")

# Message handler
async def handle_stock_symbol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.strip().upper()
    logging.info(f"Searching for stock symbol: {symbol}")
    data = fetch_stock_data_by_symbol(symbol)

    if data:
        response = f"📈 Stock Data for <b>{data['Symbol']}</b>:\n\nLTP: {data['LTP']}"
    else:
        response = f"Symbol '{symbol}' फेला परेन। कृपया सही सिम्बोल दिनुहोस्।"

    await update.message.reply_text(response, parse_mode=ParseMode.HTML)

# Application setup
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_stock_symbol))

if __name__ == "__main__":
    application.run_polling()
