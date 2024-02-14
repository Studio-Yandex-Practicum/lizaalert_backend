import pytest
from django.urls import reverse
from rest_framework import status

from lizaalert.courses.models import Lesson
from lizaalert.homeworks.models import Homework
from tests.factories.courses import ChapterWith3Lessons, CourseWithAvailableCohortFactory, SubscriptionFactory
from tests.factories.homeworks import HomeworkFactory
from tests.factories.users import UserRoleFactory


@pytest.mark.django_db(transaction=True)
class TestHomework:
    def test_creation_of_homework(self):
        """Тест, что модель Homework создается в БД."""
        homework = HomeworkFactory()
        obj = Homework.objects.get(id=homework.id)
        assert obj == homework

    def test_create_homework(self, user, user_client):
        """Проверка создания и получения домашней работы."""
        chapter = ChapterWith3Lessons()
        lesson = Lesson.objects.filter(chapter_id=chapter.id).first()
        course = CourseWithAvailableCohortFactory()
        course.chapters.add(chapter)
        text = "Тестовая запись"
        _ = UserRoleFactory(user=user)
        _ = SubscriptionFactory(course=course, user=user)
        response = user_client.post(
            reverse("lesson-homework-detail", kwargs={"lesson_id": lesson.id}),
            data={"text": text, "status": 1},
            format="json",
        )
        response_get_homework = user_client.get(reverse("lesson-homework-detail", kwargs={"lesson_id": lesson.id}))
        assert response.status_code == status.HTTP_201_CREATED
        assert response_get_homework.status_code == status.HTTP_200_OK
        assert response_get_homework.json()["text"] == text
