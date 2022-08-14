import os

if os.path.dirname(os.path.dirname(os.path.abspath(__file__))) == "/app":
    import logging
    import sys

    import django
    import psycopg2
    import pydantic
    import pytest
    from django.conf import settings

    def django_init():
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")
        django.setup()
        if not settings.configured:
            logging.critical("Can't load django settings !")

    pytest_plugins = [
        "tests.user_fixtures.user_fixtures",
        "tests.user_fixtures.course_fixtures",
        "tests.user_fixtures.level_fixtures",
        "tests.user_fixtures.role_fixtures",
    ]

    django_init()
    
else:

    pytest_plugins = [
        "tests.tests.user_fixtures.user_fixtures",
        "tests.tests.user_fixtures.course_fixtures",
        "tests.tests.user_fixtures.level_fixtures",
        "tests.tests.user_fixtures.role_fixtures",
    ]

