from django.db.models.signals import pre_save
from django.dispatch import receiver

from lizaalert.courses.models import Chapter, Lesson


@receiver(pre_save, sender=Chapter)
def chapter_order_number_pre_save(sender, instance, **kwargs):
    """Сохраняет состояние главы до сохранения, необходимо для получения order_number."""
    if instance.id:
        old_instance = type(instance).objects.get(id=instance.id)
        instance._old_order_number = old_instance.order_number
    else:
        instance._old_order_number = None


@receiver(pre_save, sender=Lesson)
def lesson_order_number_pre_save(sender, instance, **kwargs):
    """Сохраняет состояние урока до сохранения, необходимо для получения order_number."""
    if instance.id:
        old_instance = type(instance).objects.get(id=instance.id)
        instance._old_order_number = old_instance.order_number
    else:
        instance._old_order_number = None
