from http import HTTPStatus

import requests

from .conftest import SERVER_URL


def test_db(db_conn):
    # пример подключения к базе данных
    with db_conn.cursor() as cur:
        cur.execute("SELECT 1")
        res = cur.fetchone()
    assert res == (1,)


def test_request():
    result = requests.get(f"{SERVER_URL}/")
    assert result.status_code == HTTPStatus.BAD_REQUEST
