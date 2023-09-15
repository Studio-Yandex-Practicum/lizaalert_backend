from typing import List, Optional

from pydantic import BaseModel


class ContextModel(BaseModel):
    id: int
    text: str
    isCorrect: bool


class ValidateAnswersModel(BaseModel):
    context: Optional[List[ContextModel]]

    class Config:
        orm_mode = True


class AnswerModel(BaseModel):
    question_id: int
    answer_id: List[int]


class AnswerCheckModel(BaseModel):
    question_id: int
    answer_id: List[int]
    is_correct: bool


class ValidateIUserAnswersModel(BaseModel):
    answers: Optional[List[AnswerModel]]
    result: Optional[List[AnswerCheckModel]]

    class Config:
        orm_mode = True
