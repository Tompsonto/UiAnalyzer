#!/usr/bin/env python3
"""
Test script for the enhanced visual analysis module
"""
import asyncio
import json
import sys
from app.modules.renderer import WebsiteRenderer
from app.modules.visual_analysis import AdvancedVisualAnalyzer

async def test_visual_analysis():
    """Test the enhanced visual analysis with real website data"""
    
    # Test URLs with different visual characteristics
    test_urls = [
        ("https://example.com", "Simple, clean site"),
        ("https://github.com", "Developer-focused with good contrast"),
        ("https://dribbble.com", "Design-heavy site"),
        ("https://news.ycombinator.com", "Text-heavy, minimal design")
    ]
    
    print("🎨 Testing Enhanced Visual Analysis")
    print("=" * 60)
    
    for i, (url, description) in enumerate(test_urls, 1):
        print(f"\n{i}. Testing: {url}")
        print(f"   Description: {description}")
        print("-" * 40)
        
        try:
            # Render website
            async with WebsiteRenderer() as renderer:
                print("🔄 Rendering website...")
                page_data = await renderer.render_website(url)
                
                # Analyze visual clarity
                print("🔍 Analyzing visual clarity...")
                analyzer = AdvancedVisualAnalyzer()
                result = analyzer.analyze_visual_clarity(page_data)
                
                # Display results
                print(f"✅ Analysis complete!")
                print(f"📊 Visual Score: {result.get('visual_score', 0)}/100")
                print(f"🎯 WCAG Level: {result.get('wcag_compliance', {}).get('level', 'Unknown')}")
                
                # Score breakdown
                breakdown = result.get('score_breakdown', {})
                print(f"📋 Score Breakdown:")
                for category, score in breakdown.items():
                    print(f"   {category.replace('_', ' ').title()}: {score:.1f}")
                
                # Issues summary
                issues = result.get('issues', [])
                if issues:
                    print(f"⚠️  Issues Found: {len(issues)}")
                    
                    # Group issues by type and severity
                    issue_stats = {}
                    for issue in issues:
                        issue_type = issue.get('type', 'unknown')
                        severity = issue.get('severity', 'unknown')
                        key = f"{issue_type}_{severity}"
                        issue_stats[key] = issue_stats.get(key, 0) + 1
                    
                    for issue_key, count in issue_stats.items():
                        issue_type, severity = issue_key.split('_', 1)
                        emoji = {'high': '🔴', 'medium': '🟡', 'low': '🔵'}.get(severity, '⚪')
                        print(f"   {emoji} {issue_type.title()}: {count} {severity}")
                    
                    # Show top 3 issues
                    print(f"🔍 Top Issues:")
                    for j, issue in enumerate(issues[:3], 1):
                        severity_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🔵'}.get(issue.get('severity'), '⚪')
                        print(f"   {j}. {severity_emoji} {issue.get('element', 'Unknown')}: {issue.get('message', 'No message')}")
                else:
                    print("✅ No issues found!")
                
                # WCAG compliance details
                wcag = result.get('wcag_compliance', {})
                print(f"♿ WCAG Compliance:")
                print(f"   Level: {wcag.get('level', 'Unknown')}")
                print(f"   Contrast Issues: {wcag.get('contrast_issues', 0)}")
                print(f"   Accessibility Issues: {wcag.get('accessibility_issues', 0)}")
                
                # Visual metrics
                metrics = result.get('visual_metrics', {})
                if metrics:
                    print(f"📈 Visual Metrics:")
                    print(f"   DOM Elements: {metrics.get('total_elements', 0)}")
                    print(f"   CTAs: {metrics.get('cta_count', 0)} (Above fold: {metrics.get('above_fold_ctas', 0)})")
                    print(f"   Images: {metrics.get('image_count', 0)}")
                    print(f"   Headings: {metrics.get('heading_count', 0)}")
                    print(f"   Max Nesting: {metrics.get('max_nesting_depth', 0)}")
                
                # Recommendations
                recommendations = result.get('recommendations', [])
                if recommendations:
                    print(f"💡 Top Recommendations:")
                    for j, rec in enumerate(recommendations[:3], 1):
                        priority_emoji = {'Critical': '🚨', 'High': '⚡', 'Medium': '📋', 'Low': '💭'}.get(rec.get('priority'), '📝')
                        print(f"   {j}. {priority_emoji} {rec.get('action', 'Unknown action')}")
                        print(f"      Category: {rec.get('category', 'Unknown')}")
                        print(f"      Impact: {rec.get('impact', 'Unknown')}")
                
        except Exception as e:
            print(f"❌ Error analyzing {url}: {str(e)}")
            continue
    
    print("\n" + "=" * 60)
    print("🏁 Visual analysis testing complete!")

