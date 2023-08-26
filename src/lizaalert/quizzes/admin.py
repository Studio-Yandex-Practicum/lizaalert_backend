from django.contrib import admin

from .models import Question, Quiz


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "created_at", "deleted_at")
    search_fields = ("title",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("title", "quiz", "question_type", "order_number", "created_at", "deleted_at")
    list_filter = ("quiz",)
    search_fields = ("title",)
