from django.urls import path

from lizaalert.quizzes.views import QuizDetailAnswerView, QuizDetailView, RunQuizView

urlpatterns = [
    path("lessons/<int:lesson_id>/quiz/", QuizDetailView.as_view(), name="quiz"),
    path("lessons/<int:lesson_id>/quiz/run/", RunQuizView.as_view(), name="run-quiz"),
    path("lessons/<int:lesson_id>/quiz/answer/", QuizDetailAnswerView.as_view(), name="quiz-answer"),
]
