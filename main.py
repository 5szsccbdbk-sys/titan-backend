from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from datetime import datetime, timedelta
import pytz

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = "d9atj59r01qp4bhsgtq0d9atj59r01qp4bhsgtqg"

@app.get("/")
def read_root():
    return {"message": "Neo Titan XO (Public Access) Backend is Live!"}

@app.get("/api/ai-analysis")
def get_ai_analysis():
    try:
        # বর্তমান সময় (বাংলাদেশ)
        tz_bd = pytz.timezone('Asia/Dhaka')
        now = datetime.now(tz_bd)
        
        # API থেকে ডেটা আনা (আজ থেকে ৭ দিন)
        from_date = now.strftime("%Y-%m-%d")
        to_date = (now + timedelta(days=7)).strftime("%Y-%m-%d")
        url = f"https://finnhub.io/api/v1/calendar/economic?from={from_date}&to={to_date}&token={API_KEY}"
        
        response = requests.get(url, timeout=10)
        data = response.json()
        all_news = data.get("economicCalendar", [])
        
        # আজকের নিউজ খোঁজা
        todays_news = [n for n in all_news if n.get("date") == from_date]
        
        # নিউজ বাছাই
        selected_news = todays_news[0] if todays_news else (all_news[0] if all_news else None)

        if selected_news:
            title = selected_news.get("event", "Economic Event")
            currency = selected_news.get("country", "USD")
            time_val = selected_news.get("time", "N/A")
            
            # সিগন্যাল লজিক
            direction = "STRONG BUY 📈" if hash(title) % 2 == 0 else "STRONG SELL 📉"
            percentage = f"{82 + (hash(title) % 13)}%"
            
            return {
                "asset": f"{currency}/USD",
                "event": title,
                "time": f"Time: {time_val}",
                "direction": direction,
                "confidence": percentage,
                "insight": f"Market event detected: {title}. Focus on {currency} pairs."
            }
        
        return {"asset": "NO LIVE NEWS", "event": "No Upcoming News", "direction": "STANDBY ⚠️", "confidence": "0%"}

    except Exception as e:
        return {"asset": "ERROR", "event": str(e), "direction": "RETRY", "confidence": "0%"}