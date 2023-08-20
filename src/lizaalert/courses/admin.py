from django.contrib import admin

from lizaalert.courses.models import (
    Chapter,
    ChapterLesson,
    ChapterProgressStatus,
    Course,
    CourseFaq,
    CourseKnowledge,
    CourseStatus,
    FAQ,
    Knowledge,
    Lesson,
    LessonProgressStatus
)


class ChapterLessonInline(admin.TabularInline):
    model = ChapterLesson
    min_num = 1
    extra = 0


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


class CourseAdmin(admin.ModelAdmin):
    inlines = (CourseFaqInline, CourseKnowledgeInline)
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
class ChapterAdmin(admin.ModelAdmin):
    inlines = (ChapterLessonInline,)
    ordering = ("-created_at",)


@admin.register(LessonProgressStatus)
class LessonProgressStatusAdmin(admin.ModelAdmin):
    pass


@admin.register(ChapterProgressStatus)
class ChapterProgressStatusAdmin(admin.ModelAdmin):
    pass


@admin.register(FAQ)
class FaqAdmin(admin.ModelAdmin):
    """Админка для FAQ."""

    inlines = (CourseFaqInline,)


@admin.register(Knowledge)
class KnowledgeAdmin(admin.ModelAdmin):
    """Aдминка для Knowledge."""

    inlines = (CourseKnowledgeInline,)


admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson)
admin.site.register(CourseStatus)
