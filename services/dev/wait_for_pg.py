import argparse
import asyncio
import sys

import aiopg
import async_timeout
import psycopg2

TRYS_SECONDS = 30
RETRY_SECONDS = 1


async def try_connect(host: str = "localhost", port: int = 5432, user: str = "postgres", passwd: str = "password"):
    """Async test connection."""
    print("Try Postgresql connect")
    try:
        async with async_timeout.timeout(TRYS_SECONDS):
            while True:
                try:
                    conn = await aiopg.connect(user=user, password=passwd, host=host, port=port, timeout=1)
                    await conn.close()
                    print("Postgresql ready")
                    sys.exit(0)
                except psycopg2.Error:
                    print("Next try")
                    await asyncio.sleep(RETRY_SECONDS)

    except asyncio.TimeoutError:
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("passwd", type=str, dest="passwd", help="Db password", default="password")
    parser.add_argument("-u", "--user", type=str, dest="user", help="user name", default="postgres")
    parser.add_argument("-p", "--port", type=int, dest="port", help="db port", default=5432)
    parser.add_argument("-H", "--host", type=str, dest="host", help="db_host", default="localhost")
    args = parser.parse_args()

    asyncio.run(try_connect(host=args.host, port=args.port, user=args.user, passwd=args.passwd))


if __name__ == "__main__":
    main()
