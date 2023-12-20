import pytest

from lizaalert.users.models import Badge, VolunteerBadge


@pytest.fixture
def created_badge():
    """Фикстура для создания объекта Badge."""
    badge = Badge.objects.create(
        name="Test Badge",
        description="Test Description",
        badge_type=Badge.BadgeType.MANUAL,
        badge_category=Badge.BadgeCategory.ONE_TIME,
        issued_for="Test Issued For",
    )
    return badge


@pytest.fixture
def create_volunteer_badge(create_volunteer, created_badge):
    """Фикстура для создания объекта VolunteerBadge."""
    return VolunteerBadge.objects.create(
        volunteer=create_volunteer,
        badge=created_badge,
    )
