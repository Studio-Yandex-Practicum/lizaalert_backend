
# Собирает и разворачивает на локальной машине все контейнеры и применят миграции,
# предварительно удалив существующие volumes (БД, статика, медиа) и контейнеры.
new:
	-docker-compose down --volumes
	docker-compose up --detach --build \
	&& sleep 20 \
	&& docker-compose exec backend python manage.py migrate

# Запуск с пересборкой изменившихся контейнеров. Не трогает volumes (БД, статика, медиа).
run:
	docker-compose up --detach --build

# Собирает статику
collect:
	docker-compose exec backend python manage.py collectstatic --no-input

# Создает суперпользователя
superuser:
	docker-compose exec backend python manage.py createsuperuser --no-input

# Проверка кода на соответствие PEP8.
check:
	docker-compose exec backend isort --check .
	docker-compose exec backend black --check .
	docker-compose exec backend flake8 .

# Запуск тестов.
test:
	docker-compose exec backend pytest tests/

# Удаляет все контейнеры и volumes.
remove:
	-docker-compose down --volumes

build:
	docker build -f services/base/Dockerfile -t local/lizaalert_backend-base . 
	docker build -f services/local/Dockerfile -t local/lizaalert_backend . 

push:
	make build
	docker tag local/lizaalert_backend cr.yandex/crpph3mqagnq011414qt/lizaalert_backend:latest
	docker push cr.yandex/crpph3mqagnq011414qt/lizaalert_backend:latest

up:
	docker-compose up -d