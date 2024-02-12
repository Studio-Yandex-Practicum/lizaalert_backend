from django.urls import path

from lizaalert.homeworks.views import HomeworkViewSet, HomeworkDetailViewSet

urlpatterns = [
    path("homeworks/", HomeworkViewSet.as_view(), name="homework"),
    path("lessons/<int:lesson_id>/homework/", HomeworkDetailViewSet.as_view(), name="homework-detail"),
    # path("lessons/<int:lesson_id>/quiz/run/", RunQuizView.as_view(), name="run-quiz"),
    # path("lessons/<int:lesson_id>/quiz/answer/", QuizDetailAnswerView.as_view(), name="quiz-answer"),
]
