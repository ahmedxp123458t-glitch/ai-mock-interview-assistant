import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "interview_assistant.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interviews (
            id TEXT PRIMARY KEY,
            job_role TEXT NOT NULL,
            date TEXT NOT NULL,
            resume_text TEXT,
            status TEXT DEFAULT 'in_progress'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interview_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interview_id TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT,
            feedback TEXT,
            confidence_score REAL DEFAULT 0.0,
            strengths TEXT,
            weaknesses TEXT,
            suggestions TEXT,
            rating TEXT,
            timestamp TEXT,
            FOREIGN KEY (interview_id) REFERENCES interviews(id)
        )
    """)

    conn.commit()
    conn.close()


def save_interview(interview_id: str, job_role: str, resume_text: str = ""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO interviews (id, job_role, date, resume_text) VALUES (?, ?, ?, ?)",
        (interview_id, job_role, datetime.now().isoformat(), resume_text),
    )
    conn.commit()
    conn.close()


def save_question_answer(
    interview_id: str,
    question: str,
    answer: str,
    feedback: str,
    confidence_score: float,
    strengths: list,
    weaknesses: list,
    suggestions: list,
    rating: str,
):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO interview_questions
           (interview_id, question, answer, feedback, confidence_score, strengths, weaknesses, suggestions, rating, timestamp)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            interview_id,
            question,
            answer,
            feedback,
            confidence_score,
            ",".join(strengths),
            ",".join(weaknesses),
            ",".join(suggestions),
            rating,
            datetime.now().isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def get_interview_history():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT i.id, i.job_role, i.date,
                  COUNT(q.id) as total_questions,
                  COALESCE(AVG(q.confidence_score), 0) as avg_confidence,
                  COALESCE((SELECT q2.rating FROM interview_questions q2
                   WHERE q2.interview_id = i.id ORDER BY q2.id DESC LIMIT 1), 'N/A') as overall_rating
           FROM interviews i
           LEFT JOIN interview_questions q ON q.interview_id = i.id
           GROUP BY i.id
           ORDER BY i.date DESC"""
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row["id"],
            "job_role": row["job_role"],
            "date": row["date"],
            "total_questions": row["total_questions"],
            "avg_confidence": round(row["avg_confidence"], 2),
            "overall_rating": row["overall_rating"],
        }
        for row in rows
    ]


def get_interview_detail(interview_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM interviews WHERE id = ?", (interview_id,))
    interview = cursor.fetchone()
    if not interview:
        conn.close()
        return None

    cursor.execute(
        "SELECT * FROM interview_questions WHERE interview_id = ? ORDER BY id",
        (interview_id,),
    )
    questions = cursor.fetchall()
    conn.close()

    q_list = []
    for q in questions:
        q_list.append(
            {
                "question": q["question"],
                "answer": q["answer"],
                "feedback": q["feedback"],
                "confidence_score": q["confidence_score"],
                "strengths": q["strengths"].split(",") if q["strengths"] else [],
                "weaknesses": q["weaknesses"].split(",") if q["weaknesses"] else [],
                "suggestions": q["suggestions"].split(",") if q["suggestions"] else [],
                "rating": q["rating"],
            }
        )

    avg_conf = (
        sum(q["confidence_score"] for q in q_list) / len(q_list) if q_list else 0
    )
    last_rating = q_list[-1]["rating"] if q_list else "N/A"

    return {
        "id": interview["id"],
        "job_role": interview["job_role"],
        "date": interview["date"],
        "questions": q_list,
        "avg_confidence": round(avg_conf, 2),
        "overall_rating": last_rating,
    }


def get_all_analytics():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as cnt FROM interviews")
    total_interviews = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) as cnt FROM interview_questions")
    total_questions = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COALESCE(AVG(confidence_score), 0) FROM interview_questions")
    avg_confidence = round(cursor.fetchone()[0], 2)

    cursor.execute(
        """SELECT rating, COUNT(*) as cnt FROM interview_questions
           WHERE rating IS NOT NULL GROUP BY rating"""
    )
    rating_rows = cursor.fetchall()
    rating_dist = {r["rating"]: r["cnt"] for r in rating_rows}

    cursor.execute(
        """SELECT i.date, AVG(q.confidence_score) as conf
           FROM interviews i
           JOIN interview_questions q ON q.interview_id = i.id
           GROUP BY i.id ORDER BY i.date"""
    )
    trend_rows = cursor.fetchall()
    trend = [
        {"date": r["date"][:10], "avg_confidence": round(r["conf"], 2)}
        for r in trend_rows
    ]

    cursor.execute(
        """SELECT i.job_role, COUNT(q.id) as cnt, AVG(q.confidence_score) as conf
           FROM interviews i
           JOIN interview_questions q ON q.interview_id = i.id
           GROUP BY i.job_role"""
    )
    role_rows = cursor.fetchall()
    roles = [
        {
            "role": r["job_role"],
            "count": r["cnt"],
            "avg_confidence": round(r["conf"], 2),
        }
        for r in role_rows
    ]

    cursor.execute(
        """SELECT q.id, q.question, q.confidence_score, q.rating, i.job_role, i.date
           FROM interview_questions q
           JOIN interviews i ON i.id = q.interview_id
           ORDER BY q.id DESC LIMIT 10"""
    )
    recent = cursor.fetchall()
    recent_scores = [
        {
            "question": r["question"][:60],
            "confidence_score": r["confidence_score"],
            "rating": r["rating"],
            "role": r["job_role"],
            "date": r["date"][:10],
        }
        for r in recent
    ]

    conn.close()

    weights = {"Excellent": 5, "Good": 4, "Average": 3, "Fair": 2, "Poor": 1}
    weighted_sum = sum(
        weights.get(r, 0) * c for r, c in rating_dist.items()
    )
    total_ratings = sum(rating_dist.values())
    avg_rating_num = (
        round(weighted_sum / total_ratings, 1) if total_ratings else 0
    )
    avg_rating_map = {5: "Excellent", 4: "Good", 3: "Average", 2: "Fair", 1: "Poor"}
    avg_rating = avg_rating_map.get(round(avg_rating_num), "N/A")

    return {
        "total_interviews": total_interviews,
        "total_questions": total_questions,
        "avg_confidence": avg_confidence,
        "avg_rating": avg_rating,
        "rating_distribution": rating_dist,
        "confidence_trend": trend,
        "role_performance": roles,
        "recent_scores": recent_scores,
    }
