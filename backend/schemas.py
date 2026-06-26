from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

# User Schemas
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: Optional[str] = "tester"  # admin or tester

class UserLogin(BaseModel):
    username: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

# Prompt Schemas
class PromptCreate(BaseModel):
    prompt_text: str = Field(..., min_length=1)
    category: str = Field(..., pattern="^(Factual|Creative|Reasoning|Coding|Summarization|Translation|Sensitive|Safety)$")

class PromptOut(BaseModel):
    id: int
    prompt_text: str
    category: str
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Response Schemas
class ResponseOut(BaseModel):
    id: int
    prompt_id: int
    response_text: str
    model_name: str
    temperature: float
    token_count: int
    run_index: int
    created_at: datetime

    class Config:
        from_attributes = True

# Hallucination Schemas
class HallucinationOut(BaseModel):
    id: int
    response_id: int
    evaluation: str
    accuracy_score: float
    confidence_score: float
    reliability_percentage: float
    reasoning: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Sensitivity Schemas
class SensitivityTestOut(BaseModel):
    id: int
    prompt_id: int
    variation_text: str
    response_text: str
    similarity_score: float
    info_retention_score: float
    format_consistency_score: float
    stability_score: float
    created_at: datetime

    class Config:
        from_attributes = True

# Leakage Schemas
class LeakageResultOut(BaseModel):
    id: int
    prompt_id: int
    system_context: str
    evaluation_result: str
    privacy_score: float
    reasoning: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Safety Schemas
class SafetyResultOut(BaseModel):
    id: int
    response_id: int
    toxicity_score: float
    harmful_score: float
    bias_score: float
    safety_score: float
    risk_level: str
    created_at: datetime

    class Config:
        from_attributes = True

# Regression Schemas
class RegressionResultOut(BaseModel):
    id: int
    prompt_id: int
    old_response_id: Optional[int] = None
    new_response_id: Optional[int] = None
    quality_degradation_score: float
    missing_info_score: float
    format_change_score: float
    regression_score: float
    created_at: datetime

    class Config:
        from_attributes = True

# Bug Report Schemas
class BugReportCreate(BaseModel):
    severity: str = Field(..., pattern="^(Low|Medium|High|Critical)$")
    priority: str = Field(..., pattern="^(Low|Medium|High|Urgent)$")
    steps_to_reproduce: str
    expected_result: str
    actual_result: str
    root_cause: Optional[str] = None
    suggested_fix: Optional[str] = None

class BugReportUpdate(BaseModel):
    status: str = Field(..., pattern="^(Open|In Progress|Resolved)$")
    severity: Optional[str] = None
    priority: Optional[str] = None
    steps_to_reproduce: Optional[str] = None
    expected_result: Optional[str] = None
    actual_result: Optional[str] = None
    root_cause: Optional[str] = None
    suggested_fix: Optional[str] = None

class BugReportOut(BaseModel):
    id: int
    bug_uuid: str
    severity: str
    priority: str
    steps_to_reproduce: str
    expected_result: str
    actual_result: str
    root_cause: Optional[str] = None
    suggested_fix: Optional[str] = None
    status: str
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Dashboard summary schema
class DashboardSummaryOut(BaseModel):
    total_tests: int
    hallucinations_found: int
    safety_issues: int
    leakage_cases: int
    pass_rate: float
    failure_rate: float
    category_counts: dict
    recent_activity: List[dict]
