FROM python:3.13-alpine AS build
WORKDIR /application
COPY ./requirements.txt .
RUN python -m venv .venv
RUN .venv/bin/pip install --no-cache-dir -r requirements.txt
COPY . .
RUN .venv/bin/alembic upgrade head

FROM python:3.13-alpine AS runner
WORKDIR /application
COPY --from=build /application ./
RUN ls -la .venv/bin
EXPOSE 8000:8000
ENV API_HOST=0.0.0.0
CMD .venv/bin/python server.py
