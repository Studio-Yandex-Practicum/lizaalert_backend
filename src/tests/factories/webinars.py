import datetime

import factory.fuzzy

from lizaalert.courses.models import Lesson
from lizaalert.webinars.models import Webinar
from tests.factories.courses import CohortAlwaysAvailableFactory, LessonFactory


class WebinarFactory(factory.django.DjangoModelFactory):
    """Test factory for Homework model."""

    class Meta:
        model = Webinar

    lesson = factory.SubFactory(LessonFactory, lesson_type=Lesson.LessonType.WEBINAR)
    description = factory.Faker("text", max_nb_chars=5000)
    webinar_date = factory.fuzzy.FuzzyDate(
        datetime.date.today() + datetime.timedelta(days=5),
        datetime.date.today() + datetime.timedelta(days=10),
    )
    cohort = factory.SubFactory(CohortAlwaysAvailableFactory, course=factory.SelfAttribute("..lesson.chapter.course"))
