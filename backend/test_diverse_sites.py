#!/usr/bin/env python3
"""
Test enhanced detection on diverse website types
"""
import asyncio
from simple_real_backend import analyze_website_simple

async def test_diverse_sites():
    sites = [
        ('https://example.com', 'Simple landing page'),
        ('https://github.com', 'Developer platform/SaaS'),
        ('https://medium.com', 'Blog platform'),
        ('https://apple.com', 'Corporate/Business'),
    ]
    
    print('Testing Enhanced Detection on Diverse Sites')
    print('=' * 60)
    
    for url, expected in sites:
        try:
            result = await analyze_website_simple(url)
            print(f'URL: {url}')
            print(f'Expected: {expected}')
            print(f'Detected: {result.get("website_type", "unknown")} (confidence: {result.get("type_confidence", 0)*100:.1f}%)')
            print(f'Top Evidence:')
            for i, evidence in enumerate(result.get('type_evidence', [])[:3], 1):
                print(f'   {i}. {evidence}')
            print('-' * 60)
        except Exception as e:
            print(f'Error analyzing {url}: {e}')

if __name__ == "__main__":
    asyncio.run(test_diverse_sites())