import logging
import sys

import psycopg2
import pydantic
import pytest

SERVER_URL = "http://localhost:8000/admin"


class DBConfig(pydantic.BaseSettings):
    """get postgresql connection options"""

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
