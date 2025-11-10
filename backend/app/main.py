from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import analysis, optimization, preferences, prices, appliances, chatbot, training
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from database import init_db

app = FastAPI(
    title="AI Energy Optimizer API",
    description="Smart energy management with reinforcement learning",
    version="1.0.0"
)

init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router, prefix="/api", tags=["analysis"])
app.include_router(optimization.router, prefix="/api", tags=["optimization"])
app.include_router(preferences.router, prefix="/api", tags=["preferences"])
app.include_router(prices.router, prefix="/api", tags=["prices"])
app.include_router(appliances.router, prefix="/api", tags=["appliances"])
app.include_router(chatbot.router, prefix="/api", tags=["chatbot"])
app.include_router(training.router, prefix="/api", tags=["training"])

@app.get("/")
async def root():
    return {"message": "AI Energy Optimizer API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "energy-optimizer"}