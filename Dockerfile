FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc gettext \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh \
    && SECRET_KEY=build-only DEBUG=False python manage.py collectstatic --noinput

EXPOSE 8000

ENTRYPOINT ["/bin/sh", "entrypoint.sh"]
CMD ["sh", "-c", "gunicorn experio.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]
