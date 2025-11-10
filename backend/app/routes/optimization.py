from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from database import get_db
from app.services.energy_agent_service import EnergyAgentService

router = APIRouter()
agent_service = EnergyAgentService()

class OptimizationRequest(BaseModel):
    prices: List[float]
    appliances: List[Dict]
    avoid_hours: List[int] = []
    preferences: Dict = {}

class OptimizationResult(BaseModel):
    schedule: Dict[str, List[int]]
    total_cost: float
    comfort_score: float
    model_type: str
    advice: Optional[str] = None
    advice_type: Optional[str] = None

@router.post("/optimize-lp")
async def optimize_lp(request: OptimizationRequest, db: Session = Depends(get_db)):
    """Run Linear Programming optimizer"""
    try:
        from optimizer import optimize_schedule_lp
        from train_agent_with_preferences import calculate_comfort_score
        
        schedule, total_cost = optimize_schedule_lp(
            request.prices, 
            request.appliances, 
            request.avoid_hours
        )
        
        comfort_score = calculate_comfort_score(schedule, request.preferences, request.prices, request.appliances)
        
        lp_advice = f"""Linear Programming finds the mathematically optimal schedule based on current electricity prices. 
Your schedule:
- Total Cost: ${total_cost:.2f}
- Respects all avoid hours constraints
- Minimizes cost using price forecasts"""
        
        return OptimizationResult(
            schedule=schedule,
            total_cost=round(total_cost, 4),
            comfort_score=round(comfort_score, 2),
            model_type="Linear Programming (LP)",
            advice=lp_advice,
            advice_type="lp"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LP optimization failed: {str(e)}")

@router.post("/optimize-rl")
async def optimize_rl(request: OptimizationRequest, db: Session = Depends(get_db)):
    """Run RL (PPO) optimizer"""
    try:
        result = agent_service.optimize_with_preferences(
            request.prices,
            request.appliances,
            request.avoid_hours,
            request.preferences
        )
        
        rl_advice = f"""Reinforcement Learning agent learned from your preferences and constraints.
Your optimized schedule:
- Total Cost: ${result['total_cost']:.2f}
- Respects all avoid hours
- Adapts to maximize savings while maintaining comfort
- Gets better with more training on your patterns"""
        
        return OptimizationResult(
            schedule=result['schedule'],
            total_cost=round(result['total_cost'], 4),
            comfort_score=round(result['comfort_score'], 2),
            model_type="Reinforcement Learning (RL/PPO)",
            advice=rl_advice,
            advice_type="rl"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RL optimization failed: {str(e)}")
