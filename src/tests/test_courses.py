from unittest.mock import Mock

import pytest
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from lizaalert.courses.mixins import order_number_mixin
from lizaalert.courses.models import Chapter, Course, Lesson
from lizaalert.courses.signals import course_finished
from lizaalert.settings.constants import CHAPTER_STEP, LESSON_STEP
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
    Subscription,
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

    def test_lessons_appear_in_chapters(self, user_client, user):
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
        _ = SubscriptionFactory(course=course, user=user)
        response = user_client.get(reverse("courses-detail", kwargs={"pk": course.id}))
        number_of_lessons = len(response.json()["chapters"][0]["lessons"])
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["chapters"][0]["id"] == chapter.id
        assert number_of_lessons == 3
        assert response.json()["chapters"][0]["lessons"][2]["order_number"] == number_of_lessons * LESSON_STEP

    def test_course_annotation(self, user_client, user):
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
        _ = SubscriptionFactory(course=course, user=user)
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
        """
        Тест, что пользователь может подписаться на курс.

        В переменной courses создается кортеж из двух курсов.
        Первый курс начнется через неделю и при подписке на него ожидаем статус ENROLLED.
        Второй курс уже идет и при подписке на него ожидаем статус AVAILABLE.
        """
        courses = (
            (
                CourseFactory(start_date=timezone.now().date() + timezone.timedelta(days=7)),
                Subscription.Status.ENROLLED,
            ),
            (
                CourseFactory(start_date=timezone.now().date() - timezone.timedelta(days=7)),
                Subscription.Status.AVAILABLE,
            ),
        )
        for course, expected_status in courses:
            subscribe = reverse("courses-enroll", kwargs={"pk": course.id})
            subscription_response = user_client.post(subscribe)
            url = reverse("courses-detail", kwargs={"pk": course.id})
            response = user_client.get(url)
            assert response.status_code == status.HTTP_200_OK
            assert subscription_response.status_code == status.HTTP_201_CREATED
            assert response.json()["user_status"] == expected_status

        # Повторная подписка невозможна
        subscription_response = user_client.post(subscribe)
        assert subscription_response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_unsubscription_from_course(self, user_client, user):
        """Тест, что пользователь может отписаться от курса."""
        subscription = SubscriptionFactory(user=user)
        course_id = subscription.course.id
        url = reverse("courses-detail", kwargs={"pk": course_id})
        response = user_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["user_status"] == Subscription.Status.AVAILABLE

        unsubscribe_url = reverse("courses-unroll", kwargs={"pk": course_id})
        response = user_client.post(unsubscribe_url)
        response_1 = user_client.get(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response_1.json()["user_status"] == Subscription.Status.NOT_ENROLLED

    def test_another_user_unable_to_unsubscribe_from_course(self, user_client, user_2):
        """Тест, что иной пользователь не может отписаться не от своего курса."""
        subscription = SubscriptionFactory(user=user_2)
        course_id = subscription.course.id
        unsubscribe_url = reverse("courses-unroll", kwargs={"pk": course_id})
        response = user_client.post(unsubscribe_url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_lessons_appear_on_endpoint(self, user_client, user):
        """Тест, что уроки и аннотация курса корректно отображаются по эндпоинту."""
        _ = ChapterWith3Lessons()
        lesson = LessonFactory()
        _ = SubscriptionFactory(course=lesson.chapter.course, user=user)
        url = reverse("lessons-detail", kwargs={"pk": lesson.id})
        response = user_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == lesson.id
        assert response.json()["course_id"] == lesson.chapter.course_id

    def test_lessons_pagination_works(self, user_client, user):
        """
        Тест, что работает переключение между уроками.

        Создается курс с 2 Главами по 4 урока в каждой.
        Проверяется навигация по всем 8 урокам, при этой первый и последний урок
        должны выдавать None при отсутствии крайних уроков.
        """
        course = CourseWith2Chapters()
        subscription = SubscriptionFactory(course=course, user=user)
        lesson = Lesson.objects.filter(chapter__course=course).first()
        lessons = lesson.ordered

        for i, lesson in enumerate(lessons):
            url = reverse("lessons-detail", kwargs={"pk": lesson.id})
            response = user_client.get(url)
            assert response.status_code == status.HTTP_200_OK

            json_data = response.json()
            prev_lesson_id = json_data["prev_lesson"]["lesson_id"]
            next_lesson_id = json_data["next_lesson"]["lesson_id"]

            if i > 0:
                assert prev_lesson_id == lessons[i - 1].id
            else:
                assert prev_lesson_id is None

            if i < len(lessons) - 1:
                assert next_lesson_id == lessons[i + 1].id
            else:
                assert next_lesson_id is None

            lesson.finish(subscription)

    def test_breadcrumbs(self, user_client, user):
        """Тест, что breadcrumbs отображаются корректно."""
        lesson = LessonFactory()
        _ = SubscriptionFactory(course=lesson.chapter.course, user=user)
        url = reverse("lessons-detail", kwargs={"pk": lesson.id})
        response = user_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["breadcrumbs"]["course"]["id"] == lesson.chapter.course.id
        assert response.json()["breadcrumbs"]["course"]["title"] == lesson.chapter.course.title
        assert response.json()["breadcrumbs"]["chapter"]["id"] == lesson.chapter.id
        assert response.json()["breadcrumbs"]["chapter"]["title"] == lesson.chapter.title

    def test_lesson_completion(self, user_client, user):
        """
        Тест, что работает завершение урока.

        Проверяется статус прохождения урока, убеждаемся, что урок не пройден.
        После запроса POST на /complete/ проверяем статус пройденности урока.
        """
        lesson = LessonFactory()
        _ = SubscriptionFactory(course=lesson.chapter.course, user=user)
        url = reverse("courses-detail", kwargs={"pk": lesson.chapter.course_id})

        def response_assert(url, status_code, user_lesson_progress):
            response = user_client.get(url)
            assert response.status_code == status_code
            assert response.json()["chapters"][0]["lessons"][0]["user_lesson_progress"] == user_lesson_progress

        response_assert(url, status.HTTP_200_OK, 0)
        complete_url = reverse("lessons-complete", kwargs={"pk": lesson.id})
        user_client.post(complete_url)
        response_assert(url, status.HTTP_200_OK, 2)

    def test_final_lesson_completion_triggers_chapter_and_course_completion(self, user_client, user):
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
        _ = SubscriptionFactory(course=course, user=user)

        # 1. Проверяем, что курс и главы не пройдены
        url_course = reverse("courses-detail", kwargs={"pk": course.id})
        response_course = user_client.get(url_course)
        assert response_course.status_code == status.HTTP_200_OK
        assert response_course.json()["user_course_progress"] != 2
        assert response_course.json()["chapters"][0]["user_chapter_progress"] != 2

        # 2. Проверяем, что после прохождения одного урока, первая глава не пройдена
        user_client.post(reverse("lessons-complete", kwargs={"pk": c1_lesson_1.id}))
        response_course = user_client.get(url_course)
        assert response_course.json()["chapters"][0]["user_chapter_progress"] != 2

        # 3. Проверяем, что после прохождения всех уроков, первая глава пройдена. а курс не пройден
        for lesson in lesson_bulk_1:
            user_client.post(reverse("lessons-complete", kwargs={"pk": lesson.id}))
        response_course = user_client.get(url_course)
        assert response_course.json()["user_course_progress"] != 2
        assert response_course.json()["chapters"][0]["user_chapter_progress"] == 2

        # 4. Проверяем, что после прохождения первого и последнего урока второй главы (минуя второй урок)
        # вторая глава будет не пройдена
        user_client.post(reverse("lessons-complete", kwargs={"pk": c2_lesson_1.id}))
        user_client.post(reverse("lessons-complete", kwargs={"pk": c2_lesson_3.id}))
        response_course = user_client.get(url_course)
        assert response_course.json()["user_course_progress"] != 2
        assert response_course.json()["chapters"][1]["user_chapter_progress"] != 2

        # 5. Проверяем, что после прохождения всех уроков второй главы, вторая глава и курс пройдены
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
        """
        Тест, для неавторизованных пользователей.

        Курс доступен для неавторизованных пользователей.
        Урок недоступен для неавторизованных пользователей.
        """
        lesson = LessonFactory()
        course = CourseFactory()
        url_lesson = reverse("lessons-detail", kwargs={"pk": lesson.id})
        url_course_detail = reverse("courses-detail", kwargs={"pk": course.id})
        url_course_list = reverse("courses-list")
        response_lesson = anonymous_client.get(url_lesson)
        response_course_detail = anonymous_client.get(url_course_detail)
        response_course_list = anonymous_client.get(url_course_list)
        assert response_lesson.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_course_detail.status_code == status.HTTP_200_OK
        assert response_course_list.status_code == status.HTTP_200_OK

    def test_current_lesson_and_chapter_in_course(self, user_client, user):
        """
        Тест текущего урока для четырех ситуаций.

        1. Наличие текущего урока в случе если пользователь не начал прохождение уроков.
        2. Наличие текущего урока в случае, если пользователь закончил урок, но не начал следующий.
        3. Наличие текущего урока в случае, если пользователь закончил урок и начал следующий.
        4. При прохождении всех уроков current_lesson == last_lesson.
        """
        course = CourseWith2Chapters()
        subscription = SubscriptionFactory(course=course, user=user)
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
        first_lesson.finish(subscription)
        request_assert(user_client, url, second_lesson.id, second_lesson.chapter_id)

        # 3. Наличие текущего урока в случае, если пользователь закончил урок и начал следующий.
        second_lesson.activate(subscription)
        request_assert(user_client, url, second_lesson.id, second_lesson.chapter_id)

        # 4. При прохождении всех уроков current_lesson == last_lesson.
        lesson = LessonFactory()
        lesson.finish(subscription)
        url = reverse("courses-detail", kwargs={"pk": lesson.chapter.course.id})
        request_assert(user_client, url, lesson.id, lesson.chapter_id)

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

    def test_lesson_activation(self, user_client, user):
        """
        Тест активации урока.

        Проверяем активацию урока.
        """
        lesson = LessonFactory()
        _ = SubscriptionFactory(course=lesson.chapter.course, user=user)
        url = reverse("lessons-detail", kwargs={"pk": lesson.id})
        response = user_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["user_lesson_progress"] == 1

    def test_lesson_activation_changes(self, user_client, user):
        """
        Тест активации урока.

        Проверяем, что после завершения урока, невозможно его повторно активировать
         переходом по эндпоинту урока.
        """
        lesson = LessonFactory()
        _ = SubscriptionFactory(course=lesson.chapter.course, user=user)
        url = reverse("courses-detail", kwargs={"pk": lesson.chapter.course_id})
        complete_url = reverse("lessons-complete", kwargs={"pk": lesson.id})
        user_client.post(complete_url)
        response = user_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["chapters"][0]["lessons"][0]["user_lesson_progress"] == 2

    def test_permission_for_current_lesson_works(self, user_client, user):
        """
        Тест, что только текущий/пройденный урок доступен для пользователя.

        1. Проверяем, что пользователю доступен текущий урок.
        2. Проходим первый урок, проверяем, что пользователю доступен второй урок.
        3. Проверяем, что пользователю недоступен иной урок.
        4. Проверяем, что пользователю доступен пройденный урок.
        """
        chapter = ChapterWith3Lessons()
        subscription = SubscriptionFactory(course=chapter.course, user=user)
        lesson = Lesson.objects.filter(chapter=chapter).first()
        lessons = lesson.ordered
        for i, lesson in enumerate(lessons):
            url = reverse("lessons-detail", kwargs={"pk": lesson.id})
            response = user_client.get(url)
            if i == 0:
                assert response.status_code == status.HTTP_200_OK
                lesson.finish(subscription)
            elif i == 1:
                assert response.status_code == status.HTTP_200_OK
            else:
                assert response.status_code == status.HTTP_403_FORBIDDEN

        # Проверяем, что пользователю доступен пройденный урок
        url = reverse("lessons-detail", kwargs={"pk": lessons[0].id})
        response = user_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_update_subsctiptions_status(self, user, user_client):
        """
        Тест изменения статуса подписки на курс.

        Функция обновляет статусы подписки пользователя в зависимости от статуса
         прохождения курса, либо даты начала курса.
        """
        start_in_future = timezone.now().date() + timezone.timedelta(days=7)
        already_started = timezone.now().date() - timezone.timedelta(days=7)

        def assert_subscription_status(user, date, expected_status, finish_course=False, course_in_progress=False):
            course = CourseWith2Chapters(start_date=date)
            subscription = SubscriptionFactory(user=user, course=course)
            course_url = reverse("courses-detail", kwargs={"pk": course.id})
            if finish_course:
                lessons = Lesson.objects.filter(chapter__course=course)
                for lesson in lessons:
                    lesson.finish(subscription)
                course.finish(subscription)
            if course_in_progress:
                lesson = Lesson.objects.filter(chapter__course=course).first()
                url = reverse("lessons-detail", kwargs={"pk": lesson.id})
                user_client.get(url)

            response = user_client.get(course_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["user_status"] == expected_status

        # Тестируем статус при старте курса в будущем
        assert_subscription_status(user, start_in_future, Subscription.Status.ENROLLED)

        # Тестируем статус при уже стартовавшем курсе
        assert_subscription_status(user, already_started, Subscription.Status.AVAILABLE)

        # Тестируем статус при прохождении курса
        assert_subscription_status(user, already_started, Subscription.Status.IN_PROGRESS, course_in_progress=True)

        # Тестируем статус при завершенном курсе
        assert_subscription_status(user, already_started, Subscription.Status.COMPLETED, finish_course=True)

    def test_enrollment_permission_for_lessons(self, user_client, user):
        """Тест, что доступ к урокам возможен только для подписанных пользователей и на начавшийся курс."""
        start_in_future = timezone.now().date() + timezone.timedelta(days=7)
        already_started = timezone.now().date() - timezone.timedelta(days=7)

        def assert_permision(expected_status, date, subscribed=False):
            course = CourseWith2Chapters(start_date=date)
            if subscribed:
                _ = SubscriptionFactory(user=user, course=course)
            lesson = Lesson.objects.filter(chapter__course=course).first()
            url = reverse("lessons-detail", kwargs={"pk": lesson.id})
            response = user_client.get(url)
            assert response.status_code == expected_status

        # Тестируем доступ при отсутствии подсписки
        assert_permision(status.HTTP_403_FORBIDDEN, already_started)

        # Тестриуем доступ при подписке и стартовавшем курсе
        assert_permision(status.HTTP_200_OK, already_started, subscribed=True)

        # Тестируем доступ при подписке и не стартовавшем курсе
        assert_permision(status.HTTP_403_FORBIDDEN, start_in_future, subscribed=True)

    def test_course_completion_endpoint(self, user_client, user):
        """
        Тест эндпоинта завершения курса.

        Проверяем, что при завершении курса, пользователь получает статус COMPLETED.
        Проверяем что курс можно завершить только с завершенными главами, в противном случае получаем 403.
        """
        course = CourseWith2Chapters()
        url = reverse("courses-complete", kwargs={"pk": course.id})
        url_course = reverse("courses-detail", kwargs={"pk": course.id})
        response = user_client.post(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        subscription = SubscriptionFactory(user=user, course=course)
        response = user_client.post(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        response_course = user_client.get(url_course)
        lessons = Lesson.objects.filter(chapter__course=course)
        for lesson in lessons:
            lesson.finish(subscription)
        response = user_client.post(url)
        response_course = user_client.get(url_course)
        assert response.status_code == status.HTTP_200_OK
        assert response_course.json()["user_status"] == Subscription.Status.COMPLETED

    def test_signal_sent_after_complete_course(self, user):
        """Тест, что отправляется сигнал для получения ачивок после завершения курса."""
        course = CourseWith2Chapters()
        mock_receiver = Mock()

        @receiver(course_finished)
        def check_signal(sender, signal, **kwargs):
            assert kwargs["course"] == course
            assert kwargs["user"] == user
            return mock_receiver(sender, signal, **kwargs)

        course.get_achievements(course, user)
        mock_receiver.assert_called_once_with(course.__class__, course_finished, course=course, user=user)

    def test_current_lesson_endpoint(self, user_client, user):
        """
        Тест эндпоинта для получения текущего урока.

        Проверяем, что возвращается текущий урок и глава.
        """
        course = CourseWith2Chapters()
        _ = SubscriptionFactory(course=course, user=user)
        url = reverse("courses-current-lesson", kwargs={"pk": course.id})
        response = user_client.get(url)
        lesson = Lesson.objects.filter(chapter__course=course).first()
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["lesson_id"] == lesson.id
        assert response.json()["chapter_id"] == lesson.chapter_id
