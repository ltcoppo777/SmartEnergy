#!/usr/bin/env python
import subprocess
import sys

print("Starting Backend API Server on http://localhost:8000")
print("Press Ctrl+C to stop the server")
print("-" * 50)

try:
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd="."
    )
except KeyboardInterrupt:
    print("\nServer stopped")
except Exception as e:
    print(f"Error: {e}")
