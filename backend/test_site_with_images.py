#!/usr/bin/env python3
"""
Test with a site that has images to see visual issues
"""
import asyncio
from simple_real_backend import analyze_website_simple

async def test_site_with_images():
    try:
        print("Testing with GitHub (has images)...")
        url = "https://github.com"
        
        result = await analyze_website_simple(url)
        
        print(f"Visual Issues ({len(result.get('visual_issues', []))}):")
        if result.get('visual_issues'):
            for i, issue in enumerate(result['visual_issues'], 1):
                print(f"  {i}. {issue['message']} - {issue['element']}")
        else:
            print("  None")
        print()
        
        print(f"Text/SEO Issues ({len(result.get('text_seo_issues', []))}):")
        if result.get('text_seo_issues'):
            for i, issue in enumerate(result['text_seo_issues'], 1):
                print(f"  {i}. {issue['message']} - {issue['element']}")
        else:
            print("  None")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_site_with_images())