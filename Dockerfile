# Üretim imajı: Vue sitesi derlenir, Django API ile birlikte tek serviste sunulur.
# Yerel geliştirme için docker-compose.yml kullanılır; bu dosya Render ve benzeri ortamlar içindir.

FROM node:22-alpine AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBUG=False \
    FRONTEND_DIST_DIR=/app/frontend_dist
RUN apt-get update \
    && apt-get install -y --no-install-recommends gettext \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ ./
COPY --from=frontend /frontend/dist ./frontend_dist
RUN python manage.py compilemessages -l tr --ignore ".venv" >/dev/null \
    && python manage.py collectstatic --noinput >/dev/null \
    && useradd --create-home --uid 10001 app \
    && chown -R app /app
USER app
EXPOSE 8000
CMD ["sh", "./start-production.sh"]
