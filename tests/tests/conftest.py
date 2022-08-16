import logging
import os
import sys

import django
import psycopg2
import pydantic
import pytest
from django.conf import settings


class DBConfig(pydantic.BaseSettings):
    """Get postgresql connection options."""

    host: str = pydantic.Field(default="127.0.0.1", env="DB_HOST")
    db_name: str = pydantic.Field(env="DB_NAME")
    user: str = pydantic.Field(env="DB_USER")
    password: str = pydantic.Field(env="DB_PASSWORD")

    class Config:
        env_file = ".env.test"
        env_file_encoding = "utf-8"


@pytest.fixture(scope="function")
def db_conn():
    db_conf = DBConfig()
    try:
        conn = psycopg2.connect(host=db_conf.host, user=db_conf.user, password=db_conf.password)
    except psycopg2.Error:
        logging.critical("Can't connect postgresql")
        sys.exit(1)
    yield conn

    conn.close()


def django_init():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")
    django.setup()
    if not settings.configured:
        logging.critical("Can't load django settings !")


django_init()
