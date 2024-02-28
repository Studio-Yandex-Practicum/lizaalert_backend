import factory
from django.contrib.auth import get_user_model
from factory import fuzzy

from lizaalert.users.models import Badge, Level, Location, Volunteer, VolunteerBadge

User = get_user_model()
factory.Faker._DEFAULT_LOCALE = "en_US"


class UserFactory(factory.django.DjangoModelFactory):
    """User factory."""

    class Meta:
        """Factory configuration."""

        model = User
        django_get_or_create = ("username",)

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = factory.Faker("user_name")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
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
    location = factory.SubFactory(LocationFactory)
    birth_date = factory.Faker("date")


class LevelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Level

    name = fuzzy.FuzzyChoice(list(Level.LevelName))
    description = factory.Faker("paragraph")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        name = kwargs.get("name")
        level, _ = model_class.objects.get_or_create(name=name, defaults=kwargs)
        return level


class BadgeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Badge
        django_get_or_create = ("badge_slug",)

    name = factory.Faker("word")
    description = factory.Faker("sentence")
    badge_type = Badge.BadgeType.MANUAL
    badge_category = Badge.BadgeCategory.ONE_TIME
    badge_slug = factory.Sequence(lambda n: f"test_slug_{n}")
    issued_for = factory.Faker("word")
    threshold_courses = None
    threshold_course = None


class VolunteerBadgeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VolunteerBadge

    user = factory.SubFactory(UserFactory)
    badge = factory.SubFactory(BadgeFactory)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        from tests.factories.courses import CourseFactory

        user = kwargs.pop("user", None)
        volunteer = user.volunteer if user else None
        kwargs["volunteer"] = volunteer
        kwargs["course"] = CourseFactory()
        return super()._create(model_class, *args, **kwargs)
