import pytest
from django.urls import reverse
from rest_framework import status

from tests.tests.user_fixtures.course_fixtures import return_course_data
from tests.tests.user_fixtures.level_fixtures import return_levels_data


@pytest.mark.django_db(transaction=True)
class TestCourseStatusAndLevel:
    urls = [
        (reverse("courses_statuses-list"), return_course_data),
        (reverse("level-list"), return_levels_data),
    ]

    @pytest.mark.parametrize("url, test_data", urls)
    def test_not_found(self, user_client, url, test_data):
        response = user_client.get(url)
        assert response.status_code != status.HTTP_404_NOT_FOUND

    def test_anonimous(self, client):
        response = client.get(self.urls[0][0])
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize("url, test_data", urls)
    def test_coursestatus_list(self, user_client, url, test_data, create_levels, create_statuses):
        response = user_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == test_data()


@pytest.mark.django_db(transaction=True)
class TestCourse:
    url = reverse("courses-list")

    def test_not_found_courselist(self, user_client, create_chapter):
        response = user_client.get(self.url)
        assert response.status_code != status.HTTP_404_NOT_FOUND

    def test_count_lessons_count_duration(self, user_client, create_chapter):
        response = user_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["results"][0]["lessons_count"] == 2
        assert response.json()["results"][0]["course_duration"] == 3

    def test_course_status_anonymous(self, anonymous_client, create_chapter, create_volunteer_course):
        response = anonymous_client.get(self.url)
        courses = response.json()["results"]
        course_status = [course["course_status"] == "inactive" for course in courses]
        assert response.status_code == status.HTTP_200_OK
        assert all(course_status)

    def test_course_status_user(self, user_client, create_chapter, create_volunteer_course):
        response = user_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["results"][0]["course_status"] == "active"
