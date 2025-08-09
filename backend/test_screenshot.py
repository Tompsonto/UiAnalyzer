#!/usr/bin/env python3
"""
Test screenshot functionality
"""
import asyncio
from simple_real_backend import capture_website_screenshot

async def test_screenshot():
    try:
        print("Testing screenshot capture...")
        url = "https://example.com"
        
        screenshot_url = await capture_website_screenshot(url)
        
        if screenshot_url:
            print(f"SUCCESS: Screenshot captured")
            print(f"Data URL length: {len(screenshot_url)} characters")
            print(f"Starts with: {screenshot_url[:50]}...")
        else:
            print("ERROR: No screenshot captured")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_screenshot())