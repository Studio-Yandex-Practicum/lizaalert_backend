import datetime
import json

import factory.fuzzy

from lizaalert.courses.models import (
    FAQ,
    Chapter,
    Cohort,
    Course,
    CourseFaq,
    CourseKnowledge,
    Knowledge,
    Lesson,
    Subscription,
)
from tests.factories.users import LevelFactory, UserFactory


class JSONFactory(factory.DictFactory):
    """Use with factory.Dict to make JSON strings."""

    @classmethod
    def _generate(cls, create, attrs):
        obj = super()._generate(create, attrs)
        return json.dumps(obj)


class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course

    title = factory.Sequence(lambda n: "Курс {}".format(n))
    course_format = factory.Sequence(lambda n: "Курс {}".format(n))
    level = factory.SubFactory(LevelFactory)
    cover_path = factory.django.ImageField()
    short_description = factory.Sequence(lambda n: "Курс{}".format(n))
    full_description = factory.Sequence(lambda n: "Курс{}".format(n))
    user_created = factory.SubFactory(UserFactory)
    status = Course.CourseStatus.PUBLISHED


class ChapterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Chapter

    title = factory.Sequence(lambda n: "Часть{}".format(n))
    course = factory.SubFactory(CourseFactory)
    user_created = factory.SubFactory(UserFactory)
    user_modifier = factory.SubFactory(UserFactory)


class LessonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Lesson

    title = factory.Sequence(lambda n: "Урок{}".format(n))
    chapter = factory.SubFactory(ChapterFactory)
    description = factory.Faker("sentence", nb_words=5, variable_nb_words=True)
    lesson_type = Lesson.LessonType.LESSON
    status = Lesson.LessonStatus.PUBLISHED
    tags = factory.Faker("words", nb=5)
    duration = factory.fuzzy.FuzzyInteger(0, 10)
    user_created = factory.SubFactory(UserFactory)
    user_modifier = factory.SubFactory(UserFactory)
    order_number = factory.fuzzy.FuzzyInteger(0, 10)

    @factory.lazy_attribute
    def video_link(self):
        if self.lesson_type == Lesson.LessonType.VIDEOLESSON:
            return factory.Faker("url")
        return ""


class FaqFactory(factory.django.DjangoModelFactory):
    """Test factory for FAQ model."""

    class Meta:
        model = FAQ

    question = factory.Faker("sentence", nb_words=5, variable_nb_words=True)
    answer = factory.Faker("sentence", nb_words=15, variable_nb_words=True)
    author = factory.SubFactory(UserFactory)


class KnowledgeFactory(factory.django.DjangoModelFactory):
    """Test factory for Knowledge model."""

    class Meta:
        model = Knowledge

    title = factory.Sequence(lambda n: f"Знание {n}")
    description = factory.Faker("sentence", nb_words=15, variable_nb_words=True)
    author = factory.SubFactory(UserFactory)


class CourseFaqFactory(factory.django.DjangoModelFactory):
    """Test factory for Course - FAQ relation."""

    class Meta:
        model = CourseFaq

    faq = factory.SubFactory(FaqFactory)
    course = factory.SubFactory(CourseFactory)


class CourseKnowledgeFactory(factory.django.DjangoModelFactory):
    """Test factory for Course - Knowledge relation."""

    class Meta:
        model = CourseKnowledge

    knowledge = factory.SubFactory(KnowledgeFactory)
    course = factory.SubFactory(CourseFactory)


class CourseWith3FaqFactory(CourseFactory):
    """Test factory for Course with 3 FAQ fields."""

    membership1 = factory.RelatedFactory(
        CourseFaqFactory,
        factory_related_name="course",
    )
    membership2 = factory.RelatedFactory(
        CourseFaqFactory,
        factory_related_name="course",
    )
    membership3 = factory.RelatedFactory(
        CourseFaqFactory,
        factory_related_name="course",
    )


class CourseWith3KnowledgeFactory(CourseFactory):
    """Test factory for Course with 3 Knowledge fields."""

    membership1 = factory.RelatedFactory(
        CourseKnowledgeFactory,
        factory_related_name="course",
    )
    membership2 = factory.RelatedFactory(
        CourseKnowledgeFactory,
        factory_related_name="course",
    )
    membership3 = factory.RelatedFactory(
        CourseKnowledgeFactory,
        factory_related_name="course",
    )


class ChapterWith3Lessons(ChapterFactory):
    """Test Chapter factory with 3 related lessons."""

    membership1 = factory.RelatedFactory(
        LessonFactory,
        factory_related_name="chapter",
        order_number=factory.Iterator([3]),
        duration=factory.fuzzy.FuzzyInteger(0, 10),
    )
    membership2 = factory.RelatedFactory(
        LessonFactory,
        factory_related_name="chapter",
        order_number=factory.Iterator([1]),
        duration=factory.fuzzy.FuzzyInteger(0, 10),
    )
    membership3 = factory.RelatedFactory(
        LessonFactory,
        factory_related_name="chapter",
        order_number=factory.Iterator([2]),
        duration=factory.fuzzy.FuzzyInteger(0, 10),
    )


