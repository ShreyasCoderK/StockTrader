import discord
from discord.ext import commands
import yfinance as yf
from datetime import datetime, timedelta
import os

# --- Bot Setup ---
TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

# --- Get Ticker List (e.g. S&P 500) ---
def get_sp500_tickers():
    # You can expand this later to load all S&P 500 from a file or API
    return ['AAPL', 'MSFT', 'TSLA', 'GOOGL', 'NVDA', 'AMZN', 'META', 'NFLX']

# --- Detect Trending and Falling Stocks ---
def find_stock_trends(tickers):
    trending_up = []
    trending_down = []

    for ticker in tickers:
        try:
            data = yf.download(ticker, period="7d", interval="1d")
            if data.empty or len(data) < 5:
                continue

            close_prices = data["Close"].dropna()
            if len(close_prices) < 2:
                continue

            change = ((close_prices[-1] - close_prices[0]) / close_prices[0]) * 100

            if change > 5:
                trending_up.append((ticker, round(change, 2)))
            elif change < -5:
                trending_down.append((ticker, round(change, 2)))

        except Exception as e:
            print(f"⚠️ Error checking {ticker}: {e}")

    trending_up.sort(key=lambda x: -x[1])
    trending_down.sort(key=lambda x: x[1])
    return trending_up, trending_down

# --- Discord Command ---
@bot.command(name="predictstocks")
async def predictstocks(ctx):
    await ctx.send("🔍 Scanning for trending stocks...")
    tickers = get_sp500_tickers()
    trending_up, trending_down = find_stock_trends(tickers)

    message = ""

    if trending_up:
        message += "📈 Top Gainers (Past 7 Days):\n"
        for ticker, change in trending_up[:5]:
            message += f"{ticker}: +{change}%\n"
    else:
        message += "📈 No gaining stocks detected.\n"

    message += "\n"

    if trending_down:
        message += "📉 Top Losers (Past 7 Days):\n"
        for ticker, change in trending_down[:5]:
            message += f"{ticker}: {change}%\n"
    else:
        message += "📉 No falling stocks detected.\n"

    await ctx.send(message)

# --- Run Bot ---
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ DISCORD_TOKEN environment variable not set.")


