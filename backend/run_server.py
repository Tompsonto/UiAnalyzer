#!/usr/bin/env python3
"""
Run the backend server with website type detection
"""
import uvicorn
from simple_real_backend import app

if __name__ == "__main__":
    print("🚀 Starting ClarityCheck Backend with Website Type Detection...")
    print("📡 Server will run on http://localhost:8000")
    print("🔍 Website type detection: ENABLED")
    print("=" * 60)
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except OSError as e:
        if "Address already in use" in str(e) or "10048" in str(e):
            print("⚠️  Port 8000 is busy, trying port 8001...")
            uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")