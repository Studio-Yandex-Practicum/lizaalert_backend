import factory
from django.contrib.auth import get_user_model
from users.models import Level, Location, Volunteer


User = get_user_model()
factory.Faker._DEFAULT_LOCALE = "en_US"


class UserFactory(factory.django.DjangoModelFactory):
    """User factory."""

    class Meta:
        """Factory configuration."""

        model = User

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = factory.Faker("user_name")
    email = factory.Faker("email")
    password = factory.Faker("sha256")


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Location

    code = factory.Iterator(range(4))
    region = factory.Faker("city", locale="ru_RU")


class VolunteerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Volunteer

    user = factory.SubFactory(UserFactory)
    phone_number = factory.Faker("phone_number")
    location = factory.SubFactory(LocationFactory)
    birth_date = factory.Faker("date")


class LevelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Level

    name = factory.fuzzy.FuzzyChoice(list(Level.LevelName))
    description = factory.Faker("paragraph")
