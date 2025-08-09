# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Nuxt 3 application - a Vue.js framework for building web applications with server-side rendering, static site generation, and modern development features.

## Development Commands

- `npm run dev` - Start development server on http://localhost:3000
- `npm run build` - Build application for production
- `npm run generate` - Generate static site
- `npm run preview` - Preview production build locally
- `npm install` - Install dependencies

## Project Structure

- `app.vue` - Main application component (root layout)
- `nuxt.config.ts` - Nuxt configuration file
- `pages/` - File-based routing (create this directory to add routes)
- `components/` - Vue components (auto-imported)
- `layouts/` - Application layouts
- `middleware/` - Route middleware
- `plugins/` - Nuxt plugins
- `composables/` - Vue composables (auto-imported)
- `assets/` - Uncompiled assets (CSS, images, etc.)
- `static/` or `public/` - Static files served directly

## Key Concepts

- **Auto-imports**: Components, composables, and utilities are automatically imported
- **File-based routing**: Create pages by adding Vue files to the `pages/` directory
- **Server-side rendering**: Pages are rendered on both server and client
- **TypeScript**: Built-in TypeScript support without additional configuration