# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ClarityCheck** - A web-based SaaS application for analyzing websites for visual clarity and text readability. Built with Nuxt 3 frontend and Python FastAPI backend.

## Development Commands

### Frontend (Nuxt 3)
- `npm run dev` - Start frontend development server on http://localhost:3000
- `npm run build` - Build frontend for production
- `npm run generate` - Generate static site
- `npm run preview` - Preview production build locally
- `npm install` - Install frontend dependencies

### Backend (Python FastAPI)
- `cd backend && python run_server.py` - Start backend server on http://localhost:8000
- `cd backend && pip install -r requirements.txt` - Install backend dependencies
- Backend must be running on port 8000 for frontend to work correctly

## Project Structure

### Frontend
- `pages/index.vue` - Main analysis dashboard with URL input and results display
- `components/` - Vue components (AppHeader.vue, AppLayout.vue)
- `nuxt.config.ts` - Nuxt configuration
- `app.vue` - Root layout component

### Backend
- `backend/app/main.py` - FastAPI application entry point
- `backend/app/api/analysis.py` - Main analysis API endpoints (/api/v1/analyze/quick)
- `backend/app/modules/` - Analysis modules (visual_analysis.py, text_analysis.py, etc.)
- `backend/run_server.py` - Server startup script (use this to start backend)

## Key Features

- **Website Analysis**: Submit URL → get visual clarity + text readability scores
- **Screenshot Capture**: Full-page screenshots with Selenium/Playwright
- **Issue Grouping**: Visual and text issues organized by DOM sections
- **Multi-layered Analysis**: Visual clarity, text readability, accessibility, CTA analysis
- **Real-time Progress**: Loading states with analysis step tracking

## API Integration

- Frontend calls `http://127.0.0.1:8000/api/v1/analyze/quick`
- Expects response with: grouped_issues, screenshot_url, visual_issues, text_seo_issues
- Backend runs analysis modules and returns comprehensive UX report

## Troubleshooting

- If backend shows "Network error: Failed to fetch" → Check backend is running on port 8000
- If no screenshots → Backend analysis modules need to be properly configured
- If analysis is instant → Check backend is using proper analysis pipeline, not just HTTP fallback

See `context.md` for detailed project specification and architecture.

## CRITICAL DEVELOPMENT RULE

⚠️ **NEVER USE PLACEHOLDER/DEMO/MOCK DATA** unless explicitly requested by the user.

- Always implement real functionality with proper data sources
- No fake screenshots, dummy content, or sample responses  
- If real implementation isn't working, fix the underlying issue rather than using placeholders
- Users expect actual analysis results from real websites, not demo data