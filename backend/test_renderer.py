#!/usr/bin/env python3
"""
Test script for the enhanced Playwright renderer
"""
import asyncio
import json
import sys
from app.modules.renderer import WebsiteRenderer

async def test_renderer():
    """Test the enhanced website renderer with real websites"""
    
    # Test URLs - variety of different website types
    test_urls = [
        "https://example.com",
        "https://github.com",
        "https://stackoverflow.com",
        "https://tailwindcss.com"
    ]
    
    print("🧪 Testing Enhanced Playwright Renderer")
    print("=" * 50)
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n{i}. Testing: {url}")
        print("-" * 30)
        
        try:
            async with WebsiteRenderer() as renderer:
                start_time = asyncio.get_event_loop().time()
                
                # Render website
                result = await renderer.render_website(url)
                
                end_time = asyncio.get_event_loop().time()
                render_time = end_time - start_time
                
                # Display results
                print(f"✅ Render successful in {render_time:.2f}s")
                print(f"📄 Title: {result.get('title', 'No title')}")
                print(f"🌐 Final URL: {result.get('final_url', url)}")
                print(f"📊 Response Status: {result.get('performance', {}).get('response_status', 'Unknown')}")
                
                # DOM Analysis Results
                dom_data = result.get('dom_analysis', {})
                print(f"📋 Headings: {len(dom_data.get('headings', []))}")
                print(f"🔘 CTAs: {len(dom_data.get('ctas', []))}")
                print(f"📝 Forms: {len(dom_data.get('forms', []))}")
                print(f"🖼️ Images: {len(dom_data.get('images', []))}")
                
                # Text Analysis
                print(f"📝 Word Count: {result.get('word_count', 0)}")
                print(f"📰 Paragraphs: {result.get('paragraph_count', 0)}")
                
                # CSS Data
                print(f"🎨 Stylesheets: {result.get('stylesheet_count', 0)}")
                
                # Screenshots
                screenshots = result.get('screenshots', {})
                print(f"📸 Screenshots generated: {len([k for k, v in screenshots.items() if k != 'error'])}")
                
                if 'full_page' in screenshots:
                    print(f"   - Full page: {len(screenshots['full_page'])} chars (base64)")
                if 'viewport' in screenshots:
                    print(f"   - Viewport: {len(screenshots['viewport'])} chars (base64)")
                if 'mobile_viewport' in screenshots:
                    print(f"   - Mobile: {len(screenshots['mobile_viewport'])} chars (base64)")
                
                # Performance metrics
                perf = result.get('performance', {})
                print(f"⚡ Attempts: {perf.get('attempts', 1)}")
                print(f"⏱️ Total render time: {perf.get('render_time', 0):.2f}s")
                
                # Sample DOM elements (first 3 headings)
                headings = dom_data.get('headings', [])[:3]
                if headings:
                    print("📋 Sample Headings:")
                    for heading in headings:
                        print(f"   {heading['tag']}: {heading['text'][:50]}{'...' if len(heading['text']) > 50 else ''}")
                
                # Sample CTAs (first 3)
                ctas = dom_data.get('ctas', [])[:3]
                if ctas:
                    print("🔘 Sample CTAs:")
                    for cta in ctas:
                        print(f"   {cta['tag']}: {cta['text'][:30]}{'...' if len(cta['text']) > 30 else ''}")
                
                print(f"🔗 Page Hash: {result.get('page_hash', 'No hash')}")
                
        except Exception as e:
            print(f"❌ Error rendering {url}: {str(e)}")
            continue
    
    print("\n" + "=" * 50)
    print("🏁 Renderer testing complete!")

def save_sample_result(result, filename="sample_render_result.json"):
    """Save a sample result for inspection"""
    try:
        # Remove large screenshot data for readability
        result_copy = result.copy()
        if 'screenshots' in result_copy:
            screenshots_info = {}
            for key, value in result_copy['screenshots'].items():
                if key == 'error':
                    screenshots_info[key] = value
                else:
                    screenshots_info[key] = f"Base64 data ({len(value)} chars)"
            result_copy['screenshots'] = screenshots_info
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result_copy, f, indent=2, default=str)
        print(f"📁 Sample result saved to {filename}")
    except Exception as e:
        print(f"❌ Failed to save sample: {str(e)}")

async def test_single_website():
    """Test with a single website and save detailed results"""
    url = input("Enter URL to test (or press Enter for example.com): ").strip()
    if not url:
        url = "https://example.com"
    
    print(f"\n🧪 Detailed test of: {url}")
    print("=" * 50)
    
    try:
        async with WebsiteRenderer() as renderer:
            result = await renderer.render_website(url)
            
            print("✅ Render successful!")
            print(f"📄 Title: {result.get('title')}")
            print(f"📝 Description: {result.get('meta_description', 'No description')[:100]}...")
            print(f"🌐 Language: {result.get('lang', 'Unknown')}")
            print(f"🔍 Canonical: {result.get('canonical_url', 'None')}")
            
            # Save detailed result
            save_sample_result(result, f"detailed_result_{result.get('page_hash', 'unknown')}.json")
            
            # Technical data
            tech = result.get('technical_data', {})
            if tech:
                print("\n🔧 Technical Analysis:")
                perf = tech.get('performance', {})
                if perf:
                    print(f"   DOM Load: {perf.get('dom_content_loaded', 0)}ms")
                    print(f"   Total Load: {perf.get('total_load_time', 0)}ms")
                
                access = tech.get('accessibility', {})
                if access:
                    print(f"   Images w/o alt: {access.get('images_without_alt', 0)}")
                    print(f"   Links w/o text: {access.get('links_without_text', 0)}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--single":
        asyncio.run(test_single_website())
    else:
        asyncio.run(test_renderer())