import pytest

from lizaalert.users.admin import BadgeAdminForm, VolunteerBadgeAdminForm
from lizaalert.users.models import Badge, VolunteerBadge


@pytest.mark.django_db
class TestBadgeModel:
    def test_create_badge(self, created_badge):
        """Тестирование создания объекта Badge с использованием фикстуры."""
        created_badge = created_badge
        assert created_badge.id

    def test_badge_validation_both_thresholds_filled(self, create_course):
        """Тестирование валидации, когда оба поля (threshold_courses и threshold_course) заполнены."""
        form = BadgeAdminForm(
            {
                "name": "Test Badge",
                "description": "Test Description",
                "badge_type": Badge.BadgeType.MANUAL,
                "badge_category": Badge.BadgeCategory.ONE_TIME,
                "issued_for": "Test Issued For",
                "threshold_courses": 1,
                "threshold_course": create_course[0].id,
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

    def test_badge_validation_only_threshold_course_filled(self, create_course):
        """Тестирование валидации, когда заполнено только поле threshold_course."""
        form = BadgeAdminForm(
            {
                "name": "Test Badge",
                "description": "Test Description",
                "badge_type": Badge.BadgeType.MANUAL,
                "badge_category": Badge.BadgeCategory.ONE_TIME,
                "issued_for": "Test Issued For",
                "threshold_courses": None,
                "threshold_course": create_course[0].id,
            }
        )
        assert form.is_valid() is True


@pytest.mark.django_db
class TestVolunteerBadgeModel:
    def test_create_volunteer_badge_model(self, create_volunteer, created_badge):
        """Тестирование создания объекта VolunteerBadge."""
        volunteer = create_volunteer
        volunteer_badge = VolunteerBadge.objects.create(volunteer=volunteer, badge=created_badge)
        assert volunteer_badge.id

    def test_volunteer_badge_admin_form(self, create_volunteer, created_badge):
        """Тестирование валидации формы VolunteerBadgeAdminForm."""
        form = VolunteerBadgeAdminForm(
            {
                "volunteer": create_volunteer.id,
                "badge": created_badge.id,
                "created_at": "2023-01-01T12:00:00",
                "is_issued": True,
            }
        )
        assert form.is_valid() is True

    def test_unique_badge_for_volunteer(self, create_volunteer, created_badge):
        """
        Проверяет валидацию уникальности значков для волонтеров.

        Создаем объект VolunteerBadge с volunteer и badge из фикстур.
        Пытаемся создать еще один объект VolunteerBadge с теми же volunteer и badge.
        1) Убеждаемся, что форма не прошла валидацию
        2)Проверяем, что в поле __all__ появилась ошибка
        3)Проверяем, что ошибка связана с уникальностью значков для волонтера
        """
        volunteer = create_volunteer
        VolunteerBadge.objects.create(volunteer=volunteer, badge=created_badge)

        form_data = {
            "volunteer": volunteer.id,
            "badge": created_badge.id,
            "created_at": "2023-01-01T12:00:00",
            "is_issued": True,
        }
        form = VolunteerBadgeAdminForm(data=form_data)
        assert form.is_valid() is False
        assert "__all__" in form.errors
        assert "Этот значок уже был выдан данному волонтеру." in form.errors["__all__"]
