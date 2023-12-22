from django.contrib import admin

from lizaalert.courses.models import (
    FAQ,
    Chapter,
    ChapterProgressStatus,
    Cohort,
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


class CohortInline(admin.TabularInline):
    model = Cohort
    extra = 1
    readonly_fields = ["cohort_number_display"]

    def cohort_number_display(self, instance):
        return f"{instance.course.title} - Группа {instance.cohort_number}"

    cohort_number_display.short_description = "Группа"
    cohort_number_display.admin_order_field = "cohort_number"


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
    raw_id_fields = (
        "user_created",
        "user_modifier",
        "course",
    )


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
class LessonAdmin(admin.ModelAdmin):
    """Админка для урока."""

    raw_id_fields = (
        "user_created",
        "user_modifier",
        "chapter",
    )


admin.site.register(Course, CourseAdmin)
admin.site.register(Subscription)
admin.site.register(Cohort)
