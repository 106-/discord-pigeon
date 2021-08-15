FROM python:3.9 AS exporter
COPY ./poetry.lock /poetry.lock
COPY ./pyproject.toml /pyproject.toml
RUN pip install poetry
RUN poetry export -f requirements.txt > requirements.txt

FROM python:3.9 AS builder
COPY --from=exporter /requirements.txt /requirements.txt
RUN pip3 install -r requirements.txt

FROM python:3.9-slim AS runner
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
WORKDIR /app
COPY ./discord_pigeon /app/discord_pigeon
CMD ["python", "/app/discord_pigeon/main.py"]