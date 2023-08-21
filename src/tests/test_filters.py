import pytest
from django.urls import reverse
from rest_framework import status


class TestFilters:
    url = reverse("filters-list-list")

    @pytest.mark.django_db(transaction=True)
    def test_filters_list_not_found(self, user_client):
        response = user_client.get(self.url)
        assert response.status_code != status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db(transaction=True)
    def test_filters_endpoint(self, user_client, create_data_for_statuses, create_data_for_levels):
        response = user_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

        test_data = response.json()
        assert isinstance(test_data, list)
        assert len(test_data) != 0

        for data in test_data:
            assert "slug" in data, "В ответе не содержится поле slug."
            assert "name" in data, "В ответе не содержится поле name."
            assert "options" in data, "В ответе не содержится поле options."

            assert isinstance(data["slug"], str)
            assert isinstance(data["name"], str)
            assert isinstance(data["options"], list)

            for option in data["options"]:
                assert "id" in option, "В ответе не содержится поле id."
                assert "name" in option, "В ответе не содержится поле name."

                assert isinstance(option["id"], int)
                assert isinstance(option["name"], str)

    @pytest.mark.django_db(transaction=True)
    def test_filters_endpoint_values(self, user_client, create_data_for_statuses, create_data_for_levels):
        response = user_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

        test_data = response.json()

        for data in test_data:
            if data["slug"] == "coursestatus":
                assert data["name"] == "Статус курса"

                expected_options_course_status = [
                    {"id": 1, "name": "Активный"},
                    {"id": 2, "name": "Вы записаны"},
                    {"id": 3, "name": "Пройден"},
                    {"id": 4, "name": "Не активный"},
                ]

                count_status = len(expected_options_course_status)
                assert len(data["options"]) == count_status

                for option in data["options"]:
                    assert option in expected_options_course_status

            elif data["slug"] == "level":
                assert data["name"] == "Уровень"

                expected_options_level = [
                    {"id": 1, "name": "Новичок"},
                    {"id": 2, "name": "Бывалый"},
                    {"id": 3, "name": "Профессионал"},
                ]

                count_level = len(expected_options_level)
                assert len(data["options"]) == count_level

                for option in data["options"]:
                    assert option in expected_options_level
