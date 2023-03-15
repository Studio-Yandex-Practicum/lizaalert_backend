from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from courses.course_factory import LessonWith3ChapterFactory
from users.models import Level
from users.user_factory import LevelFactory, UserFactory

User = get_user_model()


class Command(BaseCommand):
    help = "Generate fake course data"

    def __generate_records(self, record_number, object_name):
        for _ in range(record_number):
            object_name()

    def handle(self, *args, **options):
        course_num = options["courses"]
        if User.objects.all().count() < 10:
            self.__generate_records(course_num, UserFactory)
        if not Level.objects.all().exists():
            self.__generate_records(course_num, LevelFactory)
        for _ in range(course_num):
            LessonWith3ChapterFactory()

    def add_arguments(self, parser):
        parser.add_argument(
            "--courses",
            type=int,
            default=5,
            help="Number of records generated with script",
        )
