FROM local/lizaalert_backend-base

EXPOSE 8000/tcp

COPY src/manage.py .
COPY src/gunicorn_conf.py .
COPY src/lizaalert-backend ./lizaalert

# устанавливаем сертификат для подключения к БД
RUN mkdir ~/.postgresql
ADD services/local/postgresql.crt ~/.postgresql/root.crt

CMD ["gunicorn", "-c", "/app/gunicorn_conf.py", "settings.wsgi"]
