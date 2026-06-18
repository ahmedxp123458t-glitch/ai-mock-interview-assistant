import os
import json
from openai import OpenAI

client = None

def get_client():
    global client
    if client is not None:
        return client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    client = OpenAI(api_key=api_key)
    return client

def generate_feedback(question: str, answer: str, job_role: str) -> dict:
    c = get_client()
    if c is None:
        return {"feedback": "OpenAI API key not configured. Set OPENAI_API_KEY in Vercel.", "confidence_score": 0.5, "strengths": [], "weaknesses": ["API key missing"], "suggestions": ["Add OPENAI_API_KEY to Vercel dashboard"], "rating": "Average"}
    try:
        response = c.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role":"system","content":"You only respond with valid JSON."},{"role":"user","content":f"Evaluate answer for {job_role}.\nQ: {question}\nA: {answer}\nReturn JSON with feedback, confidence_score(0-1), strengths, weaknesses, suggestions, rating(Excellent/Good/Average/Fair/Poor)."}], temperature=0.7, max_tokens=1000)
        content = response.choices[0].message.content.strip().replace("```json","").replace("```","").strip()
        result = json.loads(content)
        return {"feedback":result.get("feedback",""), "confidence_score":min(max(float(result.get("confidence_score",0.5)),0.0),1.0), "strengths":result.get("strengths",[]), "weaknesses":result.get("weaknesses",[]), "suggestions":result.get("suggestions",[]), "rating":result.get("rating","Average")}
    except Exception as e:
        return {"feedback":f"Error: {str(e)}","confidence_score":0.5,"strengths":[],"weaknesses":[],"suggestions":[],"rating":"Average"}

def generate_interview_questions(job_role: str, resume_text: str = "") -> list:
    c = get_client()
    if c is None:
        return [f"Tell me about yourself for {job_role}."]
    try:
        prompt = f"Generate 5 interview questions for {job_role}." + (f" Resume: {resume_text[:2000]}" if resume_text else "")
        response = c.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role":"system","content":"Return ONLY a JSON array of strings."},{"role":"user","content":prompt}], temperature=0.7, max_tokens=1000)
        content = response.choices[0].message.content.strip().replace("```json","").replace("```","").strip()
        qs = json.loads(content)
        return qs[:10] if isinstance(qs,list) and len(qs)>0 else [f"Describe your experience with {job_role}."]
    except Exception:
        return [f"Describe your experience with {job_role}."]

def extract_resume_text(file_content: bytes) -> str:
    try: return file_content.decode("utf-8",errors="ignore").strip()[:5000]
    except: return ""

def generate_questions_from_resume(job_role: str, resume_text: str) -> list:
    return generate_interview_questions(job_role, resume_text) if resume_text else [f"Tell me about yourself for {job_role}."]
