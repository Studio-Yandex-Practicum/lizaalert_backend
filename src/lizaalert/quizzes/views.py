from courses.models import Chapter
from rest_framework import generics

from .models import Question
from .serializers import QuestionSerializer, QuizSerializer


class QuizDetailView(generics.RetrieveAPIView):
    serializer_class = QuizSerializer

    def get_object(self):
        chapter_id = self.kwargs["chapter_id"]
        chapter = Chapter.objects.get(pk=chapter_id)
        return chapter.quiz


class QuestionListView(generics.ListAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        chapter_id = self.kwargs["chapter_id"]
        return Question.objects.filter(quiz__chapter_id=chapter_id)
