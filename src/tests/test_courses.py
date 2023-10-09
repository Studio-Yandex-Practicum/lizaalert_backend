import pytest
from django.urls import reverse
from rest_framework import status

from lizaalert.courses.models import Lesson
from tests.factories.courses import (
    ChapterFactory,
    ChapterWith3Lessons,
    CourseFactory,
    CourseFaqFactory,
    CourseKnowledgeFactory,
    CourseStatusFactory,
    CourseWith3FaqFactory,
    CourseWith3KnowledgeFactory,
    LessonFactory,
    SubscriptionFactory,
)
from tests.factories.users import LevelFactory
from tests.user_fixtures.course_fixtures import return_course_data
from tests.user_fixtures.level_fixtures import return_levels_data


@pytest.mark.django_db(transaction=True)
class TestCourseStatusAndLevel:
    urls = [
        (reverse("courses_statuses-list"), return_course_data),
        (reverse("level-list"), return_levels_data),
    ]

    @pytest.mark.parametrize("url, test_data", urls)
    def test_not_found(self, user_client, url, test_data):
        response = user_client.get(url)
        assert response.status_code != status.HTTP_404_NOT_FOUND

    def test_anonymous(self, client):
        response = client.get(self.urls[0][0])
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize("url, test_data", urls)
    def test_coursestatus_list(self, user_client, url, test_data):
        _ = [LevelFactory() for _ in range(3)]
        _ = [CourseStatusFactory() for _ in range(3)]
        response = user_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == test_data()


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
        print(response.json())
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["chapters"][0]["id"] == chapter.id
        assert len(response.json()["chapters"][0]["lessons"]) == 3
        assert response.json()["chapters"][0]["lessons"][2]["order_number"] == 3

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
        course = CourseFactory()
        level = course.level.name
        params = {"level": level}
        response = user_client.get(self.url, params)
        courses = response.json()["results"]
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["results"][0]["level"] == level
        assert len(courses) != 0

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
