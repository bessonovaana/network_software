# Архитектура 

## Сервисы

### `user-service` (REST, FastAPI)
- **Назначение**: регистрация и аутентификация пользователей.
- **API**:
  - `POST /users/register`
  - `POST /users/login`
  - `GET /health`
- **Хранилище**: PostgreSQL (`postgres-users`, БД `users_db`)
- **Протокол**: HTTP/REST (в т.ч. для внешнего доступа через Nginx)

### `order-service` (REST, FastAPI)
- **Назначение**: создание заказов.
- **API**:
  - `POST /orders/`
  - `GET /health`
- **Хранилище**: PostgreSQL (`postgres-orders`, БД `orders_db`)
- **Интеграции**:
  - **RabbitMQ**: публикует событие `orders.created` в очередь `orders.created`.
- **Протокол**: HTTP/REST для API; AMQP для событий

### `notification-service` (REST + consumer)
- **Назначение**: обработка событий о заказах и отправка уведомлений (в проекте — логирование события).
- **API**:
  - `GET /health`
- **Интеграции**:
  - **RabbitMQ**: подписывается на очередь `orders.created`.
- **Протокол**: HTTP/REST для health; AMQP для событий

## Инфраструктура

### Reverse proxy
`nginx` проксирует запросы на сервисы:
- `/user-service/*` → `user-service:8000`
- `/order-service/*` → `order-service:8000`
- `/notification-service/*` → `notification-service:8000`

### Сеть
Все контейнеры в одной docker-сети `backend`.

## Потоки данных

1. Клиент вызывает `order-service` (REST) для создания заказа.
2. `order-service` записывает заказ в PostgreSQL.
3. `order-service` публикует событие в RabbitMQ (`orders.created`).
4. `notification-service` читает событие из RabbitMQ и обрабатывает (в текущей реализации — пишет в лог).

