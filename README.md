### Установка

#### Установить Docker и Docker-Compose.

[См. официальная документация по установке Docker](https://docs.docker.com/engine/install/) <br>
[См. официальная документация по установке Docker compose](https://docs.docker.com/compose/install/)


#### Скопировать содержимое образца файла окружения `cp env.sample .env` в следующих директорях:
1. `lizaalert-backend/`
2. `services/postgres`

#### Собрать контейнеры

`docker-compose build`

#### Запуск

`docker-compose up -d`

### Использование

- В случае, если сборка запускается впервые, нужно выполнить следующие действия:
  - Необходимо подключиться к контейнеру Django с помощью команды `docker exec -it admin_panel bash`
  - Применить миграции `python manage.py migrate --no-input`. 
  - В случае если база была предварительно заполнена данными и зависимостями - миграции стоит применять с флагом `--fake-initial`
  - Создать суперпользователя `python manage.py createsuperuser`
  - Получить статику `python manage.py collectstatic --no-input`
  - Отключиться от контейнера: `exit`
- Админка доступна [здесь](http://localhost:8000/admin)