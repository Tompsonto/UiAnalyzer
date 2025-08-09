"""
Enhanced Website Renderer Module - Uses Playwright to render and capture comprehensive website data
"""
import asyncio
import json
import time
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError
from typing import Dict, Optional, Any, List, Tuple
import base64
from urllib.parse import urlparse, urljoin
import logging
import hashlib

from app.core.config import settings

logger = logging.getLogger(__name__)

class WebsiteRenderer:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.playwright = None
        self.context = None
    
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
                '--window-size=1920,1080',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-images',  # Disable image loading for faster rendering
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
        
        # Create browser context with specific settings
        self.context = await self.browser.new_context(
            viewport={'width': settings.VIEWPORT_WIDTH, 'height': settings.VIEWPORT_HEIGHT},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 ClarityCheck/1.0',
            java_script_enabled=True,
            accept_downloads=False,
            has_touch=False,
            is_mobile=False,
            locale='en-US',
            timezone_id='America/New_York'
        )
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def render_website(self, url: str, retry_count: int = 2) -> Dict[str, Any]:
        """
        Enhanced website rendering with retry mechanism and comprehensive data extraction
        """
        start_time = time.time()
        
        for attempt in range(retry_count + 1):
            try:
                # Validate and normalize URL
                normalized_url = self._normalize_url(url)
                parsed = urlparse(normalized_url)
                
                if not parsed.scheme or not parsed.netloc:
                    raise ValueError(f"Invalid URL format: {url}")
                
                if not self.context:
                    raise RuntimeError("Browser context not initialized")
                
                logger.info(f"Rendering website: {normalized_url} (attempt {attempt + 1}/{retry_count + 1})")
                
                # Create new page with enhanced settings
                page = await self.context.new_page()
                
                # Set timeouts
                page.set_default_timeout(settings.PLAYWRIGHT_TIMEOUT)
                page.set_default_navigation_timeout(settings.PLAYWRIGHT_TIMEOUT)
                
                # Block unnecessary resources for faster loading
                await page.route("**/*", self._route_handler)
                
                # Navigate to URL with enhanced wait conditions
                response = await page.goto(
                    normalized_url, 
                    wait_until='domcontentloaded',
                    timeout=settings.PLAYWRIGHT_TIMEOUT
                )
                
                if not response or response.status >= 400:
                    raise Exception(f"HTTP {response.status if response else 'No response'}: Failed to load {normalized_url}")
                
                # Wait for page stability
                await self._wait_for_page_stability(page)
                
                # Extract comprehensive data
                result = await self._extract_comprehensive_data(page, normalized_url)
                
                # Add performance metrics
                result['performance'] = {
                    'render_time': time.time() - start_time,
                    'attempts': attempt + 1,
                    'final_url': page.url,
                    'response_status': response.status if response else None
                }
                
                await page.close()
                return result
                
            except PlaywrightTimeoutError as e:
                logger.warning(f"Timeout on attempt {attempt + 1} for {url}: {str(e)}")
                if attempt == retry_count:
                    raise Exception(f"Timeout after {retry_count + 1} attempts: {str(e)}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
            except Exception as e:
                logger.error(f"Error on attempt {attempt + 1} for {url}: {str(e)}")
                if attempt == retry_count:
                    raise Exception(f"Failed after {retry_count + 1} attempts: {str(e)}")
                await asyncio.sleep(2 ** attempt)
    
    async def _route_handler(self, route):
        """Enhanced route handler to block unnecessary resources"""
        request = route.request
        resource_type = request.resource_type
        
        # Block unnecessary resources for faster loading
        if resource_type in ['image', 'media', 'font', 'websocket']:
            await route.abort()
        # Allow stylesheets, scripts, documents, and XHR for functionality
        elif resource_type in ['stylesheet', 'script', 'document', 'xhr', 'fetch']:
            await route.continue_()
        else:
            await route.continue_()
    
    def _normalize_url(self, url: str) -> str:
        """Normalize and validate URL"""
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    
    async def _wait_for_page_stability(self, page: Page):
        """Wait for page to be stable and interactive"""
        try:
            # Wait for network idle
            await page.wait_for_load_state('networkidle', timeout=10000)
        except:
            pass  # Continue if networkidle fails
        
        try:
            # Wait for DOM content to be loaded
            await page.wait_for_load_state('domcontentloaded', timeout=5000)
        except:
            pass
        
        # Additional wait for dynamic content
        await asyncio.sleep(2)
        
        # Wait for any lazy-loaded content
        try:
            await page.evaluate("""
                () => new Promise(resolve => {
                    if (document.readyState === 'complete') {
                        resolve();
                    } else {
                        window.addEventListener('load', resolve);
                        // Fallback timeout
                        setTimeout(resolve, 3000);
                    }
                })
            """)
        except:
            pass
    
    async def _extract_comprehensive_data(self, page: Page, url: str) -> Dict[str, Any]:
        """Extract comprehensive page data including DOM, CSS, and screenshots"""
        
        # Get basic page metadata
        metadata = await self._extract_metadata(page)
        
        # Get DOM structure and elements
        dom_data = await self._extract_dom_structure(page)
        
        # Get CSS data and computed styles
        css_data = await self._extract_css_data(page)
        
        # Get text content
        text_data = await self._extract_text_content(page)
        
        # Generate multiple screenshot types
        screenshots = await self._generate_screenshots(page)
        
        # Get performance and technical data
        technical_data = await self._extract_technical_data(page)
        
        return {
            'url': url,
            'final_url': page.url,
            **metadata,
            **dom_data,
            **css_data,
            **text_data,
            **screenshots,
            **technical_data,
            'extraction_timestamp': time.time(),
            'page_hash': self._generate_page_hash(page.url, metadata.get('title', ''))
        }
    
    async def _extract_metadata(self, page: Page) -> Dict[str, Any]:
        """Extract page metadata"""
        return await page.evaluate("""
            () => {
                const getMetaContent = (name) => {
                    const meta = document.querySelector(`meta[name="${name}"], meta[property="${name}"]`);
                    return meta ? meta.getAttribute('content') : '';
                };
                
                return {
                    title: document.title || '',
                    meta_description: getMetaContent('description'),
                    meta_keywords: getMetaContent('keywords'),
                    canonical_url: document.querySelector('link[rel="canonical"]')?.href || '',
                    lang: document.documentElement.lang || 'en',
                    charset: document.characterSet || 'UTF-8',
                    viewport: getMetaContent('viewport'),
                    robots: getMetaContent('robots'),
                    og_title: getMetaContent('og:title'),
                    og_description: getMetaContent('og:description'),
                    og_image: getMetaContent('og:image'),
                    favicon: document.querySelector('link[rel*="icon"]')?.href || ''
                };
            }
        """)
    
    async def _extract_dom_structure(self, page: Page) -> Dict[str, Any]:
        """Extract comprehensive DOM structure and elements"""
        return await page.evaluate(f"""
            () => {{
                const viewportHeight = {settings.VIEWPORT_HEIGHT};
                
                // Helper function to get element position and visibility
                const getElementInfo = (el) => {{
                    const rect = el.getBoundingClientRect();
                    const style = window.getComputedStyle(el);
                    
                    return {{
                        visible: rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none',
                        above_fold: rect.top < viewportHeight,
                        position: {{ 
                            x: Math.round(rect.x), 
                            y: Math.round(rect.y), 
                            width: Math.round(rect.width), 
                            height: Math.round(rect.height) 
                        }},
                        z_index: style.zIndex,
                        opacity: style.opacity
                    }};
                }};
                
                // Extract headings with hierarchy
                const headings = [];
                ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'].forEach(tag => {{
                    document.querySelectorAll(tag).forEach((el, index) => {{
                        const info = getElementInfo(el);
                        const text = el.innerText.trim();
                        
                        if (text && info.visible) {{
                            headings.push({{
                                tag: tag.toUpperCase(),
                                level: parseInt(tag[1]),
                                text: text,
                                length: text.length,
                                word_count: text.split(/\\s+/).length,
                                ...info,
                                has_anchor: el.querySelector('a') !== null,
                                id: el.id || '',
                                classes: Array.from(el.classList)
                            }});
                        }}
                    }});
                }});
                
                // Extract CTAs and buttons
                const ctas = [];
                const ctaSelectors = [
                    'button',
                    'input[type="submit"]',
                    'input[type="button"]',
                    'a[href]:not([href^="mailto:"]):not([href^="tel:"])',
                    '.btn', '.button', '.cta',
                    '[role="button"]'
                ];
                
                ctaSelectors.forEach(selector => {{
                    document.querySelectorAll(selector).forEach(el => {{
                        const info = getElementInfo(el);
                        const text = (el.innerText || el.value || el.getAttribute('aria-label') || '').trim();
                        
                        if (text && info.visible && text.length < 100) {{
                            const style = window.getComputedStyle(el);
                            
                            ctas.push({{
                                text: text,
                                tag: el.tagName.toLowerCase(),
                                type: el.type || '',
                                href: el.href || '',
                                ...info,
                                styles: {{
                                    backgroundColor: style.backgroundColor,
                                    color: style.color,
                                    fontSize: style.fontSize,
                                    fontWeight: style.fontWeight,
                                    padding: style.padding,
                                    margin: style.margin,
                                    border: style.border,
                                    borderRadius: style.borderRadius,
                                    textDecoration: style.textDecoration
                                }},
                                classes: Array.from(el.classList),
                                is_primary: el.classList.contains('primary') || el.classList.contains('btn-primary') || 
                                          el.classList.contains('cta-primary') || el.id.includes('primary')
                            }});
                        }}
                    }});
                }});
                
                // Extract forms
                const forms = [];
                document.querySelectorAll('form').forEach(form => {{
                    const info = getElementInfo(form);
                    if (info.visible) {{
                        const inputs = Array.from(form.querySelectorAll('input, select, textarea')).map(input => ({{
                            type: input.type || input.tagName.toLowerCase(),
                            name: input.name || '',
                            placeholder: input.placeholder || '',
                            required: input.required,
                            id: input.id || ''
                        }}));
                        
                        forms.push({{
                            action: form.action || '',
                            method: form.method || 'get',
                            inputs: inputs,
                            input_count: inputs.length,
                            ...info
                        }});
                    }}
                }});
                
                // Extract navigation elements
                const navigation = [];
                document.querySelectorAll('nav, .nav, .navbar, .navigation, [role="navigation"]').forEach(nav => {{
                    const info = getElementInfo(nav);
                    if (info.visible) {{
                        const links = Array.from(nav.querySelectorAll('a')).map(link => ({{
                            text: link.innerText.trim(),
                            href: link.href,
                            external: link.hostname && link.hostname !== window.location.hostname
                        }}));
                        
                        navigation.push({{
                            type: nav.tagName.toLowerCase(),
                            link_count: links.length,
                            links: links.slice(0, 20), // Limit to first 20 links
                            ...info
                        }});
                    }}
                }});
                
                // Extract images
                const images = [];
                document.querySelectorAll('img').forEach(img => {{
                    const info = getElementInfo(img);
                    if (info.visible) {{
                        images.push({{
                            src: img.src,
                            alt: img.alt || '',
                            title: img.title || '',
                            loading: img.loading || '',
                            ...info,
                            natural_width: img.naturalWidth,
                            natural_height: img.naturalHeight,
                            is_lazy: img.loading === 'lazy' || img.getAttribute('data-src') !== null
                        }});
                    }}
                }});
                
                return {{
                    dom_analysis: {{
                        headings: headings,
                        ctas: ctas.slice(0, 50), // Limit CTAs
                        forms: forms,
                        navigation: navigation,
                        images: images.slice(0, 30), // Limit images
                        total_elements: {{
                            headings: headings.length,
                            ctas: ctas.length,
                            forms: forms.length,
                            images: images.length,
                            links: document.querySelectorAll('a').length
                        }}
                    }}
                }};
            }}
        """)
    
    async def _extract_css_data(self, page: Page) -> Dict[str, Any]:
        """Extract CSS data and computed styles"""
        return await page.evaluate("""
            () => {
                const cssData = [];
                const computedStyles = {};
                
                // Extract CSS rules from stylesheets
                try {
                    const sheets = Array.from(document.styleSheets);
                    
                    sheets.forEach((sheet, sheetIndex) => {
                        try {
                            const rules = Array.from(sheet.cssRules || sheet.rules || []);
                            rules.forEach(rule => {
                                if (rule.cssText) {
                                    cssData.push({
                                        sheet_index: sheetIndex,
                                        rule_type: rule.constructor.name,
                                        css_text: rule.cssText,
                                        selector: rule.selectorText || ''
                                    });
                                }
                            });
                        } catch (e) {
                            // Cross-origin stylesheets might not be accessible
                            cssData.push({
                                sheet_index: sheetIndex,
                                error: 'Cross-origin or access denied',
                                href: sheet.href
                            });
                        }
                    });
                } catch (e) {
                    cssData.push({error: 'Failed to extract CSS: ' + e.message});
                }
                
                // Extract computed styles for key elements
                const keyElements = document.querySelectorAll('body, h1, h2, h3, button, a, .btn, .cta');
                keyElements.forEach((el, index) => {
                    if (index < 20) { // Limit to prevent too much data
                        const style = window.getComputedStyle(el);
                        const selector = el.tagName.toLowerCase() + (el.className ? '.' + el.className.split(' ')[0] : '');
                        
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
                
                return {
                    css_data: cssData,
                    computed_styles: computedStyles,
                    stylesheet_count: document.styleSheets.length
                };
            }
        """)
    
    async def _extract_text_content(self, page: Page) -> Dict[str, Any]:
        """Extract clean text content for analysis"""
        return await page.evaluate("""
            () => {
                // Remove script, style, and other non-content elements
                const elementsToRemove = document.querySelectorAll('script, style, noscript, nav, header, footer, .nav, .navbar, .menu');
                const clonedDoc = document.cloneNode(true);
                
                // Clean up cloned document
                clonedDoc.querySelectorAll('script, style, noscript, nav, header, footer, .nav, .navbar, .menu').forEach(el => el.remove());
                
                // Get main content text
                const bodyText = clonedDoc.body ? clonedDoc.body.innerText : '';
                
                // Extract paragraph text separately
                const paragraphs = Array.from(document.querySelectorAll('p')).map(p => p.innerText.trim()).filter(text => text.length > 0);
                
                // Get heading text
                const headingText = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6')).map(h => h.innerText.trim()).join(' ');
                
                return {
                    text_content: bodyText.trim(),
                    paragraph_text: paragraphs.join('\\n\\n'),
                    heading_text: headingText,
                    word_count: bodyText.trim().split(/\\s+/).length,
                    character_count: bodyText.length,
                    paragraph_count: paragraphs.length
                };
            }
        """)
    
    async def _generate_screenshots(self, page: Page) -> Dict[str, Any]:
        """Generate multiple types of screenshots"""
        screenshots = {}
        
        try:
            # Full page screenshot
            full_screenshot = await page.screenshot(
                type='png',
                full_page=True,
                quality=85
            )
            screenshots['full_page'] = base64.b64encode(full_screenshot).decode()
            
            # Viewport screenshot (above the fold)
            viewport_screenshot = await page.screenshot(
                type='png',
                full_page=False,
                quality=85
            )
            screenshots['viewport'] = base64.b64encode(viewport_screenshot).decode()
            
            # Mobile viewport screenshot
            await page.set_viewport_size({"width": 375, "height": 667})  # iPhone viewport
            mobile_screenshot = await page.screenshot(
                type='png',
                full_page=False,
                quality=85
            )
            screenshots['mobile_viewport'] = base64.b64encode(mobile_screenshot).decode()
            
            # Reset viewport
            await page.set_viewport_size({"width": settings.VIEWPORT_WIDTH, "height": settings.VIEWPORT_HEIGHT})
            
        except Exception as e:
            logger.error(f"Screenshot generation error: {str(e)}")
            screenshots['error'] = str(e)
        
        return {'screenshots': screenshots}
    
    async def _extract_technical_data(self, page: Page) -> Dict[str, Any]:
        """Extract technical performance and accessibility data"""
        return await page.evaluate("""
            () => {
                const technical = {};
                
                // Performance data
                try {
                    const perfData = performance.getEntriesByType('navigation')[0];
                    if (perfData) {
                        technical.performance = {
                            dom_content_loaded: Math.round(perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart),
                            load_complete: Math.round(perfData.loadEventEnd - perfData.loadEventStart),
                            first_paint: Math.round(perfData.responseEnd - perfData.requestStart),
                            total_load_time: Math.round(perfData.loadEventEnd - perfData.fetchStart)
                        };
                    }
                } catch (e) {
                    technical.performance_error = e.message;
                }
                
                // Accessibility data
                try {
                    const images_without_alt = document.querySelectorAll('img:not([alt])').length;
                    const links_without_text = Array.from(document.querySelectorAll('a')).filter(a => !a.innerText.trim()).length;
                    const headings_structure = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6')).map(h => h.tagName);
                    
                    technical.accessibility = {
                        images_without_alt: images_without_alt,
                        links_without_text: links_without_text,
                        heading_structure: headings_structure,
                        has_lang_attr: document.documentElement.hasAttribute('lang'),
                        has_title: document.title.length > 0
                    };
                } catch (e) {
                    technical.accessibility_error = e.message;
                }
                
                // Page structure
                technical.structure = {
                    total_dom_elements: document.querySelectorAll('*').length,
                    external_links: Array.from(document.querySelectorAll('a[href]')).filter(a => 
                        a.hostname && a.hostname !== window.location.hostname
                    ).length,
                    internal_links: Array.from(document.querySelectorAll('a[href]')).filter(a => 
                        !a.hostname || a.hostname === window.location.hostname
                    ).length,
                    has_footer: document.querySelector('footer, .footer') !== null,
                    has_header: document.querySelector('header, .header') !== null,
                    has_main: document.querySelector('main, .main, #main') !== null
                };
                
                return { technical_data: technical };
            }
        """)
    
    def _generate_page_hash(self, url: str, title: str) -> str:
        """Generate a hash for page identification"""
        content = f"{url}-{title}-{int(time.time() / 3600)}"  # Hour-based hash
        return hashlib.md5(content.encode()).hexdigest()[:12]