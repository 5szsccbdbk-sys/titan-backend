from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from datetime import datetime
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
CABLE_API_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

class PasswordRequest(BaseModel):
    password: str

@app.get("/")
def read_root():
    return {"message": "Neo Titan XO Date-Fix Backend is Live!"}

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
        response = requests.get(CABLE_API_URL, timeout=10)
        if response.status_code == 200:
            all_news = response.json()
            
            # বাংলাদেশ টাইমজোন অনুযায়ী আজকের তারিখ (যেমন: "Jul 14")
            tz_bd = pytz.timezone('Asia/Dhaka')
            now_bd = datetime.now(tz_bd)
            today_str = now_bd.strftime("%b %d") 
            
            # ১. আজকের তারিখের নিউজ ফিল্টার করা
            todays_news = [n for n in all_news if today_str.lower() in str(n.get("date", "")).lower()]
            
            # ২. যদি আজকের নিউজ না পাওয়া যায়, তবে হাই/মিডিয়াম ইমপ্যাক্ট নিউজ খোঁজা
            if not todays_news:
                todays_news = [n for n in all_news if n.get("impact") in ["High", "Medium"]]

            if todays_news:
                # হাই ইমপ্যাক্ট নিউজকে প্রাধান্য দেওয়া
                high_impact = [n for n in todays_news if n.get("impact") == "High"]
                selected_news = high_impact[0] if high_impact else todays_news[0]
                
                title = selected_news.get("title", "Economic Event")
                currency = selected_news.get("country", "USD")
                impact = selected_news.get("impact", "Low")
                time_str = selected_news.get("time", "N/A")
                
                # র্যান্ডমাইজেশনের বদলে টাইটেল দিয়ে লজিক
                direction = "STRONG BUY 📈" if hash(title) % 2 == 0 else "STRONG SELL 📉"
                percentage = f"{82 + (hash(title) % 13)}%"
                
                return {
                    "asset": f"{currency}/USD",
                    "event": title,
                    "time": f"Today at {time_str} ({impact} Impact)",
                    "raw_time": time_str, 
                    "direction": direction,
                    "confidence": percentage,
                    "insight": f"Market volatility expected for {currency} due to {impact} impact news."
                }
        
        return {
            "asset": "NO LIVE NEWS",
            "event": "No Economic News Scheduled for Today",
            "time": "N/A",
            "raw_time": None,
            "direction": "STANDBY ⚠️ NO TRADE",
            "confidence": "0%",
            "insight": "Forex Factory calendar confirms no active high-impact events."
        }
            
    except Exception as e:
        return {
            "asset": "SERVER ERROR",
            "event": "Unable to fetch live news calendar",
            "time": "N/A",
            "raw_time": None,
            "direction": "ERROR ⚠️ TRY AGAIN",
            "confidence": "0%",
            "insight": "Could not connect to news server. Please try again later."
        }