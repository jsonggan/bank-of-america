# Project rules

- Follow `round_1_assignment.md`; keep changes minimal.
- Backend: FastAPI. Application code in `backend/src/`: business logic in `controllers/`, in-memory state in `models/`, HTTP routes in `routes/`, app wiring in `app.py`, and application settings in `config.py`; dependencies in `backend/pyproject.toml`. Use `uv sync --locked` and `uv run --locked` from `backend/`; keep `backend/uv.lock` updated.
- Frontend: React, TypeScript, Tailwind in `frontend/src/`. Keep one App component with four numbered assignment steps; reuse `examples/`.
- Use one backend worker and in-memory storage only.
- Keep batches atomic and validation strict: no coercion, unknown row fields, duplicate JSON keys, or nonfinite numbers. Send editor JSON unchanged.
- Backend tests mirror `src/` under `backend/tests/unit/` and `backend/tests/integration/`; keep shared data in `backend/tests/fixtures.py` and browser workflows in `frontend/e2e/`.
- Write a failing regression test before changing behavior; preserve existing assertions.
- Run `make test`; also `make lint` for any backend changes, `make build` for frontend changes, and `make test-e2e` for workflow changes.
- `make start` runs backend on 8000 and frontend on 5173. Setup is in `README.md`.
