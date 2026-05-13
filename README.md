# Финальный проект 

## Запуск

Требования: установлен Docker + Docker Compose plugin.

```bash
docker compose up -d --build
```

## Проверка, что всё работает

### Через nginx (порт 80)
- `GET /user-service/health`
- `GET /order-service/health`
- `GET /notification-service/health`

Пример:

```bash
curl -sS http://localhost/user-service/health
curl -sS http://localhost/order-service/health
curl -sS http://localhost/notification-service/health
```

### Напрямую по портам
- `user-service`: `http://localhost:8001/health`
- `order-service`: `http://localhost:8002/health`
- `notification-service`: `http://localhost:8003/health`

## Остановка

```bash
docker compose down
```

## Архитектура

См. `ARCHITECTURE.md`.

