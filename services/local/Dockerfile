FROM local/lizaalert_backend-base

EXPOSE 8000/tcp

COPY tests/ tests/
COPY lizaalert-backend .

CMD ["gunicorn", "-c", "/app/gunicorn_conf.py", "settings.wsgi"]
