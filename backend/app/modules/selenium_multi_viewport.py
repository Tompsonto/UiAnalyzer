"""
Multi-Viewport Selenium Renderer - Replaces Playwright multi-viewport functionality
"""
import asyncio
import time
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import json

from app.modules.selenium_renderer import SeleniumRenderer, SeleniumRenderResult

logger = logging.getLogger(__name__)


@dataclass
class MultiViewportSeleniumReport:
    """Report containing results from multiple viewport/timing combinations"""
    results: List[SeleniumRenderResult]
    total_processing_time: float
    cache_hit: bool = False
    
    
class SeleniumMultiViewportRenderer:
    """Multi-viewport rendering using Selenium WebDriver"""
    
    VIEWPORT_CONFIGS = {
        'desktop': {'width': 1440, 'height': 900},
        'tablet': {'width': 834, 'height': 1112},
        'mobile': {'width': 390, 'height': 844}
    }
    
    TIMING_CONFIGS = {
        'T1': {'wait_time': 2, 'description': 'Fast load'},
        'T2': {'wait_time': 5, 'description': 'Complete load'}
    }
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=3)  # Limit concurrent browsers
    
    async def render_multi_viewport(
        self, 
        url: str, 
        viewports: List[str] = None, 
        timings: List[str] = None,
        use_cache: bool = False  # Cache not implemented yet, for compatibility
    ) -> MultiViewportSeleniumReport:
        """
        Render website across multiple viewport and timing combinations
        
        Args:
            url: URL to render
            viewports: List of viewport names ('desktop', 'tablet', 'mobile')
            timings: List of timing names ('T1', 'T2')  
            use_cache: Cache flag (not implemented, for compatibility)
            
        Returns:
            MultiViewportSeleniumReport with all rendering results
        """
        start_time = time.time()
        
        # Default configurations
        if viewports is None:
            viewports = ['desktop', 'mobile']
        if timings is None:
            timings = ['T1']
            
        logger.info(f"Starting multi-viewport rendering for {url}")
        logger.info(f"Viewports: {viewports}, Timings: {timings}")
        
        # Generate all combinations
        combinations = [
            (viewport, timing) 
            for viewport in viewports 
            for timing in timings
        ]
        
        # Run renderings in parallel using thread pool
        tasks = []
        loop = asyncio.get_event_loop()
        
        for viewport, timing in combinations:
            task = loop.run_in_executor(
                self.executor,
                self._render_single_combination,
                url, viewport, timing
            )
            tasks.append(task)
        
        try:
            # Wait for all renderings to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and filter out exceptions
            successful_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    viewport, timing = combinations[i]
                    logger.error(f"Rendering failed for {viewport}/{timing}: {result}")
                else:
                    successful_results.append(result)
            
            total_time = time.time() - start_time
            
            logger.info(f"Multi-viewport rendering completed in {total_time:.2f}s")
            logger.info(f"Successful renders: {len(successful_results)}/{len(combinations)}")
            
            return MultiViewportSeleniumReport(
                results=successful_results,
                total_processing_time=total_time,
                cache_hit=False  # No caching implemented yet
            )
            
        except Exception as e:
            logger.error(f"Multi-viewport rendering failed: {e}")
            raise Exception(f"Multi-viewport rendering failed: {str(e)}")
    
    def _render_single_combination(self, url: str, viewport: str, timing: str) -> SeleniumRenderResult:
        """
        Render single viewport/timing combination (runs in thread)
        
        Args:
            url: URL to render
            viewport: Viewport name
            timing: Timing name
            
        Returns:
            SeleniumRenderResult for this combination
        """
        try:
            # Get viewport configuration
            viewport_config = self.VIEWPORT_CONFIGS.get(viewport, self.VIEWPORT_CONFIGS['desktop'])
            timing_config = self.TIMING_CONFIGS.get(timing, self.TIMING_CONFIGS['T1'])
            
            logger.info(f"Rendering {viewport}/{timing} for {url}")
            
            # Create renderer with specific viewport
            with SeleniumRenderer(
                viewport_width=viewport_config['width'],
                viewport_height=viewport_config['height']
            ) as renderer:
                
                # Render with specific timing
                result = renderer.render_website(url, wait_time=timing_config['wait_time'])
                
                # Add viewport and timing info to result
                result.viewport = viewport
                result.timing = timing
                
                logger.info(f"Successfully rendered {viewport}/{timing}")
                return result
                
        except Exception as e:
            logger.error(f"Single combination rendering failed for {viewport}/{timing}: {e}")
            raise Exception(f"Rendering failed for {viewport}/{timing}: {str(e)}")
    
    def __del__(self):
        """Clean up thread pool"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)


# Convenience function to maintain API compatibility
async def render_multi_viewport_selenium(
    url: str,
    viewports: List[str] = None,
    timings: List[str] = None, 
    use_cache: bool = False
) -> MultiViewportSeleniumReport:
    """
    Convenience function for multi-viewport rendering with Selenium
    
    Maintains API compatibility with the Playwright version
    """
    renderer = SeleniumMultiViewportRenderer()
    return await renderer.render_multi_viewport(url, viewports, timings, use_cache)


# Test function
async def test_multi_viewport_rendering():
    """Test function for multi-viewport rendering"""
    try:
        url = "https://example.com"
        
        logger.info("Testing multi-viewport Selenium rendering...")
        
        result = await render_multi_viewport_selenium(
            url,
            viewports=['desktop', 'mobile'],
            timings=['T1'],
            use_cache=False
        )
        
        print(f"Rendering completed in {result.total_processing_time:.2f}s")
        print(f"Results: {len(result.results)}")
        
        for res in result.results:
            print(f"- {res.viewport}/{res.timing}: {len(res.element_bounding_boxes)} elements, "
                  f"screenshot: {'✓' if res.screenshot_base64 else '✗'}")
            
        return result
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise


if __name__ == "__main__":
    # Run test
    import asyncio
    asyncio.run(test_multi_viewport_rendering())