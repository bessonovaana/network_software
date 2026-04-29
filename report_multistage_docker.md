# Отчет по Docker

## Размер образов

**Исходный образ**: 476 MB  
**Оптимизированный (multi-stage)**: 160 MB  
**Экономия**: 316 MB 

Команда для проверки:  
```bash
docker images <image_name> --format "{{.Size}}"
```

## Количество слоёв

### Исходный Dockerfile в service2 (7 слоёв):

    FROM ubuntu:22.04 # Базовый Ubuntu

    COPY requirements.txt . # Копия requirements

    RUN apt-get update && pip install... # Все пакеты + Python deps (1 слой!)

    WORKDIR /app # Рабочая директория

    COPY . . # Копия кода приложения

    USER appuser # Смена пользователя

    CMD ["python3", "-m", "uvicorn"...] # Команда запуска

### Оптимизированный multi-stage в service1 (10 слоёв):

Builder stage (промежуточный):

    FROM python:3.11-slim AS builder # Базовый Python

    WORKDIR /app # Директория

    COPY requirements.txt . # Requirements

    RUN pip install --prefix=/install... # Установка в /install

Final stage:

    FROM python:3.11-slim # Финальный базовый слой

    WORKDIR /app # Директория

    COPY --from=builder /install... # Только нужные зависимости

    COPY . . # Код приложения

    EXPOSE 8195 # Порт (metadata)

    CMD ["uvicorn", "app.main:app"...] # Запуск

