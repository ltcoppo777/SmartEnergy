# Smart Energy Optimizer - Quick Start Guide

## First Time Setup

### 1. Install Node.js dependencies (root + frontend)
```bash
npm install
```

### 2. Install Python dependencies (backend)
```bash
cd backend
pip install -r requirements.txt
cd ..
```

OR use the combined install command:
```bash
npm run install:all
```

## Running the System

### Option 1: Run Backend + Frontend (Development)
```bash
npm run dev
```
- Backend API: http://localhost:8000
- Frontend UI: http://localhost:5173
- API Docs: http://localhost:8000/docs

### Option 2: Run Everything Including ML Training
```bash
npm run start:with-train
```
This will:
1. Start the FastAPI backend on port 8000
2. Start the React frontend on port 5173
3. Train the ML agent with preferences

### Option 3: Train ML Agent Only
```bash
npm run train:agent
```

## Manual Start (Without npm scripts)

### Terminal 1 - Backend
```bash
cd backend
python run.py
```

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

### Terminal 3 - Train ML Agent
```bash
python train_agent_with_preferences.py
```

## Troubleshooting

### Port Already in Use
- Backend (8000): Check if another process is using port 8000
- Frontend (5173): Vite will automatically try the next available port

### Python Dependencies
Make sure you have Python 3.8+ installed:
```bash
python --version
```

### Node Dependencies
Make sure you have Node.js 16+ installed:
```bash
node --version
```

## How the Optimization Works

### Comfort Score Algorithm (0-10 Scale) - Three-Tier Architecture

The system calculates comfort by stacking three independent layers:

**Tier 1 - Cost Efficiency (Foundation, 0-10)**
- Measures how well the schedule uses cheap electricity hours
- `cost_score = 5 + (avg_day_price - avg_schedule_price) / price_range × 5`
- High cost_score = schedule runs during cheap hours
- Low cost_score = schedule runs during expensive hours
- **Works even with NO user preferences**

**Tier 2 - Avoid Hours Adjustment (Penalty Layer)**
- Only applied if user sets avoid hours
- `penalty = -(violation_rate × preference_strength × 2.0)`
- Each 100% violation costs up to 6 points (with preference_strength=3)
- Zero violations = zero penalty

**Tier 3 - Preferred Hours Bonus (Incentive Layer)**
- Only applied if user sets preferred hours
- `bonus = (preferred_coverage × preference_strength × 5.0)`
- Each 100% coverage in preferred hours adds up to 5 points
- Zero coverage = zero bonus

**Final Score** (0-10):
```
comfort = cost_score + avoid_penalty + preferred_bonus
comfort = clamp(comfort, 0, 10)
```

**Key Improvement**: Score varies 0-10 even WITHOUT user preferences (based purely on cost efficiency)

### Agent Optimization Process

The trained ML agent (PPO Reinforcement Learning) generates optimized schedules by:

1. **Input**: Electricity prices ($/kWh) for each hour, appliances (power × duration), avoid hours, preferences
2. **Optimization**: Agent learns to maximize comfort while minimizing cost
3. **Output**: Schedule showing which appliances run at each hour

**Example**: 
- Dishwasher: 1.5 kW × 2 hours
- Price at 2-4 AM: $0.12/kWh (low)
- Price at 5-7 PM: $0.25/kWh (high)
- **Agent Decision**: Schedule at 2-4 AM → saves $0.39 + high comfort

## Project Structure
```
SmartEnergy-1/
├── backend/           # FastAPI backend with ML models
├── frontend/          # React + Tailwind frontend
├── train_agent_with_preferences.py  # ML training script
└── package.json       # Root package with run scripts
```
