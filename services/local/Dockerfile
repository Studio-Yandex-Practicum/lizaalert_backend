FROM local/lizaalert_backend-base

EXPOSE 8000/tcp

COPY tests/ tests/
COPY lizaalert-backend .

# устанавливаем сертификат для подключения к БД
RUN mkdir ~/.postgresql
ADD services/local/postgresql.crt /root/.postgresql/root.crt

CMD ["gunicorn", "-c", "/app/gunicorn_conf.py", "settings.wsgi"]
