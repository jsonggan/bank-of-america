# Schema-Driven Dashboard Platform

A FastAPI backend and React + TypeScript + Tailwind frontend for registering schemas, validating data, and generating dashboard summaries and tables. Trade and customer examples use the same API.

## Setup and run

Requires Python 3.11+, uv, and Node.js 22.12+ with npm. Run these commands from the repository root:

```bash
cd backend
uv sync --locked
cd ../frontend
npm ci
cd ..
make start
```

`make start` requires GNU Make and starts both servers. Open the [app](http://127.0.0.1:5173) or the [interactive API docs](http://127.0.0.1:8000/docs). No database or environment file is needed.

Without Make, start each server in a separate terminal from the repository root:

```bash
# Backend
cd backend
uv run --locked uvicorn backend.src.app:create_app --factory --host 127.0.0.1 --port 8000 --workers 1
```

```bash
# Frontend
cd frontend
npm run dev
```

All data is stored in memory and cleared when the backend restarts. Run only one backend worker.

## Try it

The UI comes prefilled with the [trade examples](examples/). Submit the four numbered sections in order:

1. **Register Schema** — define field names, types, and required fields.
2. **Ingest Data** — submit rows for validation and storage.
3. **Register Dashboard Configuration** — choose the schema, sum summaries, and table columns.
4. **Generate Dashboard Data** — retrieve the configured dashboard as JSON.

The trade example returns a sum of **3000** and three table rows. Replace the inputs with the customer examples to try another schema. Reusing a registered name returns a conflict; restart the backend for a fresh demo.

## API

| Endpoint | Purpose |
| --- | --- |
| `POST /schema` | Register a named schema with `string` and `number` fields. |
| `POST /ingest` | Validate and store rows against a schema. |
| `POST /dashboard` | Register a dashboard with an explicit `schema` reference and summary or table views. |
| `GET /dashboard/{name}` | Return the configured views using stored data. |

Validation is strict: missing required fields, unknown row fields, incorrect types, duplicate JSON keys, and nonfinite numbers are rejected. Values are never coerced. Each batch is atomic: if any row is invalid, none of the batch is stored. Summaries support `sum` on numeric fields.

Errors return an `errors` array with a path and reason; row errors also identify the row and field. Invalid input returns `422`, missing references `404`, and duplicate registration names `409`. See the [API docs](http://127.0.0.1:8000/docs) for request examples.

## Tests

Run from the repository root after setup:

```bash
make test       # Backend unit/integration and frontend component tests
make lint       # Backend Ruff checks
make build      # Frontend production build
```

For browser tests, install Chromium once, then run:

```bash
cd frontend
npx playwright install chromium
cd ..
make test-e2e
```

Browser tests start their own servers on ports 8001 and 5174; keep those ports free.

## Project structure

- `backend/src/` — controllers for business logic, models for in-memory state, routes for HTTP, plus app wiring and settings.
- `backend/tests/` — unit and integration tests.
- `frontend/src/` — the four-step UI and component tests.
- `frontend/e2e/` — browser workflows.
- `examples/` — trade and customer JSON requests shared with the UI.

See the [assignment](round_1_assignment.md) and [AI report](AI_REPORT.md) for more detail.
