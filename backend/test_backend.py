#!/usr/bin/env python3
"""
Test script to check if the real backend is working
"""
import requests
import json

def test_backend():
    try:
        print("Testing backend connection...")
        response = requests.get("http://localhost:8000/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test analysis endpoint
        print("\nTesting analysis endpoint...")
        analysis_response = requests.post(
            "http://localhost:8000/api/v1/analyze/quick",
            json={"url": "https://example.com"},
            headers={"Content-Type": "application/json"}
        )
        print(f"Analysis Status: {analysis_response.status_code}")
        result = analysis_response.json()
        print(f"Overall Score: {result.get('overall_score')}")
        print(f"Analysis Time: {result.get('analysis_time')}")
        print(f"URL Analyzed: {result.get('url_analyzed')}")
        print("✅ Real analysis is working!" if result.get('analysis_time') else "❌ Mock data detected")
        
    except Exception as e:
        print(f"❌ Backend test failed: {e}")

if __name__ == "__main__":
    test_backend()