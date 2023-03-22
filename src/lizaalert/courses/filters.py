import django_filters
from django_filters import rest_framework as filters

from .models import Course


class CourseFilter(filters.FilterSet):
    """Кастомный фильтр для модели Course."""
    format = django_filters.CharFilter(
        field_name="format",
        lookup_expr="icontains"
    )

    level = django_filters.CharFilter(
        field_name="level__name",
        lookup_expr="icontains"
    )

    class Meta:
        model = Course
        fields = ("level", "format",)