import json

from django import forms
from django.contrib import admin
from pydantic import ValidationError as PydanticValidationError

from lizaalert.quizzes.models import Question, Quiz, UserAnswer
from lizaalert.quizzes.validators import ValidateAnswersModel
from lizaalert.settings.admin_setup import BaseAdmin


class QuestionAdminForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = "__all__"

    def clean_content(self):
        content = self.cleaned_data["content"]
        data = {"content": content}
        try:
            validated_content = ValidateAnswersModel(**data)
            return json.loads(validated_content.json())["content"]
        except PydanticValidationError as e:
            raise forms.ValidationError(str(e.errors()))


@admin.register(Quiz)
class QuizAdmin(BaseAdmin):
    list_display = ("id", "title", "created_at", "deleted_at")
    search_fields = ("title",)


@admin.register(Question)
class QuestionAdmin(BaseAdmin):
    form = QuestionAdminForm
    list_display = ("id", "title", "quiz", "question_type", "order_number", "created_at", "deleted_at")
    list_filter = ("quiz",)
    search_fields = ("title",)


@admin.register(UserAnswer)
class UserAnswerAdmin(BaseAdmin):
    list_display = ("id", "user", "quiz")
    readonly_fields = ("user", "quiz")
    search_fields = ("user__username", "quiz__title")
