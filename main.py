from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import requests
import pytz

app = FastAPI(title="Neo Titan XO AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_PASSWORD = "NTXORHN"
NEWS_API = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"


class PasswordRequest(BaseModel):
    password: str


@app.get("/")
def home():
    return {
        "status": "online",
        "message": "Neo Titan XO Backend Running"
    }


@app.post("/api/verify-pass")
def verify(req: PasswordRequest):

    if req.password == SECRET_PASSWORD:
        return {"status": "success"}

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


def get_currency(news):

    currency = (
        news.get("currency")
        or news.get("country")
        or "USD"
    )

    currency = str(currency).upper()

    if "UNITED STATES" in currency:
        return "USD"

    if "EURO" in currency:
        return "EUR"

    if "UNITED KINGDOM" in currency:
        return "GBP"

    if "JAPAN" in currency:
        return "JPY"

    if "AUSTRALIA" in currency:
        return "AUD"

    if "NEW ZEALAND" in currency:
        return "NZD"

    if "CANADA" in currency:
        return "CAD"

    if "SWITZERLAND" in currency:
        return "CHF"

    return currency
def get_best_news(news_list):

    if not news_list:
        return None

    priority = [
        "Core CPI",
        "CPI",
        "Non-Farm",
        "NFP",
        "FOMC",
        "Federal Funds Rate",
        "Interest Rate",
        "GDP",
        "PPI",
        "Retail Sales",
        "PMI",
        "Employment",
        "Unemployment"
    ]

    high = []
    medium = []
    low = []

    for news in news_list:

        impact = str(news.get("impact", "")).lower()

        if impact == "high":
            high.append(news)

        elif impact == "medium":
            medium.append(news)

        else:
            low.append(news)

    for keyword in priority:

        for item in high:

            title = str(item.get("title", ""))

            if keyword.lower() in title.lower():
                return item

    if high:
        return high[0]

    if medium:
        return medium[0]

    if low:
        return low[0]

    return None


@app.post("/api/ai-analysis")
def get_ai_analysis(req: PasswordRequest):

    if req.password != SECRET_PASSWORD:
        return {
            "error": "Unauthorized Access"
        }

    try:

        response = requests.get(NEWS_API, timeout=10)

        if response.status_code != 200:
            raise Exception("News API Offline")

        all_news = response.json()

        tz = pytz.timezone("Asia/Dhaka")
        now = datetime.now(tz)

        today1 = now.strftime("%m-%d-%Y")
        today2 = now.strftime("%Y-%m-%d")
        today3 = now.strftime("%b %d").lower()
        weekday = now.strftime("%A").lower()

        todays_news = []

        for news in all_news:

            date_text = str(news.get("date", "")).lower()
            time_text = str(news.get("time", "")).lower()
            impact = str(news.get("impact", "")).lower()

            if (
                today1.lower() in date_text
                or today2.lower() in date_text
                or today3 in date_text
                or weekday in date_text
            ):
                todays_news.append(news)
                continue

            if impact in ["high", "medium"] and time_text not in ["", "n/a"]:
                todays_news.append(news)

        unique = []
        seen = set()

        for news in todays_news:

            title = str(news.get("title", "")).strip()

            if title not in seen:
                seen.add(title)
                unique.append(news)

        todays_news = unique

        selected = get_best_news(todays_news)

        if selected is None:

            return {
                "asset": "NO LIVE NEWS",
                "event": "No Important News Today",
                "time": "N/A",
                "raw_time": None,
                "direction": "WAIT",
                "confidence": "0%",
                "insight": "No High Impact Economic News Found."
            }
        title = selected.get("title", "Economic News")

        currency = get_currency(selected)

        impact = selected.get("impact", "High")

        time_str = selected.get("time")

        if not time_str:
            time_str = "N/A"

        asset = PAIR_MAP.get(currency, "EUR/USD")

        title_lower = title.lower()

        if any(word in title_lower for word in [
            "cpi",
            "core cpi",
            "ppi",
            "interest rate",
            "fomc",
            "federal funds",
            "nfp",
            "non-farm payroll"
        ]):
            direction = "HIGH VOLATILITY ⚠️"
            confidence = "95%"

        elif any(word in title_lower for word in [
            "gdp",
            "retail sales",
            "employment",
            "pmi"
        ]):
            direction = "BUY 📈"
            confidence = "90%"

        elif any(word in title_lower for word in [
            "unemployment",
            "jobless",
            "claims"
        ]):
            direction = "SELL 📉"
            confidence = "90%"

        else:
            direction = "WAIT ⏳"
            confidence = "80%"

        return {
            "asset": asset,
            "event": title,
            "time": f"Today at {time_str} ({impact} Impact)",
            "raw_time": time_str,
            "direction": direction,
            "confidence": confidence,
            "insight": f"{impact} impact economic news detected for {currency}. Trade carefully and wait for confirmation after the news release."
        }

    except Exception as e:

        return {
            "asset": "SERVER ERROR",
            "event": "Unable to fetch live news",
            "time": "N/A",
            "raw_time": None,
            "direction": "ERROR ⚠️",
            "confidence": "0%",
            "insight": str(e)
        }
