# WooCommerce CRM — Evidence-Based AI Customer Intelligence

Hackathon MVP implementing the documentation: React + Vite frontend, FastAPI backend, SQLite dummy data, explainable segmentation, seasonal campaigns, and evidence-based AI recommendations.

## Quick start

### Backend (FastAPI + SQLite)
```bash
cd backend
python3 -m pip install -r requirements.txt
PYTHONPATH=. python3 -m app.seed
PYTHONPATH=. python3 -m uvicorn app.main:app --reload --port 8000
```

### Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
# open http://localhost:5173
```

## Environment
- `OPENAI_API_KEY` — optional free-tier OpenAI-compatible key in `backend/.env`
- `DATABASE_URL` — optional, defaults to local SQLite `backend/crm.db`
- `REFERENCE_DATE` — optional override, `YYYY-MM-DD`

No PostgreSQL installation is required. The app creates a local SQLite database and fills it with clearly synthetic dummy records.

## Demo data
On startup the backend auto-seeds synthetic dummy data if the SQLite database is empty. Use **Reset Demo Data** on the dashboard or `POST /sync/demo/reset`.

## LLM setup
If `OPENAI_API_KEY` is present, the recommendation endpoint uses a free OpenAI-compatible provider for explanation/message drafting. If it is missing or fails, the API falls back to deterministic dummy drafts.

## Key endpoints
- `GET /dashboard/summary`
- `GET /customers`, `GET /customers/{id}`
- `GET /orders`
- `GET /calendar/campaigns`
- `GET /recommendations/generate?customer_id=`
- `GET/POST/PATCH /communications`