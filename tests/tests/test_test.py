
# проверяем что можем получить доступ к модулям
from users.models import Level


def test_db(db_conn):
    # пример подключения к базе данных
    with db_conn.cursor() as cur:
        cur.execute("SELECT 1")
        res = cur.fetchone()
    assert res == (1,)
