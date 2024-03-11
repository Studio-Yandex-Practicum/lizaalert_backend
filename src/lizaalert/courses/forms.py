from collections import namedtuple

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
        CohortData = namedtuple("CohortData", ["start_date", "end_date", "max_students"])
        required_data = CohortData(
            cleaned_data.get("start_date"),
            cleaned_data.get("end_date"),
            cleaned_data.get("max_students"),
        )

        match required_data:
            case CohortData(start_date, end_date, max_students) if all((start_date, end_date, max_students)):
                if start_date > end_date:
                    raise ValidationError(
                        mark_safe(
                            """
                            Дата начала не может быть больше даты окончания.
                            """
                        )
                    )
                return cleaned_data
            case CohortData(None, None, None):
                return cleaned_data
            case _:
                raise ValidationError(
                    mark_safe(
                        """
                        Некорректное создание Когорты, когорта может быть:<br>
                        <ol>
                        <li>Доступной всегда - для этого необходимо оставить поля "Дата начала",
                        "Дата окончания" и "Максимальное количество студентов" пустыми.</li>
                        <li>С запланированной датой начала - для этого необходимо заполнить поля "Дата начала",
                        "Дата конца" и "Максимальное количество студентов".</li>
                        </ol>
                        """
                    )
                )
