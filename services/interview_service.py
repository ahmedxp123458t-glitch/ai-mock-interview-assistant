import uuid
from datetime import datetime
from services.feedback_service import (
    generate_feedback,
    generate_questions_from_resume,
    extract_resume_text,
)
from services.voice_service import speech_to_text, validate_audio
from database import (
    save_interview,
    save_question_answer,
    get_interview_history as db_get_history,
    get_interview_detail as db_get_detail,
    get_all_analytics,
)


def start_interview(job_role: str, resume_text: str = ""):
    interview_id = str(uuid.uuid4())
    questions = generate_questions_from_resume(job_role, resume_text)
    save_interview(interview_id, job_role, resume_text)

    return {
        "interview_id": interview_id,
        "job_role": job_role,
        "questions": questions,
        "total_questions": len(questions),
        "started_at": datetime.now().isoformat(),
    }


def process_answer(
    interview_id: str,
    question: str,
    answer_text: str = None,
    audio_data: str = None,
):
    if audio_data:
        if not validate_audio(audio_data):
            raise ValueError("Invalid audio data provided")
        answer_text = speech_to_text(audio_data)
    elif not answer_text:
        raise ValueError("Either answer_text or audio_data must be provided")

    job_role = _get_job_role(interview_id)
    feedback_data = generate_feedback(question, answer_text, job_role)

    save_question_answer(
        interview_id=interview_id,
        question=question,
        answer=answer_text,
        feedback=feedback_data["feedback"],
        confidence_score=feedback_data["confidence_score"],
        strengths=feedback_data["strengths"],
        weaknesses=feedback_data["weaknesses"],
        suggestions=feedback_data["suggestions"],
        rating=feedback_data["rating"],
    )

    return {
        "interview_id": interview_id,
        "question": question,
        "answer": answer_text,
        "feedback": feedback_data["feedback"],
        "confidence_score": feedback_data["confidence_score"],
        "strengths": feedback_data["strengths"],
        "weaknesses": feedback_data["weaknesses"],
        "suggestions": feedback_data["suggestions"],
        "rating": feedback_data["rating"],
    }


def get_interview_history():
    return db_get_history()


def get_interview_detail(interview_id: str):
    return db_get_detail(interview_id)


def get_analytics():
    return get_all_analytics()


def process_resume(file_content: bytes, job_role: str):
    text = extract_resume_text(file_content)
    questions = generate_questions_from_resume(job_role, text)
    return {"filename": "resume.txt", "text": text, "questions": questions}


def _get_job_role(interview_id: str):
    detail = db_get_detail(interview_id)
    if detail:
        return detail["job_role"]
    return "General"
