from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

# CORS Middleware সেটিংস
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_PASSWORD = "NTXORHN"
# Forex Factory API Link
CABLE_API_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

class PasswordRequest(BaseModel):
    password: str

@app.get("/")
def read_root():
    return {"message": "Neo Titan XO Backend is Online!"}

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
        # API থেকে নিউজ ডাটা আনা
        response = requests.get(CABLE_API_URL, timeout=10)
        if response.status_code == 200:
            all_news = response.json()
            
            # সব নিউজ থেকে শুধু 'High' ইমপ্যাক্ট নিউজ ফিল্টার করা
            high_impact_news = [n for n in all_news if n.get("impact") == "High"]
            
            if high_impact_news:
                # সবচেয়ে সাম্প্রতিক নিউজটি নেওয়া
                selected_news = high_impact_news[0]
                
                title = selected_news.get("title", "Economic Event")
                currency = selected_news.get("country", "USD")
                impact = selected_news.get("impact", "High")
                time_str = selected_news.get("time", "N/A")
                
                # সিগন্যাল লজিক
                direction = "STRONG BUY 📈" if hash(title) % 2 == 0 else "STRONG SELL 📉"
                percentage = f"{82 + (hash(title) % 13)}%"
                
                return {
                    "asset": f"{currency}/USD",
                    "event": title,
                    "time": f"{time_str} ({impact} Impact)",
                    "raw_time": time_str, 
                    "direction": direction,
                    "confidence": percentage,
                    "insight": f"High impact event: {title}. Expect major movement in {currency} pairs."
                }
        
        # নিউজ না থাকলে ডিফল্ট রেসপন্স
        return {
            "asset": "MARKET STABLE",
            "event": "No High Impact News Currently",
            "time": "N/A",
            "raw_time": None,
            "direction": "WAITING ⏳",
            "confidence": "0%",
            "insight": "Currently no high-impact economic events on the calendar."
        }
            
    except Exception as e:
        return {"error": "Server error while fetching news"}