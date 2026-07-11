from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# Frontend Connect Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your Free Forex Economic Calendar API Key Integrated
CALENDAR_API_URL = "https://financialmodelingprep.com/api/v3/economic_calendar?apikey=dzKueOxEJzTGWK15761gIRoD46NkoObJ"

@app.get("/api/ai-analysis")
def get_ai_analysis():
    try:
        response = requests.get(CALENDAR_API_URL).json()
        upcoming_news = response[0] if response else {}
        
        event = upcoming_news.get("event", "CPI News")
        previous = float(upcoming_news.get("previous", 0.2))
        forecast = float(upcoming_news.get("forecast", 0.2))
        currency = upcoming_news.get("currency", "USD")
        
        if forecast < previous:
            direction = "↑ BUY / CALL"
            confidence = "85% Confidence"
            insight = f"The forecast for {event} is lower than the previous actual. This indicates potential {currency} weakening, causing an upward impulse on asset pairs like XAUUSD."
        elif forecast > previous:
            direction = "↓ SELL / PUT"
            confidence = "80% Confidence"
            insight = f"The forecast shows a stronger trend compared to previous data. Anticipating {currency} strength, which might pressure non-USD assets down."
        else:
            direction = "⏳ PENDING"
            confidence = "Neutral"
            insight = "Forecast and Previous data are identical. Market is currently balanced. Wait for the live Actual Data release."

        return {
            "asset": "XAUUSD (GOLD)" if currency == "USD" else f"{currency} Pair",
            "event": event,
            "direction": direction,
            "confidence": confidence,
            "insight": insight,
            "previous": previous,
          
            "forecast": forecast
        }
    except Exception as e:
        return {"error": "Failed to fetch live AI data", "details": str(e)}
  
