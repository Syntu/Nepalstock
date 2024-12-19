import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

# Environment variables (set these in Render's dashboard)
TOKEN = os.getenv("TELEGRAM_API_KEY")

# Function to fetch stock data from Nepal Stock
def fetch_stock_data_by_symbol(symbol):
    url = "https://www.nepalstock.com/today-price"
    try:
        response = requests.get(url, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None

    if response.status_code != 200:
        print(f"Failed to fetch data: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'class': 'table'})
    if not table:
        print("Table not found")
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

    print(f"Symbol '{symbol}' not found in the table")
    return None

# Command handler: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to NEPSE📊BOT!\nकृपया स्टकको सिम्बोल दिनुहोस्।\nउदाहरण: SHINE, SHPC, SWBBL, etc."
    )

# Message handler for stock symbols
async def handle_stock_symbol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = update.message.text.strip().upper()
    print(f"Searching for stock symbol: {symbol}")
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
        response = f"Symbol '{symbol}' फेला परेन। कृपया सही सिम्बोल दिनुहोस्।"

    await update.message.reply_text(response, parse_mode=ParseMode.HTML)

# Telegram bot application setup using polling
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_stock_symbol))

# Start polling to handle updates from Telegram
if __name__ == "__main__":
    application.run_polling()
