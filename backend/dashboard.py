from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models import models

router = APIRouter(prefix="/dashboard", tags=["Dashboard Aggregations"])

@router.get("/summary")
def get_dashboard_summary(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    total_tests = db.query(models.Response).count()
    
    # Hallucinations counts
    hallucinations_found = db.query(models.Hallucination).filter(
        models.Hallucination.evaluation == "Hallucinated"
    ).count()
    
    # Safety issues counts (Risk level Medium or High)
    safety_issues = db.query(models.SafetyResult).filter(
        models.SafetyResult.risk_level.in_(["Medium", "High"])
    ).count()
    
    # Leakage cases
    leakage_cases = db.query(models.LeakageResult).filter(
        models.LeakageResult.evaluation_result.in_(["Potential Leakage", "Leakage Detected"])
    ).count()
    
    # Category counts
    category_data = db.query(
        models.Prompt.category, func.count(models.Prompt.id)
    ).group_by(models.Prompt.category).all()
    
    category_counts = {cat: count for cat, count in category_data}
    # Default initializations for categories to avoid empty graphs
    for cat in ["Factual", "Creative", "Reasoning", "Coding", "Summarization", "Translation", "Sensitive", "Safety"]:
        if cat not in category_counts:
            category_counts[cat] = 0
            
    # Calculate pass / failure rates
    # Criteria: A test passes if it is evaluated for accuracy and safety, and passes both bounds.
    # If no evaluations exist, pass rate defaults to 100%
    if total_tests > 0:
        # Check failed runs
        failures = db.query(models.Response).join(models.Hallucination).join(models.SafetyResult).filter(
            (models.Hallucination.evaluation == "Hallucinated") | 
            (models.SafetyResult.risk_level.in_(["Medium", "High"]))
        ).count()
        
        failure_rate = round((failures / total_tests) * 100, 1)
        pass_rate = round(100 - failure_rate, 1)
    else:
        pass_rate = 100.0
        failure_rate = 0.0

    # Recent activities (last 10 prompts evaluated)
    recent_responses = db.query(models.Response).order_by(
        models.Response.created_at.desc()
    ).limit(10).all()
    
    activity_logs = []
    for resp in recent_responses:
        prompt = resp.prompt
        hallucination = resp.hallucination
        safety = resp.safety_result
        
        status_verdict = "Passed"
        if hallucination and hallucination.evaluation == "Hallucinated":
            status_verdict = "Hallucinated"
        elif safety and safety.risk_level in ["Medium", "High"]:
            status_verdict = "Unsafe"
            
        activity_logs.append({
            "response_id": resp.id,
            "prompt_text": prompt.prompt_text[:60] + "..." if len(prompt.prompt_text) > 60 else prompt.prompt_text,
            "category": prompt.category,
            "verdict": status_verdict,
            "risk_level": safety.risk_level if safety else "Low",
            "timestamp": resp.created_at.isoformat()
        })
        
    # Build chart timeline (group test executions by day)
    timeline_query = db.query(
        func.date(models.Response.created_at).label("day"),
        func.count(models.Response.id).label("count")
    ).group_by("day").order_by("day").limit(15).all()
    
    timeline = [{"date": str(t.day), "tests": t.count} for t in timeline_query]
    if not timeline:
        # Fallback empty timeline point
        import datetime
        timeline = [{"date": str(datetime.date.today()), "tests": 0}]

    return {
        "total_tests": total_tests,
        "hallucinations_found": hallucinations_found,
        "safety_issues": safety_issues,
        "leakage_cases": leakage_cases,
        "pass_rate": pass_rate,
        "failure_rate": failure_rate,
        "category_counts": category_counts,
        "recent_activity": activity_logs,
        "timeline": timeline
    }
