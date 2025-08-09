"""
Test suite for visual analysis module

Tests all 6 heuristic rules:
1. WCAG contrast analysis
2. Typography analysis 
3. Tap target analysis
4. Element overlap detection
5. Density analysis
6. Alignment analysis
"""

import pytest
from app.modules.visual_analysis import analyze_visual, VisualReport, Issue


@pytest.fixture
def contrast_test_data():
    """Test data for WCAG contrast analysis"""
    dom = """
    <html>
        <body>
            <h1>High Contrast Header</h1>
            <p class="low-contrast">Low contrast text</p>
            <button class="poor-contrast">Poor Button</button>
        </body>
    </html>
    """
    
    css_snapshot = {
        'computed_styles': {
            'h1': {'color': 'rgb(0,0,0)', 'backgroundColor': 'rgb(255,255,255)', 'fontSize': '24px'},
            '.low-contrast': {'color': 'rgb(170,170,170)', 'backgroundColor': 'rgb(255,255,255)', 'fontSize': '16px'},
            '.poor-contrast': {'color': 'rgb(200,200,200)', 'backgroundColor': 'rgb(220,220,220)', 'fontSize': '14px'}
        },
        'elements': [
            {
                'selector': 'h1',
                'text': 'High Contrast Header',
                'styles': {'color': 'rgb(0,0,0)', 'backgroundColor': 'rgb(255,255,255)', 'fontSize': '24px'},
                'bbox': {'x': 10, 'y': 10, 'width': 200, 'height': 30}
            },
            {
                'selector': '.low-contrast',
                'text': 'Low contrast text',
                'styles': {'color': 'rgb(170,170,170)', 'backgroundColor': 'rgb(255,255,255)', 'fontSize': '16px'},
                'bbox': {'x': 10, 'y': 50, 'width': 150, 'height': 20}
            },
            {
                'selector': '.poor-contrast',
                'text': 'Poor Button',
                'styles': {'color': 'rgb(200,200,200)', 'backgroundColor': 'rgb(220,220,220)', 'fontSize': '14px'},
                'bbox': {'x': 10, 'y': 80, 'width': 100, 'height': 25}
            }
        ]
    }
    
    return dom, css_snapshot


@pytest.fixture
def typography_test_data():
    """Test data for typography analysis"""
    dom = """
    <html>
        <body>
            <p class="tiny-text">Very small text</p>
            <p class="tight-line-height">Text with tight line height</p>
            <p class="long-line">This is a very long line of text that should exceed the 90 character limit for optimal readability according to typography best practices</p>
        </body>
    </html>
    """
    
    css_snapshot = {
        'computed_styles': {
            '.tiny-text': {'fontSize': '10px', 'lineHeight': 'normal'},
            '.tight-line-height': {'fontSize': '16px', 'lineHeight': '1.1'},
            '.long-line': {'fontSize': '16px', 'lineHeight': 'normal'}
        },
        'elements': [
            {
                'selector': '.tiny-text',
                'text': 'Very small text',
                'styles': {'fontSize': '10px', 'lineHeight': 'normal'},
                'bbox': {'x': 10, 'y': 10, 'width': 100, 'height': 12}
            },
            {
                'selector': '.tight-line-height',
                'text': 'Text with tight line height',
                'styles': {'fontSize': '16px', 'lineHeight': '1.1'},
                'bbox': {'x': 10, 'y': 30, 'width': 200, 'height': 18}
            },
            {
                'selector': '.long-line',
                'text': 'This is a very long line of text that should exceed the 90 character limit for optimal readability according to typography best practices',
                'styles': {'fontSize': '16px', 'lineHeight': 'normal'},
                'bbox': {'x': 10, 'y': 60, 'width': 1200, 'height': 20}
            }
        ]
    }
    
    return dom, css_snapshot


