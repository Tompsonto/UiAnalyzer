#!/usr/bin/env python3
"""
Test cleaned API without website type detection
"""
import asyncio
from simple_real_backend import analyze_website_simple

async def test_cleaned_api():
    try:
        result = await analyze_website_simple('https://example.com')
        print('API Response (cleaned):')
        print(f'Overall Score: {result["overall_score"]}')
        print(f'Clarity Score: {result["clarity_score"]}')
        print(f'Total Issues: {result["total_issues"]}')
        print(f'Analysis Time: {result["analysis_time"]}s')
        
        # Verify website type fields are removed
        if 'website_type' not in result:
            print('SUCCESS: Website type fields successfully removed')
        else:
            print('ERROR: Website type fields still present')
            
        print('\nResponse keys:', list(result.keys()))
            
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_cleaned_api())