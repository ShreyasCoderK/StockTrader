# stock_bot.py

import discord
from discord.ext import commands
import yfinance as yf
from datetime import datetime, timedelta
import os

# ✅ Load token securely from environment variable
TOKEN = os.getenv("DISCORD_TOKEN")

# ✅ Enable intents including message content
intents = discord.Intents.default()
intents.message_content = True  # Required for reading command messages

# ✅ Initialize bot
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# ✅ Function to find trending stocks
def get_trending_stocks(tickers, days=5, threshold=2.0):
    end = datetime.now()
    start = end - timedelta(days=days + 2)  # add buffer for weekends

    results = []

    for ticker in tickers:
        data = yf.download(ticker, start=start, end=end)
        if len(data) < 2:
            continue
        start_price = data['Close'].iloc[0]
        end_price = data['Close'].iloc[-1]
        change = ((end_price - start_price) / start_price) * 100

        if change >= threshold:
            results.append(f"{ticker}: 📈 +{round(change, 2)}%")

    return results

# ✅ Bot command
@bot.command(name="trendingstocks")
async def trendingstocks(ctx):
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMZN']
    await ctx.send("🔍 Checking trending stocks...")

    try:
        results = get_trending_stocks(tickers)
        if results:
            await ctx.send("📊 Stocks trending upward:\n" + "\n".join(results))
        else:
            await ctx.send("📉 No trending stocks found today.")
    except Exception as e:
        await ctx.send(f"⚠️ Error checking stocks: {e}")

# ✅ Run the bot
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ DISCORD_TOKEN environment variable is not set.")