@pytest.fixture
def tap_target_test_data():
    """Test data for tap target analysis (mobile)"""
    dom = """
    <html>
        <body>
            <button class="tiny-button">Small</button>
            <a href="#" class="small-link">Tiny Link</a>
            <button class="good-button">Good Size</button>
        </body>
    </html>
    """
    
    css_snapshot = {
        'computed_styles': {},
        'elements': [
            {
                'selector': 'button.tiny-button',
                'text': 'Small',
                'styles': {},
                'bbox': {'x': 10, 'y': 10, 'width': 30, 'height': 25}
            },
            {
                'selector': 'a.small-link',
                'text': 'Tiny Link',
                'styles': {},
                'bbox': {'x': 50, 'y': 10, 'width': 35, 'height': 20}
            },
            {
                'selector': 'button.good-button',
                'text': 'Good Size',
                'styles': {},
                'bbox': {'x': 100, 'y': 10, 'width': 50, 'height': 50}
            }
        ]
    }
    
    return dom, css_snapshot


@pytest.fixture
def overlap_test_data():
    """Test data for element overlap detection"""
    dom = """
    <html>
        <body>
            <div class="box1">Box 1</div>
            <div class="box2">Box 2 (overlapping)</div>
            <div class="box3">Box 3 (separate)</div>
        </body>
    </html>
    """
    
    css_snapshot = {
        'computed_styles': {},
        'elements': [
            {
                'selector': '.box1',
                'text': 'Box 1',
                'styles': {},
                'bbox': {'x': 10, 'y': 10, 'width': 100, 'height': 50}
            },
            {
                'selector': '.box2',
                'text': 'Box 2 (overlapping)',
                'styles': {},
                'bbox': {'x': 50, 'y': 30, 'width': 100, 'height': 50}  # 50% overlap with box1
            },
            {
                'selector': '.box3',
                'text': 'Box 3 (separate)',
                'styles': {},
                'bbox': {'x': 200, 'y': 10, 'width': 100, 'height': 50}
            }
        ]
    }
    
    return dom, css_snapshot


