from django.contrib import admin

from lizaalert.courses.models import (
    FAQ,
    Chapter,
    ChapterProgressStatus,
    Course,
    CourseFaq,
    CourseKnowledge,
    CourseStatus,
    Knowledge,
    Lesson,
    LessonProgressStatus,
    Subscription,
)


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


class LessonInline(admin.StackedInline):
    """Инлайн урока для отображения в главе."""

    model = Lesson
    min_num = 1
    extra = 0


class ChapterInline(admin.TabularInline):
    """Инлайн главы для отображения в курсе."""

    model = Chapter
    min_num = 1
    extra = 0


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
class ChapterAdmin(admin.ModelAdmin):
    """Админка главы."""

    inlines = (LessonInline,)
    ordering = ("-order_number",)


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
admin.site.register(Subscription)
