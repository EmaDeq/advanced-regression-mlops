FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MLOPS_ENV=container \
    MLOPS_PROJECT_ROOT=/app
WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ ./src/
RUN pip install --no-cache-dir .

# Starter-only: train during image build. Later CI/CD will promote one immutable image.
RUN python -m advanced_regression_mlops.train --n-iter 6
RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1
CMD ["uvicorn", "advanced_regression_mlops.api:app", "--host", "0.0.0.0", "--port", "8000"]
