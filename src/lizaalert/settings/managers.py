from django.db import models
from django.utils import timezone


class SoftQuerySet(models.QuerySet):
    """Queryset с мягким удалением и восстановлением."""

    def delete(self):
        self.update(deleted_at=timezone.now())


class SoftDeleteManager(models.Manager):
    """Менеджер модели с поддержкой мягкого удаления."""

    def get_queryset(self):
        """Возвращает queryset, исключая удаленные записи."""
        return SoftQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)
