FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

RUN addgroup -S app && adduser -S -G app -u 10001 app

COPY --chown=app:app src/ ./src/

USER app
EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=3s --start-period=2s --retries=3 \
  CMD python -c "import os, urllib.request; r = urllib.request.urlopen('http://127.0.0.1:' + os.getenv('PORT', '8080') + '/health', timeout=2); assert r.status == 200; r.close()"

CMD ["python", "-m", "src.catalog_service"]
