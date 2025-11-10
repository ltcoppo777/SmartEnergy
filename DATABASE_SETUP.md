# SmartEnergy Database Setup

## Overview
The system now uses **SQLite** to persist user preferences and price history data. This enables:
- Persistent storage of user preferences across sessions
- Historical price data tracking
- Better data management and retrieval

## Database Structure

### Tables Created

#### 1. **user_preferences**
Stores user comfort settings and scheduling preferences:
- `id` - Primary key
- `user_id` - User identifier (default: "default_user")
- `comfort_level` - Comfort vs. cost priority (1-10)
- `avoid_hours` - Hours when appliances shouldn't run
- `preferred_operating_hours` - Appliance-specific preferred hours
- `priority_appliances` - High-priority appliances
- `max_concurrent_appliances` - Max appliances to run simultaneously
- `created_at` - Record creation timestamp
- `updated_at` - Last update timestamp

#### 2. **price_history**
Tracks electricity price data:
- `id` - Primary key
- `time` - Time of the price
- `price` - Price in $/kWh
- `timestamp` - When price was recorded
- `source` - Price source (ComEd)

#### 3. **optimization_results**
Stores optimization run results:
- `id` - Primary key
- `user_id` - User who ran optimization
- `appliances` - Appliance configuration (JSON)
- `schedule` - Recommended schedule (JSON)
- `total_cost` - Calculated cost
- `comfort_score` - Comfort satisfaction score
- `optimization_type` - "lp" or "rl"
- `created_at` - When optimization ran

## New API Endpoints

### Preferences
- **GET /api/preferences** - Retrieve user preferences from database
- **POST /api/preferences** - Save user preferences to database

### Prices
- **GET /api/live-prices** - Get current prices (auto-saves to DB)
- **GET /api/price-history** - Get historical price data from database
- **GET /api/price-trends** - Get price trend analysis

## Frontend Components Updated

### LivePriceCard
- Now displays Min/Avg/Max prices from database
- Shows real-time data with database backing
- Auto-refreshes every 5 minutes

### PriceHistory (NEW)
- New component to display price trends
- Table view of historical prices
- Visual indicators for price levels (low/medium/high)
- Statistics: min, max, average prices

### PreferencesForm
- Now uses database API instead of local JSON
- Shows loading states
- Displays success/error messages
- Preferences persist across browser sessions

## How to Use

### Start the Backend
```bash
python start_backend.py
```

### Initialize Database (Auto)
Database is automatically created on first backend startup in `backend/energy_optimizer.db`

### Access the Frontend
```bash
cd frontend
npm install
npm run dev
```

## Database Operations

### Service Classes

**PreferenceService** - `backend/app/services/database_service.py`
```python
PreferenceService.save_preferences(db, preferences_dict)
PreferenceService.get_preferences(db)
```

**PriceService** - `backend/app/services/database_service.py`
```python
PriceService.save_prices(db, prices_dataframe)
PriceService.get_all_prices(db)
PriceService.get_price_history(db, hours=24)
PriceService.get_peak_hours(db)
```

## Benefits

1. **Persistence**: Data survives application restarts
2. **History**: Track how preferences and prices change over time
3. **Analytics**: Analyze historical trends and patterns
4. **Scalability**: Easy to extend with more tables/features
5. **User Management**: Ready for multi-user support (user_id field)

## Future Enhancements

- Add multi-user support with proper authentication
- Implement data export (CSV, PDF)
- Add data visualization for historical analysis
- Set up automated price data collection
- Create admin dashboard for data management
