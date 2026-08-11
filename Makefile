.PHONY: help up down logs restart backend frontend test

help:
	@echo "Garuda Kavach Development Commands"
	@echo ""
	@echo "make up        - Start infrastructure"
	@echo "make down      - Stop infrastructure"
	@echo "make logs      - Show Docker logs"
	@echo "make restart   - Restart infrastructure"
	@echo "make backend   - Start backend"
	@echo "make frontend  - Start frontend"
	@echo "make test      - Run tests"

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

restart:
	docker compose down
	docker compose up -d

backend:
	cd backend && uvicorn app.main:app --reload

frontend:
	cd frontend && npm run dev

test:
	cd backend && pytest