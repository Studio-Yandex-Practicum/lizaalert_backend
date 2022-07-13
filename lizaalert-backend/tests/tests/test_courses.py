import pytest
from django.urls import reverse
from rest_framework import status


class TestCourseStatus:
    url = reverse("courses_statuses-list")

    @pytest.mark.django_db(transaction=True)
    def test_coursestatus_list_not_found(self, user_client):
        response = user_client.get(self.url)
        assert response.status_code != status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db(transaction=True)
    def test_coursestatus_list_anonimous(self, client):
        response = client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db(transaction=True)
    def test_coursestatus_list(self, user_client, create_statuses):
        response = user_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == create_statuses
