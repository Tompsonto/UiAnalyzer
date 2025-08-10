"""
Selenium-based Website Renderer - Replaces Playwright with Selenium WebDriver
"""
import time
import base64
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse
from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from axe_selenium_python import Axe

logger = logging.getLogger(__name__)


@dataclass 
class SeleniumRenderResult:
    """Result from Selenium rendering"""
    url: str
    dom_content: str
    screenshot_base64: str
    element_bounding_boxes: List[Dict[str, Any]]
    computed_styles: Dict[str, Any]
    render_metrics: Dict[str, Any]
    viewport: str = "desktop"
    timing: str = "T1"


class SeleniumRenderer:
    """Selenium-based website renderer"""
    
    def __init__(self, viewport_width: int = 1440, viewport_height: int = 900, headless: bool = True):
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height  
        self.headless = headless
        self.driver: Optional[webdriver.Chrome] = None
        
    def __enter__(self):
        """Initialize Selenium WebDriver"""
        self._setup_driver()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")
                
    def _setup_driver(self):
        """Set up Chrome WebDriver with optimized options"""
        try:
            # Chrome options for optimal performance
            options = Options()
            
            if self.headless:
                options.add_argument('--headless=new')
                
            # Performance and stability options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')  # Faster loading
            options.add_argument('--disable-javascript-harmony-shipping')
            options.add_argument('--disable-background-networking')
            options.add_argument('--disable-background-timer-throttling')
            options.add_argument('--disable-renderer-backgrounding')
            options.add_argument('--disable-backgrounding-occluded-windows')
            options.add_argument('--disable-client-side-phishing-detection')
            options.add_argument('--disable-default-apps')
            options.add_argument('--disable-hang-monitor')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--disable-prompt-on-repost')
            options.add_argument('--disable-sync')
            options.add_argument('--disable-translate')
            options.add_argument('--metrics-recording-only')
            options.add_argument('--no-first-run')
            options.add_argument('--safebrowsing-disable-auto-update')
            options.add_argument('--enable-automation')
            options.add_argument('--password-store=basic')
            options.add_argument('--use-mock-keychain')
            
            # Set window size
            options.add_argument(f'--window-size={self.viewport_width},{self.viewport_height}')
            
            # User agent
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 ClarityCheck/1.0')
            
            # Set up ChromeDriver service with proper executable path
            chromedriver_path = ChromeDriverManager().install()
            
            # Fix path if it's pointing to wrong file
            if not chromedriver_path.endswith('.exe') and 'chromedriver' in chromedriver_path:
                import os
                # Find the actual chromedriver.exe in the directory
                driver_dir = os.path.dirname(chromedriver_path)
                for root, dirs, files in os.walk(driver_dir):
                    for file in files:
                        if file == 'chromedriver.exe':
                            chromedriver_path = os.path.join(root, file)
                            break
            
            logger.info(f"Using ChromeDriver at: {chromedriver_path}")
            service = Service(chromedriver_path)
            
            # Create WebDriver
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Set timeouts
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            # Set viewport size
            self.driver.set_window_size(self.viewport_width, self.viewport_height)
            
            logger.info(f"Selenium WebDriver initialized with viewport {self.viewport_width}x{self.viewport_height}")
            
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise
    
    def render_website(self, url: str, wait_time: int = 2) -> SeleniumRenderResult:
        """
        Render website and extract comprehensive data
        
        Args:
            url: URL to render
            wait_time: Time to wait for page stability
            
        Returns:
            SeleniumRenderResult with all extracted data
        """
        start_time = time.time()
        
        try:
            # Validate and normalize URL
            normalized_url = self._normalize_url(url)
            
            logger.info(f"Rendering website: {normalized_url}")
            
            # Navigate to URL
            self.driver.get(normalized_url)
            
            # Wait for page load
            WebDriverWait(self.driver, 15).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Additional wait for dynamic content
            time.sleep(wait_time)
            
            # Extract comprehensive data
            dom_content = self.driver.page_source
            screenshot_base64 = self._take_screenshot()
            element_boxes = self._extract_element_boxes()
            computed_styles = self._extract_computed_styles()
            
            # Performance metrics
            render_metrics = {
                'render_time': time.time() - start_time,
                'page_load_time': self._get_page_load_time(),
                'dom_elements': len(element_boxes),
                'final_url': self.driver.current_url
            }
            
            return SeleniumRenderResult(
                url=normalized_url,
                dom_content=dom_content,
                screenshot_base64=screenshot_base64,
                element_bounding_boxes=element_boxes,
                computed_styles=computed_styles,
                render_metrics=render_metrics
            )
            
        except TimeoutException:
            logger.error(f"Timeout loading {url}")
            raise Exception(f"Page load timeout for {url}")
        except WebDriverException as e:
            logger.error(f"WebDriver error for {url}: {e}")
            raise Exception(f"WebDriver error: {str(e)}")
        except Exception as e:
            logger.error(f"Rendering error for {url}: {e}")
            raise Exception(f"Rendering failed: {str(e)}")
    
    def _normalize_url(self, url: str) -> str:
        """Normalize and validate URL"""
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    
    def _take_screenshot(self) -> str:
        """Take full page screenshot and return as base64"""
        try:
            # Get full page height
            total_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # Set window size to capture full page
            self.driver.set_window_size(self.viewport_width, max(total_height, self.viewport_height))
            
            # Take screenshot
            screenshot_png = self.driver.get_screenshot_as_png()
            
            # Reset window size
            self.driver.set_window_size(self.viewport_width, self.viewport_height)
            
            # Convert to base64
            screenshot_base64 = base64.b64encode(screenshot_png).decode()
            
            return screenshot_base64
            
        except Exception as e:
            logger.error(f"Screenshot capture failed: {e}")
            return ""
    
    def _extract_element_boxes(self) -> List[Dict[str, Any]]:
        """Extract element bounding boxes and properties"""
        try:
            elements = []
            
            # Target selectors for analysis
            selectors = [
                'h1, h2, h3, h4, h5, h6',
                'p, span, div',
                'button, a[href]',
                'input, textarea, select',
                '.btn, .button, .cta',
                '[role="button"]'
            ]
            
            processed_elements = set()
            
            for selector in selectors:
                try:
                    found_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for i, element in enumerate(found_elements[:20]):  # Limit per selector
                        try:
                            # Skip if already processed
                            element_id = id(element)
                            if element_id in processed_elements:
                                continue
                            processed_elements.add(element_id)
                            
                            # Get element properties
                            location = element.location
                            size = element.size
                            text = element.text.strip()
                            tag_name = element.tag_name
                            
                            # Skip invisible or empty elements
                            if (size['width'] == 0 or size['height'] == 0 or 
                                not element.is_displayed()):
                                continue
                                
                            # Skip if no meaningful content (unless interactive)
                            is_interactive = tag_name.lower() in ['button', 'a', 'input', 'textarea', 'select']
                            if not text and not is_interactive:
                                continue
                            
                            # Create selector string
                            element_selector = self._create_selector(element, i)
                            
                            # Get computed styles
                            styles = self._get_element_styles(element)
                            
                            elements.append({
                                'selector': element_selector,
                                'text': text,
                                'tagName': tag_name,
                                'bbox': {
                                    'x': location['x'],
                                    'y': location['y'],
                                    'width': size['width'],
                                    'height': size['height']
                                },
                                'styles': styles,
                                'visible': element.is_displayed(),
                                'above_fold': location['y'] < self.viewport_height
                            })
                            
                        except Exception as e:
                            logger.debug(f"Error processing element: {e}")
                            continue
                            
                except Exception as e:
                    logger.debug(f"Error with selector {selector}: {e}")
                    continue
            
            logger.info(f"Extracted {len(elements)} elements")
            return elements
            
        except Exception as e:
            logger.error(f"Element extraction failed: {e}")
            return []
    
    def _create_selector(self, element, index: int) -> str:
        """Create CSS selector for element"""
        try:
            tag_name = element.tag_name.lower()
            element_id = element.get_attribute('id')
            class_name = element.get_attribute('class')
            
            if element_id:
                return f"{tag_name}#{element_id}"
            elif class_name:
                first_class = class_name.split()[0] if class_name.split() else ''
                if first_class:
                    return f"{tag_name}.{first_class}"
            
            return f"{tag_name}:nth-of-type({index + 1})"
            
        except:
            return f"element_{index}"
    
    def _get_element_styles(self, element) -> Dict[str, str]:
        """Get computed styles for element"""
        try:
            styles = {}
            style_properties = [
                'color', 'backgroundColor', 'fontSize', 'fontWeight', 
                'lineHeight', 'fontFamily', 'textAlign', 'padding', 
                'margin', 'border', 'borderRadius', 'display', 'position'
            ]
            
            for prop in style_properties:
                try:
                    value = element.value_of_css_property(prop.replace('backgroundColor', 'background-color')
                                                        .replace('fontSize', 'font-size')
                                                        .replace('fontWeight', 'font-weight')
                                                        .replace('lineHeight', 'line-height')
                                                        .replace('fontFamily', 'font-family')
                                                        .replace('textAlign', 'text-align')
                                                        .replace('borderRadius', 'border-radius'))
                    styles[prop] = value
                except:
                    styles[prop] = ''
                    
            return styles
            
        except Exception as e:
            logger.debug(f"Style extraction failed: {e}")
            return {}
    
    def _extract_computed_styles(self) -> Dict[str, Any]:
        """Extract computed styles for key elements"""
        try:
            styles = {}
            
            # Key elements to get styles for
            key_selectors = ['body', 'h1', 'h2', 'h3', 'p', 'button', 'a']
            
            for selector in key_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        element = elements[0]  # Get first matching element
                        styles[selector] = self._get_element_styles(element)
                except:
                    continue
                    
            return styles
            
        except Exception as e:
            logger.error(f"Computed styles extraction failed: {e}")
            return {}
    
    def _get_page_load_time(self) -> float:
        """Get page load timing information"""
        try:
            navigation_timing = self.driver.execute_script(
                "return window.performance.timing"
            )
            
            if navigation_timing:
                load_time = (navigation_timing['loadEventEnd'] - 
                           navigation_timing['navigationStart']) / 1000.0
                return load_time
                
        except Exception as e:
            logger.debug(f"Page timing extraction failed: {e}")
            
        return 0.0
    
    def run_accessibility_scan(self) -> List[Dict[str, Any]]:
        """Run accessibility scan using axe-selenium-python"""
        try:
            axe = Axe(self.driver)
            
            # Inject axe-core into page
            axe.inject()
            
            # Run accessibility scan
            results = axe.run()
            
            # Process violations
            violations = []
            for violation in results.get('violations', []):
                for node in violation.get('nodes', []):
                    violations.append({
                        'rule_id': violation.get('id', ''),
                        'description': violation.get('description', ''),
                        'impact': node.get('impact', 'moderate'),
                        'selector': node.get('target', [''])[0] if node.get('target') else '',
                        'message': f"{violation.get('help', '')} - {node.get('failureSummary', '')}",
                        'help_url': violation.get('helpUrl', '')
                    })
            
            logger.info(f"Accessibility scan found {len(violations)} violations")
            return violations
            
        except Exception as e:
            logger.error(f"Accessibility scan failed: {e}")
            return []


# Convenience functions
def render_website_selenium(url: str, viewport_width: int = 1440, viewport_height: int = 900) -> SeleniumRenderResult:
    """Convenience function to render a website with Selenium"""
    with SeleniumRenderer(viewport_width, viewport_height) as renderer:
        return renderer.render_website(url)


def run_accessibility_scan_selenium(url: str) -> List[Dict[str, Any]]:
    """Convenience function to run accessibility scan"""
    with SeleniumRenderer() as renderer:
        renderer.render_website(url)
        return renderer.run_accessibility_scan()