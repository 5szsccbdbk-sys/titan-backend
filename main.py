from flask import Flask, jsonify
import requests
import pandas as pd

from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from ta.volatility import BollingerBands, AverageTrueRange

app = Flask(__name__)

@app.route("/api/analysis")
def analysis():
    try:
        url = "https://api.binance.com/api/v3/klines"

        params = {
            "symbol": "BTCUSDT",
            "interval": "1m",
            "limit": 200
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        df = pd.DataFrame(data, columns=[
            "time","open","high","low","close","volume",
            "close_time","quote_asset_volume","trades",
            "taker_buy_base","taker_buy_quote","ignore"
        ])

        for col in ["open","high","low","close","volume"]:
            df[col] = df[col].astype(float)

        # ================= Indicators =================

        rsi = RSIIndicator(df["close"], window=14).rsi().iloc[-1]

        ema9 = EMAIndicator(df["close"], window=9).ema_indicator().iloc[-1]
        ema21 = EMAIndicator(df["close"], window=21).ema_indicator().iloc[-1]

        macd = MACD(df["close"])
        macd_line = macd.macd().iloc[-1]
        macd_signal = macd.macd_signal().iloc[-1]

        bb = BollingerBands(df["close"], window=20)
        bb_upper = bb.bollinger_hband().iloc[-1]
        bb_lower = bb.bollinger_lband().iloc[-1]

        atr = AverageTrueRange(
            high=df["high"],
            low=df["low"],
            close=df["close"],
            window=14
        ).average_true_range().iloc[-1]

        price = df["close"].iloc[-1]

        # ================= Signal Logic =================

        score = 0

        if rsi < 30:
            score += 1
        elif rsi > 70:
            score -= 1

        if ema9 > ema21:
            score += 1
        else:
            score -= 1

        if macd_line > macd_signal:
            score += 1
        else:
            score -= 1

        if price < bb_lower:
            score += 1
        elif price > bb_upper:
            score -= 1

        if score >= 3:
            signal = "BUY"
        elif score <= -3:
            signal = "SELL"
        else:
            signal = "WAIT"

        return jsonify({
            "Market": "BTCUSDT",
            "Price": round(price, 2),

            "Indicators": {
                "RSI": round(float(rsi), 2),
                "EMA9": round(float(ema9), 2),
                "EMA21": round(float(ema21), 2),
                "MACD": round(float(macd_line), 4),
                "MACD_SIGNAL": round(float(macd_signal), 4),
                "BB_UPPER": round(float(bb_upper), 2),
                "BB_LOWER": round(float(bb_lower), 2),
                "ATR": round(float(atr), 2)
            },

            "Signal": signal,
            "Score": score
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)