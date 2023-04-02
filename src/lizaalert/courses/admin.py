from django.contrib import admin

from lizaalert.courses.models import (
    Chapter,
    ChapterLesson,
    ChapterProgressStatus,
    Course,
    CourseStatus,
    Lesson,
    LessonProgressStatus,
)


class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "course_format",
        "short_description",
        "faq",
        "user_created",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)
    empty_value_display = "-пусто-"


class ChapterLessonInline(admin.TabularInline):
    model = ChapterLesson
    min_num = 1
    extra = 0


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


admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson)
admin.site.register(CourseStatus)
