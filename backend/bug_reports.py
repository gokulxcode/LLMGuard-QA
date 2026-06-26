import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models import models
from app.schemas import schemas

router = APIRouter(prefix="/bug-reports", tags=["Bug Reports"])

@router.get("/", response_model=List[schemas.BugReportOut])
def get_bug_reports(
    skip: int = 0,
    limit: int = 50,
    severity: Optional[str] = Query(None, description="Filter by severity"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.BugReport)
    if severity:
        query = query.filter(models.BugReport.severity == severity)
    if status:
        query = query.filter(models.BugReport.status == status)
    return query.order_by(models.BugReport.created_at.desc()).offset(skip).limit(limit).all()

@router.post("/", response_model=schemas.BugReportOut, status_code=status.HTTP_201_CREATED)
def create_bug_report(
    bug_in: schemas.BugReportCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_bug = models.BugReport(
        bug_uuid=f"BUG-{str(uuid.uuid4())[:8].upper()}",
        severity=bug_in.severity,
        priority=bug_in.priority,
        steps_to_reproduce=bug_in.steps_to_reproduce,
        expected_result=bug_in.expected_result,
        actual_result=bug_in.actual_result,
        root_cause=bug_in.root_cause,
        suggested_fix=bug_in.suggested_fix,
        status="Open",
        user_id=current_user.id
    )
    db.add(new_bug)
    db.commit()
    db.refresh(new_bug)
    return new_bug

@router.get("/{bug_id}", response_model=schemas.BugReportOut)
def get_bug_report(
    bug_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bug = db.query(models.BugReport).filter(models.BugReport.id == bug_id).first()
    if not bug:
        raise HTTPException(status_code=404, detail="Bug report not found")
    return bug

@router.put("/{bug_id}", response_model=schemas.BugReportOut)
def update_bug_report(
    bug_id: int,
    bug_in: schemas.BugReportUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bug = db.query(models.BugReport).filter(models.BugReport.id == bug_id).first()
    if not bug:
        raise HTTPException(status_code=404, detail="Bug report not found")
        
    update_data = bug_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(bug, field, val)
        
    db.commit()
    db.refresh(bug)
    return bug

@router.delete("/{bug_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bug_report(
    bug_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bug = db.query(models.BugReport).filter(models.BugReport.id == bug_id).first()
    if not bug:
        raise HTTPException(status_code=404, detail="Bug report not found")
        
    if current_user.role != "admin" and bug.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this bug report")
        
    db.delete(bug)
    db.commit()
    return None

@router.get("/{bug_id}/jira-export")
def export_jira_bug(
    bug_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Exports bug report details formatted in Jira markdown syntax.
    """
    bug = db.query(models.BugReport).filter(models.BugReport.id == bug_id).first()
    if not bug:
        raise HTTPException(status_code=404, detail="Bug report not found")
        
    jira_text = (
        f"h1. [LLMGuard QA] Bug Report: {bug.bug_uuid}\n\n"
        f"||Field||Details||\n"
        f"|*Bug UUID*| {bug.bug_uuid} |\n"
        f"|*Severity*| {bug.severity} |\n"
        f"|*Priority*| {bug.priority} |\n"
        f"|*Status*| {bug.status} |\n"
        f"|*Reported By User ID*| {bug.user_id} |\n"
        f"|*Created At*| {bug.created_at.strftime('%Y-%m-%d %H:%M:%S')} |\n\n"
        f"h3. Steps to Reproduce\n"
        f"{bug.steps_to_reproduce}\n\n"
        f"h3. Expected Result\n"
        f"{bug.expected_result}\n\n"
        f"h3. Actual Result\n"
        f"{bug.actual_result}\n\n"
        f"h3. Root Cause Analysis\n"
        f"{bug.root_cause if bug.root_cause else 'No root cause detailed.'}\n\n"
        f"h3. Suggested Remediation / Fix\n"
        f"{bug.suggested_fix if bug.suggested_fix else 'No suggested fix detailed.'}"
    )
    return {"jira_markdown": jira_text, "filename": f"{bug.bug_uuid}_jira.txt"}
