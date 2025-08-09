#!/usr/bin/env python3
"""
Test script for enhanced backend features
"""
import requests
import json

def test_enhanced_analysis():
    """Test enhanced heading and meta tag analysis"""
    
    test_urls = [
        "https://example.com",
        "https://github.com", 
        "https://stackoverflow.com",
        "https://wikipedia.org"
    ]
    
    print("Testing Enhanced Analysis Features...")
    print("=" * 50)
    
    for url in test_urls:
        print(f"\nAnalyzing: {url}")
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
                
                print(f"Overall Score: {result['overall_score']}/100 ({result['grade']})")
                print(f"Visual Score: {result['visual_score']}/100")
                print(f"Text Score: {result['text_score']}/100")
                print(f"Analysis Time: {result['analysis_time']}s")
                print(f"Total Issues: {result['total_issues']} ({result['critical_issues']} critical)")
                
                # Show specific issues
                if result['top_issues']:
                    print("\nTop Issues Found:")
                    for i, issue in enumerate(result['top_issues'][:3], 1):
                        severity_icon = {"high": "🔴", "medium": "🟡", "low": "🔵"}.get(issue['severity'], "⚪")
                        print(f"  {i}. {severity_icon} {issue['message']} ({issue['element']})")
                
                # Show recommendations
                if result['top_recommendations']:
                    print("\nTop Recommendations:")
                    for i, rec in enumerate(result['top_recommendations'][:2], 1):
                        priority_icon = {"Critical": "🚨", "High": "⚡", "Medium": "📋"}.get(rec['priority'], "📝")
                        print(f"  {i}. {priority_icon} {rec['action']} ({rec['category']})")
                
                print(f"\nSummary: {result['summary']}")
                
            else:
                print(f"Error: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"Failed to analyze {url}: {str(e)}")
    
    print("\n" + "=" * 50)
    print("Enhanced analysis test complete!")

if __name__ == "__main__":
    test_enhanced_analysis()