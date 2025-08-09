# Visual Analysis Module

Comprehensive visual clarity analysis for web pages, implementing WCAG guidelines and UX best practices.

## Overview

The Visual Analysis Module evaluates web pages across 6 key heuristics:

1. **WCAG Contrast Compliance** - Ensures text meets AA/AAA accessibility standards
2. **Typography Analysis** - Validates font sizes, line heights, and line lengths  
3. **Touch Target Analysis** - Checks interactive element sizes for mobile devices
4. **Element Overlap Detection** - Identifies overlapping UI components
5. **Visual Density Analysis** - Flags regions with too many interactive elements
6. **Layout Alignment** - Detects misaligned elements in columns/rows

## Installation

```bash
pip install wcag-contrast-ratio beautifulsoup4
```

## Quick Start

```python
from app.modules.visual_analysis import analyze_visual

# Basic usage
dom_html = "<html><body><p>Your website HTML</p></body></html>"
css_snapshot = {
    'computed_styles': {...},
    'elements': [...]
}
viewport = (1920, 1080)  # Desktop viewport

result = analyze_visual(dom_html, css_snapshot, viewport)

print(f"Visual Clarity Score: {result.score}/100")
print(f"Issues Found: {len(result.issues)}")
```

## API Reference

### Main Function

```python
def analyze_visual(dom: str, css_snapshot: dict, viewport: tuple[int, int]) -> VisualReport
```

**Parameters:**
- `dom`: HTML content as string
- `css_snapshot`: Dictionary with computed styles and element data
- `viewport`: Tuple of (width, height) for viewport dimensions

**Returns:** `VisualReport` object with score, issues, and feature metrics

### Data Classes

```python
@dataclass
class Issue:
    type: str          # contrast, typography, tap_target, overlap, density, alignment
    selector: str      # CSS selector or element identifier
    bbox: Dict[str, float]  # Bounding box {x, y, width, height}
    severity: str      # high, medium, low
    message: str       # Human-readable issue description

@dataclass 
class VisualReport:
    score: int         # Overall visual clarity score (0-100)
    issues: List[Issue]  # List of detected issues
    features: Dict[str, Any]  # Analysis metrics and metadata
```

## Input Data Format

### CSS Snapshot Structure

```python
css_snapshot = {
    'computed_styles': {
        'selector': {
            'color': 'rgb(0,0,0)',
            'backgroundColor': 'rgb(255,255,255)', 
            'fontSize': '16px',
            'lineHeight': '1.4',
            'fontWeight': 'normal'
        }
    },
    'elements': [
        {
            'selector': 'h1',
            'text': 'Main Heading',
            'styles': {
                'color': 'rgb(51,51,51)',
                'backgroundColor': 'rgb(255,255,255)',
                'fontSize': '32px'
            },
            'bbox': {
                'x': 20,
                'y': 50, 
                'width': 300,
                'height': 40
            }
        }
    ]
}
```

## Analysis Rules

### 1. WCAG Contrast Analysis

- **AA Standard**: 4.5:1 for normal text, 3.0:1 for large text (≥18px or ≥14px bold)
- **AAA Standard**: 7.0:1 for normal text, 4.5:1 for large text
- **Penalties**: 15 points for high severity, 10 for medium, 3 for low

### 2. Typography Analysis  

- **Font Size**: Minimum 16px desktop, 14px mobile
- **Line Height**: Minimum 1.3x font size  
- **Line Length**: Maximum 90 characters per line
- **Penalties**: 12 points for tiny fonts, 8 for small fonts, 5 for line issues

### 3. Touch Target Analysis (Mobile Only)

- **Minimum Size**: 44x44px (WCAG recommendation)
- **Critical Size**: 32x32px (high severity threshold)
- **Penalties**: 15 points for critical, 10 for small targets

### 4. Element Overlap Detection

- **Threshold**: 10% overlap of smaller element area
- **Detection**: Bounding box intersection calculation
- **Penalties**: 8 points per overlapping pair

### 5. Visual Density Analysis

- **Region Size**: 1000x800px blocks
- **Threshold**: >20 interactive elements per region
- **Penalties**: 15 points per high-density region

### 6. Layout Alignment

- **Tolerance**: 8px maximum deviation in column alignment
- **Grouping**: Elements within 20px vertical distance
- **Penalties**: 5 points per misaligned row

## Usage Examples

### Basic Analysis

```python
from app.modules.visual_analysis import analyze_visual

dom = """
<html>
<body>
    <h1>Website Title</h1>
    <p>Main content with good contrast</p>
    <button class="cta">Click Here</button>
</body>
</html>
"""

css_snapshot = {
    'computed_styles': {
        'h1': {'color': 'rgb(33,33,33)', 'backgroundColor': 'rgb(255,255,255)', 'fontSize': '28px'},
        'p': {'color': 'rgb(66,66,66)', 'backgroundColor': 'rgb(255,255,255)', 'fontSize': '16px'},
        'button': {'color': 'rgb(255,255,255)', 'backgroundColor': 'rgb(0,123,191)', 'fontSize': '16px'}
    },
    'elements': [
        {
            'selector': 'h1',
            'text': 'Website Title', 
            'styles': {'color': 'rgb(33,33,33)', 'backgroundColor': 'rgb(255,255,255)', 'fontSize': '28px'},
            'bbox': {'x': 20, 'y': 20, 'width': 200, 'height': 32}
        },
        {
            'selector': 'p',
            'text': 'Main content with good contrast',
            'styles': {'color': 'rgb(66,66,66)', 'backgroundColor': 'rgb(255,255,255)', 'fontSize': '16px'}, 
            'bbox': {'x': 20, 'y': 60, 'width': 300, 'height': 20}
        },
        {
            'selector': 'button',
            'text': 'Click Here',
            'styles': {'color': 'rgb(255,255,255)', 'backgroundColor': 'rgb(0,123,191)', 'fontSize': '16px'},
            'bbox': {'x': 20, 'y': 100, 'width': 100, 'height': 40}
        }
    ]
}

# Desktop analysis
result = analyze_visual(dom, css_snapshot, (1920, 1080))
print(f"Desktop Score: {result.score}")

# Mobile analysis  
result = analyze_visual(dom, css_snapshot, (375, 667))
print(f"Mobile Score: {result.score}")
```

