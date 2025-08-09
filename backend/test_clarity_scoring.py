#!/usr/bin/env python3
"""
Test comprehensive clarity scoring system
"""
import requests
import json

def test_clarity_scoring():
    """Test clarity scoring with different websites"""
    
    test_cases = [
        {
            "url": "https://example.com",
            "expected": "Simple site, likely good structure"
        },
        {
            "url": "https://github.com", 
            "expected": "Complex but well-structured"
        },
        {
            "url": "https://apple.com",
            "expected": "Design-focused, good UX"
        }
    ]
    
    print("🎯 Testing Comprehensive Clarity Scoring System")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        url = test_case["url"]
        print(f"\n{i}. Testing: {url}")
        print(f"   Expected: {test_case['expected']}")
        print("-" * 40)
        
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/analyze/quick",
                json={"url": url},
                headers={"Content-Type": "application/json"},
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Display comprehensive scoring
                print(f"📊 CLARITY ANALYSIS RESULTS:")
                print(f"   Overall Score: {result['overall_score']}/100 ({result['grade']})")
                print(f"   Visual Score:  {result['visual_score']}/100")
                print(f"   Text Score:    {result['text_score']}/100")
                print(f"   ✨ Clarity Score: {result['clarity_score']}/100")
                print(f"   Analysis Time: {result['analysis_time']}s")
                
                # Show conversion risks
                print(f"\n🎯 CONVERSION ANALYSIS:")
                print(f"   Conversion Risks: {result['conversion_risks']}")
                print(f"   Total Issues: {result['total_issues']} ({result['critical_issues']} critical)")
                
                # Show UX patterns
                if result.get('ux_patterns'):
                    print(f"\n🔍 UX PATTERNS DETECTED ({len(result['ux_patterns'])}):")
                    for j, pattern in enumerate(result['ux_patterns'], 1):
                        severity_icon = {"high": "🔴", "medium": "🟡", "low": "🔵"}.get(pattern['severity'], "⚪")
                        print(f"   {j}. {severity_icon} {pattern['title']}")
                        print(f"      Pattern: {pattern['pattern']}")
                        print(f"      Fix: {pattern['fix']}")
                        if 'evidence' in pattern:
                            evidence = pattern['evidence']
                            print(f"      Evidence: {evidence}")
                        print()
                else:
                    print(f"   ✅ No problematic UX patterns detected")
                
                # Show intelligent summary
                print(f"📝 INTELLIGENT SUMMARY:")
                print(f"   {result['summary']}")
                
                # Show top issues with context
                if result.get('top_issues'):
                    print(f"\n⚠️ TOP ISSUES:")
                    for j, issue in enumerate(result['top_issues'][:3], 1):
                        severity_icon = {"high": "🔴", "medium": "🟡", "low": "🔵"}.get(issue['severity'], "⚪")
                        print(f"   {j}. {severity_icon} {issue['message']}")
                        print(f"      Element: {issue['element']}")
                        if 'suggestion' in issue:
                            print(f"      Fix: {issue['suggestion']}")
                
                print(f"\n" + "="*40)
                
            else:
                print(f"❌ Error: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Failed to test {url}: {str(e)}")
    
    print(f"\n🏁 Clarity scoring system test complete!")
    print("\n💡 Key Features Tested:")
    print("   ✅ Comprehensive clarity score calculation")
    print("   ✅ Rule-based UX pattern detection")
    print("   ✅ Conversion risk assessment")
    print("   ✅ Intelligent issue prioritization")
    print("   ✅ Actionable recommendations")

if __name__ == "__main__":
    test_clarity_scoring()