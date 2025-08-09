#!/usr/bin/env python3
"""
Simple test for clarity scoring system
"""
import requests
import json

def test_clarity():
    """Test clarity scoring"""
    
    url = "https://example.com"
    print(f"Testing Comprehensive Clarity Scoring System")
    print("=" * 50)
    print(f"Analyzing: {url}")
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
            
            # Display comprehensive scoring
            print(f"CLARITY ANALYSIS RESULTS:")
            print(f"   Overall Score: {result['overall_score']}/100 ({result['grade']})")
            print(f"   Visual Score:  {result['visual_score']}/100")
            print(f"   Text Score:    {result['text_score']}/100")
            print(f"   Clarity Score: {result['clarity_score']}/100")
            print(f"   Analysis Time: {result['analysis_time']}s")
            
            # Show conversion risks
            print(f"\nCONVERSION ANALYSIS:")
            print(f"   Conversion Risks: {result['conversion_risks']}")
            print(f"   Total Issues: {result['total_issues']} ({result['critical_issues']} critical)")
            
            # Show UX patterns
            if result.get('ux_patterns'):
                print(f"\nUX PATTERNS DETECTED ({len(result['ux_patterns'])}):")
                for j, pattern in enumerate(result['ux_patterns'], 1):
                    print(f"   {j}. {pattern['title']} ({pattern['severity']})")
                    print(f"      Fix: {pattern['fix']}")
            else:
                print(f"   No problematic UX patterns detected")
            
            # Show summary
            print(f"\nSUMMARY:")
            print(f"   {result['summary']}")
            
            print(f"\nTest completed successfully!")
            print(f"Clarity scoring system is working!")
            
        else:
            print(f"Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Test failed: {str(e)}")

if __name__ == "__main__":
    test_clarity()