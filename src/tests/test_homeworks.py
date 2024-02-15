import pytest
from django.urls import reverse
from rest_framework import status

from lizaalert.courses.models import Lesson
from lizaalert.homeworks.models import Homework
from tests.factories.courses import CourseWith2Chapters, SubscriptionFactory
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
        course = CourseWith2Chapters()
        lessons = Lesson.objects.filter(chapter__course=course)
        for lesson in lessons:
            lesson.lesson_type = Lesson.LessonType.HOMEWORK
            lesson.save()
        text = "Тестовая запись"
        text_change = "Тестовая запись после замены"
        _ = UserRoleFactory(user=user)
        _ = SubscriptionFactory(course=course, user=user)
        draft_data = {"text": text, "status": "draft"}
        submit_data = {"text": text_change, "status": "submitted"}
        response_draft = user_client.post(
            reverse("lesson-homework-detail", kwargs={"lesson_id": lesson.id}),
            data=draft_data,
            format="json",
        )
        response_submitted = user_client.post(
            reverse("lesson-homework-detail", kwargs={"lesson_id": lesson.id}),
            data=submit_data,
            format="json",
        )
        response_get_homework = user_client.get(reverse("lesson-homework-detail", kwargs={"lesson_id": lesson.id}))
        assert response_draft.status_code == status.HTTP_201_CREATED
        assert response_draft.json()["text"] == text
        assert response_draft.json()["status"] == Homework.ProgressionStatus.DRAFT
        assert response_submitted.status_code == status.HTTP_201_CREATED
        assert response_submitted.json()["id"] == response_draft.json()["id"]
        assert response_submitted.json()["status"] == Homework.ProgressionStatus.SUBMITTED
        assert response_get_homework.status_code == status.HTTP_200_OK
        assert response_get_homework.json()["text"] == text_change == response_submitted.json()["text"]
