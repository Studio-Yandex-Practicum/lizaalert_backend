import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestVolunteerProfile:

    url = reverse("profile")

    def test_get_volunteer_profile(self, user_client):
        response = user_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_patch_volunteer_profile(self, user, user_client):
        user_client.force_authenticate(user=user)
        data = {
            "call_sign": "Test Sign",
            "birth_date": "2000-01-01",
        }
        response = user_client.patch(self.url, data)
        assert response.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        assert user.volunteer.call_sign == "Test Sign"
        assert str(user.volunteer.birth_date) == "2000-01-01"

    def test_patch_volunteer_profile_invalid_data(self, user_client, user):
        user_client.force_authenticate(user=user)
        invalid_data = {"call_sign": 1, "birth_date": "invalid_date"}
        response = user_client.patch(self.url, invalid_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
class TestVolunteerBadgeList:

    url = reverse("badgeslist")

    def test_get_volunteer_badge_list(self, user_client):
        response = user_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
