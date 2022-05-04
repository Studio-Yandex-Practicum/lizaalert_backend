run:
	poetry run python ./lizaalert-backend/manage.py runserver 0.0.0.0:8000
migrate:
	poetry run python ./lizaalert-backend/manage.py makemigrations
	poetry run python ./lizaalert-backend/manage.py migrate
lint:
	poetry run isort ./ && poetry run flake8 ./
superuser:
	python ./lizaalert-backend/manage.py createsuperuser
static:
	poetry run python ./lizaalert-backend/manage.py collectstatic --no-input
secret:
	poetry run python keygen.py