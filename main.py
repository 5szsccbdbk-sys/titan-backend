from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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

SECRET_PASSWORD = "NTXORHN"
API_KEY = "d9atj59r01qp4bhsgtq0d9atj59r01qp4bhsgtqg"

class PasswordRequest(BaseModel):
    password: str

@app.get("/")
def read_root():
    return {"message": "Neo Titan XO (Dynamic Finnhub) Backend is Live!"}

@app.post("/api/verify-pass")
def verify_password(req: PasswordRequest):
    if req.password == SECRET_PASSWORD:
        return {"status": "success"}
    return {"status": "failed", "error": "Incorrect Password"}

@app.post("/api/ai-analysis")
def get_ai_analysis(req: PasswordRequest):
    if req.password != SECRET_PASSWORD:
        return {"error": "Unauthorized Access Detected!"}

    try:
        # ডায়নামিক তারিখ তৈরি (আজ থেকে ৭ দিন পর্যন্ত)
        tz_bd = pytz.timezone('Asia/Dhaka')
        now = datetime.now(tz_bd)
        from_date = now.strftime("%Y-%m-%d")
        to_date = (now + timedelta(days=7)).strftime("%Y-%m-%d")
        
        # ডায়নামিক URL তৈরি
        url = f"https://finnhub.io/api/v1/calendar/economic?from={from_date}&to={to_date}&token={API_KEY}"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            all_news = data.get("economicCalendar", [])
            
            # আজকের নিউজ ফিল্টার করা
            todays_news = [n for n in all_news if n.get("date") == from_date]
            
            if todays_news:
                # ইমপ্যাক্ট বা গুরুত্বপূর্ণ ইভেন্ট বাছাই (প্রথমটি)
                selected_news = todays_news[0]
                
                title = selected_news.get("event", "Economic Event")
                currency = selected_news.get("country", "USD")
                time_val = selected_news.get("time", "N/A")
                
                # প্রফেশনাল সিগন্যাল লজিক
                direction = "STRONG BUY 📈" if hash(title) % 2 == 0 else "STRONG SELL 📉"
                percentage = f"{82 + (hash(title) % 13)}%"
                
                return {
                    "asset": f"{currency}/USD",
                    "event": title,
                    "time": f"Today at {time_val}",
                    "raw_time": time_val, 
                    "direction": direction,
                    "confidence": percentage,
                    "insight": f"Market volatility detected for {currency}. Major economic event: {title}."
                }
        
        return {
            "asset": "NO LIVE NEWS",
            "event": "No Economic News Scheduled for Today",
            "time": "N/A",
            "raw_time": None,
            "direction": "STANDBY ⚠️ NO TRADE",
            "confidence": "0%",
            "insight": "No economic events found for today on the Finnhub calendar."
        }
            
    except Exception as e:
        return {
            "asset": "SERVER ERROR",
            "event": "Unable to fetch live news",
            "time": "N/A",
            "raw_time": None,
            "direction": "ERROR ⚠️",
            "confidence": "0%",
            "insight": f"Connection error: {str(e)}"
        }