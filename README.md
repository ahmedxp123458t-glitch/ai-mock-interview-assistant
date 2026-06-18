# AI Mock Interview Assistant

An intelligent interview preparation tool that uses AI to simulate real interviews, analyze answers, and provide feedback with confidence scoring.

## Features

- **Voice-to-Text** - Record answers using your microphone, automatically converted to text
- **AI-Powered Feedback** - Get detailed analysis of your answers from OpenAI
- **Confidence Score** - Receive a numerical confidence score for each answer
- **Interview History** - Track all past interviews and review progress
- **Performance Analytics** - Visual insights into your performance over time
- **Resume-Based Questions** - Upload your resume to get personalized questions

## Tech Stack

- **Backend:** Python, FastAPI
- **AI:** OpenAI GPT API
- **Voice:** SpeechRecognition
- **Frontend:** HTML, CSS, JavaScript (Jinja2 templates)
- **Database:** SQLite

## Project Structure

```
ai-mock-interview-assistant/
├── app.py                         # FastAPI main application
├── models.py                      # Pydantic data models
├── database.py                    # SQLite database setup
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── .gitignore
├── services/
│   ├── interview_service.py       # Interview logic & orchestration
│   ├── feedback_service.py        # AI feedback generation
│   ├── voice_service.py           # Speech-to-text processing
│   └── analytics_service.py       # Performance analytics
└── templates/
    └── index.html                 # Frontend interface
```

## How to Run

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-mock-interview-assistant.git
cd ai-mock-interview-assistant
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

Copy `.env.example` to `.env` and add your OpenAI API key:

```bash
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. Run the application

```bash
python app.py
```

### 5. Open in browser

Navigate to: `http://localhost:8000`

## Project Flow

1. **Start Interview** → Select a job role (and optionally upload a resume)
2. **Answer Questions** → AI generates relevant questions; you answer via text or voice
3. **Get Feedback** → AI analyzes your answer and provides:
   - Confidence score (0-100)
   - Strengths & weaknesses
   - Improvement suggestions
   - Sample ideal answer
4. **Review History** → View all past interviews and track improvement
5. **Analytics** → See performance trends, average scores, and progress

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Frontend interface |
| POST | `/api/interview/start` | Start a new interview session |
| POST | `/api/interview/answer` | Submit an answer for feedback |
| GET | `/api/interview/history` | Get interview history |
| GET | `/api/interview/detail/{id}` | Get interview details |
| GET | `/api/interview/analytics` | Get performance analytics |
| POST | `/api/resume/upload` | Upload resume for question generation |
