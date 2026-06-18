from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class InterviewStartRequest(BaseModel):
    job_role: str
    resume_text: Optional[str] = None


class AnswerRequest(BaseModel):
    interview_id: str
    question: str
    answer_text: Optional[str] = None
    audio_data: Optional[str] = None


class FeedbackResponse(BaseModel):
    interview_id: str
    question: str
    answer: str
    feedback: str
    confidence_score: float
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    rating: str


class InterviewHistoryItem(BaseModel):
    id: str
    job_role: str
    date: str
    total_questions: int
    avg_confidence: float
    overall_rating: str


class InterviewDetail(BaseModel):
    id: str
    job_role: str
    date: str
    questions: List[dict]
    avg_confidence: float
    overall_rating: str


class AnalyticsResponse(BaseModel):
    total_interviews: int
    total_questions: int
    avg_confidence: float
    avg_rating: str
    rating_distribution: dict
    confidence_trend: List[dict]
    role_performance: List[dict]
    recent_scores: List[dict]


class ResumeUploadResponse(BaseModel):
    filename: str
    text: str
    questions: List[str]
