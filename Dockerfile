FROM python:3.13-alpine AS build
WORKDIR /application
COPY ./requirements.txt .
RUN python -m venv .venv && source .venv/bin/activate && pip install --no-cache-dir -r requirements.txt
COPY . .

FROM python:3.13-alpine AS runner
WORKDIR /application
COPY --from=build /application/.venv ./.venv
COPY --from=build /application/app ./app
COPY --from=build /application/.env ./.env
COPY --from=build /application/server.py ./server.py
EXPOSE 8000:8000
ENV API_HOST=0.0.0.0
CMD source .venv/bin/activate && python server.py
