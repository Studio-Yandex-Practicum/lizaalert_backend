import factory.fuzzy

from lizaalert.homeworks.models import Homework
from tests.factories.courses import HomeworkLessonFactory, SubscriptionFactory
from tests.factories.users import UserFactory


class HomeworkFactory(factory.django.DjangoModelFactory):
    """Test factory for Homework model."""

    class Meta:
        model = Homework

    reviewer = factory.SubFactory(UserFactory)
    lesson = factory.SubFactory(HomeworkLessonFactory)
    text = factory.Faker("text", max_nb_chars=10000)
    subscription = factory.SubFactory(SubscriptionFactory)
    required = True
