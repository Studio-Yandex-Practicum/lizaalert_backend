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

- При первичном ините проекта автоматически будет создан суперпользователь Django. Логин и пароль для входа расположен в ``lizaalert-backend/.env``
- Админка доступна [здесь](http://localhost:8000/admin)