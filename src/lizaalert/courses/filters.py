import django_filters
from django_filters import rest_framework as filters

from .models import Course


class CourseFilter(filters.FilterSet):
    """Кастомный фильтр для модели Course."""

    course_format = django_filters.CharFilter(field_name="course_format", lookup_expr="icontains")

    level = django_filters.CharFilter(field_name="level_id")

    class Meta:
        model = Course
        fields = (
            "level",
            "course_format",
        )
