
# Собирает и разворачивает на локальной машине все контейнеры, предварительно
# удалив существующие volumes (БД, статика, медиа) и контейнеры. Применяет
# миграции, собирает статику и создает суперпользователя.
new:
	-docker-compose down --volumes
	docker-compose up --detach --build \
	&& sleep 20 \
	&& docker-compose exec backend python manage.py migrate \
	&& docker-compose exec backend python manage.py collectstatic --no-input \
	&& docker-compose exec backend python manage.py createsuperuser --no-input


# Пересборка изменившихся контейнеров. Не трогает volumes (БД, статика, медиа).
run:
	docker-compose up --detach --build


# Проверка кода на соответствие PEP8.
check:
	-isort --check .
	-black --check .
	-flake8 .


# Запуск тестов.
test:
# TODO


# Удаляет все контейнеры и volumes.
remove:
	-docker-compose down --volumes