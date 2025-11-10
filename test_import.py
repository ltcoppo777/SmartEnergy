#!/usr/bin/env python
import sys
sys.path.insert(0, '.')

try:
    from backend.app.services.live_price_service import LivePriceService
    print('LivePriceService imported successfully')
    
    from backend.app.routes.preferences import UserPreferences
    print('UserPreferences imported successfully')
    
    from backend.app.routes.training import TrainingRequest
    print('TrainingRequest imported successfully')
    
    from backend.app.routes.optimization import OptimizationRequest
    print('OptimizationRequest imported successfully')
    
    print('All imports successful!')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
