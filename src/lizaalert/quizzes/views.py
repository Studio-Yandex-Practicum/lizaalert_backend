from datetime import datetime

from courses.models import Chapter
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Question, Quiz, UserAnswer
from .serializers import QuestionSerializer, QuizSerializer, UserAnswerSerializer


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


class RunQuizView(generics.CreateAPIView):
    """
    Обрабатывает начало прохождения квиза для пользователя.
    
    Если запись UserAnswer для того же пользователя и квиза уже существует,
    обновляется время в поле start_time. Если нет, создается новая запись UserAnswer.

    Возвращает:
    - 200 OK, если существующая запись UserAnswer была обновлена.
    - 201 Created, если создана новая запись UserAnswer.
    """

    serializer_class = UserAnswerSerializer

    def create(self, request, *args, **kwargs):
        chapter_id = self.kwargs["chapter_id"]
        user = self.request.user
        quiz = Quiz.objects.get(chapter__id=chapter_id)
        existing_answer = UserAnswer.objects.filter(user=user, quiz=quiz).first()

        if existing_answer:
            existing_answer.start_time = datetime.now().time()
            existing_answer.save()
            serializer = self.get_serializer(existing_answer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            start_time = datetime.now().time()

            data = {"user": user.id, "quiz": quiz.id, "start_time": start_time}

            serializer = self.get_serializer(data=data)
            try:
                serializer.is_valid(raise_exception=True)
            except ValidationError as e:
                return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
