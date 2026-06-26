from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models import models
from app.schemas import schemas
from app.services.evaluators import EvaluatorService
from app.services.gemini import GeminiService

router = APIRouter(prefix="/evaluations", tags=["Testing Evaluators"])

# --- Hallucinations ---
@router.get("/hallucinations", response_model=List[schemas.HallucinationOut])
def get_hallucination_records(
    skip: int = 0,
    limit: int = 50,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.Hallucination).order_by(models.Hallucination.created_at.desc()).offset(skip).limit(limit).all()

# --- Sensitivity Testing ---
@router.get("/sensitivity", response_model=List[schemas.SensitivityTestOut])
def get_sensitivity_records(
    skip: int = 0,
    limit: int = 50,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.SensitivityTest).order_by(models.SensitivityTest.created_at.desc()).offset(skip).limit(limit).all()

@router.post("/sensitivity/run/{prompt_id}", response_model=List[schemas.SensitivityTestOut])
def run_prompt_sensitivity(
    prompt_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Module 5: Generates semantic variations of the prompt, triggers Gemini for each variation,
    compares variations against the original prompt's latest response, and records metrics.
    """
    prompt = db.query(models.Prompt).filter(models.Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
        
    # Get latest original response (or create one if none exists)
    orig_resp = db.query(models.Response).filter(models.Response.prompt_id == prompt_id).order_by(models.Response.created_at.desc()).first()
    if not orig_resp:
        response_text, model, tokens = GeminiService.generate_response(prompt.prompt_text)
        orig_resp = models.Response(
            prompt_id=prompt_id,
            response_text=response_text,
            model_name=model,
            token_count=tokens,
            run_index=0
        )
        db.add(orig_resp)
        db.commit()
        db.refresh(orig_resp)
        
    # Run sensitivity analyzer
    analysis_results = EvaluatorService.run_sensitivity_analysis(prompt.prompt_text, orig_resp.response_text)
    
    # Save variations to database
    db_records = []
    for res in analysis_results:
        db_sens = models.SensitivityTest(
            prompt_id=prompt_id,
            variation_text=res["variation_text"],
            response_text=res["response_text"],
            similarity_score=res["similarity_score"],
            info_retention_score=res["info_retention_score"],
            format_consistency_score=res["format_consistency_score"],
            stability_score=res["stability_score"]
        )
        db.add(db_sens)
        db_records.append(db_sens)
        
    db.commit()
    for rec in db_records:
        db.refresh(rec)
        
    return db_records

# --- Context Leakage ---
@router.get("/leakage", response_model=List[schemas.LeakageResultOut])
def get_leakage_records(
    skip: int = 0,
    limit: int = 50,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.LeakageResult).order_by(models.LeakageResult.created_at.desc()).offset(skip).limit(limit).all()

# --- Safety Analysis ---
@router.get("/safety", response_model=List[schemas.SafetyResultOut])
def get_safety_records(
    skip: int = 0,
    limit: int = 50,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.SafetyResult).order_by(models.SafetyResult.created_at.desc()).offset(skip).limit(limit).all()

# --- Consistency Testing ---
@router.post("/consistency/run/{prompt_id}")
def run_prompt_consistency(
    prompt_id: int,
    runs: int = Query(3, ge=2, le=5),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Module 8: Executes the same prompt multiple times and measures response overlap,
    variability, and consistency.
    """
    prompt = db.query(models.Prompt).filter(models.Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
        
    results = EvaluatorService.run_consistency_testing(prompt.prompt_text, runs)
    
    # Save these response runs to Responses table as version history
    saved_runs = []
    base_run_count = db.query(models.Response).filter(models.Response.prompt_id == prompt_id).count()
    
    for idx, resp_text in enumerate(results["responses"]):
        db_resp = models.Response(
            prompt_id=prompt_id,
            response_text=resp_text,
            model_name="gemini-1.5-flash",
            temperature=0.8,
            token_count=len(resp_text.split()) + len(prompt.prompt_text.split()),
            run_index=base_run_count + idx
        )
        db.add(db_resp)
        saved_runs.append(db_resp)
        
    db.commit()
    
    return {
        "prompt_id": prompt_id,
        "runs_executed": runs,
        "similarity": results["similarity"],
        "variability": results["variability"],
        "consistency_score": results["consistency_score"],
        "responses": [r.response_text for r in saved_runs]
    }

# --- Regression Results ---
@router.get("/regression", response_model=List[schemas.RegressionResultOut])
def get_regression_records(
    skip: int = 0,
    limit: int = 50,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.RegressionResult).order_by(models.RegressionResult.created_at.desc()).offset(skip).limit(limit).all()
