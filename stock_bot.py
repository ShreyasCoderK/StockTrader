import discord
from discord.ext import commands
import yfinance as yf
from datetime import datetime, timedelta
import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings("ignore")

# --- Bot Setup ---
TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

# --- Get Ticker List (e.g. S&P 500) ---
def get_sp500_tickers():
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

# --- Simple AI Predictor ---
def predict_next_day_up(ticker):
    try:
        data = yf.download(ticker, period="30d", interval="1d")
        if data.empty or len(data) < 10:
            return False

        df = data[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
        df['Return'] = df['Close'].pct_change().shift(-1)
        df['Target'] = (df['Return'] > 0).astype(int)
        df = df.dropna()

        if len(df) < 10:
            return False

        X = df.drop(['Return', 'Target'], axis=1)
        y = df['Target']

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, shuffle=False)

        model = RandomForestClassifier(n_estimators=50, random_state=42)
        model.fit(X_train, y_train)

        latest = X_scaled[-1].reshape(1, -1)
        prediction = model.predict(latest)

        return prediction[0] == 1
    except Exception as e:
        print(f"Prediction error for {ticker}: {e}")
        return False

# --- Discord Command ---
@bot.command(name="predictstocks")
async def predictstocks(ctx):
    await ctx.send("🔍 Scanning for trending stocks and predictions...")
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

    message += "\n🤖 AI Buy Predictions:\n"
    ai_buys = []
    for ticker in tickers:
        if predict_next_day_up(ticker):
            ai_buys.append(ticker)

    if ai_buys:
        for ticker in ai_buys[:5]:
            message += f"✅ {ticker} is likely to go UP tomorrow.\n"
    else:
        message += "No strong buy signals detected.\n"

    await ctx.send(message)

# --- Run Bot ---
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ DISCORD_TOKEN environment variable not set.")
