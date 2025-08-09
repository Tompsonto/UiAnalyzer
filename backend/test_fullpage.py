#!/usr/bin/env python3
"""
Test full-page screenshot and analysis
"""
import asyncio
from simple_real_backend import analyze_website_simple

async def test_fullpage():
    try:
        print("Testing full-page analysis...")
        
        # Test with a site that has a lot of content
        url = "https://github.com"
        
        print(f"Analyzing: {url}")
        result = await analyze_website_simple(url)
        
        print("=== FULL-PAGE ANALYSIS RESULTS ===")
        print(f"Overall Score: {result['overall_score']}")
        print(f"Analysis Time: {result['analysis_time']}s")
        
        # Check screenshot
        screenshot_size = len(result.get('screenshot_url', ''))
        print(f"Screenshot captured: {screenshot_size} characters")
        if screenshot_size > 100000:  # Full page should be larger
            print("✓ Full-page screenshot confirmed (large size)")
        else:
            print("? Might be viewport only (small size)")
            
        # Check content analysis
        print(f"Total Issues Found: {result['total_issues']}")
        print(f"Visual Issues: {len(result.get('visual_issues', []))}")
        print(f"Text/SEO Issues: {len(result.get('text_seo_issues', []))}")
        
        print("\nVisual Issues:")
        for issue in result.get('visual_issues', [])[:3]:
            print(f"  - {issue['message']}")
            
        print("\nText/SEO Issues:")
        for issue in result.get('text_seo_issues', [])[:3]:
            print(f"  - {issue['message']}")
            
        print("\n✓ Full-page analysis completed successfully!")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fullpage())