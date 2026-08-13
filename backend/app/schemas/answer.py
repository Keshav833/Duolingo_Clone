# backend/app/schemas/answer.py

from typing import Union, List, Dict
from pydantic import BaseModel, ConfigDict


class AnswerSubmitRequest(BaseModel):
    """
    submitted_answer shape depends on exercise type — this mirrors the
    correct_answer envelope design from models.py:

      multiple_choice / type_answer / fill_blank -> str
      translate                                  -> List[str]
      match_pairs                                -> Dict[str, str]

    Pydantic v2 will try each type in the Union in order and use whichever
    matches, so the frontend just sends whatever shape fits the exercise
    it's rendering.
    """
    exercise_id: int
    submitted_answer: Union[str, List[str], Dict[str, str]]


class AnswerSubmitResponse(BaseModel):
    correct: bool
    hearts: int
    correct_answer: Union[str, List[str], Dict[str, str]]

    model_config = ConfigDict(from_attributes=True)