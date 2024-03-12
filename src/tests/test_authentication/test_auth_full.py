import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from lizaalert.authentication.views import LoginView, YandexUserData

User = get_user_model()


class TestAuthFull:
    @pytest.mark.django_db(transaction=True)
    def test_with_jwt(self, client, django_user_model):
        user_request = {"username": "lizaR", "email": "mailR@test.ru", "password": "pass"}
        response = client.post("/api/v1/auth/users/", data=user_request, content_type="application/json")
        assert response.status_code == status.HTTP_201_CREATED

        user_request = {"username": "test_user", "email": "mailT@test.ru", "password": "pass"}
        response = client.post("/api/v1/auth/users/", data=user_request, content_type="application/json")
        assert response.status_code == status.HTTP_201_CREATED

        response = client.post("/api/v1/auth/users/test/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # author but wrong user
        jwt_request = {"email": "mailR@test.ru", "password": "pass"}
        response = client.post("/api/v1/auth/jwt/create/", data=jwt_request, content_type="application/json")
        assert response.status_code == status.HTTP_200_OK
        response_obj = response.json()

        headers = {"HTTP_AUTHORIZATION": f"Bearer {response_obj['access']}"}
        response = client.post("/api/v1/auth/users/test/", **headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # auth and good user
        jwt_request = {"email": "mailT@test.ru", "password": "pass"}
        response = client.post("/api/v1/auth/jwt/create/", data=jwt_request, content_type="application/json")
        assert response.status_code == status.HTTP_200_OK
        response_obj = response.json()

        headers = {"HTTP_AUTHORIZATION": f"Bearer {response_obj['access']}"}
        response = client.post("/api/v1/auth/users/test/", **headers)
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db(transaction=True)
    def test_short_login(self, django_user_model):
        user = django_user_model.objects.create(
            username="test_user", email="mailT@test.ru", password="pass", is_active=True
        )

        client = APIClient()
        response = client.post("/api/v1/auth/users/test/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        client.force_authenticate(user=user)
        response = client.post("/api/v1/auth/users/test/")
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db(transaction=True)
    def test_yandex_get_user(self, client):
        user_data = YandexUserData(99, "TestYaUser", ["user@user.com"])
        LoginView.get_user(self, user_data)
        assert User.objects.filter(id=99, username="TestYaUser", email="user@user.com").exists
