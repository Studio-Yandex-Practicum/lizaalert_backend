import pytest
from django.urls import reverse
from rest_framework import status

from tests.factories.courses import (
    ChapterFactory,
    ChapterLessonFactory,
    CourseFactory,
    CourseStatusFactory,
    CourseWith3FaqFactory,
    CourseWith3KnowledgeFactory,
    LessonFactory,
    CourseWithAll
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

    def test_anonymous(self, client):
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

    def test_lesson_completed_field(self, user_client):
        """
        Тест, что поле lesson_completed возвращает корректный результат.

        Необходимо доделать тесты/фабрики для связи Chapter и Course
        Необходимо реализовать данный тест после того как будет решена логика работы
        lesson_completed_field.
        """
        # course = CourseFactory()
        # lessons = (
        #     LessonFactory(),
        #     LessonFactory(),
        # )
        # lesson1 = LessonFactory()
        # chapter = ChapterLessonFactory(chapter_course=course)
        # chapter.lessons.set(lesson1)

        # course = CourseFactory()
        # course = ChapterLessonCourseFactory()
        # course_id = course.course.pk
        # response = user_client.get(f"{self.url}{course_id}/")
        # print(response.json())
        # data = LessonWithChapterFactory()
        
        # chapter = [ChapterFactory()]
        # course = CourseFactory()
        # course.chapters.set(chapter)
        # _ = (
        #     ChapterLessonFactory(chapter=chapter[0], lesson__duration=1),
        #     ChapterLessonFactory(chapter=chapter[0], lesson__duration=2),
        # )
        course = CourseFactory()
        chapters = [ChapterLessonFactory()]
        course.chapters.set(chapters)
        course_id = course.pk
        response1 = user_client.get(f"{self.url}{course_id}/")
        response = user_client.get(self.url)
        print(response1.json())
        print(response.json())
        assert 0 == 1

    def test_field_faq_in_course(self, user_client):
        """
        Тест, что объекты FAQ появляются в конкретном курсе.

        При этом FAQ не связанные с данным курсом не отображаются в нем.
        """
        _ = CourseWith3FaqFactory()
        _ = CourseWith3FaqFactory()
        response = user_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["results"][0]["faq"][0] == 1
        assert response.json()["results"][0]["faq"][1] == 2
        assert len(response.json()["results"][0]["faq"]) == 3

    def test_field_knowledge_in_course(self, user_client):
        """
        Тест, что объекты Knowledge появляются в конкретном курсе.

        При этом knowledge не связанные с данным курсом не отображаются в нем.
        """
        _ = CourseWith3KnowledgeFactory()
        _ = CourseWith3KnowledgeFactory()
        response = user_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["results"][0]["knowledge"][0] == 1
        assert response.json()["results"][0]["knowledge"][1] == 2
        assert len(response.json()["results"][0]["knowledge"]) == 3
