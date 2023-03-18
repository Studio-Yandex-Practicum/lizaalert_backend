import pytest
from django.db import models


class TestRole(models.TextChoices):
    MAIN_ADMIN = "main admin", "Главный Администратор"
    ADMIN = "admin", "Администратор"
    TEACHER = "teacher", "Преподаватель"
    VOLUNTEER = "volunteer", "Волонтёр"


@pytest.fixture
def role_admin():
    return TestRole.ADMIN


@pytest.fixture
def role_main_admin():
    return TestRole.MAIN_ADMIN


@pytest.fixture
def role_teacher():
    return TestRole.TEACHER


@pytest.fixture
def role_volunteer():
    return TestRole.VOLUNTEER
