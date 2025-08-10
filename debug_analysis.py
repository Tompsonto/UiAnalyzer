#!/usr/bin/env python3
"""
Debug script to identify ClarityCheck analysis issues
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
import logging
from backend.app.api.analysis import perform_website_analysis

logging.basicConfig(level=logging.INFO)

async def debug_analysis():
    """Debug the analysis process"""
    try:
        print("=" * 50)
        print("DEBUGGING CLARITYCHECK ANALYSIS")
        print("=" * 50)
        
        # Test URL
        test_url = "https://example.com"
        
        print(f"\n1. Testing analysis for: {test_url}")
        
        # Run the analysis
        result = await perform_website_analysis(test_url)
        
        print(f"\n2. Analysis Results:")
        print(f"   Overall Score: {result.get('overall_score', 'N/A')}")
        print(f"   Visual Score: {result.get('visual_score', 'N/A')}")
        print(f"   Text Score: {result.get('text_score', 'N/A')}")
        
        print(f"\n3. Screenshot Status:")
        screenshot_url = result.get('screenshot_url', '')
        if screenshot_url:
            if screenshot_url.startswith('data:image'):
                print(f"   [OK] Screenshot captured (base64 data, length: {len(screenshot_url)})")
            else:
                print(f"   [OK] Screenshot URL: {screenshot_url}")
        else:
            print(f"   [ERROR] NO SCREENSHOT CAPTURED")
        
        print(f"\n4. Data Analysis:")
        print(f"   Visual Issues: {len(result.get('visual_issues', []))}")
        print(f"   Text Issues: {len(result.get('text_seo_issues', []))}")
        print(f"   Grouped Issues: {len(result.get('grouped_issues', []))}")
        
        print(f"\n5. Multi-viewport Data:")
        multi_viewport = result.get('multi_viewport', {})
        if multi_viewport:
            print(f"   Processing Time: {multi_viewport.get('total_processing_time', 'N/A')}s")
            print(f"   Viewports Analyzed: {multi_viewport.get('viewports_analyzed', 'N/A')}")
            desktop_data = multi_viewport.get('desktop_data')
            if desktop_data:
                desktop_screenshot = desktop_data.get('screenshot_base64', '')
                print(f"   Desktop Screenshot: {'[OK] Present' if desktop_screenshot else '[ERROR] Missing'}")
                print(f"   Desktop Elements: {desktop_data.get('elements_detected', 'N/A')}")
            else:
                print(f"   Desktop Data: [ERROR] Missing")
        else:
            print(f"   [ERROR] NO MULTI-VIEWPORT DATA")
        
        print(f"\n6. Enhanced Analysis:")
        print(f"   Accessibility Score: {result.get('accessibility_score', 'N/A')}")
        print(f"   CTA Score: {result.get('cta_score', 'N/A')}")
        cta_analysis = result.get('cta_analysis', {})
        if cta_analysis:
            print(f"   Total CTAs: {cta_analysis.get('total_ctas', 'N/A')}")
        
        print(f"\n7. Analysis Speed Check:")
        if multi_viewport.get('total_processing_time', 0) < 5:
            print(f"   [WARNING] ANALYSIS TOO FAST ({multi_viewport.get('total_processing_time', 0)}s)")
            print(f"   Expected: 10-15 seconds for real Selenium analysis")
        else:
            print(f"   [OK] Analysis took appropriate time")
        
        return result
        
    except Exception as e:
        print(f"\n[ERROR] DEBUG FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(debug_analysis())