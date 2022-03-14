#!/bin/sh

# если база еще не запущена
echo "DB not yet run..."
# Проверяем доступность хоста и порта
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "DB did run."

if [ $1 = "migrate" ]
then
  # Выполняем миграции
  python manage.py makemigrations core
  python manage.py migrate
  python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL
else
  python manage.py collectstatic --noinput
  gunicorn -c './gunicorn_conf.py' settings.wsgi
fi
exec "$@"