#!/usr/bin/env python3
"""
Test multiple sites with potential Cloudflare protection
"""
import asyncio
from simple_real_backend import analyze_website_simple

async def test_multiple_sites():
    sites = [
        "https://shopify.com",
        "https://canva.com", 
        "https://notion.so"
    ]
    
    print("Testing multiple protected sites...")
    print("=" * 50)
    
    for url in sites:
        print(f"\nTesting: {url}")
        try:
            result = await analyze_website_simple(url)
            print(f"SUCCESS - Score: {result['overall_score']}, Screenshot: {len(result.get('screenshot_url', ''))} chars")
        except Exception as e:
            print(f"FAILED - Error: {str(e)[:100]}...")

if __name__ == "__main__":
    asyncio.run(test_multiple_sites())