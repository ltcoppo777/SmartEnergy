from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from train_agent_with_preferences import train_agent_with_preferences
from app.services.energy_agent_service import EnergyAgentService

router = APIRouter()
training_status = {"is_training": False, "progress": ""}

class TrainingRequest(BaseModel):
    prices: List[float]
    appliances: List[Dict]
    avoid_hours: List[int] = []
    preferences: Dict = {}

class TrainingStatus(BaseModel):
    is_training: bool
    progress: str

@router.get("/training-status")
async def get_training_status():
    """Get current training status"""
    return TrainingStatus(
        is_training=training_status["is_training"],
        progress=training_status["progress"]
    )

@router.post("/train-agent")
async def train_agent(request: TrainingRequest, background_tasks: BackgroundTasks):
    """
    Train the ML agent with current preferences and save to .zip file
    """
    if training_status["is_training"]:
        raise HTTPException(status_code=400, detail="Training already in progress")
    
    try:
        training_status["is_training"] = True
        training_status["progress"] = "Initializing training..."
        
        def train_in_background():
            try:
                training_status["progress"] = "Building environment..."
                
                preferences = request.preferences or {}
                
                model = train_agent_with_preferences(
                    prices=request.prices,
                    appliances=request.appliances,
                    restricted_hours=request.avoid_hours,
                    preferences=preferences
                )
                
                training_status["progress"] = "Saving model..."
                
                models_dir = Path(__file__).parent.parent.parent / "models"
                models_dir.mkdir(exist_ok=True)
                model.save(str(models_dir / "energy_agent_preferences"))
                
                training_status["progress"] = "Reloading agent service..."
                agent_service = EnergyAgentService()
                agent_service.load_models()
                
                training_status["progress"] = "Training complete!"
                training_status["is_training"] = False
                
            except Exception as e:
                training_status["progress"] = f"Error: {str(e)}"
                training_status["is_training"] = False
        
        background_tasks.add_task(train_in_background)
        
        return {
            "status": "training_started",
            "message": "Agent training started in background"
        }
        
    except Exception as e:
        training_status["is_training"] = False
        raise HTTPException(status_code=500, detail=f"Training error: {str(e)}")
