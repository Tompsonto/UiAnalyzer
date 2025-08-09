#!/usr/bin/env python3
"""
Test full-page HTML analysis
"""
import asyncio
from simple_real_backend import analyze_website_simple

async def test_fullpage_html():
    try:
        print("Testing full-page HTML analysis...")
        
        # Test with GitHub which has lots of content
        url = "https://github.com"
        result = await analyze_website_simple(url)
        
        print("=== FULL-PAGE HTML ANALYSIS RESULTS ===")
        print(f"Overall Score: {result['overall_score']}")
        print(f"Analysis Time: {result['analysis_time']}s")
        
        # Check content analysis depth
        print(f"Total Issues: {result['total_issues']}")
        print(f"Visual Issues: {len(result.get('visual_issues', []))}")
        print(f"Text/SEO Issues: {len(result.get('text_seo_issues', []))}")
        
        print("\nVisual Issues Found:")
        for i, issue in enumerate(result.get('visual_issues', [])[:3], 1):
            print(f"  {i}. {issue['message']} ({issue['element']})")
            
        print("\nText/SEO Issues Found:")
        for i, issue in enumerate(result.get('text_seo_issues', [])[:3], 1):
            print(f"  {i}. {issue['message']} ({issue['element']})")
        
        print(f"\nScreenshot: {'Empty (disabled)' if not result.get('screenshot_url') else 'Captured'}")
        print("SUCCESS: Full-page HTML analysis working!")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fullpage_html())