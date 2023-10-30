from datetime import datetime

from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response

from lizaalert.courses.models import Lesson
from lizaalert.quizzes.models import Question, Quiz, UserAnswer
from lizaalert.quizzes.serializers import QuizWithQuestionsSerializer, UserAnswerSerializer
from lizaalert.quizzes.utils import compare_answers


class QuizException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST


class TestNotStartedException(QuizException):
    default_detail = "Тест еще не начат."


class TimeExpiredException(QuizException):
    default_detail = "Время вышло. Вы не успели."


class CountExpiredException(QuizException):
    default_detail = "Закончилось количество попыток."


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

    Создает новую запись UserAnswer для каждого запроса.

    Возвращает:
    - 201 Created, всегда создается новая запись UserAnswer.
    """

    serializer_class = UserAnswerSerializer

    def create(self, request, *args, **kwargs):
        lesson_id = self.kwargs["lesson_id"]
        user = self.request.user
        quiz = Quiz.objects.get(lesson__id=lesson_id)
        user_answer = UserAnswer.objects.filter(user=user, quiz=quiz).order_by("-id").first()
        retry_count = 0
        if user_answer:
            try:
                if quiz.retries != 0 and user_answer.retry_count >= quiz.retries:
                    raise CountExpiredException("Попытки закончились")
            except CountExpiredException as e:
                return Response({"message": e.detail}, status=e.status_code)
            retry_count = user_answer.retry_count = user_answer.retry_count + 1
        else:
            if quiz.retries != 0:
                retry_count = 1

        start_date = datetime.now()

        data = {"user": user.id, "quiz": quiz.id, "start_date": start_date, "retry_count": retry_count}

        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class QuizDetailAnswerView(generics.CreateAPIView, generics.RetrieveAPIView):
    """
    Создает и обновляет запись UserAnswer для ответов пользователя на квиз.

    При GET-запросе возвращает информацию о текущем UserAnswer пользователя для данного квиза.

    При POST-запросе обновляет ответы пользователя и вычисляет результаты теста.
    """

    serializer_class = UserAnswerSerializer

    def get_object(self):
        user = self.request.user
        lesson_id = self.kwargs["lesson_id"]
        user_answer = (
            UserAnswer.objects.filter(user=user, quiz_id__in=Lesson.objects.filter(id=lesson_id).values("quiz_id"))
            .order_by("-id")
            .first()
        )
        return user_answer

    def post(self, request, *args, **kwargs):
        data = request.data

        user = self.request.user

        lesson_id = self.kwargs["lesson_id"]
        quiz = Quiz.objects.get(lesson=lesson_id)

        try:
            user_answer = (
                UserAnswer.objects.filter(user=user, quiz_id__in=Lesson.objects.filter(id=lesson_id).values("quiz_id"))
                .order_by("-id")
                .first()
            )
            user_answer.end_date = timezone.now()
            solution_time = user_answer.end_date - user_answer.start_date
            solution_time_minutes = solution_time.total_seconds() / 60

            try:
                if solution_time_minutes > quiz.duration_minutes:
                    raise TimeExpiredException("Время истекло")
            except TimeExpiredException as e:
                return Response({"message": e.detail}, status=e.status_code)

            serializer = UserAnswerSerializer(user_answer, data={"answers": data}, partial=True)
            if serializer.is_valid():
                user_answer.result, user_answer.score = compare_answers(data, quiz)
            if quiz.passing_score > user_answer.score:
                user_answer.final_result = False
            else:
                user_answer.final_result = True
        except TestNotStartedException as e:
            return Response({"message": e.detail}, status=e.status_code)
        serializer = UserAnswerSerializer(user_answer, data={"answers": data}, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
