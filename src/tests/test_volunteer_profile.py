import pytest
from django.urls import reverse
from rest_framework import status

from tests.factories.courses import CourseFactory, DivisionFactory
from tests.factories.users import BadgeFactory, VolunteerBadgeFactory


@pytest.mark.django_db
class TestVolunteerProfile:

    url = reverse("profile")

    def test_get_volunteer_profile(self, user_client):
        """Проверка, что получение профиля волонтера возвращает статус HTTP 200 OK."""
        response = user_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_patch_volunteer_profile(self, user, user_client):
        """Проверка изменения профиля волонтера через PATCH-запрос."""
        user_client.force_authenticate(user=user)
        data = {
            "call_sign": "Test Sign",
            "birth_date": "2000-01-01",
        }
        response = user_client.patch(self.url, data)
        assert response.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        assert user.volunteer.call_sign == data["call_sign"]
        assert str(user.volunteer.birth_date) == data["birth_date"]

    def test_patch_volunteer_profile_invalid_data(self, user_client, user):
        """Проверка, что изменение профиля с недопустимыми данными возвращает код 400."""
        user_client.force_authenticate(user=user)
        invalid_data = {"call_sign": 1, "birth_date": "invalid_date"}
        response = user_client.patch(self.url, invalid_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestVolunteerBadgeList:

    url = reverse("badgeslist-list")

    def test_get_volunteer_badge_list(self, user_client, user):
        """Проверка соответствия выдачи по запросу ачивок пользователя."""
        badge = BadgeFactory()
        _ = VolunteerBadgeFactory(user=user, badge=badge)
        response = user_client.get(self.url)
        data_fields = ["name", "description", "image", "issued_for"]
        assert response.status_code == status.HTTP_200_OK
        for field in data_fields:
            assert response.json()[0][field] == getattr(badge, field)


@pytest.mark.django_db
class TestVolunteerProfileDivision:

    url = reverse("profile")

    def test_get_volunteer_profile_division(self, user_client, user):
        """Проверка присутствия направлений в профиле пользователя."""
        division = DivisionFactory()
        course = CourseFactory(division=division)
        params = {"division": division.id}
        response = user_client.get(self.url, params)
        assert response.status_code == status.HTTP_200_OK
        assert course.division == division
