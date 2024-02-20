import factory.fuzzy

from lizaalert.courses.models import Lesson
from lizaalert.homeworks.models import Homework
from tests.factories.courses import LessonFactory, SubscriptionFactory
from tests.factories.users import UserFactory


class HomeworkFactory(factory.django.DjangoModelFactory):
    """Test factory for Homework model."""

    class Meta:
        model = Homework

    reviewer = factory.SubFactory(UserFactory)
    lesson = factory.SubFactory(LessonFactory, lesson_type=Lesson.LessonType.HOMEWORK)
    text = factory.Faker("text", max_nb_chars=10000)
    subscription = factory.SubFactory(SubscriptionFactory)
    required = True
