# 📄 AI CONTEXT FILE — ClarityCheck App (v1.0)

## 🎯 MAIN PROJECT GOAL

Build a **web-based SaaS application** called **ClarityCheck**, allowing users to analyze websites for **visual clarity** and **text readability**. The app generates a comprehensive UX report with actionable recommendations, enabling optimization **before A/B testing or launch.**

The application works fully automatically after a user submits a URL.
No code injection or JavaScript is required on the client site.

---

## 🧠 MARKET GAP & ORIGIN

Current tools are split into three main categories:

1. **Heatmaps and recordings (Hotjar, Clarity)** – show *what* users do, not *why* they struggle.
2. **SEO-content checkers (SurferSEO, Clearscope)** – focus on SEO, not UX or language.
3. **Readability checkers (Hemingway, Grammarly)** – analyze language but ignore visual layout.

ClarityCheck bridges these gaps:
✅ renders the page like a user,
✅ assesses design, structure, and text,
✅ synthesizes results into actionable insights and scores.

---

## 🧩 ANALYSIS SCOPE (LAYERED ARCHITECTURE)

### 1. 🖥️ VISUAL CLARITY ANALYSIS (Layout Layer)

DOM + CSS + screenshot-based analysis.
Techniques:

* Playwright for full DOM + CSS rendering and screenshots
* CSS heuristics: contrast, font-size, line-height
* Custom rules: CTA visibility above-the-fold, grid overload, font-size < 14px, narrow padding/margins
* Component detection: CTA, pricing boxes, hero, navbar, modals

Results:

* Visual Clarity Score (0–100)
* Issues list: low contrast, CTA overload, invisible primary CTA

### 2. 📚 LANGUAGE READABILITY ANALYSIS (Language Layer)

Parsing and analyzing visible HTML content.
Techniques:

* `textstat`: Flesch–Kincaid, Fog, SMOG indexes
* `spaCy`: passive voice, long sentences, complex structures
* Regex-based rules: no paragraphing, CTAs in large blocks, no segmentation
* Heading structure analysis (H1–H6 logic, length, clarity)

Results:

* Text Clarity Score (0–100)
* Language suggestions

### 3. 🔁 SEMANTIC STRUCTURE & HIERARCHY (Semantic Layer)

* Is there only one H1?
* Logical H1 → H2 → H3 progression?
* Do headings reflect benefits, promises, or CTAs?
* Presence/absence of meta tags (title, description)

### 4. 🧠 CAUSALITY SYNTHESIS (Causality Layer)

Rule-based logic engine:

* If CTA = invisible + complex language + low FK score → suggest layout + copy fix
* If pricing = small font + wall of text + no FAQ → suggest chunking + common Qs

Goal: not just detect issues, but understand *why users don’t convert.*

---

## 🔧 TECHNICAL INFRASTRUCTURE

### Backend:

* Python + FastAPI
* Modules:

  * `renderer.py`: Playwright-based renderer
  * `visual_analysis.py`: layout heuristics
  * `text_analysis.py`: NLP and readability scoring
  * `structure.py`: heading and hierarchy analysis
  * `scoring.py`: layer fusion and final score
  * `report.py`: HTML + PDF report generator

### Frontend:

* Nuxt 3 (Vue) + Tailwind CSS
* Views:

  * Home
  * Analysis results
  * History
  * Pricing + Auth

### Other:

* Supabase: auth, DB, screenshot storage
* Railway / Vercel: hosting
* Stripe: billing and subscriptions
* Redis: domain-level analysis cache (6h)

---

## 📥 USER FLOW

1. User pastes URL → clicks “Analyze”
2. Page is rendered using Playwright; DOM, CSS and screenshots are extracted
3. Visual + Text Analyzers process the data
4. Scoring engine outputs results and suggestions
5. Dashboard shows clarity scores, issues, recommendations
6. Pro plan includes: PDF exports, full history, API access

---

## 📊 EXAMPLE ANALYSIS OUTPUT (JSON)

```json
{
  "visual_score": 68,
  "text_score": 54,
  "overall_score": 61,
  "issues": [
    {
      "type": "contrast",
      "section": "hero CTA",
      "description": "Low contrast on CTA button",
      "suggestion": "Improve background or text color for better visibility"
    },
    {
      "type": "text",
      "section": "pricing",
      "description": "Average sentence length: 29 words",
      "suggestion": "Break content into shorter paragraphs and simplify wording"
    }
  ]
}
```

---

## 💵 BUSINESS MODEL (B2B / B2C HYBRID)

| Plan       | Price   | Target Users                          |
| ---------- | ------- | ------------------------------------- |
| Free       | \$0     | 3 analyses/month                      |
| Pro        | \$9/mo  | UX writers, designers, LP builders    |
| Agency     | \$29/mo | Agencies, freelancers (PDF + history) |
| Enterprise | \$99+   | API, integrations, white-label        |

---

## 🧠 FUTURE EXPANSIONS (V2+)

* AI-assisted CTA & content rewriting (prompt: “Simplify this sentence”)
* Plugins for Webflow, Framer, Wix
* Side-by-side version comparison (A/B test candidate pages)
* Conversion-oriented recommendations (CRO layer)
* Readability-based heatmaps (e.g. EyeQuant-style prediction)

---

## 🧭 FUNCTIONAL GOALS

* Page analyzed in < 15 seconds
* UX for non-tech users (marketers, designers)
* No embedded code or script required
* Stable, documented API
* Clear dashboard with prioritized action items

---

## 🧠 AI AGENT INSTRUCTIONS

If you are an AI agent with access to APIs, files, and NLP/CV models:

1. Use Playwright to render the submitted page URL
2. Extract DOM, CSS, screenshots and text content
3. Apply NLP & visual heuristics modules
4. Generate analysis JSON + HTML report
5. Export PDF and store results in Supabase

Each module should be modular, testable, and independently deployable.
All data should be cached per domain for 6 hours.
