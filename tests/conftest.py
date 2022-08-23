import os

import logging

import django
from django.conf import settings


def django_init():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")
    django.setup()
    if not settings.configured:
        logging.critical("Can't load django settings !")

django_init()

pytest_plugins = [
    "tests.user_fixtures.user_fixtures",
    "tests.user_fixtures.course_fixtures",
    "tests.user_fixtures.level_fixtures",
    "tests.user_fixtures.role_fixtures",
]
