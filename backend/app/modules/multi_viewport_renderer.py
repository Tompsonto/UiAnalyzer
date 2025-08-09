"""
Multi-Viewport Website Renderer with Redis Caching
Extends rendering capabilities to support multiple viewports and timing scenarios
"""

import asyncio
import json
import time
import hashlib
from dataclasses import dataclass, field
from typing import Dict, Optional, Any, List, Tuple, NamedTuple
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError
import base64
from urllib.parse import urlparse
import logging
import redis
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ViewportConfig(NamedTuple):
    """Viewport configuration"""
    name: str
    width: int
    height: int
    is_mobile: bool


class TimingConfig(NamedTuple):
    """Timing configuration for different capture points"""
    name: str
    wait_time_ms: int
    description: str


@dataclass
class ViewportRenderResult:
    """Results for a single viewport at a single timing"""
    viewport: str
    timing: str
    dom_content: str
    computed_styles: Dict[str, Any]
    element_bounding_boxes: List[Dict[str, Any]]
    fold_position: int
    screenshot_base64: str
    render_metrics: Dict[str, Any]


@dataclass
class MultiViewportReport:
    """Complete multi-viewport rendering report"""
    url: str
    results: List[ViewportRenderResult] = field(default_factory=list)
    total_processing_time: float = 0
    cache_hit: bool = False
    cache_key: str = ""


