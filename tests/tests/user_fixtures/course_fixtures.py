import pytest

statuses = [
    {
        "id": 1,
        "name": "Активный",
        "slug": "active"
    },
    {
        "id": 2,
        "name": "Вы записаны",
        "slug": "booked"
    },
    {
        "id": 3,
        "name": "Пройден",
        "slug": "finished"
    },
    {
        "id": 4,
        "name": "Не активный",
        "slug": "inactive"
    }
]
@pytest.fixture()
def create_statuses(token):
    from courses.models import CourseStatus
    [CourseStatus.objects.create(**status) for status in statuses]


def return_course_data():
    from courses.models import CourseStatus
    out = list(CourseStatus.objects.all().values())
    return out