@pytest.fixture
def density_test_data():
    """Test data for interactive element density analysis"""
    dom = """
    <html>
        <body>
            <!-- Create 25 interactive elements in a small region to trigger density warning -->
        </body>
    </html>
    """
    
    # Create 25 buttons in same region (0-1000, 0-800)
    elements = []
    for i in range(25):
        x = (i % 5) * 50  # 5 columns
        y = (i // 5) * 40  # 5 rows
        elements.append({
            'selector': f'button.btn-{i}',
            'text': f'Button {i}',
            'styles': {},
            'bbox': {'x': x, 'y': y, 'width': 40, 'height': 30}
        })
    
    css_snapshot = {
        'computed_styles': {},
        'elements': elements
    }
    
    return dom, css_snapshot


@pytest.fixture
def alignment_test_data():
    """Test data for element alignment analysis"""
    dom = """
    <html>
        <body>
            <div class="row1-item1">Item 1</div>
            <div class="row1-item2">Item 2</div>
            <div class="row1-item3">Item 3 (misaligned)</div>
        </body>
    </html>
    """
    
    css_snapshot = {
        'computed_styles': {},
        'elements': [
            {
                'selector': '.row1-item1',
                'text': 'Item 1',
                'styles': {},
                'bbox': {'x': 10, 'y': 50, 'width': 80, 'height': 30}
            },
            {
                'selector': '.row1-item2',
                'text': 'Item 2',
                'styles': {},
                'bbox': {'x': 10, 'y': 60, 'width': 80, 'height': 30}  # Same row, aligned
            },
            {
                'selector': '.row1-item3',
                'text': 'Item 3 (misaligned)',
                'styles': {},
                'bbox': {'x': 25, 'y': 55, 'width': 80, 'height': 30}  # Same row, 15px deviation
            }
        ]
    }
    
    return dom, css_snapshot


class TestVisualAnalysis:
    """Test suite for visual analysis functionality"""
    
    def test_analyze_visual_returns_visual_report(self):
        """Test that analyze_visual returns a VisualReport object"""
        dom = "<html><body><p>Test</p></body></html>"
        css_snapshot = {'computed_styles': {}, 'elements': []}
        viewport = (1920, 1080)
        
        result = analyze_visual(dom, css_snapshot, viewport)
        
        assert isinstance(result, VisualReport)
        assert isinstance(result.score, int)
        assert 0 <= result.score <= 100
        assert isinstance(result.issues, list)
        assert isinstance(result.features, dict)
    
    def test_contrast_analysis(self, contrast_test_data):
        """Test WCAG contrast analysis detects contrast issues"""
        dom, css_snapshot = contrast_test_data
        viewport = (1920, 1080)
        
        result = analyze_visual(dom, css_snapshot, viewport)
        
        # Should find contrast issues
        contrast_issues = [issue for issue in result.issues if issue.type == 'contrast']
        assert len(contrast_issues) >= 2  # low-contrast and poor-contrast elements
        
        # Check severity levels
        high_severity_issues = [issue for issue in contrast_issues if issue.severity == 'high']
        medium_severity_issues = [issue for issue in contrast_issues if issue.severity == 'medium']
        
        assert len(high_severity_issues) >= 1 or len(medium_severity_issues) >= 1
        
        # Score should be penalized
        assert result.score < 100
    
    def test_typography_analysis(self, typography_test_data):
        """Test typography analysis detects font and line height issues"""
        dom, css_snapshot = typography_test_data
        viewport = (1920, 1080)  # Desktop viewport
        
        result = analyze_visual(dom, css_snapshot, viewport)
        
        # Should find typography issues
        typography_issues = [issue for issue in result.issues if issue.type == 'typography']
        assert len(typography_issues) >= 2  # tiny text and tight line height
        
        # Check for specific issues
        messages = [issue.message for issue in typography_issues]
        font_size_issues = [msg for msg in messages if 'Font size' in msg]
        line_height_issues = [msg for msg in messages if 'Line height' in msg]
        line_length_issues = [msg for msg in messages if 'Line length' in msg]
        
        assert len(font_size_issues) >= 1
        assert len(line_height_issues) >= 1
        assert len(line_length_issues) >= 1
    
    def test_tap_target_analysis_mobile(self, tap_target_test_data):
        """Test tap target analysis for mobile viewport"""
        dom, css_snapshot = tap_target_test_data
        viewport = (375, 667)  # Mobile viewport
        
        result = analyze_visual(dom, css_snapshot, viewport)
        
        # Should find tap target issues on mobile
        tap_target_issues = [issue for issue in result.issues if issue.type == 'tap_target']
        assert len(tap_target_issues) >= 2  # tiny-button and small-link
        
        # Check for 44x44px minimum requirement
        messages = [issue.message for issue in tap_target_issues]
        small_target_messages = [msg for msg in messages if '44x44px' in msg]
        assert len(small_target_messages) >= 2
    
    def test_tap_target_analysis_desktop(self, tap_target_test_data):
        """Test tap target analysis for desktop viewport (should not trigger)"""
        dom, css_snapshot = tap_target_test_data
        viewport = (1920, 1080)  # Desktop viewport
        
        result = analyze_visual(dom, css_snapshot, viewport)
        
        # Should not find tap target issues on desktop
        tap_target_issues = [issue for issue in result.issues if issue.type == 'tap_target']
        assert len(tap_target_issues) == 0
    
    def test_overlap_detection(self, overlap_test_data):
        """Test element overlap detection"""
        dom, css_snapshot = overlap_test_data
        viewport = (1920, 1080)
        
        result = analyze_visual(dom, css_snapshot, viewport)
        
        # Should find overlap between box1 and box2
        overlap_issues = [issue for issue in result.issues if issue.type == 'overlap']
        assert len(overlap_issues) >= 1
        
        # Check overlap message
        messages = [issue.message for issue in overlap_issues]
        overlap_messages = [msg for msg in messages if 'overlap' in msg.lower()]
        assert len(overlap_messages) >= 1
    
    def test_density_analysis(self, density_test_data):
        """Test interactive element density analysis"""
        dom, css_snapshot = density_test_data
        viewport = (1920, 1080)
        
        result = analyze_visual(dom, css_snapshot, viewport)
        
        # Should find high density issue (25 elements > 20 threshold)
        density_issues = [issue for issue in result.issues if issue.type == 'density']
        assert len(density_issues) >= 1
        
        # Check density message
        messages = [issue.message for issue in density_issues]
        density_messages = [msg for msg in messages if 'density' in msg.lower()]
        assert len(density_messages) >= 1
    
    def test_alignment_analysis(self, alignment_test_data):
        """Test element alignment analysis"""
        dom, css_snapshot = alignment_test_data
        viewport = (1920, 1080)
        
        result = analyze_visual(dom, css_snapshot, viewport)
        
        # Should find alignment issue (15px deviation > 8px threshold)
        alignment_issues = [issue for issue in result.issues if issue.type == 'alignment']
        assert len(alignment_issues) >= 1
        
        # Check alignment message
        messages = [issue.message for issue in alignment_issues]
        alignment_messages = [msg for msg in messages if 'alignment' in msg.lower() or 'deviation' in msg.lower()]
        assert len(alignment_messages) >= 1
    
    def test_viewport_affects_mobile_detection(self):
        """Test that viewport size affects mobile-specific analysis"""
        dom = "<html><body><button>Test</button></body></html>"
        css_snapshot = {
            'computed_styles': {},
            'elements': [{
                'selector': 'button',
                'text': 'Test',
                'styles': {},
                'bbox': {'x': 10, 'y': 10, 'width': 30, 'height': 30}
            }]
        }
        
        # Mobile viewport
        mobile_result = analyze_visual(dom, css_snapshot, (375, 667))
        assert mobile_result.features['is_mobile'] is True
        
        # Desktop viewport
        desktop_result = analyze_visual(dom, css_snapshot, (1920, 1080))
        assert desktop_result.features['is_mobile'] is False
    
    def test_feature_metrics_included(self):
        """Test that feature metrics are properly included in results"""
        dom = "<html><body><p>Test content</p></body></html>"
        css_snapshot = {
            'computed_styles': {},
            'elements': [{
                'selector': 'p',
                'text': 'Test content',
                'styles': {'fontSize': '16px'},
                'bbox': {'x': 10, 'y': 10, 'width': 100, 'height': 20}
            }]
        }
        viewport = (1920, 1080)
        
        result = analyze_visual(dom, css_snapshot, viewport)
        
        # Check required feature metrics
        required_features = [
            'contrast_score', 'typography_score', 'tap_target_score',
            'overlap_score', 'density_score', 'alignment_score',
            'viewport_width', 'viewport_height', 'is_mobile',
            'total_elements', 'total_issues'
        ]
        
        for feature in required_features:
            assert feature in result.features
    
    def test_error_handling(self):
        """Test error handling for malformed input"""
        # Test with invalid DOM
        result = analyze_visual("invalid html", {}, (1920, 1080))
        
        assert isinstance(result, VisualReport)
        assert result.score >= 0  # Should not crash
        
        # Test with missing css_snapshot keys
        result = analyze_visual("<html><body></body></html>", {}, (1920, 1080))
        
        assert isinstance(result, VisualReport)
        assert result.score >= 0
    
    def test_issue_dataclass_structure(self, contrast_test_data):
        """Test that Issue objects have proper structure"""
        dom, css_snapshot = contrast_test_data
        viewport = (1920, 1080)
        
        result = analyze_visual(dom, css_snapshot, viewport)
        
        if result.issues:
            issue = result.issues[0]
            
            assert hasattr(issue, 'type')
            assert hasattr(issue, 'selector')
            assert hasattr(issue, 'bbox')
            assert hasattr(issue, 'severity')
            assert hasattr(issue, 'message')
            
            assert isinstance(issue.type, str)
            assert isinstance(issue.selector, str)
            assert isinstance(issue.bbox, dict)
            assert isinstance(issue.severity, str)
            assert isinstance(issue.message, str)
            
            # Check severity values
            assert issue.severity in ['high', 'medium', 'low']
            
            # Check bbox structure
            if issue.bbox:
                bbox_keys = ['x', 'y', 'width', 'height']
                for key in bbox_keys:
                    if key in issue.bbox:
                        assert isinstance(issue.bbox[key], (int, float))


if __name__ == "__main__":
    pytest.main([__file__])