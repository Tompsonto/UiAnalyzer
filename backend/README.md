# ClarityCheck Backend

Python FastAPI backend for ClarityCheck - Website Visual Clarity and Text Readability Analysis.

## Features

- 🖥️ **Website Rendering**: Playwright-based page rendering and data extraction
- 👀 **Visual Analysis**: Color contrast, layout, CTA visibility analysis
- 📝 **Text Analysis**: Readability scoring, structure analysis, complexity detection
- 🎯 **Smart Scoring**: Weighted scoring system with actionable recommendations
- 📊 **API Endpoints**: RESTful API for frontend integration
- 💾 **Data Storage**: SQLAlchemy with PostgreSQL/SQLite support

## Quick Start

1. **Install Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Install Playwright Browsers**
   ```bash
   playwright install chromium
   ```

3. **Set Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the Server**
   ```bash
   python run.py
   ```

The API will be available at `http://localhost:8000`

## API Endpoints

### Analysis
- `POST /api/v1/analyze` - Create new analysis (background processing)
- `POST /api/v1/analyze/quick` - Quick analysis (synchronous)
- `GET /api/v1/analysis/{id}` - Get analysis by ID
- `GET /api/v1/analyses` - List analyses
- `DELETE /api/v1/analysis/{id}` - Delete analysis

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/v1/health` - Analysis service health

## Analysis Modules

### 1. Renderer (`app/modules/renderer.py`)
- Uses Playwright to render websites
- Extracts DOM, CSS, text content, and screenshots
- Handles dynamic content loading

### 2. Visual Analysis (`app/modules/visual_analysis.py`)
- **Contrast Analysis**: WCAG-compliant color contrast checking
- **Layout Analysis**: CTA placement, whitespace, element density
- **Typography**: Font size validation and readability
- **CTA Visibility**: Above-the-fold positioning and clarity

### 3. Text Analysis (`app/modules/text_analysis.py`)
- **Readability Metrics**: Flesch-Kincaid, Gunning Fog, SMOG indices
- **Structure Analysis**: Heading hierarchy, paragraph length
- **Complexity Detection**: Sentence length, passive voice, jargon

### 4. Scoring Engine (`app/modules/scoring.py`)
- Combines visual and text scores with configurable weights
- Generates letter grades (A-F)
- Creates human-readable summaries
- Prioritizes issues by severity

## Database Schema

### Analysis Table
- Basic info: URL, domain, scores, grade
- Analysis data: Visual/text analysis results, issues, recommendations
- Metadata: Title, meta description, screenshot URL
- Status tracking: pending, processing, completed, failed

### User Table (for future use)
- User management and plan limits
- Subscription tracking
- Usage analytics

## Configuration

Key settings in `app/core/config.py`:

```python
# Analysis timeouts and limits
MAX_ANALYSIS_TIME = 30  # seconds
CACHE_EXPIRY = 21600    # 6 hours

# Playwright settings
VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080

# Scoring weights
VISUAL_SCORE_WEIGHTS = {
    "contrast": 0.3,
    "layout": 0.25, 
    "cta_visibility": 0.25,
    "font_size": 0.2
}
```

## Example Analysis Output

```json
{
  "overall_score": 74.2,
  "visual_score": 68.0,
  "text_score": 82.5,
  "grade": "C",
  "summary": "Moderate clarity. Some users may struggle with visual elements.",
  "total_issues": 8,
  "critical_issues": 2,
  "issues": [
    {
      "type": "contrast",
      "severity": "high",
      "element": "CTA Button",
      "message": "Low contrast ratio: 2.1",
      "suggestion": "Increase contrast between text and background colors"
    }
  ],
  "recommendations": [
    {
      "category": "Visual Clarity",
      "priority": "High",
      "action": "Improve Color Contrast",
      "description": "Ensure text and background colors meet WCAG AA standards"
    }
  ]
}
```

## Development

### Adding New Analysis Rules

1. **Visual Rules**: Add to `VisualAnalyzer` class methods
2. **Text Rules**: Add to `TextAnalyzer` class methods  
3. **Scoring Logic**: Modify weights in `ScoringEngine`

### Testing

```bash
# Run a quick test analysis
curl -X POST "http://localhost:8000/api/v1/analyze/quick" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

## Deployment

1. **Environment**: Set production environment variables
2. **Database**: Configure PostgreSQL connection
3. **Redis**: Set up Redis for caching (optional)
4. **Playwright**: Ensure browsers are installed in production
5. **Process Manager**: Use supervisord, PM2, or similar for process management

## Architecture Notes

- **Async Processing**: Background tasks for long-running analyses
- **Caching**: Domain-level caching to avoid duplicate analyses
- **Modularity**: Separate modules for different analysis types
- **Extensibility**: Easy to add new analysis rules and metrics
- **Error Handling**: Comprehensive error tracking and recovery