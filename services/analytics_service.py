from database import get_all_analytics as db_get_analytics


def get_performance_analytics():
    return db_get_analytics()


def calculate_confidence_score(feedback_data: dict) -> float:
    score = feedback_data.get("confidence_score", 0.5)
    return max(0.0, min(1.0, float(score)))


def get_rating_label(score: float) -> str:
    if score >= 0.9:
        return "Excellent"
    elif score >= 0.75:
        return "Good"
    elif score >= 0.5:
        return "Average"
    elif score >= 0.3:
        return "Fair"
    else:
        return "Poor"
