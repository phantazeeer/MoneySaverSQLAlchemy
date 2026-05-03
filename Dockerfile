FROM python:3.13-alpine AS build
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /application
COPY ./pyproject.toml ./
COPY ./uv.lock ./
COPY .env.template .env
RUN uv sync --locked
COPY . .
RUN uv run alembic upgrade head
EXPOSE 8000:8000
CMD ["uv", "run", "server.py"]
