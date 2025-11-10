import sys
from pathlib import Path
import numpy as np
from sqlalchemy.orm import Session

root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

from database import get_db
from train_agent import calculate_comfort_level, generate_optimization_advice
from .live_price_service import LivePriceService
from .database_service import PriceService


class OptimizationAdviceService:
    """Generate optimization advice based on user preferences and pricing"""
    
    @staticmethod
    def get_optimization_advice(db: Session, avoid_hours: list, appliances: list = None):
        """
        Generate optimization advice based on avoid hours and current prices.
        
        Args:
            db: Database session
            avoid_hours: List of hours to avoid (0-23)
            appliances: Optional list of appliances for better recommendations
            
        Returns:
            dict with comfort_level and optimization_advice
        """
        try:
            # Get current prices from database
            price_history = PriceService.get_all_prices(db)
            
            if not price_history:
                # Fallback to live prices
                price_service = LivePriceService()
                prices_df = price_service.fetch_live_prices()
                prices = prices_df['price'].tolist()
            else:
                # Use database prices (last 24 hours or available)
                prices = [p['price'] for p in price_history[-24:]]
                # Pad with zeros if less than 24 hours
                while len(prices) < 24:
                    prices = [prices[0]] + prices
            
            # Use sample appliances if not provided
            if not appliances:
                appliances = [
                    {"name": "Washer", "power": 0.5, "duration": 2},
                    {"name": "Dryer", "power": 2.5, "duration": 1},
                    {"name": "Dishwasher", "power": 1.2, "duration": 2}
                ]
            
            # Calculate comfort level
            comfort_level = calculate_comfort_level(prices, appliances, avoid_hours)
            
            # Generate sample schedule for advice (all appliances scheduled)
            schedule = {}
            for app in appliances:
                schedule[app["name"]] = "Optimized based on pricing"
            
            # Generate optimization advice
            advice = generate_optimization_advice(prices, appliances, avoid_hours, schedule)
            
            return {
                "comfort_level": comfort_level,
                "advice": advice,
                "prices": {
                    "current_range": f"${min(prices):.4f} - ${max(prices):.4f}",
                    "average": f"${np.mean(prices):.4f}"
                }
            }
            
        except Exception as e:
            raise Exception(f"Advice generation failed: {str(e)}")