### Handling Results

```python
result = analyze_visual(dom, css_snapshot, (1920, 1080))

# Overall metrics
print(f"Visual Clarity Score: {result.score}/100")
print(f"Total Issues: {len(result.issues)}")

# Issue breakdown
issue_counts = {}
for issue in result.issues:
    issue_counts[issue.type] = issue_counts.get(issue.type, 0) + 1
    
print("Issues by type:", issue_counts)

# High priority issues
critical_issues = [issue for issue in result.issues if issue.severity == 'high']
print(f"Critical Issues: {len(critical_issues)}")

# Feature analysis
features = result.features
print(f"Contrast Score: {features['contrast_score']}")
print(f"Typography Score: {features['typography_score']}")
print(f"Is Mobile: {features['is_mobile']}")
```

## Sample Output

### VisualReport JSON Structure

```json
{
    "score": 73,
    "issues": [
        {
            "type": "contrast",
            "selector": ".low-contrast-text",
            "bbox": {"x": 20, "y": 150, "width": 250, "height": 18},
            "severity": "medium", 
            "message": "Contrast ratio 3.2:1 fails WCAG AA (requires 4.5:1)"
        },
        {
            "type": "typography",
            "selector": ".small-print",
            "bbox": {"x": 20, "y": 200, "width": 180, "height": 12},
            "severity": "high",
            "message": "Font size 11px below minimum 16px for desktop"
        },
        {
            "type": "tap_target", 
            "selector": "button.tiny-btn",
            "bbox": {"x": 50, "y": 250, "width": 30, "height": 28},
            "severity": "medium",
            "message": "Tap target 30x28px below 44x44px minimum"
        },
        {
            "type": "overlap",
            "selector": ".modal ∩ .header",
            "bbox": {"x": 0, "y": 0, "width": 100, "height": 60},
            "severity": "medium", 
            "message": "Elements overlap by 500px² (12.5%)"
        },
        {
            "type": "density",
            "selector": "region_0_0", 
            "bbox": {"x": 100, "y": 50, "width": 40, "height": 30},
            "severity": "medium",
            "message": "High interactive element density: 23 elements in 1000x800px region"
        },
        {
            "type": "alignment",
            "selector": "row_y_320",
            "bbox": {"x": 35, "y": 320, "width": 80, "height": 30},
            "severity": "low",
            "message": "Column alignment deviation 12px exceeds 8px threshold"
        }
    ],
    "features": {
        "contrast_score": 82.0,
        "typography_score": 71.0, 
        "tap_target_score": 85.0,
        "overlap_score": 92.0,
        "density_score": 85.0,
        "alignment_score": 95.0,
        "viewport_width": 1920,
        "viewport_height": 1080,
        "is_mobile": false,
        "total_elements": 15,
        "total_issues": 6
    }
}
```

## Testing

Run the comprehensive test suite:

```bash
cd backend
python -m pytest tests/test_visual_analysis.py -v
```

Test coverage includes:
- ✅ All 6 heuristic rules with dedicated fixtures
- ✅ Mobile vs desktop viewport differences  
- ✅ Error handling and edge cases
- ✅ Data structure validation
- ✅ Score calculation accuracy

## Integration Example

```python
# Integration with ClarityCheck analysis pipeline
from app.modules.visual_analysis import analyze_visual
from app.modules.renderer import render_page

async def analyze_website_clarity(url: str) -> dict:
    # Render page with Playwright
    page_data = await render_page(url)
    
    # Extract visual data
    dom = page_data['html_content']
    css_snapshot = {
        'computed_styles': page_data.get('computed_styles', {}),
        'elements': page_data.get('elements', [])
    }
    
    # Analyze for both desktop and mobile
    desktop_result = analyze_visual(dom, css_snapshot, (1920, 1080))
    mobile_result = analyze_visual(dom, css_snapshot, (375, 667))
    
    return {
        'desktop': {
            'score': desktop_result.score,
            'issues': len(desktop_result.issues),
            'features': desktop_result.features
        },
        'mobile': {
            'score': mobile_result.score, 
            'issues': len(mobile_result.issues),
            'features': mobile_result.features
        }
    }
```

## Performance Notes

- **Complexity**: O(n²) for overlap detection, O(n) for other analyses
- **Memory**: ~1MB per 1000 elements analyzed
- **Speed**: ~50ms for typical webpage (100-500 elements)
- **Recommendations**: Limit element analysis to visible viewport for large pages

## Contributing

When extending the module:

1. **Add new heuristic rules** in separate `_analyze_*` methods
2. **Update weights** in the main `analyze()` method  
3. **Add corresponding tests** with fixtures
4. **Document rule thresholds** and penalties
5. **Follow PEP8** and add type hints

## License

Part of the ClarityCheck project - see main project license.