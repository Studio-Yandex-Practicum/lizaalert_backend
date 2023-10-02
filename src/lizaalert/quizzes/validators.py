from typing import List, Optional

from pydantic import BaseModel


class ContentAnswerModel(BaseModel):
    id: int
    text: str
    is_correct: bool


class ValidateAnswersModel(BaseModel):
    content: Optional[List[ContentAnswerModel]]

    class Config:
        from_attributes = True


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
        from_attributes = True
