from typing import Any, Dict, List, Tuple

from django.shortcuts import get_list_or_404

from lizaalert.quizzes.models import Question, Quiz


def compare_answers(
    user_answers: List[Dict[str, Any]], quiz: Quiz
) -> Tuple[List[Dict[str, int | List[int] | bool]], int]:
    """
    Сравнивает ответы пользователя на вопросы с правильными ответами для теста.

    :param user_answers: Список словарей с ответами пользователя. Каждый словарь содержит
                        "question_id" (идентификатор вопроса)
                        и "answer_id" (список идентификаторов ответов пользователя).
    :param quiz: Тест, для которого проводится сравнение ответов.

    :return: Кортеж, содержащий список словарей с информацией о каждом вопросе и количеством правильных ответов.
             Каждый словарь содержит "question_id" (идентификатор вопроса), "correct_answer_id" (список идентификаторов
             правильных ответов) и "is_correct" (булево значение, показывающее, правильные ли ответы пользователя).
             Второй элемент кортежа - количество правильных ответов.
    """
    correct_count = 0
    all_questions = {q.id: q for q in get_list_or_404(Question, quiz=quiz)}
    result = []

    for user_answer in user_answers:
        question_id = user_answer["question_id"]
        user_answer_ids = user_answer["answer_id"]

        question = all_questions.get(question_id)
        if question:
            if question.question_type in ["checkbox", "radio"]:
                correct_answer_ids = [answer["id"] for answer in question.content if answer["is_correct"]]
                is_correct = sorted(user_answer_ids) == sorted(correct_answer_ids)

                if is_correct:
                    correct_count += 1

                result.append(
                    {"question_id": question_id, "correct_answer_id": correct_answer_ids, "is_correct": is_correct}
                )
        else:
            result.append({"question_id": question_id, "correct_answer_id": [], "is_correct": False})

    return result, correct_count
