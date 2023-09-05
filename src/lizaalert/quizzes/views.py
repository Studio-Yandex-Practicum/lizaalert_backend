from datetime import datetime

from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from lizaalert.courses.models import Lesson
from lizaalert.quizzes.models import Question, Quiz, UserAnswer
from lizaalert.quizzes.serializers import QuizWithQuestionsSerializer, UserAnswerSerializer


class QuizDetailView(generics.RetrieveAPIView):
    serializer_class = QuizWithQuestionsSerializer

    def get_object(self):
        lesson_id = self.kwargs["lesson_id"]
        lesson = Lesson.objects.get(pk=lesson_id)
        return lesson.quiz

    def get_queryset(self):
        lesson_id = self.kwargs["lesson_id"]
        return Question.objects.filter(quiz__lesson_id=lesson_id)


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
        lesson_id = self.kwargs["lesson_id"]
        user = self.request.user
        quiz = Quiz.objects.get(lesson__id=lesson_id)
        existing_answer = UserAnswer.objects.filter(user=user, quiz=quiz).first()

        if existing_answer:
            existing_answer.start_time = datetime.now().time()
            existing_answer.save()
            serializer = self.get_serializer(existing_answer)
            return Response(serializer.data, status=status.HTTP_200_OK)

        start_time = datetime.now().time()

        data = {"user": user.id, "quiz": quiz.id, "start_time": start_time}

        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
