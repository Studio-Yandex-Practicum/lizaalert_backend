from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class Command(BaseCommand):
    help = "Generate jwt token for user. If user is absent in db user will be created"

    def handle(self, *args, **options):
        user = options["username"]
        user_object, _ = User.objects.get_or_create(username=user)
        refresh = RefreshToken.for_user(user_object)
        print(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            required=True,
            help="Generate jwt token for provided username. If user with "
            "provided username absent in db he will be created",
        )
