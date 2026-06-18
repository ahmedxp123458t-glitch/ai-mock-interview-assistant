import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from models import (
    InterviewStartRequest,
    AnswerRequest,
    FeedbackResponse,
    InterviewHistoryItem,
    InterviewDetail,
    AnalyticsResponse,
    ResumeUploadResponse,
)
from services.interview_service import (
    start_interview,
    process_answer,
    get_interview_history,
    get_interview_detail,
    get_analytics,
    process_resume,
)
from database import init_db

load_dotenv()

app = FastAPI(title="AI Mock Interview Assistant")

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.on_event("startup")
def startup():
    init_db()


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/interview/start")
def api_start_interview(req: InterviewStartRequest):
    try:
        result = start_interview(req.job_role, req.resume_text or "")
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/interview/answer", response_model=dict)
def api_answer_question(req: AnswerRequest):
    try:
        result = process_answer(
            interview_id=req.interview_id,
            question=req.question,
            answer_text=req.answer_text,
            audio_data=req.audio_data,
        )
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/interview/history")
def api_interview_history():
    try:
        history = get_interview_history()
        return {"success": True, "data": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/interview/detail/{interview_id}")
def api_interview_detail(interview_id: str):
    try:
        detail = get_interview_detail(interview_id)
        if not detail:
            raise HTTPException(status_code=404, detail="Interview not found")
        return {"success": True, "data": detail}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/interview/analytics")
def api_analytics():
    try:
        analytics = get_analytics()
        return {"success": True, "data": analytics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/resume/upload")
async def api_upload_resume(file: UploadFile = File(...), job_role: str = Form(...)):
    try:
        content = await file.read()
        result = process_resume(content, job_role)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
