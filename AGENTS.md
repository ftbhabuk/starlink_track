# Repository Guidelines

## Project Structure & Module Organization
- `backend/` contains the FastAPI service and data ingest pipeline.
- `backend/main.py` defines API routes, `backend/database.py` handles PostgreSQL access, and `backend/ingest.py` loads Starlink data.
- `backend/Schema.sql` defines database schema (case-sensitive filename).
- `frontend/` contains the Vite + React app.
- `frontend/src/components/` holds UI modules (for example `SatelliteTable.jsx`, `BoosterDashboard.jsx`), and `frontend/src/App.jsx` wires views and API calls.
- `.github/workflows/` is reserved for automation (currently minimal).

## Build, Test, and Development Commands
- Backend setup: `cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- Run backend API: `cd backend && source .venv/bin/activate && uvicorn main:app --reload`
- Run ingest job: `cd backend && source .venv/bin/activate && python ingest.py`
- Frontend setup/run: `cd frontend && npm install && npm run dev`
- Frontend production build: `cd frontend && npm run build`
- Frontend build preview: `cd frontend && npm run preview`

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
