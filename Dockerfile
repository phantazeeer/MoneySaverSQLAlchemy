FROM python:3.13-alpine AS build
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /application
RUN apk add curl
COPY ./pyproject.toml ./
COPY ./uv.lock ./
COPY .env.template .env
RUN uv sync --extra docker
COPY . .
CMD ["uv", "run", "gunicorn", "-c", "gunicorn.conf.py", "--capture-output", "server:app"]
