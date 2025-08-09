#!/usr/bin/env python3
"""
Test enhanced website type detection
"""
import asyncio
from simple_real_backend import analyze_website_simple

async def test_enhanced_detection():
    sites = [
        ('https://nuxt.com', 'Expected: SaaS/Framework'),
        ('https://surferseo.com', 'Expected: SaaS'),
        ('https://shopify.com', 'Expected: E-commerce/SaaS')
    ]
    
    print('Testing Enhanced Website Type Detection')
    print('=' * 60)
    
    for url, expected in sites:
        try:
            result = await analyze_website_simple(url)
            print(f'URL: {url}')
            print(f'Expected: {expected}')
            print(f'Detected: {result.get("website_type", "unknown")} (confidence: {result.get("type_confidence", 0)*100:.1f}%)')
            print(f'Evidence ({len(result.get("type_evidence", []))} items):')
            for i, evidence in enumerate(result.get('type_evidence', [])[:5], 1):
                print(f'   {i}. {evidence}')
            if len(result.get('type_evidence', [])) > 5:
                print(f'   ... and {len(result.get("type_evidence", [])) - 5} more')
            print('-' * 60)
        except Exception as e:
            print(f'Error analyzing {url}: {e}')
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_enhanced_detection())