import pytest

from tests.user_fixtures.course_fixtures import statuses
from tests.user_fixtures.level_fixtures import levels


@pytest.fixture()
def create_data_for_levels():
    from lizaalert.users.models import Level

    [
        Level.objects.create(id=level_data["id"], name=level_data["name"], description="Description")
        for level_data in levels
    ]


@pytest.fixture()
def create_data_for_statuses():
    from lizaalert.courses.models import CourseStatus

    [
        CourseStatus.objects.create(
            id=course_status_data["id"], name=course_status_data["name"], slug=course_status_data["slug"]
        )
        for course_status_data in statuses
    ]
