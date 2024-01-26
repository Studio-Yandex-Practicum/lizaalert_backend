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
    ordering = ("-updated_at",)
    empty_value_display = "-пусто-"


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    """Админка главы."""

    inlines = (LessonInline,)
    ordering = ("-order_number",)
    raw_id_fields = (
        "user_created",
        "user_modifier",
        "course",
    )
    list_display = (
        "title",
        "course",
        "user_created",
        "created_at",
        "updated_at",
    )


@admin.register(LessonProgressStatus)
class LessonProgressStatusAdmin(admin.ModelAdmin):
    ordering = ("-updated_at",)
    list_display = (
        "lesson",
        "progress",
        "subscription",
        "created_at",
        "updated_at",
    )


@admin.register(ChapterProgressStatus)
class ChapterProgressStatusAdmin(admin.ModelAdmin):

    raw_id_fields = ("subscription",)
    ordering = ("-updated_at",)
    list_display = (
        "chapter",
        "progress",
        "subscription",
        "created_at",
        "updated_at",
    )


@admin.register(CourseProgressStatus)
class CourseProgressStatusAdmin(admin.ModelAdmin):

    raw_id_fields = ("subscription",)
    ordering = ("-updated_at",)
    list_display = (
        "course",
        "progress",
        "subscription",
        "created_at",
        "updated_at",
    )


@admin.register(FAQ)
class FaqAdmin(admin.ModelAdmin):
    """Админка для FAQ."""

    inlines = (CourseFaqInline,)
    ordering = ("-updated_at",)
    list_display = (
        "question",
        "author",
        "created_at",
        "updated_at",
    )


@admin.register(Knowledge)
class KnowledgeAdmin(admin.ModelAdmin):
    """Aдминка для Knowledge."""

    inlines = (CourseKnowledgeInline,)
    ordering = ("-updated_at",)
    list_display = (
        "title",
        "author",
        "created_at",
        "updated_at",
    )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Админка для урока."""

    raw_id_fields = (
        "user_created",
        "user_modifier",
        "chapter",
    )
    list_display = (
        "title",
        "chapter",
        "lesson_type",
        "user_created",
        "created_at",
        "updated_at",
    )

    ordering = ("-updated_at",)


admin.site.register(Course, CourseAdmin)
admin.site.register(Subscription)
