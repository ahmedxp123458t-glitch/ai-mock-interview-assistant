import os
import json
import json
from openai import OpenAI


client = None


def get_client():
    global client
    if client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
    global client
    if client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        client = OpenAI(api_key=api_key)
    return client


def generate_feedback(question: str, answer: str, job_role: str) -> dict:
    client = get_client()

    prompt = f"""You are an expert interview coach evaluating a candidate for a {job_role} position.

Question: {question}
Candidate's Answer: {answer}

Provide a detailed evaluation in JSON format with these fields:
1. "feedback": A 2-3 sentence overall feedback on the answer
2. "confidence_score": A number from 0.0 to 1.0 indicating how confident the answer sounds
3. "strengths": A list of 2-3 specific strengths of this answer
4. "weaknesses": A list of 1-3 specific areas for improvement
5. "suggestions": A list of 2-3 actionable suggestions to improve the answer
6. "rating": One word - "Excellent", "Good", "Average", "Fair", or "Poor"

Return ONLY valid JSON, no other text."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert interview coach. You only respond with valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1000,
        )

        content = response.choices[0].message.content.strip()
        content = content.replace("```json", "").replace("```", "").strip()
        result = json.loads(content)

        return {
            "feedback": result.get("feedback", "No feedback generated."),
            "confidence_score": min(max(float(result.get("confidence_score", 0.5)), 0.0), 1.0),
            "strengths": result.get("strengths", []),
            "weaknesses": result.get("weaknesses", []),
            "suggestions": result.get("suggestions", []),
            "rating": result.get("rating", "Average"),
        }

    except json.JSONDecodeError:
        return {
            "feedback": "Could not parse AI feedback. Please try again.",
            "confidence_score": 0.5,
            "strengths": [],
            "weaknesses": ["Unable to analyze fully"],
            "suggestions": ["Please rephrase and resubmit your answer"],
            "rating": "Average",
        }
    except Exception as e:
        raise RuntimeError(f"OpenAI API error: {str(e)}")


def generate_interview_questions(job_role: str, resume_text: str = "") -> list:
    client = get_client()

    resume_context = f"\nBased on this resume:\n{resume_text[:2000]}" if resume_text else ""

    prompt = f"""Generate 5 technical and behavioral interview questions for a {job_role} position.{resume_context}

Return ONLY a JSON array of strings, no other text."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You only respond with valid JSON arrays.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1000,
        )

        content = response.choices[0].message.content.strip()
        content = content.replace("```json", "").replace("```", "").strip()
        questions = json.loads(content)

        if isinstance(questions, list) and len(questions) > 0:
            return questions[:10]
        return _get_default_questions(job_role)

    except Exception:
        return _get_default_questions(job_role)


def _get_default_questions(job_role: str) -> list:
    return [
        f"Tell me about yourself and why you are interested in the {job_role} role.",
        f"What are your greatest strengths relevant to this {job_role} position?",
        f"Describe a challenging project you worked on and how you handled it.",
        f"Where do you see yourself in 5 years as a {job_role} professional?",
        f"Why should we hire you for this {job_role} position?",
    ]


def extract_resume_text(file_content: bytes) -> str:
    try:
        text = file_content.decode("utf-8", errors="ignore")
        return text.strip()[:5000]
    except Exception:
        return ""


def generate_questions_from_resume(job_role: str, resume_text: str) -> list:
    if not resume_text:
        return _get_default_questions(job_role)
    return generate_interview_questions(job_role, resume_text)
