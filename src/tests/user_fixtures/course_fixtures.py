import datetime

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


@pytest.fixture()
def create_course(user, create_level):
    from lizaalert.courses.models import Course

    start_date = datetime.date.today() + datetime.timedelta(days=3)
    course1 = Course.objects.create(
        title="Course1",
        course_format="Курс",
        start_date=start_date,
        short_description="Курс",
        level=create_level[0],
        user_created=user,
        full_description="Курс",
    )
    course2 = Course.objects.create(
        title="Course2",
        course_format="Курс",
        start_date=start_date,
        short_description="Курс",
        level=create_level[1],
        user_created=user,
        full_description="Курс",
    )
    return course1, course2


@pytest.fixture()
def create_chapter(user, create_lesson, create_course):
    from lizaalert.courses.models import Chapter, ChapterLesson

    chapter = Chapter.objects.create(title="Глава", user_created=user, user_modifier=user, course=create_course[0])
    ChapterLesson.objects.create(chapter=chapter, lesson=create_lesson[0], order_number=1)
    ChapterLesson.objects.create(chapter=chapter, lesson=create_lesson[1], order_number=2)
    return chapter


@pytest.fixture()
def create_faq(user, create_course):
    from lizaalert.courses.models import FAQ, CourseFaq

    faq1 = FAQ.objects.create(question="Вопрос", answer="Ответ", author=user)
    faq2 = FAQ.objects.create(question="Вопрос2", answer="Ответ2", author=user)
    CourseFaq.objects.create(faq=faq1, course=create_course[0])
    CourseFaq.objects.create(faq=faq2, course=create_course[0])
    return faq1


@pytest.fixture()
def create_knowledge(user, create_course):
    from lizaalert.courses.models import CourseKnowledge, Knowledge

    knowledge1 = Knowledge.objects.create(title="Знание", description="Описание", author=user)
    knowledge2 = Knowledge.objects.create(title="Знание2", description="Описание2", author=user)
    CourseKnowledge.objects.create(knowledge=knowledge1, course=create_course[0])
    CourseKnowledge.objects.create(knowledge=knowledge2, course=create_course[0])
    return knowledge1
