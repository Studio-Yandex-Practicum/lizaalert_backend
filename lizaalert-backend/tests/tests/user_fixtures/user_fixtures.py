import pytest

statuses = [
  {
    "id": 1,
    "name": "Активный",
    "slug": "active"
  },
  {
    "id": 2,
    "name": "Вы записаны",
    "slug": "booked"
  },
  {
    "id": 3,
    "name": "Пройден",
    "slug": "finished"
  },
  {
    "id": 4,
    "name": "Не активный",
    "slug": "inactive"
  }
]



@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(username='TestUser', password='1234567')


@pytest.fixture
def user_2(django_user_model):
    return django_user_model.objects.create_user(username='TestUser2', password='1234567')


@pytest.fixture
def token(user):
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@pytest.fixture
def user_client(token):
    from rest_framework.test import APIClient
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token["access"]}')
    return client

@pytest.fixture
def create_statuses(token):
    from users.models import CourseStatus
    out = [CourseStatus.objects.create(**status) for status in statuses]
    return out