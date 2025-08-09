#!/usr/bin/env python3
"""
Test Cloudflare bypass with screenshot and HTML fetching
"""
import asyncio
from simple_real_backend import capture_website_screenshot, analyze_website_simple

async def test_cloudflare_sites():
    # Test sites that typically use Cloudflare
    test_sites = [
        "https://discord.com",  # Usually has Cloudflare
        "https://shopify.com",  # E-commerce with protection
        "https://github.com"    # Microsoft, might have protection
    ]
    
    print("Testing Cloudflare bypass...")
    print("=" * 50)
    
    for url in test_sites:
        print(f"\nTesting: {url}")
        print("-" * 30)
        
        try:
            # Test screenshot capture
            print("Testing screenshot capture...")
            screenshot_url = await capture_website_screenshot(url)
            
            if screenshot_url and len(screenshot_url) > 100:
                print(f"✅ Screenshot captured: {len(screenshot_url)} chars")
            else:
                print("❌ Screenshot failed or empty")
            
            # Test full analysis
            print("Testing full analysis...")
            result = await analyze_website_simple(url)
            
            print(f"✅ Analysis completed:")
            print(f"   Overall Score: {result['overall_score']}")
            print(f"   Screenshot: {'Yes' if result.get('screenshot_url') else 'No'}")
            print(f"   Issues: {result['total_issues']}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_cloudflare_sites())