.PHONY: up down logs ps test

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f --tail=200

ps:
	docker compose ps

# Минимальный "test" для локальной самопроверки.
# В учебном репозитории обычно есть свой make test WEEK=17,
# но если его нет — этот таргет хотя бы валидирует наличие ключевых файлов.
test:
	@test -f ARCHITECTURE.md
	@test -f README.md
	@echo "OK: required docs exist"

