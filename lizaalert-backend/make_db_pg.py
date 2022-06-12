"""
Prepare db
"""

import logging
import os
import sys

import django
import psycopg2
import pydantic
from django.conf import settings
from django.core.management import call_command
from psycopg2.errors import InvalidCatalogName

USER_NAME = "admin"
USER_PASSWORD = "password"
USER_EMAIL = "mail@mail.ru"


logging.basicConfig(level=logging.INFO)


class DBConfig(pydantic.BaseSettings):
    """get postgresql connection options"""

    host: str = pydantic.Field(default="127.0.0.1", env="DB_HOST")
    db_name: str = pydantic.Field(env="DB_NAME")
    user: str = pydantic.Field(env="DB_USER")
    password: str = pydantic.Field(env="DB_PASSWORD")

    class Config:
        env_file = ".env.test"
        env_file_encoding = "utf-8"


def refresh_db():
    db_conf = DBConfig()
    try:
        conn = psycopg2.connect(host=db_conf.host, user=db_conf.user, password=db_conf.password)
    except psycopg2.Error:
        logging.critical("Can't connect postgresql")
        sys.exit(1)
    conn.autocommit = True
    with conn.cursor() as cur:
        try:
            cur.execute(f"DROP DATABASE {db_conf.db_name}")
            conn.commit()
        except InvalidCatalogName:
            logging.info(f" Can't drop database {db_conf.db_name}")
        cur.execute(f"CREATE DATABASE {db_conf.db_name}")
        logging.info("Create db %s", db_conf.db_name)
    conn.commit()
    conn.close()


def schema_migration():
    """ """
    # migrate
    call_command("migrate")
    # add superuser
    from django.contrib.auth.models import User

    User.objects.create_user(
        username=USER_NAME, email=USER_EMAIL, password=USER_PASSWORD, is_staff=True, is_active=True, is_superuser=True
    )


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")
    refresh_db()
    django.setup()
    if not settings.configured:
        logging.critical("Can't load django settings !")
    schema_migration()
    sys.exit(0)


if __name__ == "__main__":
    main()
