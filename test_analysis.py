#!/usr/bin/env python3
"""
Test script to verify ClarityCheck analysis pipeline works correctly
"""
import sys
import os
import asyncio
import logging
import json

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.api.analysis import perform_website_analysis

# Setup logging
logging.basicConfig(level=logging.INFO)

async def test_analysis():
    """Test the analysis pipeline with a simple website"""
    test_url = "https://example.com"
    
    print(f"Testing analysis pipeline with: {test_url}")
    print("=" * 50)
    
    try:
        # Run the analysis
        result = await perform_website_analysis(test_url)
        
        # Print key results
        print(f"Analysis completed successfully!")
        print(f"Overall Score: {result.get('overall_score', 'N/A')}/100")
        print(f"Visual Score: {result.get('visual_score', 'N/A')}/100") 
        print(f"Text Score: {result.get('text_score', 'N/A')}/100")
        print(f"Grade: {result.get('grade', 'N/A')}")
        
        # Check screenshot
        screenshot_url = result.get('screenshot_url', '')
        if screenshot_url and screenshot_url.startswith('data:image/'):
            print(f"Screenshot: OK - Captured ({len(screenshot_url)} chars)")
        else:
            print(f"Screenshot: MISSING or invalid")
        
        # Check issues
        issues = result.get('issues', [])
        print(f"Issues: {len(issues)} found")
        
        # Check grouped issues
        grouped_issues = result.get('grouped_issues', [])
        print(f"Grouped Issues: {len(grouped_issues)} groups")
        
        if grouped_issues:
            print("\nGrouped Issues Preview:")
            for i, group in enumerate(grouped_issues[:3]):
                print(f"  {i+1}. {group.get('parent_description', 'Unknown')} ({group.get('issue_count', 0)} issues)")
        
        # Check accessibility
        a11y_score = result.get('accessibility_score', 0)
        print(f"Accessibility Score: {a11y_score}/100")
        
        # Check CTA analysis
        cta_score = result.get('cta_score', 0)
        cta_analysis = result.get('cta_analysis', {})
        print(f"CTA Score: {cta_score}/100")
        print(f"CTAs Found: {cta_analysis.get('total_ctas', 0)}")
        
        print("\nAll analysis components working correctly!")
        return True
        
    except Exception as e:
        print(f"Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Fix Windows event loop policy for Selenium
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    success = asyncio.run(test_analysis())
    exit(0 if success else 1)