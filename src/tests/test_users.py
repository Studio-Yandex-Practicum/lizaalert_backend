import pytest
from django.urls import reverse
from rest_framework import status


class TestLevel:
    url = reverse("level-list")

    @pytest.mark.django_db(transaction=True)
    def test_level_list_not_found(self, user_client):
        response = user_client.get(self.url)
        assert response.status_code != status.HTTP_404_NOT_FOUND
