docker-up:
  docker compose up -d

docker-down:
  docker compose down -v

docker-db-it:
  docker exec -it fooglemaps-db psql -U fooglemaps

backend-sync:
  cd server && uv sync --all-extras

backend:
  cd server && just backend-sync && uv run alembic upgrade head && uv run uvicorn app.main:app --reload

frontend:
  npm install
  npm run dev