from django.urls import path

from .views import QuestionListView, QuizDetailView, RunQuizView

urlpatterns = [
    path("chapter/<int:chapter_id>/quiz/", QuizDetailView.as_view(), name="quiz"),
    path("chapter/<int:chapter_id>/quizz/questions/", QuestionListView.as_view(), name="questions"),
    path("chapter/<int:chapter_id>/quiz/run/", RunQuizView.as_view(), name="run-quiz"),
]
