from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from lizaalert.courses.models import Cohort


class CohortForm(forms.ModelForm):
    """
    Форма для модели Cohort.

    Обеспечивает создание записи Когорта.
    Позволяет создать 2 типа когорт:
    1) Открытая когорта, без даты начала, даты конца и максимального количества студентов.
    2) Когорта, обязательный дата начала, дата конца и максимальное количество студентов.
    """

    class Meta:

        model = Cohort
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        required_data = (
            cleaned_data.get("start_date"),
            cleaned_data.get("end_date"),
            cleaned_data.get("max_students"),
        )

        if all(required_data) or not any(required_data):
            return cleaned_data

        raise ValidationError(
            mark_safe(
                """
            Некорректное создание Когорты, когорта может быть:<br>
            1. Доступной всегда - для этого необходимо оставить поля "Дата начала",
            "Дата окончания" и "Максимальное количество студентов" пустыми.<br>
            2. С запланированной датой начала - для этого необходимо заполнить поля "Дата начала",
            "Дата конца" и "Максимальное количество студентов".
            """
            )
        )
