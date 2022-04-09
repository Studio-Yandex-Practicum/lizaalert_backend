## Платформа для обучения добровольцев "ЛизаАлерт" - Backend

[Список задач](https://github.com/Studio-Yandex-Practicum/lizaalert_backend/issues/19)

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


## Make команды

[Описание установки make для windows](https://gist.github.com/evanwill/0207876c3243bbb6863e65ec5dc3f058)

* **run** - запуск сервера разработки.
* **migrate** - синхронизация состояние базы данных с текущим состоянием моделей и миграций.
* **lint** - проверка правильности кода.
* **packages** - установка dev-зависимостей.
* **superuser** - создание учётной записи администратора.
* **static** - сбор статики.
* **secret** - генерация нового секретного ключа для локального окружения.


### Общие требования к коду проекта и принципы код-ревью

- [Общие требования к коду проекта](docs/codestyle.md)
