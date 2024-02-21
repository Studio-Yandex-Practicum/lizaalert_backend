from collections import namedtuple
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from lizaalert.authentication.views import TokenExchange

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
    def test_yandex_auth(self, client):
        url = reverse("token_exchange")
        oauth_token = {"oauth_token": "fake_token"}
        with patch.object(TokenExchange, "get_yandex_user_data") as mock_user_data:
            mock_user_data.return_value = (None, status.HTTP_400_BAD_REQUEST)
            response = client.post(url, data=oauth_token)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert response.data == {"yandex_response_status": status.HTTP_400_BAD_REQUEST}
            assert len(User.objects.all()) == 0

            user_data = namedtuple("UserData", ("id", "login"))(1, "test_user")
            mock_user_data.return_value = (user_data, status.HTTP_200_OK)
            response = client.post(url, data=oauth_token)
            assert response.status_code == status.HTTP_201_CREATED
            assert bool(response.data.get("refresh", False)) + bool(response.data.get("refresh", False)) == 2
            assert len(User.objects.all()) == 1
            assert User.objects.filter(id=1, username="test_user").exists()

            response = client.post(url, data=oauth_token)
            assert response.status_code == status.HTTP_201_CREATED
            assert bool(response.data.get("refresh", False)) + bool(response.data.get("refresh", False)) == 2
            assert len(User.objects.all()) == 1

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