class ChapterWith4Lessons(ChapterFactory):
    """Test Chapter factory with 4 related lessons."""

    membership1 = factory.RelatedFactory(
        LessonFactory,
        factory_related_name="chapter",
        order_number=factory.Iterator([10]),
        title=factory.Iterator([1]),
        duration=factory.fuzzy.FuzzyInteger(0, 10),
    )
    membership2 = factory.RelatedFactory(
        LessonFactory,
        factory_related_name="chapter",
        order_number=factory.Iterator([20]),
        title=factory.Iterator([2]),
        duration=factory.fuzzy.FuzzyInteger(0, 10),
    )
    membership3 = factory.RelatedFactory(
        LessonFactory,
        factory_related_name="chapter",
        order_number=factory.Iterator([30]),
        title=factory.Iterator([3]),
        duration=factory.fuzzy.FuzzyInteger(0, 10),
    )
    membership4 = factory.RelatedFactory(
        LessonFactory,
        factory_related_name="chapter",
        order_number=factory.Iterator([40]),
        title=factory.Iterator([4]),
        duration=factory.fuzzy.FuzzyInteger(0, 10),
    )


class CohortFactory(factory.django.DjangoModelFactory):
    """Test factory for Cohort model."""

    class Meta:
        model = Cohort

    course = factory.SubFactory(CourseFactory)
    start_date = factory.fuzzy.FuzzyDate(
        datetime.date.today() + datetime.timedelta(days=5),
        datetime.date.today() + datetime.timedelta(days=10),
    )
    end_date = factory.LazyAttribute(lambda o: o.start_date + datetime.timedelta(days=30))
    teacher = factory.SubFactory(UserFactory)
    students_count = factory.fuzzy.FuzzyInteger(0, 10)
    max_students = factory.fuzzy.FuzzyInteger(20, 40)


class CohortTodayFactory(CohortFactory):
    """Test factory for Cohort model with start date today."""

    start_date = datetime.date.today()
    end_date = datetime.date.today() + datetime.timedelta(days=30)


class CohortAlwaysAvailableFactory(factory.django.DjangoModelFactory):
    """Test factory for Cohort model with no requirements."""

    class Meta:
        model = Cohort

    course = factory.SubFactory(CourseFactory)
    teacher = factory.SubFactory(UserFactory)
    students_count = factory.fuzzy.FuzzyInteger(0, 10)


class CourseWithAvailableCohortFactory(CourseFactory):
    """Test factory for Course with available Cohort."""

    membership1 = factory.RelatedFactory(
        CohortAlwaysAvailableFactory,
        factory_related_name="course",
    )


class SubscriptionFactory(factory.django.DjangoModelFactory):
    """Test factory for user Subscription on Course."""

    class Meta:
        model = Subscription

    user = factory.SubFactory(UserFactory)
    course = factory.SubFactory(CourseWithAvailableCohortFactory)


class SubscriptionAlwaysAvailableFactory(SubscriptionFactory):
    """Test factory for user Subscription on Course with no requirements/start date."""

    membership1 = factory.RelatedFactory(
        CohortAlwaysAvailableFactory,
        factory_related_name="subscriptions",
    )


class CourseWith2Chapters(CourseFactory):
    """
    Создает курс, 2 главы с 4 уроками в каждой.

    В заголовках прописана изначальная нумерация для проверки
     корректности работы ordering.
    """

    membership1 = factory.RelatedFactory(
        ChapterWith4Lessons,
        factory_related_name="course",
        title=factory.Iterator([1]),
    )
    membership2 = factory.RelatedFactory(
        ChapterWith4Lessons,
        factory_related_name="course",
        title=factory.Iterator([2]),
    )
    membership3 = factory.RelatedFactory(
        CohortAlwaysAvailableFactory,
        factory_related_name="course",
    )


class CourseWithFutureCohortFactory(CourseFactory):
    """Test factory for Course with Cohort thats starts in future."""

    membership1 = factory.RelatedFactory(
        CohortFactory,
        factory_related_name="course",
    )


class CourseWithTodayCohortFactory(CourseFactory):
    """Test factory for Course with Cohort thats starts today."""

    membership1 = factory.RelatedFactory(
        CohortTodayFactory,
        factory_related_name="course",
    )


class UnpublishedLessonFactory(LessonFactory):
    """Test factory for unpublished Lesson."""

    status = Lesson.LessonStatus.DRAFT


class UnpublishedCourseFactory(CourseFactory):
    """Test factory for unpublished Course."""

    status = Course.CourseStatus.DRAFT


class HomeworkLessonFactory(LessonFactory):
    """Test factory for Lesson with Homework."""

    lesson_type = Lesson.LessonType.HOMEWORK