class MultiViewportRenderer:
    """Enhanced renderer with multi-viewport and timing support"""
    
    # Standard viewport configurations
    VIEWPORTS = {
        'desktop': ViewportConfig('desktop', 1440, 900, False),
        'tablet': ViewportConfig('tablet', 834, 1112, True),
        'mobile': ViewportConfig('mobile', 390, 844, True)
    }
    
    # Timing configurations
    TIMINGS = {
        'T1': TimingConfig('T1', 1200, 'Early capture after 1.2s'),
        'T2': TimingConfig('T2', 5000, 'Late capture after network idle')
    }
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.browser: Optional[Browser] = None
        self.playwright = None
        self.redis_client = None
        self.cache_enabled = True
        self.cache_ttl = 6 * 60 * 60  # 6 hours
        
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=False)
            # Test connection
            self.redis_client.ping()
        except Exception as e:
            logger.warning(f"Redis not available, caching disabled: {e}")
            self.cache_enabled = False
    
    async def __aenter__(self):
        """Initialize Playwright with optimized settings"""
        self.playwright = await async_playwright().start()
        
        # Launch browser with optimized flags
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-javascript-harmony-shipping',
                '--disable-background-networking',
                '--disable-background-timer-throttling',
                '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows',
                '--disable-client-side-phishing-detection',
                '--disable-default-apps',
                '--disable-hang-monitor',
                '--disable-popup-blocking',
                '--disable-prompt-on-repost',
                '--disable-sync',
                '--disable-translate',
                '--metrics-recording-only',
                '--no-first-run',
                '--safebrowsing-disable-auto-update',
                '--enable-automation',
                '--password-store=basic',
                '--use-mock-keychain'
            ]
        )
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        if self.redis_client:
            self.redis_client.close()
    
    async def render_multi_viewport(
        self, 
        url: str, 
        viewports: List[str] = None,
        timings: List[str] = None,
        use_cache: bool = True
    ) -> MultiViewportReport:
        """
        Render website across multiple viewports and timing scenarios
        
        Args:
            url: URL to render
            viewports: List of viewport names (default: all)
            timings: List of timing names (default: all)
            use_cache: Whether to use Redis caching
            
        Returns:
            MultiViewportReport with results for each viewport/timing combination
        """
        start_time = time.time()
        
        # Default to all viewports and timings if not specified
        if viewports is None:
            viewports = list(self.VIEWPORTS.keys())
        if timings is None:
            timings = list(self.TIMINGS.keys())
        
        # Generate cache key
        cache_key = self._generate_cache_key(url, viewports, timings)
        
        # Try cache first
        if use_cache and self.cache_enabled:
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                logger.info(f"Cache hit for {url}")
                return cached_result
        
        # Render for all viewport/timing combinations
        results = []
        
        for viewport_name in viewports:
            if viewport_name not in self.VIEWPORTS:
                logger.warning(f"Unknown viewport: {viewport_name}")
                continue
                
            viewport_config = self.VIEWPORTS[viewport_name]
            
            for timing_name in timings:
                if timing_name not in self.TIMINGS:
                    logger.warning(f"Unknown timing: {timing_name}")
                    continue
                    
                timing_config = self.TIMINGS[timing_name]
                
                try:
                    result = await self._render_single_viewport_timing(
                        url, viewport_config, timing_config
                    )
                    results.append(result)
                except Exception as e:
                    logger.error(f"Failed to render {viewport_name}/{timing_name} for {url}: {e}")
                    # Add error result
                    results.append(ViewportRenderResult(
                        viewport=viewport_name,
                        timing=timing_name,
                        dom_content="",
                        computed_styles={},
                        element_bounding_boxes=[],
                        fold_position=0,
                        screenshot_base64="",
                        render_metrics={"error": str(e)}
                    ))
        
        # Create report
        report = MultiViewportReport(
            url=url,
            results=results,
            total_processing_time=time.time() - start_time,
            cache_hit=False,
            cache_key=cache_key
        )
        
        # Cache the result
        if use_cache and self.cache_enabled and results:
            self._save_to_cache(cache_key, report)
        
        return report
    
    async def _render_single_viewport_timing(
        self, 
        url: str, 
        viewport: ViewportConfig, 
        timing: TimingConfig
    ) -> ViewportRenderResult:
        """Render a single viewport at a specific timing"""
        
        # Create new context for this viewport
        context = await self.browser.new_context(
            viewport={'width': viewport.width, 'height': viewport.height},
            user_agent=self._get_user_agent(viewport.is_mobile),
            java_script_enabled=True,
            accept_downloads=False,
            has_touch=viewport.is_mobile,
            is_mobile=viewport.is_mobile,
            locale='en-US',
            timezone_id='America/New_York'
        )
        
        page = await context.new_page()
        
        try:
            # Navigate to URL
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # Wait for specific timing
            if timing.name == 'T1':
                # Early capture - wait 1200ms
                await asyncio.sleep(timing.wait_time_ms / 1000)
            elif timing.name == 'T2':
                # Late capture - wait for network idle, then additional time
                try:
                    await page.wait_for_load_state('networkidle', timeout=10000)
                    await asyncio.sleep(2)  # Additional 2 seconds after network idle
                except:
                    # Fallback to just waiting 5 seconds
                    await asyncio.sleep(timing.wait_time_ms / 1000)
            
            # Collect render metrics
            render_start = time.time()
            
            # Extract comprehensive data
            dom_content = await page.content()
            computed_styles = await self._extract_computed_styles(page)
            element_boxes = await self._extract_element_bounding_boxes(page)
            fold_position = viewport.height
            
            # Take screenshot
            screenshot_bytes = await page.screenshot(type='png', full_page=False)
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode()
            
            render_time = time.time() - render_start
            
            # Performance metrics
            performance_metrics = await page.evaluate("""
                () => {
                    const nav = performance.getEntriesByType('navigation')[0];
                    return {
                        dom_content_loaded: nav ? nav.domContentLoadedEventEnd - nav.domContentLoadedEventStart : 0,
                        load_complete: nav ? nav.loadEventEnd - nav.loadEventStart : 0,
                        first_paint: nav ? nav.responseEnd - nav.requestStart : 0
                    };
                }
            """)
            
            return ViewportRenderResult(
                viewport=viewport.name,
                timing=timing.name,
                dom_content=dom_content,
                computed_styles=computed_styles,
                element_bounding_boxes=element_boxes,
                fold_position=fold_position,
                screenshot_base64=screenshot_base64,
                render_metrics={
                    'render_time': render_time,
                    'viewport_width': viewport.width,
                    'viewport_height': viewport.height,
                    'timing_ms': timing.wait_time_ms,
                    'performance': performance_metrics
                }
            )
            
        finally:
            await page.close()
            await context.close()
    
    async def _extract_computed_styles(self, page: Page) -> Dict[str, Any]:
        """Extract computed styles for key elements"""
        return await page.evaluate("""
            () => {
                const computedStyles = {};
                const keyElements = document.querySelectorAll('body, h1, h2, h3, button, a, .btn, .cta, p');
                
                keyElements.forEach((el, index) => {
                    if (index < 30) { // Limit to prevent too much data
                        const style = window.getComputedStyle(el);
                        const selector = el.tagName.toLowerCase() + (el.className ? '.' + el.className.split(' ')[0] : '') + `:nth(${index})`;
                        
                        computedStyles[selector] = {
                            fontFamily: style.fontFamily,
                            fontSize: style.fontSize,
                            fontWeight: style.fontWeight,
                            lineHeight: style.lineHeight,
                            color: style.color,
                            backgroundColor: style.backgroundColor,
                            margin: style.margin,
                            padding: style.padding,
                            border: style.border,
                            borderRadius: style.borderRadius,
                            display: style.display,
                            position: style.position,
                            zIndex: style.zIndex
                        };
                    }
                });
                
                return computedStyles;
            }
        """)
    
    async def _extract_element_bounding_boxes(self, page: Page) -> List[Dict[str, Any]]:
        """Extract bounding boxes for all significant elements"""
        return await page.evaluate("""
            () => {
                const elements = [];
                const selectors = [
                    'h1, h2, h3, h4, h5, h6',
                    'p, span, div',
                    'button, a',
                    'input, textarea, select',
                    'img',
                    '.btn, .cta, .button'
                ];
                
                const allElements = new Set();
                
                selectors.forEach(selector => {
                    try {
                        document.querySelectorAll(selector).forEach(el => allElements.add(el));
                    } catch (e) {
                        // Skip invalid selectors
                    }
                });
                
                Array.from(allElements).slice(0, 100).forEach((element, index) => {
                    const rect = element.getBoundingClientRect();
                    const style = window.getComputedStyle(element);
                    
                    if (rect.width > 0 && rect.height > 0) {
                        elements.push({
                            selector: element.tagName.toLowerCase() + (element.id ? '#' + element.id : '') + `:nth(${index})`,
                            bbox: {
                                x: Math.round(rect.x + window.scrollX),
                                y: Math.round(rect.y + window.scrollY),
                                width: Math.round(rect.width),
                                height: Math.round(rect.height)
                            },
                            text: element.textContent?.trim().substring(0, 100) || '',
                            visible: style.visibility !== 'hidden' && style.display !== 'none',
                            above_fold: rect.top < window.innerHeight
                        });
                    }
                });
                
                return elements;
            }
        """)
    
    def _get_user_agent(self, is_mobile: bool) -> str:
        """Get appropriate user agent for viewport"""
        if is_mobile:
            return 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1 ClarityCheck/1.0'
        else:
            return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 ClarityCheck/1.0'
    
    def _generate_cache_key(self, url: str, viewports: List[str], timings: List[str]) -> str:
        """Generate cache key for URL + viewport + timing combination"""
        key_data = f"{url}|{','.join(sorted(viewports))}|{','.join(sorted(timings))}"
        return f"mvr:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[MultiViewportReport]:
        """Get cached result"""
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                data = json.loads(cached_data.decode())
                
                # Reconstruct objects
                results = []
                for result_data in data['results']:
                    results.append(ViewportRenderResult(
                        viewport=result_data['viewport'],
                        timing=result_data['timing'],
                        dom_content=result_data['dom_content'],
                        computed_styles=result_data['computed_styles'],
                        element_bounding_boxes=result_data['element_bounding_boxes'],
                        fold_position=result_data['fold_position'],
                        screenshot_base64=result_data['screenshot_base64'],
                        render_metrics=result_data['render_metrics']
                    ))
                
                report = MultiViewportReport(
                    url=data['url'],
                    results=results,
                    total_processing_time=data['total_processing_time'],
                    cache_hit=True,
                    cache_key=cache_key
                )
                
                return report
                
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")
            
        return None
    
    def _save_to_cache(self, cache_key: str, report: MultiViewportReport):
        """Save result to cache"""
        try:
            # Convert to serializable format
            data = {
                'url': report.url,
                'total_processing_time': report.total_processing_time,
                'results': []
            }
            
            for result in report.results:
                data['results'].append({
                    'viewport': result.viewport,
                    'timing': result.timing,
                    'dom_content': result.dom_content,
                    'computed_styles': result.computed_styles,
                    'element_bounding_boxes': result.element_bounding_boxes,
                    'fold_position': result.fold_position,
                    'screenshot_base64': result.screenshot_base64,
                    'render_metrics': result.render_metrics
                })
            
            # Save to Redis with TTL
            self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(data)
            )
            
        except Exception as e:
            logger.warning(f"Cache save failed: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.cache_enabled:
            return {"enabled": False}
        
        try:
            info = self.redis_client.info()
            return {
                "enabled": True,
                "connected_clients": info.get('connected_clients', 0),
                "used_memory": info.get('used_memory_human', 'unknown'),
                "keyspace_hits": info.get('keyspace_hits', 0),
                "keyspace_misses": info.get('keyspace_misses', 0)
            }
        except:
            return {"enabled": False, "error": "Redis connection failed"}


# Convenience function
async def render_multi_viewport(
    url: str,
    viewports: List[str] = None,
    timings: List[str] = None,
    use_cache: bool = True
) -> MultiViewportReport:
    """Convenience function for multi-viewport rendering"""
    async with MultiViewportRenderer() as renderer:
        return await renderer.render_multi_viewport(url, viewports, timings, use_cache)


# Performance benchmark helper
async def benchmark_rendering(url: str, iterations: int = 3) -> Dict[str, Any]:
    """Benchmark rendering performance"""
    results = {
        'url': url,
        'iterations': iterations,
        'timings': [],
        'average_time': 0,
        'cache_performance': {}
    }
    
    async with MultiViewportRenderer() as renderer:
        # First run (cache miss)
        start_time = time.time()
        report1 = await renderer.render_multi_viewport(url, use_cache=True)
        first_run_time = time.time() - start_time
        results['timings'].append(first_run_time)
        
        # Subsequent runs (should hit cache)
        for i in range(iterations - 1):
            start_time = time.time()
            report = await renderer.render_multi_viewport(url, use_cache=True)
            run_time = time.time() - start_time
            results['timings'].append(run_time)
        
        results['average_time'] = sum(results['timings']) / len(results['timings'])
        results['cache_performance'] = {
            'first_run_time': first_run_time,
            'subsequent_avg': sum(results['timings'][1:]) / max(1, len(results['timings']) - 1),
            'cache_speedup': first_run_time / (sum(results['timings'][1:]) / max(1, len(results['timings']) - 1)) if len(results['timings']) > 1 else 1
        }
        
        results['cache_stats'] = renderer.get_cache_stats()
    
    return results