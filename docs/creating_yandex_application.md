## Создание Яндекс приложения для авторизации.
1) Заходим на https://oauth.yandex.ru/client/new
2) Заполняем:
   - Название сервиса
   - Картинка
   - Для какой платформы нужно приложение: "Веб-сервисы"
     - Добавляем адреса Callback URL:
       - http[s]://адрес[:порт]/auth/yandex/login/callback/ - для продашена
       - http://localhost:8000/auth/yandex/login/callback/ - для локальных тестов
       - https://oauth.yandex.ru/verification_code/ - для любых тестов
   - Какие данные вам нужны: 
     - API Яндекс ID: 
       - Доступ к дате рождения
       - Доступ к адресу электронной почты
       - Доступ к логину, имени и фамилии, полу
   - Email для связи
3) Можно скопировать полученный от Яндекса _ClientID_ и _Client secret_ 
в `settings.py` => `SOCIALACCOUNT_PROVIDERS.yandex.APP` в _client_id_ и _secret_ соответственно.
Или использовать непосредственно переменные окружения `YANDEX_CLIENT_ID` и `YANDEX_SECRET`.
