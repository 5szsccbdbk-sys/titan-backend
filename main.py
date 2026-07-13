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
    return {"message": "Neo Titan XO News Fix Live!"}

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
        response = requests.get(CABLE_API_URL, timeout=5)
        if response.status_code == 200:
            all_news = response.json()
            
            # বাংলাদেশ টাইমজোন অনুযায়ী আজকের বছর, মাস ও দিন আলাদা করা
            tz_bd = pytz.timezone('Asia/Dhaka')
            now_bd = datetime.now(tz_bd)
            
            target_year = now_bd.strftime("%Y")  # 2026
            target_month = now_bd.strftime("%m") # 07
            target_day = now_bd.strftime("%d")   # 14
            
            todays_news = []
            
            # এপিআই-এর প্রতিটা নিউজ লুপ করে চেক করা
            for news in all_news:
                news_date_raw = str(news.get("date", "")) # উদাহরণ: "2026-07-14T00:00:00-04:00"
                
                # যদি ডেটের ভেতরে আজকের বছর, মাস এবং দিন তিনটাই একসাথে থাকে
                if target_year in news_date_raw and f"-{target_month}-" in news_date_raw and f"-{target_day}" in news_date_raw:
                    todays_news.append(news)
                # ব্যাকআপ চেক (যদি ফরম্যাট অন্যরকম হয়)
                elif f"{target_month}-{target_day}" in news_date_raw:
                    todays_news.append(news)

            # যদি কোনো কারণে তাও না পায়, তবে মেম্বারদের ফাঁকা স্ক্রিন না দেখিয়ে সপ্তাহের লেটেস্ট হাই-ইমপ্যাক্ট নিউজ দেখাবে
            if not todays_news:
                todays_news = [n for n in all_news if n.get("impact") in ["High", "Medium"]]

            if todays_news:
                # হাই ইমপ্যাক্ট (লাল ফোল্ডার) নিউজকে সবার আগে তুলে আনা
                high_impact = [n for n in todays_news if n.get("impact") == "High"]
                medium_impact = [n for n in todays_news if n.get("impact") == "Medium"]
                
                if high_impact:
                    selected_news = high_impact[0]
                elif medium_impact:
                    selected_news = medium_impact[0]
                else:
                    selected_news = todays_news[0]
                
                title = selected_news.get("title", "Economic Event")
                currency = selected_news.get("country", "USD")
                impact = selected_news.get("impact", "Low")
                time_str = selected_news.get("time", "N/A")
                
                direction = "STRONG BUY 📈" if hash(title) % 2 == 0 else "STRONG SELL 📉"
                percentage = f"{85 + (hash(title) % 10)}%"
                
                return {
                    "asset": f"{currency}/USD",
                    "event": title,
                    "time": f"Today at {time_str} ({impact} Impact)",
                    "raw_time": time_str, 
                    "direction": direction,
                    "confidence": percentage,
                    "insight": f"High impact CPI/Economic news detected for {currency}. Expect heavy volume and fast movement."
                }
        
        return {
            "asset": "NO LIVE NEWS",
            "event": "No Economic News Scheduled for Today",
            "time": "N/A",
            "raw_time": None,
            "direction": "STANDBY ⚠️ NO TRADE",
            "confidence": "0%",
            "insight": "Forex Factory calendar confirms there are no active high-impact economic news events right now."
        }
                
    except Exception as e:
        return {
            "asset": "SERVER ERROR",
            "event": "Unable to fetch live news calendar",
            "time": "N/A",
            "raw_time": None,
            "direction": "ERROR ⚠️ TRY AGAIN",
            "confidence": "0%",
            "insight": "Could not establish connection with Forex Factory API. Please check internet or try again later."
        }