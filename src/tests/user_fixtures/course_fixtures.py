import pytest

statuses = [
    {"id": 1, "name": "Активный", "slug": "active"},
    {"id": 2, "name": "Вы записаны", "slug": "booked"},
    {"id": 3, "name": "Пройден", "slug": "finished"},
    {"id": 4, "name": "Не активный", "slug": "inactive"},
]


@pytest.fixture()
def create_statuses(token):
    from lizaalert.courses.models import CourseStatus

    course_statuses = [CourseStatus.objects.create(**status) for status in statuses]
    return course_statuses


def return_course_data():
    from lizaalert.courses.models import CourseStatus

    out = list(CourseStatus.objects.all().values())
    return out


@pytest.fixture()
def create_lesson(user):
    from lizaalert.courses.models import Lesson

    lessons = [
        Lesson.objects.create(
            title=f"Урок{i}",
            lesson_type=Lesson.LessonType.choices[0][0],
            duration=i,
            user_created=user,
            user_modifier=user,
            lesson_status=Lesson.LessonStatus.choices[1][0],
        )
        for i in range(1, 3)
    ]

    return lessons
