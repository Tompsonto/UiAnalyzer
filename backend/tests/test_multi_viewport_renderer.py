"""
Tests for multi-viewport renderer module
"""

import asyncio
import pytest
import tempfile
import os
import json
from unittest.mock import Mock, patch
from app.modules.multi_viewport_renderer import (
    MultiViewportRenderer, 
    render_multi_viewport,
    benchmark_rendering,
    ViewportConfig, 
    TimingConfig,
    ViewportRenderResult,
    MultiViewportReport
)

# Simple test HTML
TEST_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Multi-Viewport Test Page</title>
    <style>
        body { margin: 0; padding: 20px; font-family: Arial, sans-serif; }
        .desktop-only { display: block; }
        .mobile-only { display: none; }
        
        @media (max-width: 768px) {
            .desktop-only { display: none; }
            .mobile-only { display: block; }
        }
        
        .cta-button {
            background: #007bff;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
        }
        
        .content-section {
            margin: 20px 0;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <h1>Multi-Viewport Test Page</h1>
    
    <div class="desktop-only">
        <h2>Desktop Content</h2>
        <p>This content is only visible on desktop viewports.</p>
    </div>
    
    <div class="mobile-only">
        <h2>Mobile Content</h2>
        <p>This content is only visible on mobile viewports.</p>
    </div>
    
    <div class="content-section">
        <h3>Universal Content</h3>
        <p>This content is visible across all viewports.</p>
        <button class="cta-button">Call to Action</button>
    </div>
    
    <div class="content-section">
        <h3>Another Section</h3>
        <p>More content to test element detection and bounding boxes.</p>
        <a href="#" class="cta-button" style="display: inline-block; text-decoration: none;">Link CTA</a>
    </div>
    
    <!-- Add some content to test fold calculation -->
    <div style="height: 800px; background: linear-gradient(to bottom, #f0f0f0, #e0e0e0);">
        <p style="padding-top: 400px; text-align: center;">Below the fold content</p>
    </div>
</body>
</html>
"""


@pytest.fixture
def test_html_file():
    """Create a temporary HTML file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(TEST_HTML)
        f.flush()
        file_path = f.name
    
    yield f"file://{file_path}"
    
    # Cleanup
    try:
        os.unlink(file_path)
    except OSError:
        pass


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing caching"""
    with patch('redis.from_url') as mock_redis:
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.get.return_value = None
        mock_client.setex.return_value = True
        mock_redis.return_value = mock_client
        yield mock_client


class TestMultiViewportRenderer:
    """Test cases for MultiViewportRenderer"""
    
    @pytest.mark.asyncio
    async def test_basic_multi_viewport_rendering(self, test_html_file):
        """Test basic multi-viewport rendering functionality"""
        async with MultiViewportRenderer() as renderer:
            report = await renderer.render_multi_viewport(
                test_html_file,
                viewports=['desktop', 'mobile'],
                timings=['T1'],
                use_cache=False
            )
            
            # Should be a MultiViewportReport
            assert isinstance(report, MultiViewportReport)
            assert report.url == test_html_file
            
            # Should have results for both viewports
            assert len(report.results) == 2  # desktop + mobile
            
            # Check viewport names
            viewport_names = {result.viewport for result in report.results}
            assert viewport_names == {'desktop', 'mobile'}
            
            # Should have processing time
            assert report.total_processing_time > 0
    
    @pytest.mark.asyncio
    async def test_viewport_configurations(self, test_html_file):
        """Test different viewport configurations"""
        async with MultiViewportRenderer() as renderer:
            # Test all viewports
            report = await renderer.render_multi_viewport(
                test_html_file,
                viewports=['desktop', 'tablet', 'mobile'],
                timings=['T1'],
                use_cache=False
            )
            
            assert len(report.results) == 3
            
            # Check each result has proper structure
            for result in report.results:
                assert isinstance(result, ViewportRenderResult)
                assert result.viewport in ['desktop', 'tablet', 'mobile']
                assert result.timing == 'T1'
                assert result.dom_content  # Should have DOM content
                assert isinstance(result.computed_styles, dict)
                assert isinstance(result.element_bounding_boxes, list)
                assert result.fold_position > 0
                assert result.screenshot_base64  # Should have screenshot
                assert isinstance(result.render_metrics, dict)
    
    @pytest.mark.asyncio
    async def test_timing_configurations(self, test_html_file):
        """Test different timing configurations"""
        async with MultiViewportRenderer() as renderer:
            report = await renderer.render_multi_viewport(
                test_html_file,
                viewports=['desktop'],
                timings=['T1', 'T2'],
                use_cache=False
            )
            
            assert len(report.results) == 2  # T1 + T2
            
            timing_names = {result.timing for result in report.results}
            assert timing_names == {'T1', 'T2'}
            
            # T2 should generally take longer to process than T1
            t1_result = next(r for r in report.results if r.timing == 'T1')
            t2_result = next(r for r in report.results if r.timing == 'T2')
            
            # Both should have valid render metrics
            assert 'render_time' in t1_result.render_metrics
            assert 'render_time' in t2_result.render_metrics
    
    @pytest.mark.asyncio
    async def test_element_bounding_boxes(self, test_html_file):
        """Test element bounding box extraction"""
        async with MultiViewportRenderer() as renderer:
            report = await renderer.render_multi_viewport(
                test_html_file,
                viewports=['desktop'],
                timings=['T1'],
                use_cache=False
            )
            
            result = report.results[0]
            boxes = result.element_bounding_boxes
            
            # Should have detected multiple elements
            assert len(boxes) > 5
            
            # Check box structure
            for box in boxes[:3]:  # Check first few
                assert 'selector' in box
                assert 'bbox' in box
                assert 'text' in box
                assert 'visible' in box
                assert 'above_fold' in box
                
                # Bounding box should have coordinates
                bbox = box['bbox']
                assert 'x' in bbox and 'y' in bbox
                assert 'width' in bbox and 'height' in bbox
                assert bbox['width'] >= 0 and bbox['height'] >= 0
    
    @pytest.mark.asyncio
    async def test_computed_styles_extraction(self, test_html_file):
        """Test computed styles extraction"""
        async with MultiViewportRenderer() as renderer:
            report = await renderer.render_multi_viewport(
                test_html_file,
                viewports=['desktop'],
                timings=['T1'],
                use_cache=False
            )
            
            result = report.results[0]
            styles = result.computed_styles
            
            # Should have extracted styles for multiple elements
            assert len(styles) > 3
            
            # Check style structure
            for selector, style_dict in list(styles.items())[:2]:
                assert isinstance(style_dict, dict)
                
                # Should have key CSS properties
                expected_properties = ['fontSize', 'color', 'backgroundColor', 'fontFamily']
                for prop in expected_properties:
                    assert prop in style_dict
    
    @pytest.mark.asyncio
    async def test_screenshot_generation(self, test_html_file):
        """Test screenshot generation for different viewports"""
        async with MultiViewportRenderer() as renderer:
            report = await renderer.render_multi_viewport(
                test_html_file,
                viewports=['desktop', 'mobile'],
                timings=['T1'],
                use_cache=False
            )
            
            for result in report.results:
                # Should have base64 screenshot
                assert result.screenshot_base64
                assert len(result.screenshot_base64) > 1000  # Should be substantial data
                
                # Should be valid base64
                import base64
                try:
                    base64.b64decode(result.screenshot_base64)
                except Exception:
                    pytest.fail(f"Invalid base64 screenshot for {result.viewport}")
    
    @pytest.mark.asyncio
    async def test_caching_functionality(self, test_html_file, mock_redis):
        """Test Redis caching functionality"""
        async with MultiViewportRenderer() as renderer:
            # First call - should cache
            report1 = await renderer.render_multi_viewport(
                test_html_file,
                viewports=['desktop'],
                timings=['T1'],
                use_cache=True
            )
            
            assert not report1.cache_hit  # First call shouldn't be cache hit
            
            # Mock cache hit for second call
            mock_redis.get.return_value = json.dumps({
                'url': test_html_file,
                'total_processing_time': 1.0,
                'results': [{
                    'viewport': 'desktop',
                    'timing': 'T1',
                    'dom_content': '<html></html>',
                    'computed_styles': {},
                    'element_bounding_boxes': [],
                    'fold_position': 900,
                    'screenshot_base64': 'dGVzdA==',
                    'render_metrics': {'test': True}
                }]
            }).encode()
            
            # Second call - should hit cache
            report2 = await renderer.render_multi_viewport(
                test_html_file,
                viewports=['desktop'],
                timings=['T1'],
                use_cache=True
            )
            
            assert report2.cache_hit  # Should be cache hit
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling for invalid URLs"""
        async with MultiViewportRenderer() as renderer:
            report = await renderer.render_multi_viewport(
                "invalid-url",
                viewports=['desktop'],
                timings=['T1'],
                use_cache=False
            )
            
            # Should have error results
            assert len(report.results) == 1
            result = report.results[0]
            assert 'error' in result.render_metrics
    
    @pytest.mark.asyncio
    async def test_cache_key_generation(self):
        """Test cache key generation"""
        async with MultiViewportRenderer() as renderer:
            key1 = renderer._generate_cache_key("http://example.com", ['desktop'], ['T1'])
            key2 = renderer._generate_cache_key("http://example.com", ['desktop'], ['T2'])
            key3 = renderer._generate_cache_key("http://example.com", ['mobile'], ['T1'])
            
            # Different parameters should generate different keys
            assert key1 != key2
            assert key1 != key3
            assert key2 != key3
            
            # Same parameters should generate same key
            key4 = renderer._generate_cache_key("http://example.com", ['desktop'], ['T1'])
            assert key1 == key4


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    @pytest.mark.asyncio
    async def test_render_multi_viewport_function(self, test_html_file):
        """Test the convenience function"""
        report = await render_multi_viewport(
            test_html_file,
            viewports=['desktop'],
            timings=['T1'],
            use_cache=False
        )
        
        assert isinstance(report, MultiViewportReport)
        assert len(report.results) == 1
    
    @pytest.mark.asyncio 
    async def test_benchmark_function(self, test_html_file):
        """Test benchmarking functionality"""
        # Use a small number of iterations for testing
        benchmark_result = await benchmark_rendering(test_html_file, iterations=2)
        
        assert 'url' in benchmark_result
        assert 'iterations' in benchmark_result
        assert 'timings' in benchmark_result
        assert 'average_time' in benchmark_result
        assert 'cache_performance' in benchmark_result
        
        assert len(benchmark_result['timings']) == 2
        assert benchmark_result['average_time'] > 0


class TestDataStructures:
    """Test data structure classes"""
    
    def test_viewport_config(self):
        """Test ViewportConfig"""
        config = ViewportConfig('test', 1024, 768, False)
        assert config.name == 'test'
        assert config.width == 1024
        assert config.height == 768
        assert config.is_mobile == False
    
    def test_timing_config(self):
        """Test TimingConfig"""
        config = TimingConfig('test', 1000, 'Test timing')
        assert config.name == 'test'
        assert config.wait_time_ms == 1000
        assert config.description == 'Test timing'
    
    def test_viewport_render_result(self):
        """Test ViewportRenderResult"""
        result = ViewportRenderResult(
            viewport='desktop',
            timing='T1',
            dom_content='<html></html>',
            computed_styles={'body': {'color': 'black'}},
            element_bounding_boxes=[{'selector': 'body', 'bbox': {'x': 0, 'y': 0, 'width': 100, 'height': 100}}],
            fold_position=800,
            screenshot_base64='dGVzdA==',
            render_metrics={'time': 1.0}
        )
        
        assert result.viewport == 'desktop'
        assert result.timing == 'T1'
        assert 'html' in result.dom_content
        assert len(result.computed_styles) == 1
        assert len(result.element_bounding_boxes) == 1


if __name__ == "__main__":
    # Run a simple test
    async def simple_test():
        print("Running simple multi-viewport test...")
        
        # Create sample HTML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(TEST_HTML)
            f.flush()
            file_url = f"file://{f.name}"
        
        try:
            report = await render_multi_viewport(
                file_url,
                viewports=['desktop', 'mobile'],
                timings=['T1'],
                use_cache=False
            )
            
            print(f"Rendered {len(report.results)} viewport/timing combinations")
            print(f"Total processing time: {report.total_processing_time:.2f}s")
            
            for result in report.results:
                print(f"- {result.viewport}/{result.timing}: {len(result.element_bounding_boxes)} elements detected")
                
        finally:
            os.unlink(f.name)
    
    asyncio.run(simple_test())