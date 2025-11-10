from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import pandas as pd
import os
import sys
from pathlib import Path
from ..services.optimization_service import OptimizationService

root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from database import get_db, ApplianceUsage, PriceHistory

router = APIRouter()
optimization_service = OptimizationService()

@router.get("/analyze")
async def get_energy_analysis(db: Session = Depends(get_db)):
    """
    Get current energy consumption analysis and cost breakdown based on user input
    """
    try:
        appliances = db.query(ApplianceUsage).filter(
            ApplianceUsage.user_id == "default_user"
        ).all()
        
        prices = db.query(PriceHistory).all()
        
        if not prices:
            raise HTTPException(status_code=400, detail="No price data available. Fetch live prices first.")
        
        if not appliances:
            return {
                "summary": {
                    "total_power_kw": 0,
                    "estimated_daily_usage_kwh": 0,
                    "estimated_daily_cost": 0,
                    "average_price_per_kwh": 0
                },
                "appliance_breakdown": [],
                "peak_hours": []
            }
        
        price_df = pd.DataFrame([
            {"time": p.time, "price": p.price} for p in prices
        ])
        
        total_power_kw = sum(app.power_kw for app in appliances)
        total_daily_usage_kwh = 0
        total_daily_cost = 0
        all_prices_used = []
        
        appliance_breakdown = []
        for appliance in appliances:
            start_hour = appliance.start_time
            duration = appliance.duration_hours
            power = appliance.power_kw
            
            appliance_cost = 0
            appliance_usage = 0
            
            for hour_offset in range(int(duration) + 1):
                hour_idx = (start_hour + hour_offset) % 24
                
                matching_prices = price_df[price_df['time'].str.contains(f"{hour_idx:02d}:", na=False)]
                
                if len(matching_prices) > 0:
                    price_at_hour = matching_prices['price'].iloc[0]
                else:
                    price_at_hour = price_df['price'].mean()
                
                if hour_offset < int(duration):
                    hour_usage = power
                else:
                    hour_usage = power * (duration % 1)
                
                appliance_usage += hour_usage
                appliance_cost += hour_usage * price_at_hour
                all_prices_used.append(price_at_hour)
            
            total_daily_usage_kwh += appliance_usage
            total_daily_cost += appliance_cost
            
            appliance_breakdown.append({
                "name": appliance.appliance_name,
                "power": round(power, 2),
                "duration": round(duration, 2),
                "start_time": f"{appliance.start_time:02d}:00",
                "estimated_cost": round(appliance_cost, 4)
            })
        
        avg_price = sum(all_prices_used) / len(all_prices_used) if all_prices_used else price_df['price'].mean()
        
        return {
            "summary": {
                "total_power_kw": round(total_power_kw, 2),
                "estimated_daily_usage_kwh": round(total_daily_usage_kwh, 2),
                "estimated_daily_cost": round(total_daily_cost, 2),
                "average_price_per_kwh": round(avg_price, 4)
            },
            "appliance_breakdown": appliance_breakdown,
            "peak_hours": optimization_service.identify_peak_hours(price_df)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")