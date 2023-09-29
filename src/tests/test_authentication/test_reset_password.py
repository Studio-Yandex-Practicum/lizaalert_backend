import pytest
from rest_framework import status


class TestResetPassword:
    @pytest.mark.django_db(transaction=True)
    def test_bad_request(self, client):
        user_request = {"eemail": "mail@test.ru"}

        response = client.post("/api/v1/auth/users/reset_password/", data=user_request, content_type="application/json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db(transaction=True)
    def test_unknown_email(self, client):
        user_request = {"email": "fake@test.ru"}
        response = client.post("/api/v1/auth/users/reset_password/", data=user_request, content_type="application/json")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.skip(reason="Haven't working mail server")
    @pytest.mark.django_db(transaction=True)
    def test_fail_mail_server(self, client, django_user_model):
        django_user_model.objects.create(username="lizaa", email="mail@test.ru", password="pass")
        user_request = {"email": "mail@test.ru"}
        response = client.post("/api/v1/auth/users/reset_password/", data=user_request, content_type="application/json")
        assert response.status_code == status.HTTP_424_FAILED_DEPENDENCY

    @pytest.mark.django_db(transaction=True)
    def test_send_mail(self, client, django_user_model):
        django_user_model.objects.create(username="lizaa", email="mail@test.ru", password="pass")
        user_request = {"email": "mail@test.ru"}
        response = client.post("/api/v1/auth/users/reset_password/", data=user_request, content_type="application/json")
        assert response.status_code == status.HTTP_200_OK
