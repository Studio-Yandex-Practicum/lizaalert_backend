from django.db import transaction
from django.db.models import Q

from .models import Badge, Volunteer, VolunteerBadge, VolunteerCourseCompletion


def assign_achievements_for_course(user, course_id):
    """Присваивает пользователю ачивки в зависимости от завершенных курсов."""
    badges_for_course = Badge.objects.filter(threshold_course_id=course_id)
    user_received_badge_for_course = None

    if VolunteerBadge.objects.filter(volunteer__user=user).exists():
        user_received_badge_for_course = VolunteerBadge.objects.filter(
            volunteer__user=user, badge__in=badges_for_course, course_id=course_id
        )

    badges_to_create = []

    for badge in badges_for_course:
        if not user_received_badge_for_course or not user_received_badge_for_course.filter(badge=badge).exists():
            badges_to_create.append(VolunteerBadge(volunteer=user.volunteer, badge=badge, course_id=course_id))

    with transaction.atomic():
        VolunteerBadge.objects.bulk_create(badges_to_create)


def assign_achievements_for_completion(user, course_id):
    """Присваивает пользователю ачивки в зависимости от количества завершенных курсов."""
    completed_courses_count = VolunteerCourseCompletion.objects.get(volunteer__user=user).completed_courses_count
    badges_for_completion = Badge.objects.filter(
        Q(threshold_courses__isnull=False) & Q(threshold_courses__lte=completed_courses_count)
    )
    user_received_badges = None

    if VolunteerBadge.objects.filter(volunteer__user=user).exists():
        user_received_badges = VolunteerBadge.objects.filter(volunteer__user=user, badge__in=badges_for_completion)

    badges_to_create = []

    for badge in badges_for_completion:
        if not user_received_badges or not user_received_badges.filter(badge=badge).exists():
            badges_to_create.append(VolunteerBadge(volunteer=user.volunteer, badge=badge, course_id=course_id))

    with transaction.atomic():
        VolunteerBadge.objects.bulk_create(badges_to_create)


def increment_completed_courses_count(user):
    """Увеличивает количество завершенных курсов пользователя."""
    volunteer = Volunteer.objects.get(user=user)
    volunteer_completion, created = VolunteerCourseCompletion.objects.get_or_create(
        volunteer=volunteer, defaults={"completed_courses_count": 1}
    )
    if not created:
        volunteer_completion.completed_courses_count += 1
        volunteer_completion.save()

    return volunteer_completion.completed_courses_count
