from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..services.live_price_service import LivePriceService
from ..services.database_service import PriceService
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from database import get_db

router = APIRouter()
price_service = LivePriceService()

@router.get("/live-prices")
async def get_live_prices(db: Session = Depends(get_db)):
    """
    Get real-time electricity prices from database or fetch from API
    """
    try:
        prices_data = price_service.fetch_live_prices()
        
        PriceService.save_prices(db, prices_data)
        
        return {
            "prices": prices_data['price'].tolist(),
            "times": prices_data['time'].tolist(),
            "min_price": float(prices_data['price'].min()),
            "max_price": float(prices_data['price'].max()),
            "avg_price": float(prices_data['price'].mean())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Price fetch error: {str(e)}")

@router.get("/price-trends")
async def get_price_trends(db: Session = Depends(get_db)):
    """
    Get price trends and patterns
    """
    try:
        trends = price_service.analyze_price_trends()
        peak_hours = PriceService.get_peak_hours(db)
        
        return {
            **trends,
            "peak_hours_db": peak_hours
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analysis error: {str(e)}")

@router.get("/price-history")
async def get_price_history(db: Session = Depends(get_db)):
    """
    Get historical price data
    """
    try:
        history = PriceService.get_all_prices(db)
        if history:
            prices = [h['price'] for h in history]
            return {
                "history": history,
                "min_price": min(prices),
                "max_price": max(prices),
                "avg_price": sum(prices) / len(prices)
            }
        else:
            return {"history": [], "message": "No price history available"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Price history error: {str(e)}")