
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
	cd src
	isort --check .
	flake8 .
	black --check .
	cd ..

black:
	isort ./src
	black ./src

# Запуск тестов.
test:
	docker-compose exec backend pytest tests/

# Удаляет все контейнеры и volumes.
remove:
	-docker-compose down --volumes

build:
	docker build -f services/base/Dockerfile -t local/lizaalert_backend-base . 
	docker build -f services/local/Dockerfile -t local/lizaalert_backend . 
	docker build -f services/nginx/local.Dockerfile -t local/lizaalert_nginx .

push:
	make build
	docker tag local/lizaalert_backend cr.yandex/crpabbati0r6r7i5ee8c/lizaalert_backend:latest
	docker push cr.yandex/crpabbati0r6r7i5ee8c/lizaalert_backend:latest

update-ci:
	docker build -f services/base/Dockerfile -t local/lizaalert_backend-base . 
	docker build -f services/ci/Dockerfile -t local/lizaalert_backend-ci . 
	docker tag local/lizaalert_backend-ci cr.yandex/crpabbati0r6r7i5ee8c/lizaalert_backend-ci:latest

update-nginx:
	docker build -f services/nginx/Dockerfile -t cr.yandex/crpabbati0r6r7i5ee8c/nginx:latest .
	docker push cr.yandex/crpabbati0r6r7i5ee8c/nginx:latest

up:
	docker-compose up -d