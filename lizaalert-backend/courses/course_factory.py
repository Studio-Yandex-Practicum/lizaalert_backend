import random

import factory.fuzzy
from courses.models import Chapter, ChapterLesson, Course, Lesson
from users import models


class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course

    title = factory.Sequence(lambda n: "Курс{}".format(random.randrange(10)))
    format = factory.Sequence(lambda n: "Курс{}".format(n))
    level = factory.fuzzy.FuzzyChoice(models.Level.objects.all())
    cover_path = factory.django.ImageField()
    short_description = factory.Sequence(lambda n: "Курс{}".format(n))
    full_description = factory.Sequence(lambda n: "Курс{}".format(n))
    user_created = factory.fuzzy.FuzzyChoice(models.User.objects.all())


class LessonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Lesson

    title = factory.Sequence(lambda n: "Урок{}".format(n))
    description = factory.Faker("sentence", nb_words=5, variable_nb_words=True)
    lesson_type = factory.fuzzy.FuzzyChoice(list(Lesson.LessonType))
    lesson_status = Lesson.LessonStatus.READY
    tags = factory.Faker("words", nb=5)
    duration = factory.fuzzy.FuzzyInteger(0, 10)
    user_created = factory.fuzzy.FuzzyChoice(models.User.objects.all())
    user_modifier = factory.fuzzy.FuzzyChoice(models.User.objects.all())


class ChapterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Chapter

    title = factory.Sequence(lambda n: "Часть{}".format(n))
    course = factory.SubFactory(CourseFactory)
    user_created = factory.fuzzy.FuzzyChoice(models.User.objects.all())
    user_modifier = factory.fuzzy.FuzzyChoice(models.User.objects.all())


class ChapterLessonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ChapterLesson

    chapter = factory.SubFactory(ChapterFactory)
    lesson = factory.SubFactory(LessonFactory)
    order_number = factory.fuzzy.FuzzyInteger(0, 10)
    created_at = factory.Faker("date_object")


class LessonWithChapterFactory(LessonFactory):
    membership = factory.RelatedFactory(
        ChapterLessonFactory, factory_related_name="lesson",
    )


class LessonWith3ChapterFactory(ChapterFactory):
    membership1 = factory.RelatedFactory(
        ChapterLessonFactory, factory_related_name="chapter",
    )
    membership2 = factory.RelatedFactory(
        ChapterLessonFactory, factory_related_name="chapter",
    )
    membership3 = factory.RelatedFactory(
        ChapterLessonFactory, factory_related_name="chapter",
    )
