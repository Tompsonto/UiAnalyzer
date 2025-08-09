#!/usr/bin/env python3
"""
ClarityCheck Backend Runner
"""
import uvicorn
from app.core.database import init_db

def main():
    """Initialize database and run the application"""
    print("🔧 Initializing ClarityCheck backend...")
    
    # Initialize database
    init_db()
    
    # Run the application
    print("🚀 Starting ClarityCheck API server...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()