from django.contrib import admin

from .models import Course, Chapter, Lesson


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


admin.site.register(Course, CourseAdmin)
admin.site.register(Chapter)
admin.site.register(Lesson)
