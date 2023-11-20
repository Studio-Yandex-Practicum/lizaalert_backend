from django.db.models.signals import pre_save
from django.dispatch import receiver

from lizaalert.courses.mixins import order_number_mixin
from lizaalert.courses.models import Chapter, Lesson


@receiver(pre_save, sender=Chapter)
def chapter_order_number_pre_save(sender, instance, **kwargs):
    """Сохраняет состояние главы до сохранения, необходимо для получения order_number."""
    order_number_mixin(None, None).old_order_number_getter(instance)


@receiver(pre_save, sender=Lesson)
def lesson_order_number_pre_save(sender, instance, **kwargs):
    """Сохраняет состояние урока до сохранения, необходимо для получения order_number."""
    order_number_mixin(None, None).old_order_number_getter(instance)
