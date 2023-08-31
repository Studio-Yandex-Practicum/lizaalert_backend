from django.db import models


class TimeStampedMixin(models.Model):
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    deleted_at = models.DateTimeField("Дата удаления", null=True, blank=True)

    class Meta:
        abstract = True
