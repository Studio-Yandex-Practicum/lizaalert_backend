import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from lizaalert.courses.models import Lesson
from lizaalert.homeworks.models import Homework, ProgressionStatus
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

    def test_create_homework(self, user, user_client: APIClient):
        """Проверка создания и получения домашней работы."""
        course = CourseWith2Chapters()
        lessons = Lesson.objects.filter(chapter__course=course)
        for lesson in lessons:
            lesson.lesson_type = Lesson.LessonType.HOMEWORK
            lesson.save()
        _ = UserRoleFactory(user=user)
        _ = SubscriptionFactory(course=course, user=user)

        def assert_status_homework(
            user, user_client, status_code, text="", request_method="get", result=ProgressionStatus.DRAFT
        ):

            data = {"text": text, "status": result}
            if request_method == "post":
                response = user_client.post(
                    reverse("lesson-homework-detail", kwargs={"lesson_id": lesson.id}),
                    data=data,
                    format="json",
                )
                assert response.status_code == status_code
            else:
                response = user_client.get(reverse("lesson-homework-detail", kwargs={"lesson_id": lesson.id}))
            assert response.data["text"] == text
            assert response.data["status"] == result
            assert response.status_code == status_code

        # 1. Проверяем, что при get-запросе не существующей домашней работе возвращается код 204 и пустое поле текст.
        assert_status_homework(user, user_client, status.HTTP_204_NO_CONTENT)
        # 2. Проверяем, что создается объект домашней работы возвращается код 201 и поле текст соответствует
        # переданному тексту.
        assert_status_homework(user, user_client, status.HTTP_201_CREATED, "Текст", "post")
        # 3. Проверяем, что при get-запросе существующей домашней работе возвращается код 200 и поле текст==текст в б.д.
        assert_status_homework(user, user_client, status.HTTP_200_OK, "Текст")
        # 4. Проверяем, что при post-запросе изменяется объект домашней работе возвращается код 201.
        assert_status_homework(
            user, user_client, status.HTTP_201_CREATED, "Текст1", "post", ProgressionStatus.SUBMITTED
        )
        # 5. Проверяем, что при get-запросе получаем измененный объект домашней работе возвращается код 200 и
        # новый статус.
        assert_status_homework(user, user_client, status.HTTP_200_OK, "Текст1", result=ProgressionStatus.SUBMITTED)
