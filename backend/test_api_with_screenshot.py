#!/usr/bin/env python3
"""
Test API with screenshot functionality
"""
import asyncio
from simple_real_backend import analyze_website_simple

async def test_api_with_screenshot():
    try:
        print("Testing full API with screenshot...")
        url = "https://example.com"
        
        result = await analyze_website_simple(url)
        
        print(f"Overall Score: {result['overall_score']}")
        print(f"Analysis Time: {result['analysis_time']}s")
        
        if result.get('screenshot_url'):
            print(f"Screenshot captured: {len(result['screenshot_url'])} characters")
            print("SUCCESS: Screenshot included in API response")
        else:
            print("ERROR: No screenshot in API response")
            
        print("Response keys:", list(result.keys()))
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_api_with_screenshot())