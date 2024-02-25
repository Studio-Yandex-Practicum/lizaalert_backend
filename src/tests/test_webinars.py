import datetime

import pytest
from django.urls import reverse

from lizaalert.courses.models import Lesson
from tests.factories.courses import CohortAlwaysAvailableFactory, LessonFactory, SubscriptionFactory
from tests.factories.webinars import WebinarFactory


@pytest.mark.django_db(transaction=True)
class TestWebinar:
    def test_webinar(self, user_client, user):
        """
        Тест корректной работы вебинаров.

        Создаем урок с 3 вебинарами. 1 вебинар для одной когорты, 2 вебинара для второй.
        При этом вебинар первой когорты начинается раньше всех.
        Проверяем, что студент когорты видит один свой ближайший вебинар.
        """
        lesson = LessonFactory(lesson_type=Lesson.LessonType.WEBINAR)
        cohort_with_2_web = CohortAlwaysAvailableFactory(course=lesson.chapter.course)
        cohort_with_1_web = CohortAlwaysAvailableFactory(course=lesson.chapter.course)
        webinar_to_show = WebinarFactory(
            lesson=lesson,
            webinar_date=datetime.date.today() + datetime.timedelta(days=5),
            cohort=cohort_with_2_web,
        )

        # Второй вебинар для второй когорты, начинается позже.
        _ = WebinarFactory(
            lesson=lesson,
            webinar_date=datetime.date.today() + datetime.timedelta(days=6),
            cohort=cohort_with_2_web,
        )

        # Вебинар для первой когорты, начинается раньше всех.
        _ = WebinarFactory(
            lesson=lesson,
            webinar_date=datetime.date.today() + datetime.timedelta(days=1),
            cohort=cohort_with_1_web,
        )

        _ = SubscriptionFactory(user=user, course=lesson.chapter.course, cohort=cohort_with_2_web)

        url = reverse("lesson-webinar-detail", kwargs={"lesson_id": lesson.id})
        response = user_client.get(url)
        assert response.status_code == 200
        assert response.json()["id"] == webinar_to_show.id
