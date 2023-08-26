from courses.models import Chapter
from rest_framework import generics

from .serializers import QuizSerializer


class QuizDetailView(generics.RetrieveAPIView):
    serializer_class = QuizSerializer

    def get_object(self):
        chapter_id = self.kwargs['chapter_id']
        chapter = Chapter.objects.get(pk=chapter_id)
        return chapter.quiz
