import datetime

import pytest

from lizaalert.users.models import UserRole


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(username="TestUser", password="1234567", email="test@test.com")


@pytest.fixture
def user_2(django_user_model):
    return django_user_model.objects.create_user(username="TestUser2", password="1234567", email="test2@test.com")


@pytest.fixture
def token(user):
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


@pytest.fixture
def user_client(token):
    from rest_framework.test import APIClient

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token["access"]}')
    return client


@pytest.fixture
def user_admin_teacher_role(user, role_admin, role_teacher):
    UserRole.objects.create(user=user, role=role_admin)
    UserRole.objects.create(user=user, role=role_teacher)


@pytest.fixture
def anonymous_client():
    from rest_framework.test import APIClient

    client = APIClient()
    return client


@pytest.fixture()
def create_location():
    from lizaalert.users.models import Location

    location = Location.objects.create(region="Москва")
    return location


@pytest.fixture()
def create_volunteer(user, create_location):
    from lizaalert.users.models import Volunteer

    volunteer, created = Volunteer.objects.get_or_create(
        user=user,
        defaults={
            "phone_number": "+375291112233",
            "birth_date": datetime.date.today(),
            "location": create_location,
        },
    )
    return volunteer


@pytest.fixture()
def create_level():
    from lizaalert.users.models import Level

    levels = [Level.objects.create(name=choice[1], description=choice[0]) for choice in Level.LevelName.choices]
    yield levels
    # Level.objects.filter(id__in=[level.id for level in levels]).delete()


@pytest.fixture()
def create_user_role(user):
    from lizaalert.users.models import UserRole

    volunteer, created = UserRole.objects.get_or_create(user=user, role=UserRole.Role.VOLUNTEER)
    return volunteer
