"""
Tests for CTA detector module
"""

import pytest
from app.modules.cta_detector import (
    CTADetector, 
    detect_ctas, 
    CTAAnalysis, 
    CTAReport, 
    CTAIssue
)

# Sample HTML with various CTA types
SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>CTA Test Page</title>
    <style>
        .primary-btn {
            background-color: #007bff;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            font-size: 16px;
        }
        .secondary-btn {
            background-color: transparent;
            color: #007bff;
            padding: 8px 16px;
            border: 2px solid #007bff;
            border-radius: 4px;
        }
        .small-cta {
            background: #28a745;
            color: white;
            padding: 4px 8px;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <!-- Primary CTA above fold -->
    <button class="primary-btn" id="main-cta">Get Started Free</button>
    
    <!-- Secondary CTA -->
    <a href="/learn-more" class="secondary-btn">Learn More</a>
    
    <!-- Good CTA with clear action -->
    <button class="primary-btn">Download Now</button>
    
    <!-- Poor CTA - vague text -->
    <button class="secondary-btn">Click Here</button>
    
    <!-- Poor CTA - too small -->
    <button class="small-cta">Buy</button>
    
    <!-- Good CTA with jargon (should be flagged) -->
    <button class="primary-btn">Leverage Our Platform</button>
    
    <!-- CTA with too many words -->
    <button class="primary-btn">Start Your Amazing Journey With Our Comprehensive Platform Today</button>
    
    <!-- Below fold CTA -->
    <div style="margin-top: 1000px;">
        <button class="primary-btn">Subscribe to Newsletter</button>
    </div>
    
    <!-- Form submit button -->
    <form>
        <input type="email" placeholder="Email">
        <input type="submit" value="Join Now" class="primary-btn">
    </form>
    
    <!-- Link that looks like CTA -->
    <a href="/signup" class="btn btn-primary">Sign Up Today</a>
</body>
</html>
"""

# Sample element bounding boxes data
SAMPLE_ELEMENT_BOXES = [
    {
        'selector': 'button#main-cta',
        'text': 'Get Started Free',
        'bbox': {'x': 100, 'y': 200, 'width': 150, 'height': 44},
        'visible': True,
        'above_fold': True
    },
    {
        'selector': 'a.secondary-btn',
        'text': 'Learn More',
        'bbox': {'x': 300, 'y': 200, 'width': 120, 'height': 36},
        'visible': True,
        'above_fold': True
    },
    {
        'selector': 'button.primary-btn:nth(2)',
        'text': 'Download Now',
        'bbox': {'x': 100, 'y': 300, 'width': 140, 'height': 44},
        'visible': True,
        'above_fold': True
    },
    {
        'selector': 'button.secondary-btn:nth(2)',
        'text': 'Click Here',
        'bbox': {'x': 300, 'y': 300, 'width': 100, 'height': 36},
        'visible': True,
        'above_fold': True
    },
    {
        'selector': 'button.small-cta',
        'text': 'Buy',
        'bbox': {'x': 100, 'y': 400, 'width': 30, 'height': 20},
        'visible': True,
        'above_fold': True
    },
    {
        'selector': 'button.primary-btn:nth(3)',
        'text': 'Leverage Our Platform',
        'bbox': {'x': 100, 'y': 500, 'width': 200, 'height': 44},
        'visible': True,
        'above_fold': True
    },
    {
        'selector': 'button.primary-btn:nth(4)',
        'text': 'Start Your Amazing Journey With Our Comprehensive Platform Today',
        'bbox': {'x': 100, 'y': 600, 'width': 400, 'height': 44},
        'visible': True,
        'above_fold': True
    },
    {
        'selector': 'button.primary-btn:nth(5)',
        'text': 'Subscribe to Newsletter',
        'bbox': {'x': 100, 'y': 1100, 'width': 180, 'height': 44},
        'visible': True,
        'above_fold': False
    },
    {
        'selector': 'input[type="submit"]',
        'text': 'Join Now',
        'bbox': {'x': 200, 'y': 800, 'width': 100, 'height': 44},
        'visible': True,
        'above_fold': True
    },
    {
        'selector': 'a.btn.btn-primary',
        'text': 'Sign Up Today',
        'bbox': {'x': 100, 'y': 850, 'width': 130, 'height': 44},
        'visible': True,
        'above_fold': True
    }
]

# Sample computed styles
SAMPLE_COMPUTED_STYLES = {
    'button#main-cta': {
        'backgroundColor': 'rgb(0, 123, 255)',
        'color': 'rgb(255, 255, 255)',
        'fontSize': '16px',
        'padding': '12px 24px'
    },
    'button.small-cta': {
        'backgroundColor': 'rgb(40, 167, 69)',
        'color': 'rgb(255, 255, 255)',
        'fontSize': '12px',
        'padding': '4px 8px'
    }
}


class TestCTADetector:
    """Test cases for CTADetector"""
    
    def test_cta_detection_basic(self):
        """Test basic CTA detection"""
        detector = CTADetector(viewport_width=1440, viewport_height=900)
        report = detector.detect_ctas(SAMPLE_HTML, SAMPLE_ELEMENT_BOXES, SAMPLE_COMPUTED_STYLES)
        
        # Should be a CTAReport
        assert isinstance(report, CTAReport)
        
        # Should find multiple CTAs
        assert len(report.ctas) >= 5
        assert report.total_ctas_found >= 5
        
        # Should have processing time
        assert report.processing_time > 0
    
    def test_primary_cta_identification(self):
        """Test primary CTA identification"""
        detector = CTADetector(viewport_width=1440, viewport_height=900)
        report = detector.detect_ctas(SAMPLE_HTML, SAMPLE_ELEMENT_BOXES, SAMPLE_COMPUTED_STYLES)
        
        # Should identify a primary CTA
        assert report.primary_cta is not None
        assert report.primary_cta.is_primary is True
        
        # Primary CTA should have good characteristics
        primary = report.primary_cta
        assert primary.above_fold  # Should be above fold
        assert primary.overall_score > 50  # Should have decent score
        
        # Primary should be in the list of CTAs
        assert primary in report.ctas
    
    def test_cta_analysis_structure(self):
        """Test CTA analysis data structure"""
        detector = CTADetector()
        report = detector.detect_ctas(SAMPLE_HTML, SAMPLE_ELEMENT_BOXES, SAMPLE_COMPUTED_STYLES)
        
        for cta in report.ctas:
            # Check structure
            assert isinstance(cta, CTAAnalysis)
            assert cta.selector
            assert cta.text
            assert cta.element_type in ['button', 'link', 'input', 'element']
            assert isinstance(cta.bbox, dict)
            assert 'x' in cta.bbox and 'y' in cta.bbox
            assert 'width' in cta.bbox and 'height' in cta.bbox
            
            # Check scores
            assert 0 <= cta.visibility_score <= 100
            assert 0 <= cta.tap_target_score <= 100
            assert 0 <= cta.text_clarity_score <= 100
            assert 0 <= cta.overall_score <= 100
            
            # Check issues
            assert isinstance(cta.issues, list)
            for issue in cta.issues:
                assert isinstance(issue, CTAIssue)
                assert issue.type
                assert issue.severity in ['high', 'medium', 'low']
                assert issue.message
                assert issue.suggestion
    
    def test_above_fold_detection(self):
        """Test above/below fold detection"""
        detector = CTADetector(viewport_width=1440, viewport_height=900)
        report = detector.detect_ctas(SAMPLE_HTML, SAMPLE_ELEMENT_BOXES, SAMPLE_COMPUTED_STYLES)
        
        # Should have both above and below fold CTAs
        above_fold_ctas = [cta for cta in report.ctas if cta.above_fold]
        below_fold_ctas = [cta for cta in report.ctas if not cta.above_fold]
        
        assert len(above_fold_ctas) > 0
        assert len(below_fold_ctas) > 0
        assert report.above_fold_ctas == len(above_fold_ctas)
        
        # CTAs with y > 900 should be below fold
        for cta in below_fold_ctas:
            assert cta.bbox.get('y', 0) > 900
    
    def test_visibility_analysis(self):
        """Test CTA visibility analysis"""
        detector = CTADetector()
        
        # Test small CTA (should have visibility issues)
        small_cta = next(cta for cta in SAMPLE_ELEMENT_BOXES if cta['text'] == 'Buy')
        analysis = detector._analyze_single_cta(small_cta, None)
        
        assert analysis.visibility_score < 100  # Should lose points for small size
        visibility_issues = [issue for issue in analysis.issues if issue.type == 'visibility']
        assert len(visibility_issues) > 0
    
    def test_tap_target_analysis(self):
        """Test tap target analysis"""
        detector = CTADetector()
        
        # Small tap target
        small_bbox = {'width': 30, 'height': 20}
        score, issues = detector._analyze_tap_target(small_bbox)
        
        assert score < 100  # Should lose points
        assert len(issues) > 0
        assert any('too small' in issue.message.lower() for issue in issues)
        
        # Good tap target
        good_bbox = {'width': 50, 'height': 50}
        score, issues = detector._analyze_tap_target(good_bbox)
        
        assert score == 100  # Should be perfect
        assert len(issues) == 0
    
    def test_text_clarity_analysis(self):
        """Test text clarity analysis"""
        detector = CTADetector()
        
        # Good CTA text
        score, issues = detector._analyze_text_clarity('Get Started')
        assert score > 80
        
        # Poor CTA text - too long
        score, issues = detector._analyze_text_clarity('Start Your Amazing Journey With Our Comprehensive Platform Today')
        assert score < 100
        long_text_issues = [issue for issue in issues if 'long' in issue.message.lower()]
        assert len(long_text_issues) > 0
        
        # Poor CTA text - jargon
        score, issues = detector._analyze_text_clarity('Leverage Our Platform')
        assert score < 100
        jargon_issues = [issue for issue in issues if 'jargon' in issue.message.lower()]
        assert len(jargon_issues) > 0
        
        # Poor CTA text - vague
        score, issues = detector._analyze_text_clarity('Click Here')
        assert score < 100
        vague_issues = [issue for issue in issues if 'vague' in issue.message.lower()]
        assert len(vague_issues) > 0
    
    def test_element_type_detection(self):
        """Test element type detection"""
        detector = CTADetector()
        
        assert detector._get_element_type('button#main-cta') == 'button'
        assert detector._get_element_type('input[type="submit"]') == 'input'
        assert detector._get_element_type('a.btn-primary') == 'link'
        assert detector._get_element_type('div.cta') == 'element'
    
    def test_potential_cta_identification(self):
        """Test potential CTA identification"""
        detector = CTADetector()
        
        # Clear button should be identified
        assert detector._is_potential_cta('button.primary', 'Get Started', {}, {})
        
        # Element with CTA class should be identified
        assert detector._is_potential_cta('div.cta', 'Download', {}, {})
        
        # Element with CTA text should be identified
        assert detector._is_potential_cta('div.some-class', 'Buy Now', {}, {})
        
        # Random element should not be identified
        assert not detector._is_potential_cta('p.text', 'This is just text', {}, {})
    
    def test_overall_score_calculation(self):
        """Test overall score calculation"""
        detector = CTADetector()
        
        # Perfect scores should give 100
        score = detector._calculate_overall_score(100, 7.0, 100, 100)
        assert score == 100
        
        # Poor scores should give low overall score
        score = detector._calculate_overall_score(20, 2.0, 30, 40)
        assert score < 50
        
        # Mixed scores should give reasonable result
        score = detector._calculate_overall_score(80, 4.5, 90, 70)
        assert 70 <= score <= 90


class TestConvenienceFunction:
    """Test convenience function"""
    
    def test_detect_ctas_function(self):
        """Test the convenience function"""
        report = detect_ctas(
            SAMPLE_HTML, 
            SAMPLE_ELEMENT_BOXES, 
            SAMPLE_COMPUTED_STYLES,
            viewport_width=1440,
            viewport_height=900
        )
        
        assert isinstance(report, CTAReport)
        assert len(report.ctas) > 0
        assert report.primary_cta is not None


class TestDataStructures:
    """Test data structure classes"""
    
    def test_cta_issue(self):
        """Test CTAIssue"""
        issue = CTAIssue(
            type='visibility',
            severity='high',
            message='CTA is too small',
            suggestion='Make it larger'
        )
        
        assert issue.type == 'visibility'
        assert issue.severity == 'high'
        assert issue.message == 'CTA is too small'
        assert issue.suggestion == 'Make it larger'
    
    def test_cta_analysis(self):
        """Test CTAAnalysis"""
        analysis = CTAAnalysis(
            selector='button#test',
            text='Click Me',
            element_type='button',
            bbox={'x': 0, 'y': 0, 'width': 100, 'height': 50},
            is_primary=True,
            above_fold=True,
            visibility_score=90.0,
            contrast_ratio=4.5,
            tap_target_score=85.0,
            text_clarity_score=80.0,
            overall_score=85.0
        )
        
        assert analysis.selector == 'button#test'
        assert analysis.text == 'Click Me'
        assert analysis.is_primary is True
        assert analysis.above_fold is True
        assert analysis.visibility_score == 90.0
        assert analysis.overall_score == 85.0
    
    def test_cta_report(self):
        """Test CTAReport"""
        cta1 = CTAAnalysis(
            selector='button#1', text='CTA 1', element_type='button',
            bbox={}, is_primary=False, above_fold=True,
            visibility_score=80, contrast_ratio=4.5,
            tap_target_score=90, text_clarity_score=85,
            overall_score=85
        )
        
        cta2 = CTAAnalysis(
            selector='button#2', text='CTA 2', element_type='button',
            bbox={}, is_primary=True, above_fold=False,
            visibility_score=90, contrast_ratio=5.0,
            tap_target_score=95, text_clarity_score=90,
            overall_score=92
        )
        
        report = CTAReport(
            ctas=[cta1, cta2],
            primary_cta=cta2,
            total_ctas_found=2,
            above_fold_ctas=1,
            processing_time=1.5
        )
        
        assert len(report.ctas) == 2
        assert report.primary_cta == cta2
        assert report.total_ctas_found == 2
        assert report.above_fold_ctas == 1
        assert report.processing_time == 1.5


if __name__ == "__main__":
    # Run a simple test
    def simple_test():
        print("Running simple CTA detection test...")
        
        report = detect_ctas(
            SAMPLE_HTML,
            SAMPLE_ELEMENT_BOXES,
            SAMPLE_COMPUTED_STYLES
        )
        
        print(f"Found {len(report.ctas)} CTAs")
        print(f"Primary CTA: {report.primary_cta.text if report.primary_cta else 'None'}")
        print(f"Above fold CTAs: {report.above_fold_ctas}")
        
        for cta in report.ctas[:3]:  # Show first 3
            print(f"- {cta.text}: Score {cta.overall_score}, Issues: {len(cta.issues)}")
    
    simple_test()