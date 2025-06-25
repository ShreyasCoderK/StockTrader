import discord
from discord.ext import commands
import yfinance as yf
from datetime import datetime, timedelta
import os

# Load token securely from environment
TOKEN = os.getenv("DISCORD_TOKEN")

# Enable required intents
intents = discord.Intents.default()
intents.message_content = True

# Create the bot
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# ✅ Fixed function: no ambiguous Series comparisons
def get_trending_stocks(tickers, days=5, threshold=2.0):
    end = datetime.now()
    start = end - timedelta(days=days + 2)

    results = []

    for ticker in tickers:
        data = yf.download(ticker, start=start, end=end)

        # Safely skip if there's no data
        if data.empty or 'Close' not in data.columns:
            continue

        closes = data['Close'].dropna()

        if len(closes) < 2:
            continue

        start_price = closes.iloc[0]
        end_price = closes.iloc[-1]
        change = ((end_price - start_price) / start_price) * 100

        if change >= threshold:
            results.append(f"{ticker}: 📈 +{round(change, 2)}%")

    return results

# Bot command to show trending stocks
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
        print(f"⚠️ DEBUG ERROR: {e}")

# Run the bot
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ DISCORD_TOKEN is not set.")
