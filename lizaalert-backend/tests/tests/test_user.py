import pytest
from django.urls import reverse
from rest_framework import status

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


class TestCourseStatus:
    url = reverse('users-list')

    def test_coursestatus_list_not_found(self, user_client):

        response = user_client.get(self.url)
        assert response.status_code != status.HTTP_404_NOT_FOUND

    def test_coursestatus_list_anonimous(self, client):
        response = client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_coursestatus_list(self, user_client, create_statuses):
        response = user_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == statuses
