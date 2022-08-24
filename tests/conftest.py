import logging
import os

import django
from django.conf import settings


pytest_plugins = [
    "tests.user_fixtures.user_fixtures",
    "tests.user_fixtures.course_fixtures",
    "tests.user_fixtures.level_fixtures",
    "tests.user_fixtures.role_fixtures",
]
