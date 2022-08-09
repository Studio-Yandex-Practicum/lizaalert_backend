import pytest
from django.urls import reverse
from rest_framework import status

from tests.tests.user_fixtures.level_fixtures import return_levels_data


class TestLevel:
    url = reverse("level-list")

    @pytest.mark.django_db(transaction=True)
    def test_level_list_not_found(self, user_client):
        response = user_client.get(self.url)
        assert response.status_code != status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db(transaction=True)
    def test_level_list(self, user_client, create_levels):
        response = user_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == return_levels_data()
