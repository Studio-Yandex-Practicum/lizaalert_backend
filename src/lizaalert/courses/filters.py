import django_filters
from django_filters import rest_framework as filters

from .models import Course


class CourseFilter(filters.FilterSet):
    """
    Кастомный фильтр для модели Course.

    Фильтрация по формату курса, ID уровня и по направлению.
    """

    course_format = django_filters.CharFilter(field_name="course_format", lookup_expr="icontains")

    level = django_filters.BaseInFilter(field_name="level_id", lookup_expr="in")

    direction = django_filters.CharFilter(field_name="direction", lookup_expr="icontains")

    class Meta:
        model = Course
        fields = (
            "level",
            "course_format",
            "direction",
        )
