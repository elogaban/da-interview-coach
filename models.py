from pydantic import BaseModel
from typing import List, Optional

class InterviewQuestion(BaseModel):
    question: str
    category: str
    difficulty: str
    company_context: Optional[str] = None
    perfect_answer: str 
    explanation_child: str 

class QuestionList(BaseModel):
    questions: List[InterviewQuestion]