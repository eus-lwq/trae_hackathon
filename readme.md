# Community-Driven Travel Planner

## Why This Topic
- Current travel planning tools lack authentic community insight; they are dominated by ads and stale content.
- Real travelers share timely, on-the-ground updates in community platforms, but that signal is scattered and hard to use.
- Capturing real-time posts and turning them into actionable trip plans improves relevance, trust, and local discovery.

## What's Different
- Community-based insight gathering from platforms like Xiaohongshu/RED, Reddit, and Nextdoor (real user posts, not ads).
- Near real-time aggregation and tagging of posts to surface fresh places, tips, and cautions.
- A planner that converts community signals into routes, day plans, and map overlays tailored to preferences.

## Architecture

```text
         Community Sources                     Processing                    Delivery                 Experience
 ┌──────────────────────────┐        ┌──────────────────────────┐      ┌─────────────────────┐      ┌──────────────────────────┐
 │  RED (Xiaohongshu)       │  --->  │  Ingestion (scrapers/API)│ ---> │  Planner API (TBD)  │ ---> │  React Frontend (SPA)     │
 │  Reddit                  │        │  NLP + Tagging            │      │  REST/GraphQL         │      │  Map + Cards + Chat Assist │
 │  Nextdoor               │        │  Geocoding + Dedup        │      │  Caching              │      │  Leaflet map + Zustand     │
 └──────────────────────────┘        └──────────────────────────┘      └─────────────────────┘      └──────────────────────────┘
                                                      │
                                                      ▼
                                          Trip Plan Generator (routes, days, constraints)
```

Notes
- This repository currently implements the frontend SPA and uses mock data for attractions.
- The backend ingestion and planner API are not yet included; they are planned components.

## Tech Stack
- Frontend: React 18, Vite 6, TypeScript, Tailwind CSS, React Router, Leaflet (react-leaflet), Zustand.
- Backend: Not present in this repo (planned ingestion and planner services).
- Deployment: Vercel SPA (`vercel.json` rewrites all routes to `index.html`).
