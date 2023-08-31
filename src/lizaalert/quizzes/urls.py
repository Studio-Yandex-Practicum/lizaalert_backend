from django.urls import path

from .views import QuizDetailView, RunQuizView

urlpatterns = [
    path("lesson/<int:lesson_id>/quiz/", QuizDetailView.as_view(), name="quiz"),
    path("lesson/<int:lesson_id>/quiz/run/", RunQuizView.as_view(), name="run-quiz"),
]
