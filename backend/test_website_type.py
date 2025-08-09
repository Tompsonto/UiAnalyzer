#!/usr/bin/env python3
"""
Test website type detection directly
"""
import asyncio
import requests
import json

async def test_website_type_detection():
    """Test website type detection"""
    
    test_urls = [
        "https://example.com",
        "https://github.com", 
        "https://apple.com"
    ]
    
    print("Testing Website Type Detection...")
    print("=" * 50)
    
    for url in test_urls:
        print(f"\nTesting: {url}")
        print("-" * 30)
        
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/analyze/quick",
                json={"url": url},
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if website type fields are present
                if 'website_type' in result:
                    print(f"Website Type: {result['website_type']}")
                    print(f"Confidence: {result.get('type_confidence', 0)*100:.1f}%")
                    if result.get('type_evidence'):
                        print(f"Evidence: {', '.join(result['type_evidence'][:3])}")
                else:
                    print("Website type detection not found in response")
                    print("Available keys:", list(result.keys()))
                
            else:
                print(f"Error: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"Failed to test {url}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_website_type_detection())