import datetime
import json

import factory.fuzzy

from lizaalert.courses.models import Chapter, ChapterLesson, Course, CourseStatus, Lesson
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
    knowledge = factory.Dict(
        {
            "title": factory.Faker("sentence"),
            "description": factory.Faker("text"),
        },
        dict_factory=JSONFactory,
    )
    cover_path = factory.django.ImageField()
    start_date = factory.fuzzy.FuzzyDate(
        start_date=datetime.date.today() - datetime.timedelta(days=5),
        end_date=datetime.date.today() + datetime.timedelta(days=100),
    )
    short_description = factory.Sequence(lambda n: "Курс{}".format(n))
    full_description = factory.Sequence(lambda n: "Курс{}".format(n))
    faq = factory.Faker("sentence", nb_words=5, variable_nb_words=True)
    user_created = factory.SubFactory(UserFactory)


class LessonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Lesson

    title = factory.Sequence(lambda n: "Урок{}".format(n))
    description = factory.Faker("sentence", nb_words=5, variable_nb_words=True)
    lesson_type = factory.fuzzy.FuzzyChoice(list(Lesson.LessonType))
    lesson_status = Lesson.LessonStatus.READY
    tags = factory.Faker("words", nb=5)
    duration = factory.fuzzy.FuzzyInteger(0, 10)
    user_created = factory.SubFactory(UserFactory)
    user_modifier = factory.SubFactory(UserFactory)


class ChapterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Chapter

    title = factory.Sequence(lambda n: "Часть{}".format(n))
    course = factory.SubFactory(CourseFactory)
    user_created = factory.SubFactory(UserFactory)
    user_modifier = factory.SubFactory(UserFactory)


class CourseStatusFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CourseStatus

    name = factory.Sequence(lambda n: "Статус {}".format(n))
    slug = factory.fuzzy.FuzzyChoice(list(CourseStatus.SlugStatus))


class ChapterLessonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ChapterLesson

    chapter = factory.SubFactory(ChapterFactory)
    lesson = factory.SubFactory(LessonFactory)
    order_number = factory.fuzzy.FuzzyInteger(0, 10)
    created_at = factory.Faker("date_object")


class LessonWithChapterFactory(LessonFactory):
    membership = factory.RelatedFactory(
        ChapterLessonFactory,
        factory_related_name="lesson",
    )


class LessonWith3ChapterFactory(ChapterFactory):
    membership1 = factory.RelatedFactory(
        ChapterLessonFactory,
        factory_related_name="chapter",
    )
    membership2 = factory.RelatedFactory(
        ChapterLessonFactory,
        factory_related_name="chapter",
    )
    membership3 = factory.RelatedFactory(
        ChapterLessonFactory,
        factory_related_name="chapter",
    )
