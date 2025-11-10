from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from ..services.database_service import PreferenceService
from ..services.optimization_advice_service import OptimizationAdviceService
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from database import get_db

router = APIRouter()

class UserPreferences(BaseModel):
    avoid_hours: List[int] = []
    priority_appliances: List[str] = []

class ComfortCalculation(BaseModel):
    avoid_hours: List[int] = []

@router.post("/preferences")
async def save_preferences(preferences: UserPreferences, db: Session = Depends(get_db)):
    """
    Save user scheduling preferences to database and generate optimization advice
    """
    try:
        pref_dict = preferences.dict()
        PreferenceService.save_preferences(db, pref_dict)
        
        # Generate optimization advice based on avoid hours and current prices
        advice_data = OptimizationAdviceService.get_optimization_advice(
            db, 
            pref_dict.get("avoid_hours", [])
        )
        
        return {
            "message": "Preferences saved successfully",
            "status": "success",
            "data": pref_dict,
            "comfort_level": advice_data["comfort_level"],
            "advice": advice_data["advice"],
            "prices": advice_data["prices"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preferences save error: {str(e)}")

@router.get("/preferences")
async def get_preferences(db: Session = Depends(get_db)):
    """
    Get saved user preferences from database with calculated comfort level
    """
    try:
        preferences = PreferenceService.get_preferences(db)
        
        # Calculate comfort level based on avoid hours
        advice_data = OptimizationAdviceService.get_optimization_advice(
            db,
            preferences.get("avoid_hours", [])
        )
        
        return {
            "avoid_hours": preferences.get("avoid_hours", []),
            "priority_appliances": preferences.get("priority_appliances", []),
            "comfort_level": advice_data["comfort_level"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preferences load error: {str(e)}")

@router.post("/calculate-comfort")
async def calculate_comfort(data: ComfortCalculation, db: Session = Depends(get_db)):
    """
    Calculate comfort level and optimization advice based on avoid hours (real-time)
    """
    try:
        advice_data = OptimizationAdviceService.get_optimization_advice(
            db,
            data.avoid_hours
        )
        
        return {
            "comfort_level": advice_data["comfort_level"],
            "advice": advice_data["advice"],
            "prices": advice_data["prices"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comfort calculation error: {str(e)}")