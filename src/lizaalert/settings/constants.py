"""Settings file for constants."""


# Lesson and chapter ordering step
LESSON_STEP = 10
CHAPTER_STEP = 1000

# Default webinar length
DEFAULT_WEBINAR_LENGTH = 60


# Subscription statuses to allow access to the course
def get_access_statuses():
    """Вернуть статусы подписки с которыми разрешен доступ к курсу и его урокам."""
    from lizaalert.courses.models import Subscription

    return [
        Subscription.Status.AVAILABLE,
        Subscription.Status.IN_PROGRESS,
        Subscription.Status.COMPLETED,
    ]
