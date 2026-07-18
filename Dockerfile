FROM node:22-slim AS frontend
WORKDIR /ui
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STUDIO_MODE=hosted
COPY pyproject.toml README.md LICENSE NOTICE ./
COPY src/ ./src/
COPY fixtures/ ./fixtures/
COPY --from=frontend /ui/dist/ ./src/moe_autopilot_studio/static/
RUN pip install --no-cache-dir .
EXPOSE 7860
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:7860/api/health', timeout=3)"
CMD ["uvicorn", "moe_autopilot_studio.app:app", "--host", "0.0.0.0", "--port", "7860"]
