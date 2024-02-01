from datetime import datetime

import pytest
from django.urls import reverse

from lizaalert.users.admin import BadgeAdminForm, VolunteerBadgeAdminForm
from lizaalert.users.models import Badge, VolunteerBadge, VolunteerCourseCompletion
from lizaalert.users.utils import (
    assign_achievements_for_completion,
    assign_achievements_for_course,
    increment_completed_courses_count,
)
from tests.factories.courses import CourseFactory, CourseWith2Chapters, SubscriptionFactory
from tests.factories.users import BadgeFactory, UserFactory, VolunteerBadgeFactory


@pytest.mark.django_db
class TestBadgeModel:
    def test_create_badge(self):
        """Тестирование создания объекта Badge с использованием фикстуры."""
        created_badge = BadgeFactory()
        assert created_badge.id

    def test_badge_validation_both_thresholds_filled(self):
        """Тестирование валидации, когда оба поля (threshold_courses и threshold_course) заполнены."""
        created_course = CourseFactory()
        form = BadgeAdminForm(
            {
                "name": "Test Badge",
                "description": "Test Description",
                "badge_type": Badge.BadgeType.MANUAL,
                "badge_category": Badge.BadgeCategory.ONE_TIME,
                "issued_for": "Test Issued For",
                "threshold_courses": 1,
                "threshold_course": created_course.id,
            }
        )
        assert form.is_valid() is False
        assert "threshold_courses" in form.errors and "threshold_course" in form.errors

    def test_badge_validation_only_threshold_courses_filled(self):
        """Тестирование валидации, когда заполнено только поле threshold_courses."""
        form = BadgeAdminForm(
            {
                "name": "Test Badge",
                "description": "Test Description",
                "badge_type": Badge.BadgeType.MANUAL,
                "badge_category": Badge.BadgeCategory.ONE_TIME,
                "issued_for": "Test Issued For",
                "threshold_courses": 1,
                "threshold_course": None,
            }
        )
        assert form.is_valid() is True

    def test_badge_validation_only_threshold_course_filled(self):
        """Тестирование валидации, когда заполнено только поле threshold_course."""
        created_course = CourseFactory()
        form = BadgeAdminForm(
            {
                "name": "Test Badge",
                "description": "Test Description",
                "badge_type": Badge.BadgeType.MANUAL,
                "badge_category": Badge.BadgeCategory.ONE_TIME,
                "issued_for": "Test Issued For",
                "threshold_courses": None,
                "threshold_course": created_course.id,
            }
        )
        assert form.is_valid() is True


@pytest.mark.django_db
class TestVolunteerBadgeModel:
    def test_create_volunteer_badge_model(self):
        """Тестирование создания объекта VolunteerBadge."""
        created_volunteer_badge = VolunteerBadgeFactory()
        assert created_volunteer_badge.id

    def test_volunteer_badge_admin_form(self):
        """Тестирование валидации формы VolunteerBadgeAdminForm."""
        created_user = UserFactory()
        created_badge = BadgeFactory()
        form = VolunteerBadgeAdminForm(
            {"volunteer": created_user.volunteer.id, "badge": created_badge.id, "created_at": datetime.now()}
        )
        assert form.is_valid() is True

    def test_unique_badge_for_volunteer(self):
        """
        Проверяет валидацию уникальности значков для волонтеров.

        Создаем объект VolunteerBadge с volunteer и badge из фабрик.
        Пытаемся создать еще один объект VolunteerBadge с теми же volunteer и badge.
        1) Убеждаемся, что форма не прошла валидацию
        2)Проверяем, что в поле __all__ появилась ошибка
        3)Проверяем, что ошибка связана с уникальностью значков для волонтера
        """
        created_volunteer_badge = VolunteerBadgeFactory()

        form_data = {
            "volunteer": created_volunteer_badge.volunteer.id,
            "badge": created_volunteer_badge.badge.id,
            "created_at": datetime.now(),
        }
        form = VolunteerBadgeAdminForm(data=form_data)
        assert form.is_valid() is False
        assert "__all__" in form.errors
        assert (
            f"Волонтер '{created_volunteer_badge.volunteer}' уже имеет значок '{created_volunteer_badge.badge}'."
            in form.errors["__all__"]
        )


@pytest.mark.django_db
class TestBadgeAssignments:
    def test_increment_completed_courses_count(self):
        """Тест функции инкремента счетчика завершенных курсов."""
        user = UserFactory()
        volunteer = user.volunteer
        _ = VolunteerCourseCompletion.objects.create(volunteer=volunteer)

        for _ in range(5):
            count_before = volunteer.course_completion.first().completed_courses_count
            increment_completed_courses_count(user)
            count_after = volunteer.course_completion.first().completed_courses_count
            assert count_after == count_before + 1

    def test_assign_achievements_for_completion(self):
        """Тест функции присвоения ачивок за завершенные курсы."""
        user = UserFactory()
        course = CourseFactory()
        BadgeFactory(threshold_courses=1)

        increment_completed_courses_count(user)
        assign_achievements_for_completion(user, course.id)

        assert VolunteerBadge.objects.filter(volunteer__user=user, course_id=course.id).exists()

    def test_assign_achievements_for_course(self):
        """Тест функции присвоения ачивок за конкретный курс."""
        user = UserFactory()
        course = CourseFactory()
        BadgeFactory(threshold_course=course)

        assign_achievements_for_course(user, course.id)

        assert VolunteerBadge.objects.filter(volunteer__user=user, course_id=course.id).exists()

    def test_course_completion_signal(self, user_client):
        """Проверяем, есть ли у пользователя соответствующие значки и увеличен ли счетчик завершенных курсов после вызова эндпоинта завершения курса."""
        user = UserFactory(username="course_completion_signal_user")
        user_client.force_authenticate(user=user)
        volunteer = user.volunteer
        course = CourseWith2Chapters()
        _ = SubscriptionFactory(user=user, course=course)

        BadgeFactory(threshold_course=course)
        BadgeFactory(threshold_courses=1)

        url = reverse("courses-complete", kwargs={"pk": course.id})
        _ = user_client.post(url)

        assert VolunteerBadge.objects.filter(volunteer__user=user, course_id=course.id).exists()
        assert volunteer.course_completion.first().completed_courses_count == 1
