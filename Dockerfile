FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml .

RUN pip install --no-cache-dir .

COPY . /app

ENV PYTHONPATH="/app/src"

EXPOSE 8000

ENTRYPOINT [ "python", "-m", "service_health_checker.cli" ]

CMD ["--help"]
