# Repository Guidelines

## Project Structure & Module Organization

- `backend/` contains the FastAPI service and data ingest pipeline.
- `backend/main.py` defines API routes, `backend/database.py` handles PostgreSQL access, and `backend/ingest.py` loads Starlink data.
- `backend/Schema.sql` defines database schema (case-sensitive filename).
- `frontend/` contains the Vite + React app.
- `frontend/src/components/` holds UI modules (for example `SatelliteTable.jsx`, `BoosterDashboard.jsx`), and `frontend/src/App.jsx` wires views and API calls.
- `worker/` contains the Hono + Cloudflare Workers edge API (production).
- `.github/workflows/` is reserved for automation (currently minimal).

## Build, Test, and Development Commands

- Backend setup: `cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- Run backend API: `cd backend && source .venv/bin/activate && uvicorn main:app --reload`
- Run ingest job: `cd backend && source .venv/bin/activate && python ingest.py`
- Run SpaceX assets sync: `cd backend && source .venv/bin/activate && python sync_spacex_assets.py`
- Frontend setup/run: `cd frontend && npm install && npm run dev`
- Frontend production build: `cd frontend && npm run build`
- Frontend build preview: `cd frontend && npm run preview`
- Worker setup: `cd worker && npm install`
- Worker local dev: `cd worker && npm run dev` (uses wrangler dev)
- Worker deploy: `cd worker && npx wrangler deploy`

## Coding Style & Naming Conventions

- Python: PEP 8 style, 4-space indentation, `snake_case` for functions/variables, `UPPER_SNAKE_CASE` for constants.
- React/JSX: 2-space indentation, `PascalCase` component files and exports, `camelCase` hooks/state/helpers.
- Keep modules focused: API logic in `main.py`, SQL/data access in `database.py`, UI broken into component-sized files.
- Prefer descriptive names aligned with current patterns (`fetchSatellites`, `get_stats`, `boosterIntel`).

## Testing Guidelines

- No automated test suite is committed yet.
- For backend changes, validate endpoints manually via `http://localhost:8000/docs` and verify key routes (`/satellites`, `/stats`, SpaceX endpoints).
- For frontend changes, run `npm run build` and verify flows in `npm run dev` (home, boosters, starlink views).
- When adding tests, place backend tests under `backend/tests/` and frontend tests under `frontend/src/__tests__/`.

## Commit & Pull Request Guidelines

- Follow the repository’s existing commit style: short, imperative summaries (examples: `Fix booster status filter...`, `Add DB-backed SpaceX asset seed...`).
- Keep commits scoped to one logical change.
- PRs should include: purpose, key files changed, local verification steps, and screenshots/GIFs for UI updates.
- Link related issues and note any schema/env changes (`backend/.env`, DB migrations) in the PR description.

## Security & Configuration Tips

- Do not commit secrets. Keep credentials in `backend/.env` and `frontend/.env`.
- Typical local variables: `DATABASE_URL`, `SPACETRACK_USER`, `SPACETRACK_PASS`, `VITE_API_URL`.
- Use non-production credentials for local development data sources.
- For worker local development, use `worker/.dev.vars` (copy from `.dev.vars.example`).
- For production, set `DATABASE_URL` as a secret in Cloudflare dashboard.

## Key Architecture Notes

- Backend API serves as both development API and data ingest layer.
- Worker serves as production edge API (Cloudflare Workers).
- Frontend connects to backend API in dev (`VITE_API_URL=http://localhost:8000`) and to worker in production.
- Database schema in `backeqnd/Schema.sql` is shared between backend and worker.
- Data ingest pipelines:
  - `backend/ingest.py`: Starlink satellite data from space-track.org
  - `backend/sync_spacex_assets.py`: Booster/capsule data from spacexnow.com
- GitHub Actions workflows automate data synchronization:
  - Sync SpaceX Assets (runs `sync_spacex_assets.py`)
  - Ingest Starlink Data (runs `ingest.py`)

