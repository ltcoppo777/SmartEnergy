import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from fetch_live_prices import fetch_comed_prices


class LivePriceService:
    @staticmethod
    def fetch_live_prices():
        """
        Fetch live electricity prices from ComEd API
        Returns a pandas DataFrame with 'time' and 'price' columns
        """
        return fetch_comed_prices()
    
    @staticmethod
    def analyze_price_trends():
        """
        Analyze price trends from current data
        """
        try:
            df = fetch_comed_prices()
            if df.empty:
                return {
                    "trend": "stable",
                    "min_price": 0,
                    "max_price": 0,
                    "avg_price": 0
                }
            
            prices = df['price'].values
            return {
                "trend": "increasing" if prices[-1] > prices[0] else "decreasing",
                "min_price": float(df['price'].min()),
                "max_price": float(df['price'].max()),
                "avg_price": float(df['price'].mean()),
                "current_price": float(prices[-1]) if len(prices) > 0 else 0
            }
        except Exception as e:
            print(f"Error analyzing price trends: {e}")
            return {
                "trend": "error",
                "min_price": 0,
                "max_price": 0,
                "avg_price": 0,
                "error": str(e)
            }
