import pytest
from django.urls import reverse
from rest_framework import status

from lizaalert.courses.mixins import order_number_mixin
from lizaalert.courses.models import Chapter, Course, Lesson, LessonProgressStatus
from lizaalert.settings.base import CHAPTER_STEP, LESSON_STEP
from tests.factories.courses import (
    ChapterFactory,
    ChapterWith3Lessons,
    CourseFactory,
    CourseFaqFactory,
    CourseKnowledgeFactory,
    CourseWith2Chapters,
    CourseWith3FaqFactory,
    CourseWith3KnowledgeFactory,
    LessonFactory,
    SubscriptionFactory,
)
from tests.factories.users import LevelFactory


@pytest.mark.django_db(transaction=True)
class TestCourse:
    url = reverse("courses-list")

    def test_not_found_courselist(self, user_client):
        _ = ChapterFactory()
        response = user_client.get(self.url)
        assert response.status_code != status.HTTP_404_NOT_FOUND

    def test_lessons_appear_in_chapters(self, user_client):
        """
        Tests Course -> Chapter -> Lesson relation.

        Creates Course and adds to it Chapter with 3 Lessons
        Creates additional Lesson instance, to check it doesn't
        interfere with our Course.
        Asserts created course with correct chapter id,
        number of lessons, correct order nubmer.
        Asserts "lessons_count" field returns correct value.
        Asserts "course_duration" field returns correct value.
        """
        chapter = ChapterWith3Lessons()
        _ = LessonFactory()
        course = CourseFactory()
        course.chapters.add(chapter)
        response = user_client.get(reverse("courses-detail", kwargs={"pk": course.id}))
        number_of_lessons = len(response.json()["chapters"][0]["lessons"])
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["chapters"][0]["id"] == chapter.id
        assert number_of_lessons == 3
        assert response.json()["chapters"][0]["lessons"][2]["order_number"] == number_of_lessons * LESSON_STEP

    def test_course_annotation(self, user_client):
        """
        Tests course annotation functions.

        Creates Course and adds to it Chapter with 3 Lessons
        Creates additional Lesson instance, to check it doesn't
        interfere with our Course.
        Asserts correct lessons_count.
        Asserts correct total course duration.
        """
        chapter = ChapterWith3Lessons()
        lessons = Lesson.objects.filter(chapter_id=chapter.id)
        course_duration = sum([lesson.duration for lesson in lessons])
        _ = LessonFactory()
        course = CourseFactory()
        course.chapters.add(chapter)
        response = user_client.get(reverse("courses-detail", kwargs={"pk": course.id}))
        assert response.json()["lessons_count"] == 3
        assert response.json()["course_duration"] == course_duration

    def test_course_status_anonymous(self, anonymous_client):
        response = anonymous_client.get(self.url)
        courses = response.json()["results"]
        course_status = [course["course_status"] == "inactive" for course in courses]
        assert response.status_code == status.HTTP_200_OK
        assert all(course_status)

    def test_filter_courses_by_course_format(self, user_client):
        course = CourseFactory()
        course_format = course.course_format
        params = {"course_format": course_format}
        response = user_client.get(self.url, params)
        courses = response.json()["results"]
        assert response.status_code == status.HTTP_200_OK
        assert len(courses) != 0

    def test_test_filter_courses_by_level(self, user_client):
        """
        Тест на работу фильтров.

        Проверка фильтрации по level id.
        Создается 2 курса с разными уровнями.
        1) проверяем что при фильтрации по id уровня novice остается один курс
        2) проверяем что при фильтрации по id уровня proffesional остается один курс
        3) проверям, что при фильтрации одновременно по 2м id показывается два курса
        4) проверяем что без фильтрации показывается 2 курса.
        """
        novice = LevelFactory(name="novice")
        prof = LevelFactory(name="professional")
        course_1 = CourseFactory(level=novice)
        course_2 = CourseFactory(level=prof)
        _ = CourseFactory()
        level_1 = course_1.level
        level_2 = course_2.level
        params = {"level": level_1.id}
        params_2 = {"level": level_2.id}
        params_3 = {"level": f"{level_1.id},{level_2.id}"}
        response = user_client.get(self.url, params)
        response_2 = user_client.get(self.url, params_2)
        response_3 = user_client.get(self.url, params_3)
        response_full = user_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["results"][0]["level"] == level_1.name
        assert response_2.json()["results"][0]["level"] == level_2.name
        assert len(response.json()["results"]) == 1
        assert len(response_2.json()["results"]) == 1
        assert len(response_3.json()["results"]) == 2
        assert len(response_full.json()["results"]) == 3

    def test_field_faq_in_course(self, user_client):
        """
        Тест, что объекты FAQ появляются в конкретном курсе.

        При этом FAQ не связанные с данным курсом не отображаются в нем.
        """
        course = CourseFaqFactory()
        _ = CourseWith3FaqFactory()
        faq = course.faq
        response = user_client.get(self.url)
        results = response.json()["results"][0]
        assert response.status_code == status.HTTP_200_OK
        assert results["faq"][0]["question"] == faq.question
        assert results["faq"][0]["answer"] == faq.answer

    def test_field_knowledge_in_course(self, user_client):
        """
        Тест, что объекты Knowledge появляются в конкретном курсе.

        При этом knowledge не связанные с данным курсом не отображаются в нем.
        """
        course = CourseKnowledgeFactory()
        _ = CourseWith3KnowledgeFactory()
        knowledge = course.knowledge
        response = user_client.get(self.url)
        results = response.json()["results"][0]
        assert response.status_code == status.HTTP_200_OK
        assert results["knowledge"][0]["title"] == knowledge.title
        assert results["knowledge"][0]["description"] == knowledge.description

    def test_user_subscription_to_course(self, user_client, user, user_2):
        """Тест, что пользователь может подписаться на курс."""
        subscription_1 = SubscriptionFactory(user=user)
        subscription_2 = SubscriptionFactory(user=user_2)
        course_id_1 = subscription_1.course.id
        course_id_2 = subscription_2.course.id
        url_1 = reverse("courses-detail", kwargs={"pk": course_id_1})
        url_2 = reverse("courses-detail", kwargs={"pk": course_id_2})
        response_1 = user_client.get(url_1)
        response_2 = user_client.get(url_2)
        assert response_1.status_code == status.HTTP_200_OK
        assert response_1.json()["user_status"] == "True"
        assert response_2.json()["user_status"] == "False"

    def test_user_unsubscription_from_course(self, user_client, user):
        """Тест, что пользователь может отписаться от курса."""
        subscription = SubscriptionFactory(user=user)
        course_id = subscription.course.id
        url = reverse("courses-detail", kwargs={"pk": course_id})
        response = user_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["user_status"] == "True"

        unsubscribe_url = reverse("courses-unroll", kwargs={"pk": course_id})
        response = user_client.post(unsubscribe_url)
        response_1 = user_client.get(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response_1.json()["user_status"] == "False"

    def test_another_user_unable_to_unsubscribe_from_course(self, user_client, user_2):
        """Тест, что иной пользователь не может отписаться не от своего курса."""
        subscription = SubscriptionFactory(user=user_2)
        course_id = subscription.course.id
        unsubscribe_url = reverse("courses-unroll", kwargs={"pk": course_id})
        response = user_client.post(unsubscribe_url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_lessons_appear_on_endpoint(self, user_client):
        """Тест, что уроки и аннотация курса корректно отображаются по эндпоинту."""
        _ = ChapterWith3Lessons()
        lesson = LessonFactory()
        url = reverse("lessons-detail", kwargs={"pk": lesson.id})
        response = user_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == lesson.id
        assert response.json()["course_id"] == lesson.chapter.course_id

    def test_lessons_pagination_works(self, user_client):
        """
        Тест, что работает переключение между уроками.

        Создается курс с 2 Главами по 4 урока в каждой.
        Проверяется навигация по всем 8 урокам, при этой первый и последний урок
        должны выдавать None при отсутствии крайних уроков.
        """
        course = CourseWith2Chapters()
        lesson = Lesson.objects.filter(chapter__course=course).first()
        lessons = lesson.ordered
        lesson_id = None
        chapter_id = None
        for lesson in lessons:
            url = reverse("lessons-detail", kwargs={"pk": lesson.id})
            response = user_client.get(url)
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["prev_lesson"]["lesson_id"] == lesson_id
            assert response.json()["prev_lesson"]["chapter_id"] == chapter_id
            lesson_id = response.json()["id"]
            chapter_id = response.json()["chapter_id"]

        lesson = Lesson.objects.filter(chapter__course=course).first()
        lessons = lesson.ordered.order_by("-ordering")
        lesson_id = None
        chapter_id = None
        for lesson in lessons:
            url = reverse("lessons-detail", kwargs={"pk": lesson.id})
            response = user_client.get(url)
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["next_lesson"]["lesson_id"] == lesson_id
            assert response.json()["next_lesson"]["chapter_id"] == chapter_id
            lesson_id = response.json()["id"]
            chapter_id = response.json()["chapter_id"]

    def test_breadcrumbs(self, user_client):
        """Тест, что breadcrumbs отображаются корректно."""
        lesson = LessonFactory()
        url = reverse("lessons-detail", kwargs={"pk": lesson.id})
        response = user_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["breadcrumbs"]["course"]["id"] == lesson.chapter.course.id
        assert response.json()["breadcrumbs"]["course"]["title"] == lesson.chapter.course.title
        assert response.json()["breadcrumbs"]["chapter"]["id"] == lesson.chapter.id
        assert response.json()["breadcrumbs"]["chapter"]["title"] == lesson.chapter.title

    def test_lesson_completion(self, user_client):
        """
        Тест, что работает завершение урока.

        Проверяется статус прохождения урока, убеждаемся, что урок не пройден.
        После запроса POST на /complete/ проверяем статус пройденности урока.
        """
        lesson = LessonFactory()
        url = reverse("lessons-detail", kwargs={"pk": lesson.id})
        response = user_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["user_lesson_progress"] != 2
        complete_url = reverse("lessons-complete", kwargs={"pk": lesson.id})
        user_client.post(complete_url)
        response = user_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["user_lesson_progress"] == 2

    def test_final_lesson_completion_triggers_chapter_and_course_completion(self, user_client):
        """
        Тест, что завершение последнего урока в главе завершает главу.

        Если это последняя глава в курсе, то также завершается курс.
        1) Проверяем, что курс и главы не пройдены
        2) Проверяем, что после прохождения одного урока, первая глава не пройдена
        3) Проверяем, что после прохождения всех уроков, первая глава пройдена. а курс не пройден
        4) Проверяем, что после прохождения первого и последнего урока второй главы (минуя второй урок)
         вторая глава будет не пройдена
        5) Проверяем, что после прохождения всех уроков второй главы, вторая глава и курс пройдены.
        """
        chapter_1 = ChapterFactory(order_number=1)
        c1_lesson_1 = LessonFactory(chapter=chapter_1, order_number=1)
        c1_lesson_2 = LessonFactory(chapter=chapter_1, order_number=2)
        c1_lesson_3 = LessonFactory(chapter=chapter_1, order_number=3)
        lesson_bulk_1 = [c1_lesson_1, c1_lesson_2, c1_lesson_3]
        chapter_2 = ChapterFactory(order_number=2)
        c2_lesson_1 = LessonFactory(chapter=chapter_2, order_number=1)
        c2_lesson_2 = LessonFactory(chapter=chapter_2, order_number=2)
        c2_lesson_3 = LessonFactory(chapter=chapter_2, order_number=3)
        lesson_bulk_2 = [c2_lesson_1, c2_lesson_2, c2_lesson_3]
        course = CourseFactory()
        course.chapters.add(chapter_1)
        course.chapters.add(chapter_2)

        # Проверяем, что курс и главы не пройдены
        url_course = reverse("courses-detail", kwargs={"pk": course.id})
        response_course = user_client.get(url_course)
        assert response_course.status_code == status.HTTP_200_OK
        assert response_course.json()["user_course_progress"] != 2
        assert response_course.json()["chapters"][0]["user_chapter_progress"] != 2

        # # Проверяем, что после прохождения одного урока, первая глава не пройдена
        user_client.post(reverse("lessons-complete", kwargs={"pk": c1_lesson_1.id}))
        response_course = user_client.get(url_course)
        assert response_course.json()["chapters"][0]["user_chapter_progress"] != 2

        # Проверяем, что после прохождения всех уроков, первая глава пройдена. а курс не пройден
        for lesson in lesson_bulk_1:
            user_client.post(reverse("lessons-complete", kwargs={"pk": lesson.id}))
        response_course = user_client.get(url_course)
        assert response_course.json()["user_course_progress"] != 2
        assert response_course.json()["chapters"][0]["user_chapter_progress"] == 2

        # Проверяем, что после прохождения первого и последнего урока второй главы (минуя второй урок)
        # вторая глава будет не пройдена
        user_client.post(reverse("lessons-complete", kwargs={"pk": c2_lesson_1.id}))
        user_client.post(reverse("lessons-complete", kwargs={"pk": c2_lesson_3.id}))
        response_course = user_client.get(url_course)
        assert response_course.json()["user_course_progress"] != 2
        assert response_course.json()["chapters"][1]["user_chapter_progress"] != 2

        # Проверяем, что после прохождения всех уроков второй главы, вторая глава и курс пройдены
        for lesson in lesson_bulk_2:
            user_client.post(reverse("lessons-complete", kwargs={"pk": lesson.id}))
        response_course = user_client.get(url_course)
        assert response_course.status_code == status.HTTP_200_OK
        assert response_course.json()["user_course_progress"] == 2
        assert response_course.json()["chapters"][0]["user_chapter_progress"] == 2
        assert response_course.json()["chapters"][1]["user_chapter_progress"] == 2

    def test_unpublished_courses_dont_appear_on_endopoint(self, user_client):
        """Тест, что Курс со статусом DRAFT/ARCHIVED не появляется в выдаче."""
        _ = CourseFactory()
        _ = CourseFactory(status=Course.CourseStatus.DRAFT)
        _ = CourseFactory(status=Course.CourseStatus.ARCHIVE)
        url = reverse("courses-list")
        response = user_client.get(url)
        assert len(response.json()["results"]) == 1

    def test_lesson_course_endpoints_for_unauth_users(self, anonymous_client):
        """Тест, что эндпоинты урока и курсов доступны для незарегистрированных пользователей."""
        lesson = LessonFactory()
        course = CourseFactory()
        url_lesson = reverse("lessons-detail", kwargs={"pk": lesson.id})
        url_course_detail = reverse("courses-detail", kwargs={"pk": course.id})
        url_course_list = reverse("courses-list")
        response_lesson = anonymous_client.get(url_lesson)
        response_course_detail = anonymous_client.get(url_course_detail)
        response_course_list = anonymous_client.get(url_course_list)
        assert response_lesson.status_code == status.HTTP_200_OK
        assert response_course_detail.status_code == status.HTTP_200_OK
        assert response_course_list.status_code == status.HTTP_200_OK

    def test_current_lesson_and_chapter_in_course(self, user_client, user):
        """
        Тест текущего урока для четырех ситуаций.

        1. Наличие текущего урока в случе если пользователь не начал прохождение уроков.
        2. Наличие текущего урока в случае, если пользователь закончил урок, но не начал следующий.
        3. Наличие текущего урока в случае, если пользователь закончил урок и начал следующий.
        4. При прохождении всех уроков current_lesson == Null.
        """
        course = CourseWith2Chapters()
        url = reverse("courses-detail", kwargs={"pk": course.id})
        lessons = Lesson.objects.filter(chapter__course=course).order_by("id")
        first_lesson = lessons[0]
        second_lesson = lessons[1]

        def request_assert(user_client, url, expected_lesson_id, expected_chapter_id):
            """Шаблон для проверки ответа."""
            response = user_client.get(url)
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["current_lesson"]["chapter_id"] == expected_chapter_id
            assert response.json()["current_lesson"]["lesson_id"] == expected_lesson_id

        # 1. Наличие текущего урока в случе если пользователь не начал прохождение уроков.
        request_assert(user_client, url, first_lesson.id, first_lesson.chapter_id)

        # 2. Наличие текущего урока в случае, если пользователь закончил урок, но не начал следующий.
        first_lesson.finish(user)
        request_assert(user_client, url, second_lesson.id, second_lesson.chapter_id)

        # 3. Наличие текущего урока в случае, если пользователь закончил урок и начал следующий.
        # TODO после реализации функционала .activate() заменить
        first_lesson.lesson_progress.userlessonprogress = LessonProgressStatus.ProgressStatus.ACTIVE
        request_assert(user_client, url, second_lesson.id, second_lesson.chapter_id)

        # 4. При прохождении всех уроков current_lesson == Null.
        lesson = LessonFactory()
        lesson.finish(user)
        url = reverse("courses-detail", kwargs={"pk": lesson.chapter.course.id})
        request_assert(user_client, url, None, None)

    def test_ordering_working_properly(self, user_client):
        """Тест, что автоматическое назначение очередности работает корректно."""
        course = CourseWith2Chapters()
        url = reverse("courses-detail", kwargs={"pk": course.id})
        response = user_client.get(url)
        assert response.status_code == status.HTTP_200_OK

        # Проверяем корректность изначального порядка в главах и уроках
        for i in range(1, 3):
            chapter = response.json()["chapters"][i - 1]
            assert chapter["title"] == str(i)
            assert chapter["order_number"] == CHAPTER_STEP * i

            for n in range(1, 5):
                lesson = chapter["lessons"][n - 1]
                assert lesson["title"] == str(n)
                assert lesson["order_number"] == n * LESSON_STEP

        # Проверям корректность порядка, после переноса урока на другую позицию
        chapter = Chapter.objects.filter(course=course).order_by("order_number").first()
        lesson = Lesson.objects.filter(chapter=chapter, title="4").first()

        # Проверяем порядок уроков
        lesson.order_number = 13
        lesson.save()

        response_new_order = user_client.get(url)
        assert response_new_order.status_code == status.HTTP_200_OK
        lessons = response_new_order.json()["chapters"][0]["lessons"]
        new_order = ("1", "4", "2", "3")  # новый порядок уроков
        for n in range(4):
            lesson = lessons[n]
            assert lesson["order_number"] == (n + 1) * LESSON_STEP
            assert lesson["title"] == new_order[n]

        # Проверяем порядок глав
        chapter.order_number = 3947
        chapter.save()

        response_new_chapter_order = user_client.get(url)
        assert response_new_order.status_code == status.HTTP_200_OK
        chapters = response_new_chapter_order.json()["chapters"]
        new_order = ("2", "1")
        for i in range(1):
            chapter = chapters[i]
            assert chapter["order_number"] == CHAPTER_STEP * (i + 1)
            assert chapter["title"] == new_order[i]
            # Проверяем, что после изменения порядка глав, номера уроков такжже поменялись
            for n in range(4):
                lesson = chapter["lessons"][n]
                assert lesson["order_number"] == (n + 1) * LESSON_STEP

    def test_set_ordering_chapter(self):
        """Тест функции распределения порядковых номеров главы."""
        CourseWith2Chapters()
        new_chapter = ChapterFactory.build()
        queryset = Chapter.objects.all()
        mixin = order_number_mixin(CHAPTER_STEP, "course")
        mixin.set_ordering(new_chapter, queryset, CHAPTER_STEP)
        assert new_chapter.order_number == 3000

    def test_set_ordering_lesson(self):
        """Тест функции распределения порядковых номеров урока."""
        _ = ChapterWith3Lessons()
        new_lesson = LessonFactory.build()
        queryset = Lesson.objects.all()
        mixin = order_number_mixin(LESSON_STEP, "chapter")
        mixin.set_ordering(new_lesson, queryset, LESSON_STEP)
        assert new_lesson.order_number == 40
