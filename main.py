from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from datetime import datetime
import pytz

app = FastAPI(title="Titan AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

SECRET_PASSWORD = "NTXORHN"

CABLE_API_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"


class PasswordRequest(BaseModel):
    password: str


@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Titan AI Backend Running Successfully"
    }


@app.post("/api/verify-pass")
def verify(req: PasswordRequest):

    if req.password == SECRET_PASSWORD:
        return {
            "status": "success"
        }

    return {
        "status": "failed",
        "error": "Wrong Password"
    }


PAIR_MAP = {
    "USD": "EUR/USD",
    "EUR": "EUR/USD",
    "GBP": "GBP/USD",
    "JPY": "USD/JPY",
    "AUD": "AUD/USD",
    "NZD": "NZD/USD",
    "CAD": "USD/CAD",
    "CHF": "USD/CHF"
}
@app.post("/api/ai-analysis")
def get_ai_analysis(req: PasswordRequest):

    if req.password != SECRET_PASSWORD:
        return {
            "error": "Unauthorized Access!"
        }

    try:

        response = requests.get(CABLE_API_URL, timeout=10)

        if response.status_code != 200:
            raise Exception("API Error")

        all_news = response.json()

        tz = pytz.timezone("Asia/Dhaka")
        now = datetime.now(tz)

        today1 = now.strftime("%m-%d-%Y")
        today2 = now.strftime("%Y-%m-%d")
        today3 = now.strftime("%b %d")
        weekday = now.strftime("%A").lower()
todays_news = []

for news in all_news:

    impact = str(news.get("impact", "")).lower()

    date_text = str(news.get("date", "")).lower()

    time_text = str(news.get("time", "")).lower()

    # আজকের নিউজ
    if (
        today1.lower() in date_text
        or today2.lower() in date_text
        or today3.lower() in date_text
        or weekday in date_text
    ):
        todays_news.append(news)
        continue

    # API যদি date না দেয় কিন্তু time দেয়
    if impact in ["high", "medium"] and time_text not in ["", "n/a", "all day"]:
        todays_news.append(news)

# Duplicate remove
unique = []
titles = set()

for news in todays_news:

    title = str(news.get("title", "")).strip()

    if title not in titles:
        titles.add(title)
        unique.append(news)

todays_news = unique

# Backup
if len(todays_news) == 0:

    todays_news = [
        n for n in all_news
        if str(n.get("impact", "")).lower() == "high"
    ]

if len(todays_news) == 0:

    todays_news = [
        n for n in all_news
        if str(n.get("impact", "")).lower() == "medium"
    ]
        
        if len(todays_news) == 0:

            return {
                "asset": "NO LIVE NEWS",
                "event": "No High Impact News",
                "time": "N/A",
                "raw_time": None,
                "direction": "STANDBY ⚠️",
                "confidence": "0%",
                "insight": "No major economic news found."
            }

        high = [n for n in todays_news if n.get("impact") == "High"]

        medium = [n for n in todays_news if n.get("impact") == "Medium"]

        if high:
            selected = high[0]
        elif medium:
            selected = medium[0]
        else:
            selected = todays_news[0]

        title = selected.get("title", "Economic News")

        currency = (
            selected.get("currency")
            or selected.get("country")
            or "USD"
        )

        impact = selected.get("impact", "High")

        time_str = selected.get("time")

        if not time_str:
            time_str = "N/A"

        asset = PAIR_MAP.get(currency, "EUR/USD")
                # Stable Direction Logic
        title_lower = title.lower()

        buy_words = [
            "gdp",
            "employment",
            "payroll",
            "retail sales",
            "manufacturing",
            "services pmi",
            "interest rate",
            "cpi"
        ]

        sell_words = [
            "unemployment",
            "jobless",
            "claims",
            "recession",
            "housing",
            "consumer confidence"
        ]

        score = sum(word in title_lower for word in buy_words) - \
                sum(word in title_lower for word in sell_words)

        if score >= 1:
            direction = "STRONG BUY 📈"
            confidence = "91%"
        elif score <= -1:
            direction = "STRONG SELL 📉"
            confidence = "91%"
        else:
            # Stable fallback (Python hash() ব্যবহার না করে)
            if sum(ord(c) for c in title) % 2 == 0:
                direction = "BUY 📈"
            else:
                direction = "SELL 📉"

            confidence = "84%"

        return {
            "asset": asset,
            "event": title,
            "time": f"Today at {time_str} ({impact} Impact)",
            "raw_time": time_str,
            "direction": direction,
            "confidence": confidence,
            "insight": f"{impact} impact economic news detected for {currency}. Trade carefully because volatility may increase."
        }

    except Exception as e:

        return {
            "asset": "SERVER ERROR",
            "event": str(e),
            "time": "N/A",
            "raw_time": None,
            "direction": "ERROR ⚠️",
            "confidence": "0%",
            "insight": "Unable to connect to the news server. Please try again in a few moments."
        }
def get_best_news(news_list):

    high = []
    medium = []
    low = []

    for news in news_list:

        impact = str(news.get("impact", "")).lower()

selected = get_best_news(todays_news)

if selected is None:

    return {
        "asset": "NO LIVE NEWS",
        "event": "No News Found",
        "time": "N/A",
        "raw_time": None,
        "direction": "WAIT",
        "confidence": "0%",
        "insight": "No economic event available."
    }
        
    priority_keywords = [
        "Non-Farm",
        "NFP",
        "CPI",
        "Core CPI",
        "FOMC",
        "Interest Rate",
        "Federal Funds Rate",
        "PPI",
        "GDP",
        "Retail Sales",
        "Unemployment",
        "PMI",
        "CPI m/m",
        "Core CPI m/m"
    ]

    if high:

        for key in priority_keywords:

            for item in high:

                title = str(item.get("title", ""))

                if key.lower() in title.lower():
                    return item

        return high[0]

    if medium:
        return medium[0]

    if low:
        return low[0]

    return None
    def get_currency(news):

    currency = get_currency(selected)
    
    currency = str(currency).upper()

    if "USD" in currency or "UNITED STATES" in currency:
        return "USD"

    if "EUR" in currency or "EURO" in currency:
        return "EUR"

    if "GBP" in currency or "UNITED KINGDOM" in currency:
        return "GBP"

    if "JPY" in currency or "JAPAN" in currency:
        return "JPY"

    if "AUD" in currency or "AUSTRALIA" in currency:
        return "AUD"

    if "NZD" in currency or "NEW ZEALAND" in currency:
        return "NZD"

    if "CAD" in currency or "CANADA" in currency:
        return "CAD"

    if "CHF" in currency or "SWITZERLAND" in currency:
        return "CHF"

    return "USD"
    