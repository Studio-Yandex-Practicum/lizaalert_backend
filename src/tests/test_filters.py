import pytest
from django.urls import reverse
from rest_framework import status

from tests.factories.courses import CourseFactory, CourseStatusFactory
from tests.factories.users import LevelFactory


@pytest.mark.django_db(transaction=True)
class TestFilters:
    url = reverse("filters-list-list")

    def test_filters_list_not_found(self, user_client):
        response = user_client.get(self.url)
        assert response.status_code != status.HTTP_404_NOT_FOUND

    def test_filters_endpoint(self, user_client):
        _ = [LevelFactory() for _ in range(3)]
        _ = [CourseStatusFactory() for _ in range(4)]
        response = user_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

        test_data = response.json()
        assert isinstance(test_data, list)
        assert len(test_data) != 0

        for data in test_data:

            data_types = {"slug": str, "name": str, "options": list}

            for key, data_type in data_types.items():
                assert isinstance(data[key], data_type)
                assert key in data, f"В ответе не содержится поле {key}."

            for option in data["options"]:

                data_types = {"id": int, "name": str}

                for key, data_type in data_types.items():
                    assert isinstance(option[key], data_type)
                    assert key in option, f"В ответе не содержится поле {key}."

    def test_filters_endpoint_values(self, user_client):
        levels = [
            LevelFactory(name="Новичок"),
            LevelFactory(name="Бывалый"),
            LevelFactory(name="Профессионал"),
        ]

        statuses = [
            CourseStatusFactory(name="Активный"),
            CourseStatusFactory(name="Вы записаны"),
            CourseStatusFactory(name="Пройден"),
            CourseStatusFactory(name="Не активный"),
        ]
        response = user_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

        test_data = response.json()

        for data in test_data:
            if data["slug"] == "coursestatus":
                assert data["name"] == "Статус курса"

                expected_options_course_status = [
                    {"id": course_status.id, "name": course_status.name} for course_status in statuses
                ]

                count_status = len(expected_options_course_status)
                assert len(data["options"]) == count_status

                for option in data["options"]:
                    assert option in expected_options_course_status

            elif data["slug"] == "level":
                assert data["name"] == "Уровень"

                expected_options_level = [{"id": level.id, "name": level.name} for level in levels]

                count_level = len(expected_options_level)
                assert len(data["options"]) == count_level

                for option in data["options"]:
                    assert option in expected_options_level


@pytest.mark.django_db(transaction=True)
class TestCourseFilters:
    url = reverse("courses-list")

    def test_course_by_filter_found(self, user_client):
        course = CourseFactory(level=LevelFactory(name="Новичок"))
        course_level = course.level.name
        level = LevelFactory(name="Новичок")
        params = {"level": level.name}
        response = user_client.get(self.url, params)
        courses = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert len(courses["results"]) != 0
        assert courses["results"][0]["level"] == course_level

    def test_course_by_filter_not_found(self, user_client):
        course = CourseFactory(level=LevelFactory(name="Бывалый"))
        course_level = course.level.name
        level = LevelFactory(name="Новичок")
        params = {"level": level.name}
        response = user_client.get(self.url, params)
        courses = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert len(courses["results"]) == 0
        assert course_level not in courses["results"]