async def test_single_site_detailed():
    """Test a single site with detailed output"""
    url = input("Enter URL to test (or press Enter for example.com): ").strip()
    if not url:
        url = "https://example.com"
    
    print(f"\n🔍 Detailed Visual Analysis: {url}")
    print("=" * 60)
    
    try:
        # Render and analyze
        async with WebsiteRenderer() as renderer:
            print("🔄 Rendering website...")
            page_data = await renderer.render_website(url)
            
            print("🎨 Performing visual analysis...")
            analyzer = AdvancedVisualAnalyzer()
            result = analyzer.analyze_visual_clarity(page_data)
            
            # Save detailed result
            filename = f"visual_analysis_{result.get('visual_score', 0):.0f}_score.json"
            
            # Remove large data for readability
            save_result = result.copy()
            if 'visual_metrics' in save_result:
                # Keep metrics but limit size
                pass
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(save_result, f, indent=2, default=str)
            
            print(f"💾 Detailed results saved to: {filename}")
            
            # Display comprehensive analysis
            print(f"\n📊 COMPREHENSIVE VISUAL ANALYSIS RESULTS")
            print("=" * 50)
            print(f"🌐 URL: {url}")
            print(f"📈 Overall Score: {result.get('visual_score', 0)}/100")
            print(f"🎯 Grade: {'A' if result.get('visual_score', 0) >= 90 else 'B' if result.get('visual_score', 0) >= 80 else 'C' if result.get('visual_score', 0) >= 70 else 'D' if result.get('visual_score', 0) >= 60 else 'F'}")
            
            # Detailed score breakdown
            print(f"\n📋 DETAILED SCORE BREAKDOWN:")
            breakdown = result.get('score_breakdown', {})
            for category, score in breakdown.items():
                status = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
                print(f"   {status} {category.replace('_', ' ').title(): <15}: {score:5.1f}/100")
            
            # WCAG compliance details
            wcag = result.get('wcag_compliance', {})
            print(f"\n♿ WCAG ACCESSIBILITY COMPLIANCE:")
            level_emoji = {'AAA': '🥇', 'AA': '🥈', 'FAIL': '❌'}.get(wcag.get('level'), '❓')
            print(f"   {level_emoji} Compliance Level: {wcag.get('level', 'Unknown')}")
            print(f"   📊 Total Issues: {wcag.get('total_issues', 0)}")
            print(f"   🔴 High Priority: {wcag.get('high_priority_issues', 0)}")
            print(f"   🎨 Contrast Issues: {wcag.get('contrast_issues', 0)}")
            print(f"   ♿ Accessibility Issues: {wcag.get('accessibility_issues', 0)}")
            
            # All issues categorized
            issues = result.get('issues', [])
            if issues:
                print(f"\n⚠️  ALL ISSUES DETECTED ({len(issues)} total):")
                
                # Group by type
                by_type = {}
                for issue in issues:
                    issue_type = issue.get('type', 'unknown')
                    if issue_type not in by_type:
                        by_type[issue_type] = []
                    by_type[issue_type].append(issue)
                
                for issue_type, type_issues in by_type.items():
                    print(f"\n   📂 {issue_type.upper()} ISSUES ({len(type_issues)}):")
                    for issue in type_issues[:5]:  # Show first 5 of each type
                        severity_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🔵'}.get(issue.get('severity'), '⚪')
                        element = issue.get('element', 'Unknown')[:30]
                        message = issue.get('message', 'No message')[:60]
                        print(f"      {severity_emoji} {element}: {message}")
                        if 'suggestion' in issue:
                            print(f"         💡 {issue['suggestion'][:80]}...")
            
            # Detailed recommendations
            recommendations = result.get('recommendations', [])
            if recommendations:
                print(f"\n💡 ACTIONABLE RECOMMENDATIONS:")
                for i, rec in enumerate(recommendations, 1):
                    priority_emoji = {'Critical': '🚨', 'High': '⚡', 'Medium': '📋', 'Low': '💭'}.get(rec.get('priority'), '📝')
                    print(f"\n   {i}. {priority_emoji} {rec.get('action', 'Unknown action')}")
                    print(f"      📂 Category: {rec.get('category', 'Unknown')}")
                    print(f"      📊 Priority: {rec.get('priority', 'Unknown')}")
                    print(f"      📝 Description: {rec.get('description', 'No description')}")
                    print(f"      🎯 Impact: {rec.get('impact', 'Unknown impact')}")
                    print(f"      ⚡ Effort: {rec.get('effort', 'Unknown effort')}")
            
            # Visual metrics summary
            metrics = result.get('visual_metrics', {})
            if metrics:
                print(f"\n📈 VISUAL STRUCTURE METRICS:")
                print(f"   🏗️  DOM Elements: {metrics.get('total_elements', 0)}")
                print(f"   🔘 Call-to-Actions: {metrics.get('cta_count', 0)}")
                print(f"   👆 Above Fold CTAs: {metrics.get('above_fold_ctas', 0)}")
                print(f"   🖼️  Images: {metrics.get('image_count', 0)}")
                print(f"   📝 Headings: {metrics.get('heading_count', 0)}")
                print(f"   📋 Forms: {metrics.get('form_count', 0)}")
                print(f"   🎨 Stylesheets: {metrics.get('stylesheet_count', 0)}")
                print(f"   📊 Max Nesting Depth: {metrics.get('max_nesting_depth', 0)}")
            
            print(f"\n💾 Full analysis data saved to: {filename}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_color_parsing():
    """Test color parsing functionality"""
    print("\n🎨 Testing Color Parsing")
    print("=" * 30)
    
    analyzer = AdvancedVisualAnalyzer()
    
    test_colors = [
        "rgb(255, 255, 255)",
        "rgb(0, 0, 0)", 
        "rgba(255, 0, 0, 0.8)",
        "#ffffff",
        "#000000",
        "#ff0000",
        "#f00",
        "white",
        "black",
        "red"
    ]
    
    for color in test_colors:
        try:
            rgb = analyzer._parse_color_to_rgb(color)
            if rgb:
                print(f"✅ {color: <20} -> RGB{rgb}")
            else:
                print(f"❌ {color: <20} -> Failed to parse")
        except Exception as e:
            print(f"❌ {color: <20} -> Error: {str(e)}")
    
    # Test contrast calculation
    print(f"\n🔍 Testing Contrast Calculations:")
    test_pairs = [
        ((255, 255, 255), (0, 0, 0)),      # White on black - perfect
        ((255, 255, 255), (128, 128, 128)),  # White on gray - medium
        ((0, 0, 255), (255, 255, 0)),      # Blue on yellow - good
        ((255, 0, 0), (0, 255, 0)),        # Red on green - poor
    ]
    
    for bg, text in test_pairs:
        try:
            contrast = analyzer._calculate_wcag_contrast(bg, text)
            aa_pass = "✅" if contrast >= 4.5 else "❌"
            aaa_pass = "✅" if contrast >= 7.0 else "❌"
            print(f"   BG{bg} + Text{text}: {contrast:.2f} (AA:{aa_pass} AAA:{aaa_pass})")
        except Exception as e:
            print(f"   BG{bg} + Text{text}: Error - {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--single":
            asyncio.run(test_single_site_detailed())
        elif sys.argv[1] == "--color":
            test_color_parsing()
    else:
        asyncio.run(test_visual_analysis())