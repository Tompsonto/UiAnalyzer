#!/usr/bin/env python3
"""
Simple test for Cloudflare bypass
"""
import asyncio
from simple_real_backend import analyze_website_simple

async def test_simple():
    try:
        print("Testing Discord.com (Cloudflare protected)...")
        url = "https://discord.com"
        
        result = await analyze_website_simple(url)
        
        print(f"SUCCESS: Analysis completed")
        print(f"Overall Score: {result['overall_score']}")
        print(f"Screenshot captured: {'Yes' if result.get('screenshot_url') else 'No'}")
        print(f"Screenshot length: {len(result.get('screenshot_url', ''))} chars")
        print(f"Total Issues: {result['total_issues']}")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple())