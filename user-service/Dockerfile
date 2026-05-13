FROM python:3.11-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim
WORKDIR /app

# Копируем установленные пакеты
COPY --from=builder /install /usr/local

# Копируем ВСЕ файлы проекта (т.к. нет папки src/)
COPY . .

# Создаём пользователя и меняем права ТОЛЬКО на /app
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000 50051

HEALTHCHECK --interval=30s --timeout=5s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Если main.py в корне, а не в src/
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]