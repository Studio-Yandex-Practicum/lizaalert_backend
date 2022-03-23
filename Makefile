run:
	python ./lizaalert-backend/manage.py runserver
migrate:
	python ./lizaalert-backend/manage.py makemigrations
	python ./lizaalert-backend/manage.py migrate
lint:
	isort ./ && flake8 ./
packages:
	pip install -r ./lizaalert-backend/requirements/dev.txt
superuser:
	python ./lizaalert-backend/manage.py createsuperuser
static:
	python ./lizaalert-backend/manage.py collectstatic --no-input
secret:
	python keygen.py
