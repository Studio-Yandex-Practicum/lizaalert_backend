from django.contrib import admin

from .models import Course, Chapter, Lesson, ChapterLesson, CourseStatus


class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "format",
        "short_description",
        "user_created",
        "created_at",
        "updated_at",
    )
    empty_value_display = "-пусто-"


class ChapterLessonInline(admin.TabularInline):
    model = ChapterLesson
    min_num = 1
    extra = 0


@admin.register(Chapter)
class ChapterLessonAdmin(admin.ModelAdmin):
    inlines = (ChapterLessonInline,)
    ordering = ('-created_at',)


admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson)
admin.site.register(CourseStatus)
