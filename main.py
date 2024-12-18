import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Flask app for webhook
app = Flask(__name__)

# Environment variables
TOKEN = os.getenv("TELEGRAM_API_KEY")
APP_URL = os.getenv("APP_URL")

# Function to fetch stock data from Nepal Stock
def fetch_stock_data_by_symbol(symbol):
    url = "https://www.nepalstock.com/today-price"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'class': 'table'})
    if not table:
        return None

    rows = table.find_all('tr')[1:]
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 10:  # Ensure the row has enough columns
            continue

        row_symbol = cols[1].text.strip()
        if row_symbol.upper() == symbol.upper():
            day_high = cols[4].text.strip()
            day_low = cols[5].text.strip()
            closing_price = cols[9].text.strip()
            previous_closing = cols[10].text.strip()
            volume = cols[6].text.strip()
            turnover = cols[7].text.strip()

            return {
                'Symbol': symbol,
                'Day High': day_high,
                'Day Low': day_low,
                'LTP': closing_price,
                'Previous Closing': previous_closing,
                'Volume': volume,
                'Turnover': turnover,
            }
    return None

# Command handler: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Syntu's NEPSE💹BOT!\nकृपया स्टकको सिम्बोल दिनुहोस्।\nउदाहरण: SHINE, SHPC, SWBBL, etc."
    )

# Message handler for stock symbols
async def handle_stock_symbol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.strip().upper()
    data = fetch_stock_data_by_symbol(symbol)

    if data:
        response = (
            f"📈 Stock Data for <b>{data['Symbol']}</b>:\n\n"
            f"LTP: {data['LTP']}\n"
            f"Day High: {data['Day High']}\n"
            f"Day Low: {data['Day Low']}\n"
            f"Previous Closing: {data['Previous Closing']}\n"
            f"Volume: {data['Volume']}\n"
            f"Turnover: {data['Turnover']}"
        )
    else:
        response = f"Symbol '{symbol}' ल्या फेला परेन हौं 🤗🤗\nSymbol राम्रो सङ्ग हेरेर फेरि Try गर्नुस है 🙏।"

    await update.message.reply_text(response, parse_mode=ParseMode.HTML)

# Telegram bot application setup
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_stock_symbol))

# Flask route for Telegram Webhook
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put(update)
    return "OK", 200

# Set webhook on Flask startup using `before_request`
@app.before_request
def set_webhook():
    # Set the webhook to the Telegram API
    webhook_url = f"{APP_URL}/{TOKEN}"
    application.bot.set_webhook(webhook_url)

# Root route to handle GET requests
@app.route("/", methods=["GET"])
def index():
    return "NEPSE BOT is running!", 200

# Run Flask app and set webhook
if __name__ == "__main__":
    # Run Flask app
    port = int(os.getenv("PORT", 5000))  # Default port is 5000 if not set
    app.run(host="0.0.0.0", port=port)
