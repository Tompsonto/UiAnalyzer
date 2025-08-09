#!/usr/bin/env python3
"""
Test the analysis function directly to debug website type detection
"""
import asyncio
from simple_real_backend import analyze_website_simple

async def test_direct_analysis():
    """Test analysis function directly"""
    
    url = "https://example.com"
    print(f"Testing direct analysis of {url}...")
    
    try:
        result = await analyze_website_simple(url)
        
        print("Analysis result keys:", list(result.keys()))
        
        if 'website_type' in result:
            print(f"Website Type: {result['website_type']}")
            print(f"Confidence: {result['type_confidence']:.2f}")
            print(f"Evidence: {result['type_evidence']}")
        else:
            print("Website type fields missing from result")
            
        return result
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_direct_analysis())