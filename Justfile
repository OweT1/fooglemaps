docker-up:
  docker compose up -d

docker-down:
  docker compose down -v

docker-db-it:
  docker exec -it fooglemaps-db psql -U fooglemaps

backend-sync:
  cd backend && uv sync --all-extras

backend:
  cd backend && just backend-sync && uv run alembic upgrade head && uv run uvicorn fooglemaps.main:app --reload

frontend:
  cd frontend/fooglemaps && npm install && npm run dev