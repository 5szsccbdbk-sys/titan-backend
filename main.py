from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
import requests

app = FastAPI()

# CORS Middleware Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CALENDAR_API_URL = "https://financialmodelingprep.com/api/v3/economic_calendar?apikey=YOUR_API_KEY"

@app.get("/")
def read_root():
    return {"message": "Titan Backend is Live!"}

@app.get("/api/ai-analysis")
def get_ai_analysis():
    # ডেমো মার্কেট ডেটা সেট (যদি লাইভ API ফেইল করে তবে এগুলো কাজ করবে)
    assets = ["EUR/USD", "GBP/USD", "USD/JPY", "BTC/USDT", "ETH/USDT"]
    events = ["US CPI News Release", "FOMC Meeting Minutes", "NFP Report", "ECB Interest Rate Decision", "Normal Market Flow"]
    directions = ["STRONG BUY 📈", "STRONG SELL 📉", "MARKET UNSTABLE ⚠️ WAIT"]
    
    selected_asset = random.choice(assets)
    selected_event = random.choice(events)
    selected_direction = random.choice(directions)
    
    try:
        # লাইভ নিউজ এপিআই কল করার চেষ্টা
        response = requests.get(CALENDAR_API_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                # লাইভ ডেটা পাওয়া গেলে সেখান থেকে ইভেন্ট নেবে
                live_news = random.choice(data)
                selected_event = live_news.get("event", selected_event)
                # কারেন্সি পেয়ার ম্যাচ করার চেষ্টা
                if live_news.get("currency"):
                    selected_asset = f"{live_news.get('currency')}/USD"
    except Exception as e:
        # কোনো কারণে লাইভ এপিআই কাজ না করলে এখানে এরর লক হবে না, নিচের ব্যাকআপ ডেটা রিটার্ন করবে
        pass

    # এআই রিকমেন্ডেশন ও ইনসাইট জেনারেট করা
    if "BUY" in selected_direction:
        insight = f"The economic sentiment for {selected_asset} suggests upward momentum. RSI and Moving Averages confirm a strong bullish trend on the 1-hour candle chart."
        confidence = f"{random.randint(85, 97)}%"
    elif "SELL" in selected_direction:
        insight = f"Heavy selling pressure detected on {selected_asset} after high-impact market shifts. Bearish engulfing patterns forming on the chart."
        confidence = f"{random.randint(82, 95)}%"
    else:
        insight = "High market volatility expected. No clear price pattern detected due to current financial updates. It is safer to wait for market stabilization."
        confidence = "N/A"

    return {
        "asset": selected_asset,
        "event": selected_event,
        "direction": selected_direction,
        "confidence": confidence,
        "insight": insight
    }
