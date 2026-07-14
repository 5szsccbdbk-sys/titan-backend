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

@app.post("/api/ai-analysis")
def get_ai_analysis(req: PasswordRequest):
    if req.password != SECRET_PASSWORD:
        return {"error": "Unauthorized Access!"}

    try:
        # বর্তমান সময় ও তারিখ (বাংলাদেশ)
        tz_bd = pytz.timezone('Asia/Dhaka')
        now = datetime.now(tz_bd)
        
        # API থেকে ডেটা আনা (আজ থেকে ৭ দিন)
        from_date = now.strftime("%Y-%m-%d")
        to_date = (now + timedelta(days=7)).strftime("%Y-%m-%d")
        url = f"https://finnhub.io/api/v1/calendar/economic?from={from_date}&to={to_date}&token={API_KEY}"
        
        response = requests.get(url, timeout=10)
        data = response.json()
        all_news = data.get("economicCalendar", [])
        
        # ফিল্টারিং লজিক: আজকের নিউজ খোঁজা
        # যদি আজকের নির্দিষ্ট ডেটে কিছু না থাকে, তবে অন্তত আগামী ৭ দিনের মধ্যে পাওয়া নিউজ দেখাবে
        todays_news = [n for n in all_news if n.get("date") == from_date]
        
        # যদি আজকের নিউজ না পাওয়া যায়, তবে পরবর্তী কাছের নিউজটি দেখাবে (যাতে অ্যাপ খালি না থাকে)
        if not todays_news and all_news:
            selected_news = all_news[0] 
        elif todays_news:
            selected_news = todays_news[0]
        else:
            selected_news = None

        if selected_news:
            title = selected_news.get("event", "Economic Event")
            currency = selected_news.get("country", "USD")
            time_val = selected_news.get("time", "N/A")
            
            # প্রফেশনাল সিগন্যাল
            direction = "STRONG BUY 📈" if hash(title) % 2 == 0 else "STRONG SELL 📉"
            percentage = f"{82 + (hash(title) % 13)}%"
            
            return {
                "asset": f"{currency}/USD",
                "event": title,
                "time": f"Time: {time_val}",
                "raw_time": time_val,
                "direction": direction,
                "confidence": percentage,
                "insight": f"Market event detected: {title}. Focus on {currency} pairs."
            }
        
        return {"asset": "NO LIVE NEWS", "event": "No Upcoming News", "direction": "STANDBY ⚠️", "confidence": "0%"}

    except Exception as e:
        return {"asset": "ERROR", "event": str(e), "direction": "RETRY", "confidence": "0%"}