#!/usr/bin/env python3
"""
Test new two-column layout with categorized issues
"""
import asyncio
from simple_real_backend import analyze_website_simple

async def test_new_layout():
    try:
        print("Testing new two-column layout design...")
        url = "https://example.com"
        
        result = await analyze_website_simple(url)
        
        print(f"Overall Score: {result['overall_score']}")
        print(f"Visual Score: {result['visual_score']}")
        print(f"Text Score: {result['text_score']}")
        print()
        
        print("Visual Issues:")
        if result.get('visual_issues'):
            for i, issue in enumerate(result['visual_issues'], 1):
                print(f"  {i}. {issue['message']} ({issue['severity']})")
        else:
            print("  None")
        print()
        
        print("Text/SEO Issues:")
        if result.get('text_seo_issues'):
            for i, issue in enumerate(result['text_seo_issues'], 1):
                print(f"  {i}. {issue['message']} ({issue['severity']})")
        else:
            print("  None")
        print()
        
        print("Visual Recommendations:")
        if result.get('visual_recommendations'):
            for i, rec in enumerate(result['visual_recommendations'], 1):
                print(f"  {i}. {rec['action']} ({rec['priority']})")
        else:
            print("  None")
        print()
        
        print("Text/SEO Recommendations:")
        if result.get('text_seo_recommendations'):
            for i, rec in enumerate(result['text_seo_recommendations'], 1):
                print(f"  {i}. {rec['action']} ({rec['priority']})")
        else:
            print("  None")
        
        print(f"\nScreenshot: {'Yes' if result.get('screenshot_url') else 'No'}")
        print("SUCCESS: New layout working!")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_new_layout())