#!/usr/bin/env python3
"""
Test just the screenshot function
"""
import asyncio
from simple_real_backend import capture_website_screenshot

async def test_screenshot_only():
    try:
        print("Testing screenshot capture only...")
        
        url = "https://example.com"
        screenshot_url = await capture_website_screenshot(url)
        
        if screenshot_url:
            print(f"SUCCESS: {len(screenshot_url)} characters")
            # Check if it starts with expected base64 format
            if screenshot_url.startswith("data:image/png;base64,"):
                print("✓ Valid screenshot format")
            else:
                print("? Unexpected format")
        else:
            print("FAILED: Empty screenshot")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_screenshot_only())