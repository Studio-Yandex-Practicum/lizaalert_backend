from django.db import models


class QuestionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by("order_number")
