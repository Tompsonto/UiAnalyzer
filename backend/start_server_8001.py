#!/usr/bin/env python3
"""
Start server on port 8001 for testing
"""
from simple_real_backend import app
import uvicorn

if __name__ == "__main__":
    print("Starting ClarityCheck API on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")