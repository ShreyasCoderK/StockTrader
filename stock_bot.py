import discord
from discord.ext import commands
import yfinance as yf
from datetime import datetime, timedelta
import os

# Load the Discord token from environment variable
TOKEN = os.getenv("DISCORD_TOKEN")

# Enable required intents
intents = discord.Intents.default()
intents.message_content = True

# Create the bot
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# ✅ Safe, debugged trending stock checker
def get_trending_stocks(tickers, days=5, threshold=2.0):
    end = datetime.now()
    start = end - timedelta(days=days + 2)

    results = []

    for ticker in tickers:
        try:
            print(f"🔍 Checking {ticker}")
            data = yf.download(ticker, start=start, end=end)

            if data.empty or 'Close' not in data.columns:
                print(f"❌ Skipping {ticker}: no data or missing 'Close'")
                continue

            closes = data['Close'].dropna()

            if len(closes) < 2:
                print(f"❌ Skipping {ticker}: not enough closing data")
                continue

            start_price = closes.iloc[0]
            end_price = closes.iloc[-1]

            # Log and convert to float
            print(f"{ticker}: Start = {start_price}, End = {end_price}")

            start_price = float(start_price)
            end_price = float(end_price)

            change = ((end_price - start_price) / start_price) * 100
            print(f"{ticker}: Change = {change:.2f}%")

            if change >= float(threshold):
                results.append(f"{ticker}: 📈 +{round(change, 2)}%")

        except Exception as e:
            print(f"⚠️ Error processing {ticker}: {e}")

    return results

# Discord command to trigger stock check
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
        print(f"⚠️ Bot error: {e}")

# Run the bot
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ DISCORD_TOKEN environment variable is not set.")

