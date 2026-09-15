# Schema-Driven Dashboard Platform

A FastAPI backend and React + TypeScript + Tailwind frontend for registering schemas, validating data, and generating dashboard summaries and tables. Trade and customer examples use the same API.

## Setup and run

Requires Python 3.11+, uv, and Node.js 22.12+ with npm. Run from the repository root:

```bash
cd backend
uv sync --locked
cd ../frontend
npm ci
cd ..
make start
```

See `round_1_assignment.md` and `AI_REPORT.md` for more detail.
