from django.contrib import admin
from django.db.models import F
from django.urls import reverse
from django.utils.html import format_html

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
    readonly_fields = ("get_chapter_link",)
    fields = (
        "get_chapter_link",
        "order_number",
        "title",
        "deleted_at",
    )

    # Метод для отображения ссылки на главу курса
    def get_chapter_link(self, obj):
        url = reverse("admin:courses_chapter_change", args=(obj.id,))
        return format_html('<a href="{}">{}</a>', url, obj.title)

    get_chapter_link.short_description = "Глава"


@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    """
    Админка когорты.

    При созданиии объекта исключается поле cohort_number.
    """

    model = Cohort
    extra = 1
    list_display = (
        "course_title",
        "start_date",
        "end_date",
        "teacher",
        "created_at",
        "updated_at",
    )
    list_select_related = ("course__title",)
    ordering = ("-updated_at",)

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related("course").annotate(course_title=F("course__title"))
        return qs

    def course_title(self, obj):
        return obj.course_title

    course_title.short_description = "Курс"


@admin.register(Course)
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
        "subscribed_user",
        "lesson",
        "progress",
        "subscription",
        "created_at",
        "updated_at",
    )
    list_display_links = [
        "subscription",
        "lesson",
        "progress",
        "subscribed_user",
    ]

    list_select_related = ["subscription__user"]

    @admin.display(description="Студент")
    def subscribed_user(self, obj):
        return obj.subscription.user


@admin.register(ChapterProgressStatus)
class ChapterProgressStatusAdmin(admin.ModelAdmin):
    raw_id_fields = ("user",)

    raw_id_fields = ("subscription",)
    ordering = ("-updated_at",)
    list_display = (
        "subscribed_user",
        "chapter",
        "progress",
        "subscription",
        "created_at",
        "updated_at",
    )
    list_display_links = [
        "subscription",
        "chapter",
        "progress",
        "subscribed_user",
    ]

    list_select_related = ["subscription__user"]

    @admin.display(description="Студент")
    def subscribed_user(self, obj):
        return obj.subscription.user


@admin.register(CourseProgressStatus)
class CourseProgressStatusAdmin(admin.ModelAdmin):
    raw_id_fields = ("user",)

    raw_id_fields = ("subscription",)
    ordering = ("-updated_at",)
    list_display = (
        "subscribed_user",
        "course",
        "progress",
        "subscription",
        "created_at",
        "updated_at",
    )
    list_display_links = [
        "subscription",
        "course",
        "progress",
        "subscribed_user",
    ]
    list_select_related = ["subscription__user"]

    @admin.display(description="Студент")
    def subscribed_user(self, obj):
        return obj.subscription.user


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


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Админка подписки."""

    raw_id_fields = ("user", "course")
    list_display = (
        "__str__",
        "user",
        "course",
        "status",
        "created_at",
        "updated_at",
    )
    list_display_links = [
        "__str__",
        "user",
        "course",
        "status",
    ]

    ordering = ("-updated_at",)
