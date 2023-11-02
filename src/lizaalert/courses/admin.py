from django.contrib import admin

from lizaalert.courses.models import (
    FAQ,
    Chapter,
    ChapterProgressStatus,
    Course,
    CourseFaq,
    CourseKnowledge,
    CourseProgressStatus,
    Knowledge,
    Lesson,
    LessonProgressStatus,
    Subscription,
)
from lizaalert.courses.utils import HideOrderNumberMixin


class CourseFaqInline(admin.TabularInline):
    """Таблица отношений Course - FAQ."""

    model = CourseFaq
    min_num = 0
    extra = 0


class CourseKnowledgeInline(admin.TabularInline):
    """Таблица отношений Course - Knowledge."""

    model = CourseKnowledge
    min_num = 0
    extra = 0


class LessonInline(HideOrderNumberMixin, admin.StackedInline):
    """Инлайн урока для отображения в главе."""

    model = Lesson
    min_num = 1
    extra = 0

    def get_fields(self, request, obj=None):
        """Убираем поле order_number при создании Главы с уроками, оставляем при редактировании."""
        fields = super().get_fields(request, obj)
        if obj:
            return fields
        return [field for field in fields if field != "order_number"]


class ChapterInline(HideOrderNumberMixin, admin.TabularInline):
    """Инлайн главы для отображения в курсе."""

    model = Chapter
    min_num = 1
    extra = 0

    def get_fields(self, request, obj=None):
        """Убираем поле order_number при создании Курса с главами, оставляем при редактировании."""
        fields = super().get_fields(request, obj)
        if obj:
            return fields
        return [field for field in fields if field != "order_number"]


class CourseAdmin(admin.ModelAdmin):
    """Админка курса."""

    inlines = (CourseFaqInline, CourseKnowledgeInline, ChapterInline)
    model = Course
    list_display = (
        "title",
        "course_format",
        "short_description",
        "user_created",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)
    empty_value_display = "-пусто-"


@admin.register(Chapter)
class ChapterAdmin(HideOrderNumberMixin, admin.ModelAdmin):
    """Админка главы."""

    inlines = (LessonInline,)
    ordering = ("-order_number",)


@admin.register(LessonProgressStatus)
class LessonProgressStatusAdmin(admin.ModelAdmin):
    pass


@admin.register(ChapterProgressStatus)
class ChapterProgressStatusAdmin(admin.ModelAdmin):

    raw_id_fields = ("user",)


@admin.register(CourseProgressStatus)
class CourseProgressStatusAdmin(admin.ModelAdmin):

    raw_id_fields = ("user",)


@admin.register(FAQ)
class FaqAdmin(admin.ModelAdmin):
    """Админка для FAQ."""

    inlines = (CourseFaqInline,)


@admin.register(Knowledge)
class KnowledgeAdmin(admin.ModelAdmin):
    """Aдминка для Knowledge."""

    inlines = (CourseKnowledgeInline,)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin, HideOrderNumberMixin):
    """Админка для урока."""

    pass


admin.site.register(Course, CourseAdmin)
admin.site.register(Subscription)
