from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from database import get_db, ApplianceUsage

router = APIRouter()

class ApplianceInput(BaseModel):
    appliance_name: str
    power_kw: float
    start_time: int
    duration_hours: float

class ApplianceResponse(BaseModel):
    id: int
    appliance_name: str
    power_kw: float
    start_time: int
    duration_hours: float

@router.post("/appliances")
async def save_appliances(appliances: List[ApplianceInput], db: Session = Depends(get_db)):
    try:
        db.query(ApplianceUsage).delete()
        
        for appliance in appliances:
            db_appliance = ApplianceUsage(
                appliance_name=appliance.appliance_name,
                power_kw=appliance.power_kw,
                start_time=appliance.start_time,
                duration_hours=appliance.duration_hours,
                user_id="default_user"
            )
            db.add(db_appliance)
        
        db.commit()
        return {"status": "success", "count": len(appliances)}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving appliances: {str(e)}")

@router.get("/appliances", response_model=List[ApplianceResponse])
async def get_appliances(db: Session = Depends(get_db)):
    try:
        appliances = db.query(ApplianceUsage).filter(
            ApplianceUsage.user_id == "default_user"
        ).all()
        return appliances
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving appliances: {str(e)}")
