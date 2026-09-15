SHELL := /bin/bash

.PHONY: start backend frontend test test-backend test-frontend test-e2e lint build

start:
	@trap 'kill 0' INT TERM EXIT; \
	(cd backend && uv run --locked uvicorn backend.src.app:create_app --factory --host 127.0.0.1 --port 8000 --workers 1) & \
	(cd frontend && npm run dev) & \
	wait

backend:
	cd backend && uv run --locked uvicorn backend.src.app:create_app --factory --host 127.0.0.1 --port 8000 --workers 1

frontend:
	cd frontend && npm run dev

test: test-backend test-frontend

test-backend:
	cd backend && uv run --locked pytest -q

test-frontend:
	cd frontend && npm test -- --run

test-e2e:
	cd frontend && npm run test:e2e

lint:
	cd backend && uv run --locked ruff check .

build:
	cd frontend && npm run build
