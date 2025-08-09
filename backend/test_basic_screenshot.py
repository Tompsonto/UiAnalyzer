#!/usr/bin/env python3
"""
Test very basic screenshot function
"""
import asyncio
from playwright.async_api import async_playwright
import base64

async def test_basic():
    try:
        print("Testing basic screenshot...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            print("Going to example.com...")
            await page.goto("https://example.com", timeout=10000)
            
            print("Taking screenshot...")
            screenshot_bytes = await page.screenshot(type="png", full_page=True)
            
            await browser.close()
            
            print(f"Success: {len(screenshot_bytes)} bytes")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_basic())