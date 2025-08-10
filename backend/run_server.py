#!/usr/bin/env python3
"""
Run the backend server with website type detection
"""
import uvicorn
import sys
import os

# Add the app directory to sys.path so we can import from it
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.main import app

if __name__ == "__main__":
    print("Starting ClarityCheck Backend with Website Type Detection...")
    print("Server will run on http://localhost:8000")
    print("Website type detection: ENABLED")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")