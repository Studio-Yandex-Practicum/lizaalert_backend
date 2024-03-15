
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

# Запуск с контейнером minio
run-with-minio:
	docker-compose -f docker-compose.yml -f docker-compose.s3.yml up --detach --build

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
	docker tag local/lizaalert_backend cr.yandex/crpabbati0r6r7i5ee8c/lizaalert_backend:latest
	docker push cr.yandex/crpabbati0r6r7i5ee8c/lizaalert_backend:latest

build_push:
	make build
	make push

update-ci:
	docker build -f services/base/Dockerfile -t local/lizaalert_backend-base .
	docker build -f services/ci/Dockerfile -t local/lizaalert_backend-ci .
	docker tag local/lizaalert_backend-ci cr.yandex/crpabbati0r6r7i5ee8c/lizaalert_backend-ci:latest

update-nginx:
	docker build -f services/nginx/Dockerfile -t cr.yandex/crpabbati0r6r7i5ee8c/nginx:latest .
	docker push cr.yandex/crpabbati0r6r7i5ee8c/nginx:latest

up:
	docker-compose up -d

DEV_CONTAINER = dev_lizaalert
DEV_DB_CONTAINER = dev_db_psql
DEV_DB_VOLUME = dev_db_volume
DEV_DB_NAME = lizaalert
DEV_DB_USER = postgres
DEV_DB_PASSWORD = password

DEV_USER = Liza
DEV_USER_MAIL = liza@alert.ru
DEV_USER_PS = ps

dev-rebuild:
	-docker stop $(DEV_CONTAINER)
	-docker stop $(DEV_DB_CONTAINER)
	-docker volume rm $(DEV_DB_VOLUME)

	docker run -d --rm\
    --name $(DEV_DB_CONTAINER) \
    -p 5432:5432 \
    --mount type=volume,src=$(DEV_DB_VOLUME),dst=/var/lib/postgresql/data \
    -e POSTGRES_PASSWORD=$(DEV_DB_PASSWORD) \
	-e POSTGRES_DB=$(DEV_DB_NAME) \
    postgres:14-alpine


	docker build -f services/base/Dockerfile -t local/lizaalert_backend-base .
	docker build -f services/dev/Dockerfile -t local/lizaalert_backend_dev .

	docker run -d -t -i --rm --network host\
		--name $(DEV_CONTAINER) local/lizaalert_backend_dev
	-docker exec -it \
		-e DB_USER=$(DEV_DB_USER) \
		-e DB_PASSWORD=$(DEV_DB_PASSWORD) \
		-e DB_NAME=$(DEV_DB_NAME) \
		$(DEV_CONTAINER) python3 manage.py migrate

	- docker exec -it \
		-e DB_USER=$(DEV_DB_USER) \
		-e DB_PASSWORD=$(DEV_DB_PASSWORD) \
		-e DB_NAME=$(DEV_DB_NAME) \
		-e DJANGO_SUPERUSER_PASSWORD=$(DEV_USER_PS) \
		-e DJANGO_SUPERUSER_USERNAME=$(DEV_USER) \
		-e DJANGO_SUPERUSER_EMAIL=$(DEV_USER_MAIL) \
		$(DEV_CONTAINER) python3 manage.py createsuperuser --no-input

	docker stop $(DEV_CONTAINER)

dev-run:
	@docker start $(DEV_DB_CONTAINER) || docker run -d --rm\
    --name $(DEV_DB_CONTAINER) \
    -p 5432:5432 \
    --mount type=volume,src=$(DEV_DB_VOLUME),dst=/var/lib/postgresql/data \
    -e POSTGRES_PASSWORD=$(DEV_DB_PASSWORD) \
	-e POSTGRES_DB=$(DEV_DB_NAME) \
    postgres:14-alpine

	docker build -f services/dev/Dockerfile -t local/lizaalert_backend_dev .

	docker run -d -t -i --rm --network host\
		-p 8000:8000 \
		--name $(DEV_CONTAINER) local/lizaalert_backend_dev
	-docker exec -it \
		-e DB_USER=$(DEV_DB_USER) \
		-e DB_PASSWORD=$(DEV_DB_PASSWORD) \
		-e DB_NAME=$(DEV_DB_NAME) \
		-e DEBUG=true \
		$(DEV_CONTAINER) python3 manage.py runserver 0.0.0.0:8000 --settings lizaalert.settings.local --verbosity 2


	docker stop $(DEV_CONTAINER)

dev-stop:
	-docker stop $(DEV_DB_CONTAINER)
	-docker stop $(DEV_CONTAINER)

dev-test:
	docker build -f services/dev/Dockerfile -t local/lizaalert_backend_dev .
	docker run -d -t -i --rm --network host\
		--name $(DEV_CONTAINER) local/lizaalert_backend_dev

	-docker exec -it \
		$(DEV_CONTAINER) python3 -m pytest -s

	docker stop $(DEV_CONTAINER)
