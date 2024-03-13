from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from lizaalert.courses.forms import CohortForm
from lizaalert.courses.models import (
    FAQ,
    Chapter,
    ChapterProgressStatus,
    Cohort,
    Course,
    CourseFaq,
    CourseKnowledge,
    CourseProgressStatus,
    Division,
    Knowledge,
    Lesson,
    LessonProgressStatus,
    Subscription,
)
from lizaalert.settings.admin_setup import BaseAdmin


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
        "title",
    )

    # Метод для отображения ссылки на главу курса
    def get_chapter_link(self, obj):
        title = obj.title or "Нет названия"
        if not (id := obj.id):
            return format_html("<span>{}</span>", title)
        return format_html('<a href="{}">{}</a>', reverse("admin:courses_chapter_change", args=(id,)), title)

    get_chapter_link.short_description = "Глава"


class DivisionInline(admin.StackedInline):
    """Инлайн направления для отображения в главе."""

    model = Division
    min_num = 1
    extra = 0


@admin.register(Cohort)
class CohortAdmin(BaseAdmin):
    """
    Админка когорты.

    При созданиии объекта исключается поле cohort_number.
    """

    model = Cohort
    extra = 1
    form = CohortForm
    list_display = (
        "course_title",
        "start_date",
        "end_date",
        "teacher",
        "created_at",
        "updated_at",
    )
    list_select_related = ("course",)
    ordering = ("-updated_at",)
    readonly_fields = ("cohort_number", "students_count")
    raw_id_fields = ("teacher",)

    def course_title(self, obj):
        return obj.course.title

    course_title.short_description = "Курс"


@admin.register(Course)
class CourseAdmin(BaseAdmin):
    """Админка курса."""

    inlines = (CourseFaqInline, CourseKnowledgeInline, ChapterInline)
    list_filter = [
        "division",
    ]
    model = Course
    list_display = (
        "title",
        "course_format",
        "short_description",
        "user_created",
        "created_at",
        "updated_at",
        "division",
    )
    ordering = ("-updated_at",)
    empty_value_display = "-пусто-"

    # Автоматическое заполнение полей user_created и user_modifier для главы
    def save_formset(self, request, form, formset, change):
        if formset.model == Chapter:
            chapters = formset.save(commit=False)
            for chapter in chapters:
                if not chapter.id:
                    chapter.user_created = request.user
                chapter.user_modifier = request.user
                chapter.save()
            formset.save_m2m()
        else:
            super().save_formset(request, form, formset, change)


@admin.register(Chapter)
class ChapterAdmin(BaseAdmin):
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
class LessonProgressStatusAdmin(BaseAdmin):
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
class ChapterProgressStatusAdmin(BaseAdmin):

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
class CourseProgressStatusAdmin(BaseAdmin):

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
class FaqAdmin(BaseAdmin):
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
class KnowledgeAdmin(BaseAdmin):
    """Aдминка для Knowledge."""

    inlines = (CourseKnowledgeInline,)
    ordering = ("-updated_at",)
    list_display = ("title", "author", "created_at", "updated_at")


@admin.register(Lesson)
class LessonAdmin(BaseAdmin):
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
class SubscriptionAdmin(BaseAdmin):
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


@admin.register(Division)
class DivisionAdmin(BaseAdmin):
    """Aдминка для Division."""

    ordering = ("-updated_at",)
    list_display = ("title", "author", "updated_at", "courses")
    exclude = ("author",)
    list_select_related = ("author",)

    @admin.display(description="Курсы")
    def courses(self, obj):
        """Показывает курсы по этим направлениям."""
        return [[course.title] for course in obj.course_set.all()]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("course_set")

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        obj.save()
