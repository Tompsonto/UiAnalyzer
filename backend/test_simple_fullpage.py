#!/usr/bin/env python3
"""
Test full-page with a simple site
"""
import asyncio
from simple_real_backend import analyze_website_simple

async def test_simple_fullpage():
    try:
        print("Testing full-page with simple site...")
        
        url = "https://example.com"
        print(f"Analyzing: {url}")
        
        result = await analyze_website_simple(url)
        
        print("SUCCESS!")
        print(f"Analysis Time: {result['analysis_time']}s")
        
        # Check screenshot size
        screenshot_size = len(result.get('screenshot_url', ''))
        print(f"Screenshot size: {screenshot_size} characters")
        
        # Check if it's actually full page by comparing to expected size
        if screenshot_size > 20000:  # Full page should be significantly larger
            print("✓ Full-page screenshot confirmed")
        else:
            print("? Might be viewport screenshot")
            
        print(f"Issues found: {result['total_issues']}")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_simple_fullpage())