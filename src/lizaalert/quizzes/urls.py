from django.urls import path

from .views import QuestionListView, QuizDetailView

urlpatterns = [
    path("chapter/<int:chapter_id>/quiz/", QuizDetailView.as_view(), name="quiz"),
    path("chapter/<int:chapter_id>/quizzes/questions/", QuestionListView.as_view(), name="questions"),
]
