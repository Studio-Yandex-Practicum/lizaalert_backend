import pytest
from rest_framework import status


class TestCreateUser:
    @pytest.mark.django_db(transaction=True)
    def test_bad_request(self, client, django_user_model):
        user_request = {"username": "lizaa", "email": "mail@test.ru"}
        response = client.post("/api/v1/auth/users/", data=user_request, content_type="application/json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # user exists
        django_user_model.objects.create(username="lizaa", email="mail@test.ru", password="pass")
        # with same name
        user_request = {"username": "lizaa", "email": "maila@test.ru", "password": "pass"}
        response = client.post("/api/v1/auth/users/", data=user_request, content_type="application/json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # with same email
        user_request = {"username": "lizar", "email": "mail@test.ru", "password": "pass"}
        response = client.post("/api/v1/auth/users/", data=user_request, content_type="application/json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db(transaction=True)
    def test_create_user(self, client, django_user_model):
        user_request = {"username": "lizaa", "email": "mail@test.ru", "password": "pass"}
        response = client.post("/api/v1/auth/users/", data=user_request, content_type="application/json")
        assert response.status_code == status.HTTP_201_CREATED

        response_obj = response.json()
        assert "id" in response_obj

        new_user = django_user_model.objects.get(id=response_obj["id"])
        assert new_user.username == "lizaa"
        assert new_user.email == "mail@test.ru"
