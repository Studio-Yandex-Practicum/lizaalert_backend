from django.urls import path

from .views import QuizDetailView

urlpatterns = [
    path('chapter/<int:chapter_id>/quizzes/', QuizDetailView.as_view(), name='chapter-quizzes'),
]
