#!/usr/bin/env python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from app.services.optimization_service import OptimizationService
    print("[OK] Import successful: OptimizationService loaded")
    
    # Test the method exists
    print(f"[OK] Method exists: identify_peak_hours = {hasattr(OptimizationService, 'identify_peak_hours')}")
except Exception as e:
    print(f"[ERROR] Import failed: {e}")
    sys.exit(1)
