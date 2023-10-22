from django.shortcuts import get_list_or_404

from lizaalert.quizzes.models import Question


def compare_answers(user_answers, quiz):
    correct_count = 0
    all_questions = {q.id: q for q in get_list_or_404(Question, quiz=quiz)}
    result = []

    for user_answer in user_answers:
        question_id = user_answer["question_id"]
        user_answer_ids = user_answer["answer_id"]

        question = all_questions.get(question_id)

        if question:
            correct_answer_ids = [answer["id"] for answer in question.content if answer["is_correct"]]
            is_correct = sorted(user_answer_ids) == sorted(correct_answer_ids)

            if is_correct:
                correct_count += 1

            result.append(
                {"question_id": question_id, "correct_answer_id": correct_answer_ids, "is_correct": is_correct}
            )

    return result, correct_count
