#!/usr/bin/env python3
"""Entry point script for running the Photobook application."""

import sys
from pathlib import Path

# Add the backend directory to Python path
backend_path = str(Path(__file__).parent / "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import and run the application
from app.main import app

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug",
    )
