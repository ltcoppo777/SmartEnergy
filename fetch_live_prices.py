# fetch_live_prices.py
import os
import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz


def fetch_comed_prices():
    """
    Fetches ComEd 5-minute real-time prices and aggregates them into hourly averages.
    Falls back to sample data if the API fails.
    """
    URL = "https://hourlypricing.comed.com/api?type=5minutefeed"
    headers = {"User-Agent": "Mozilla/5.0"}
    tz = pytz.timezone("America/Chicago")

    try:
        r = requests.get(URL, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()

        # Convert JSON to DataFrame
        df = pd.DataFrame(data)
        df["millisUTC"] = pd.to_numeric(df["millisUTC"], errors="coerce")
        df["price"] = pd.to_numeric(df["price"], errors="coerce")

        # Convert UTC → Chicago local time
        df["datetime"] = pd.to_datetime(df["millisUTC"], unit="ms", utc=True)
        df["datetime"] = df["datetime"].dt.tz_convert(tz)

        # Keep only recent data (past 36 hours)
        now = datetime.now(tz)
        window_start = now - timedelta(hours=36)
        df = df[df["datetime"] >= window_start]

        # Group by hour and average (¢/kWh → $/kWh)
        df["hour"] = df["datetime"].dt.floor("H")
        hourly = df.groupby("hour")["price"].mean().reset_index()
        hourly["price"] = hourly["price"] / 100.0  # convert cents to dollars
        hourly["time"] = hourly["hour"].dt.strftime("%I:%M %p")
        # Sort chronologically
        hourly = hourly.sort_values("hour").reset_index(drop=True)

        # Keep last 24 hours
        hourly = hourly.tail(24)

        os.makedirs("data", exist_ok=True)
        hourly[["time", "price"]].to_csv("data/prices.csv", index=False)

        print(f"✅ Saved {len(hourly)} hourly points from live ComEd feed.")
        return hourly[["time", "price"]]

    except Exception as e:
        print(f"⚠️ Could not fetch ComEd 5-minute feed: {e}")
        print("📊 Using sample data instead…")

        # Sample fallback data
        now = datetime.now(tz)
        hours, prices = [], []
        for i in range(24):
            t = now - timedelta(hours=23 - i)
            hours.append(t.strftime("%I:%M %p"))
            base = 0.05 + 0.03 * (0.5 - abs((t.hour - 12) / 12))  # mild daytime peak
            prices.append(round(base, 4))

        df = pd.DataFrame({"time": hours, "price": prices})
        os.makedirs("data", exist_ok=True)
        df.to_csv("data/prices.csv", index=False)
        return df


if __name__ == "__main__":
    df = fetch_comed_prices()
    print(df.head(10))
