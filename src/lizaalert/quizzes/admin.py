from django.contrib import admin

from .models import Question, Quiz, UserAnswer


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_at", "deleted_at")
    search_fields = ("title",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "quiz", "question_type", "order_number", "created_at", "deleted_at")
    list_filter = ("quiz",)
    search_fields = ("title",)


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "quiz")
    readonly_fields = ("user", "quiz")
    search_fields = ("user__username", "quiz__title")
