import pytest
from django.urls import reverse
from rest_framework import status

from tests.factories.courses import (
    ChapterFactory,
    ChapterLessonFactory,
    CourseFactory,
    CourseStatusFactory,
    LessonFactory,
)
from tests.factories.users import LevelFactory
from tests.user_fixtures.course_fixtures import return_course_data
from tests.user_fixtures.level_fixtures import return_levels_data


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
    def test_coursestatus_list(self, user_client, url, test_data):
        _ = [LevelFactory() for _ in range(3)]
        _ = [CourseStatusFactory() for _ in range(3)]
        response = user_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == test_data()


@pytest.mark.django_db(transaction=True)
class TestCourse:
    url = reverse("courses-list")

    def test_not_found_courselist(self, user_client):
        _ = ChapterFactory()
        response = user_client.get(self.url)
        assert response.status_code != status.HTTP_404_NOT_FOUND

    def test_count_lessons_count_duration(self, user_client):
        chapter = ChapterFactory()
        _ = (
            ChapterLessonFactory(chapter=chapter, lesson__duration=1),
            ChapterLessonFactory(chapter=chapter, lesson__duration=2),
        )

        response = user_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["results"][0]["lessons_count"] == 2
        assert response.json()["results"][0]["course_duration"] == 3

    def test_course_status_anonymous(self, anonymous_client):
        response = anonymous_client.get(self.url)
        courses = response.json()["results"]
        course_status = [course["course_status"] == "inactive" for course in courses]
        assert response.status_code == status.HTTP_200_OK
        assert all(course_status)

    # def test_course_status_user(self, user_client):
    #     response = user_client.get(self.url)
    #     assert response.status_code == status.HTTP_200_OK
    #     assert response.json()["results"][0]["course_status"] == "active"

    def test_filter_courses_by_course_format(self, user_client):
        course = CourseFactory()
        course_format = course.course_format
        params = {"course_format": course_format}
        response = user_client.get(self.url, params)
        courses = response.json()["results"]
        assert response.status_code == status.HTTP_200_OK
        assert len(courses) != 0

    def test_test_filter_courses_by_level(self, user_client):
        course = CourseFactory()
        level = course.level.name
        params = {"level": level}
        response = user_client.get(self.url, params)
        courses = response.json()["results"]
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["results"][0]["level"] == level
        assert len(courses) != 0

    def test_field_faq_is_courses_list(self, user_client):
        course = CourseFactory()
        course_faq = course.faq
        response = user_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["results"][0]["faq"] == course_faq

    def test_field_faq_is_course(self, user_client):
        course = CourseFactory()
        course_id = course.pk
        course_faq = course.faq
        response = user_client.get(self.url, {"id": course_id})
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["results"][0]["faq"] == course_faq


@pytest.mark.django_db(transaction=True)
class TestLessonDetailView:
    # устанавливаем URL для доступа к представлению урока
    url = reverse("lesson_detail", args=[1])

    def test_lesson_detail_view(self, user_client):
        # создаем объект Lesson с помощью фабрики
        lesson = LessonFactory()

        # делаем GET запрос к уроку по его ID
        response = user_client.get(reverse("lesson_detail", args=[lesson.id]))

        # проверяем, что ответ имеет код 200 OK
        assert response.status_code == status.HTTP_200_OK
        # проверяем, что данные ответа соответствуют ожидаемым значениям
        assert response.json()["id"] == lesson.id
        assert response.json()["title"] == lesson.title
        assert response.json()["description"] == lesson.description
        assert response.json()["lesson_type"] == lesson.lesson_type
        assert eval(response.json()["tags"]) == lesson.tags
        assert response.json()["duration"] == lesson.duration
        assert response.json()["additional"] == lesson.additional
        assert response.json()["diploma"] == lesson.diploma
        assert response.json()["next_lesson"] is None
        assert response.json()["prev_lesson"] is None
