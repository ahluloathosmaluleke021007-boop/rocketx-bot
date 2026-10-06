import os, requests, datetime
from flask import Flask
import yfinance as yf
import ta

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") # 6993641983
app = Flask(__name__)

def get_gold_analysis():
    data = yf.download("GC=F", period="2mo", interval="1d")
    close = data['Close']
    high = data['High']
    low = data['Low']
    
    rsi = float(ta.momentum.RSIIndicator(close).rsi().iloc[-1])
    ema20 = float(ta.trend.EMAIndicator(close, 20).ema_indicator().iloc[-1])
    ema50 = float(ta.trend.EMAIndicator(close, 50).ema_indicator().iloc[-1])
    price = float(close.iloc[-1])
    atr = float(ta.volatility.AverageTrueRange(high, low, close).average_true_range().iloc[-1])

    # STRONG BUY & STRONG SELL LOGIC
    if ema20 > ema50 and rsi < 38 and price > ema20:
        trend = "🟢🟢 STRONG BUY"; bias = "strong bullish"
        tip = f"Oversold bounce! RSI {rsi:.0f} + price above EMA20. Target +{atr*2:.0f}$"
    elif ema20 > ema50 and price > ema20:
        trend = "🟢 BUY"; bias = "bullish"
        tip = f"Uptrend intact. Buy dips above {ema20:.0f}."
    elif ema20 < ema50 and rsi > 62 and price < ema20:
        trend = "🔴🔴 STRONG SELL"; bias = "strong bearish"
        tip = f"Strong sell! RSI {rsi:.0f} overbought + below EMAs. Target -{atr*2:.0f}$"
    elif ema20 < ema50 and price < ema20:
        trend = "🔴 SELL"; bias = "bearish"
        tip = f"Downtrend. Sell rallies below {ema20:.0f}."
    else:
        trend = "⚪ HOLD"; bias = "neutral"
        tip = "Choppy, no edge today. Wait for breakout."

    return price, trend, rsi, ema20, ema50, bias, tip, atr

def send_telegram():
    price, trend, rsi, fast, slow, bias, tip, atr = get_gold_analysis()
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    emoji = "🚨" if "STRONG" in trend else "📊"
    if "BUY" in trend: emoji = "🚀🚀" if "STRONG" in trend else "🚀"
    if "SELL" in trend: emoji = "💥💥" if "STRONG" in trend else "💥"

    msg = f"""{emoji} Daily Gold Brief - {date}
💰 Price: {price:.2f}
Trend: {trend}
📊 RSI: {rsi:.1f} | EMA20: {fast:.1f} vs EMA50: {slow:.1f}
🎯 Bias: {bias}
💡 {tip}

Your Auto Bot does this 24/7 → wa.me/27815374449 R750 Lifetime"""

    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}")
    return f"Sent: {trend} @ {price:.2f}"

@app.route("/")
def home(): return "RocketX v4 - Strong Buys & Sells LIVE"
@app.route("/daily-brief")
def daily(): return send_telegram()
@app.route("/test")
def test(): return send_telegram()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
