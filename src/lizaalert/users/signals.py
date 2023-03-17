from django.db.models.signals import post_save
from django.dispatch import receiver

from lizaalert.users.models import User, Volunteer


@receiver(post_save, sender=User)
def create_volunteer(instance, created, raw, **kwargs):
    if created and isinstance(instance, User):
        if not Volunteer.objects.filter(user=instance).exists():
            Volunteer.objects.create(user=instance)
