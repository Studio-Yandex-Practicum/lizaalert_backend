"""Check is postgres ready for work."""
import logging
import sys
import time

import psycopg2
import pydantic

TRYS = 20


logging.basicConfig(level=logging.INFO)


class DBConfig(pydantic.BaseSettings):
    """Get postgresql connection options."""

    host: str = pydantic.Field(default="127.0.0.1", env="DB_HOST")
    db_name: str = pydantic.Field(env="DB_NAME")
    user: str = pydantic.Field(env="DB_USER")
    password: str = pydantic.Field(env="DB_PASSWORD")

    class Config:
        env_file = ".env.test"
        env_file_encoding = "utf-8"


def main():
    logging.info("Waiting postgresql")
    db_conf = DBConfig()
    trys = 0
    while trys <= TRYS:
        try:
            conn = psycopg2.connect(
                host=db_conf.host, user=db_conf.user, password=db_conf.password
            )
            conn.close()
            logging.info("Postgresql ready.")
            sys.exit(0)

        except psycopg2.Error:
            logging.info("Try %s crashed ...", trys)
            time.sleep(1)
            trys += 1
    logging.critical("Can't connect postgresql")
    sys.exit(1)


if __name__ == "__main__":
    main()
