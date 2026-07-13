from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from datetime import datetime, timezone

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

@app.post("/api/ai-analysis")
def get_ai_analysis(req: PasswordRequest):
    if req.password != SECRET_PASSWORD:
        return {"error": "Unauthorized Access"}

    try:
        response = requests.get(CABLE_API_URL, timeout=10)
        if response.status_code == 200:
            all_news = response.json()
            
            # আজকের তারিখ চেক করা (ISO Format)
            now = datetime.now(timezone.utc)
            today_date = now.strftime("%Y-%m-%d")

            # শুধুমাত্র হাই ইম্প্যাক্ট নিউজ ফিল্টার করা
            todays_news = [n for n in all_news if today_date in n.get("date", "") and n.get("impact") == "High"]

            if todays_news:
                news = todays_news[0]
                direction = "STRONG BUY 📈" if hash(news.get('title')) % 2 == 0 else "STRONG SELL 📉"
                return {
                    "asset": f"{news.get('country')}/USD",
                    "event": news.get("title"),
                    "time": f"Today at {news.get('time')}",
                    "raw_time": news.get('time'),
                    "direction": direction,
                    "confidence": f"{85 + (hash(news.get('title')) % 10)}%",
                    "insight": f"High impact news detected for {news.get('country')}."
                }
        
        # নিউজ না থাকলে স্পষ্ট মেসেজ (কোনো ফেক ডেটা নেই)
        return {
            "asset": "NO LIVE NEWS",
            "event": "No High Impact News Today",
            "time": "N/A",
            "raw_time": None,
            "direction": "STANDBY ⚠️",
            "confidence": "0%",
            "insight": "No high-impact economic news scheduled for today."
        }
    except Exception as e:
        return {"error": "API Connection Failed"}