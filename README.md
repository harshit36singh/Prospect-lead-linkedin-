# Prospect Lead

A local B2B lead-generation and prospecting platform: define an Ideal Customer
Profile (ICP), discover matching companies, find real decision-makers,
enrich contact info, verify and score leads, dedupe, and export to Google
Sheets and PDF reports.

## Why not LinkedIn?

LinkedIn's User Agreement prohibits automated data collection, and there's
no public/unauthenticated feed for company or people search the way Reddit
publishes RSS feeds — bulk prospecting access is what LinkedIn sells
(Sales Navigator), not something they give away for free automation. So this
project sources real leads from data that's genuinely public and intended
for programmatic use instead:

- A curated seed list of real companies (`backend/data/seed_companies.json`)
- GitHub's public REST API for decision-makers + tech stack, for companies
  with a public GitHub org

See `backend/data/seed_companies.json` to add more companies.

## Requirements

- Python 3.11+
- Node.js 20+

## Setup

```powershell
# Backend
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env   # optional: add PROSPECTLEAD_GITHUB_TOKEN / GOOGLE_SERVICE_ACCOUNT_JSON

# Frontend
cd ../frontend
npm install
```

## Running

```powershell
# Terminal 1
cd backend
.venv\Scripts\uvicorn app.main:app --reload

# Terminal 2
cd frontend
npm run dev
```

Open http://localhost:5173.

## Project structure

```
backend/            FastAPI app (models, routers, discovery, enrichment,
                     verification, scoring, dedupe, export, pipeline)
backend/data/        seed_companies.json (real company reference data)
backend/reports/     generated PDF reports (gitignored)
frontend/            React + Vite + TypeScript dashboard
```
