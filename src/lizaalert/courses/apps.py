from django.apps import AppConfig


class CoursesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "lizaalert.courses"

    def ready(self) -> None:
        import lizaalert.courses.signals  # noqa
