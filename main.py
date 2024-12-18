import os
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.constants import ParseMode
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv

# Environment variables load
load_dotenv()
TOKEN = os.getenv("TELEGRAM_API_KEY")
APP_URL = os.getenv("APP_URL")

# Flask app
app = Flask(__name__)

# Telegram bot application
application = ApplicationBuilder().token(TOKEN).build()

# Function to fetch stock data
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
        if len(cols) < 10:
            continue

        row_symbol = cols[1].text.strip()
        if row_symbol.upper() == symbol.upper():
            return {
                'Symbol': symbol,
                'Day High': cols[4].text.strip(),
                'Day Low': cols[5].text.strip(),
                'LTP': cols[9].text.strip(),
                'Previous Closing': cols[10].text.strip(),
                'Volume': cols[6].text.strip(),
                'Turnover': cols[7].text.strip(),
            }
    return None

# Command handler for /start
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
        response = f"Symbol '{symbol}'ल्या फेला परेन त हौ 😅😅।\n Symbol राम्रो सङ्ग हेरेर फेरि Try गर्नुस है 🤗🙏।"

    await update.message.reply_text(response, parse_mode=ParseMode.HTML)

# Adding handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_stock_symbol))

# Flask route for Telegram Webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_data = request.get_json(force=True)
    update = Update.de_json(json_data, application.bot)
    application.update_queue.put(update)
    return "OK", 200

# Webhook setup
def set_webhook():
    webhook_url = f"{APP_URL}/{TOKEN}"
    application.bot.set_webhook(url=webhook_url)
    print(f"Webhook set to: {webhook_url}")

# Flask app run
if __name__ == "__main__":
    set_webhook()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
