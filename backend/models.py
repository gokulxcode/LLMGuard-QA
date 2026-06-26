from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="tester", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    prompts = relationship("Prompt", back_populates="user", cascade="all, delete-orphan")
    bug_reports = relationship("BugReport", back_populates="user", cascade="all, delete-orphan")


class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    prompt_text = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # Factual, Creative, Reasoning, Coding, Summarization, Translation, Sensitive, Safety
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="prompts")
    responses = relationship("Response", back_populates="prompt", cascade="all, delete-orphan")
    sensitivity_tests = relationship("SensitivityTest", back_populates="prompt", cascade="all, delete-orphan")
    leakage_results = relationship("LeakageResult", back_populates="prompt", cascade="all, delete-orphan")
    regression_results = relationship("RegressionResult", foreign_keys="[RegressionResult.prompt_id]", back_populates="prompt", cascade="all, delete-orphan")


class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False)
    response_text = Column(Text, nullable=False)
    model_name = Column(String(50), nullable=False)
    temperature = Column(Float, default=0.7)
    token_count = Column(Integer, default=0)
    run_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    prompt = relationship("Prompt", back_populates="responses")
    hallucination = relationship("Hallucination", back_populates="response", uselist=False, cascade="all, delete-orphan")
    safety_result = relationship("SafetyResult", back_populates="response", uselist=False, cascade="all, delete-orphan")
    
    regression_olds = relationship("RegressionResult", foreign_keys="[RegressionResult.old_response_id]", back_populates="old_response", cascade="all, delete")
    regression_news = relationship("RegressionResult", foreign_keys="[RegressionResult.new_response_id]", back_populates="new_response", cascade="all, delete")


class Hallucination(Base):
    __tablename__ = "hallucinations"

    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("responses.id", ondelete="CASCADE"), unique=True, nullable=False)
    evaluation = Column(String(30), nullable=False)  # Correct, Partially Correct, Hallucinated
    accuracy_score = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    reliability_percentage = Column(Float, nullable=False)
    reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    response = relationship("Response", back_populates="hallucination")


class SensitivityTest(Base):
    __tablename__ = "sensitivity_tests"

    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False)
    variation_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=False)
    similarity_score = Column(Float, nullable=False)
    info_retention_score = Column(Float, nullable=False)
    format_consistency_score = Column(Float, nullable=False)
    stability_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    prompt = relationship("Prompt", back_populates="sensitivity_tests")


class LeakageResult(Base):
    __tablename__ = "leakage_results"

    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False)
    system_context = Column(Text, nullable=False)
    evaluation_result = Column(String(30), nullable=False)  # Safe, Potential Leakage, Leakage Detected
    privacy_score = Column(Float, nullable=False)
    reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    prompt = relationship("Prompt", back_populates="leakage_results")


class SafetyResult(Base):
    __tablename__ = "safety_results"

    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("responses.id", ondelete="CASCADE"), unique=True, nullable=False)
    toxicity_score = Column(Float, nullable=False)
    harmful_score = Column(Float, nullable=False)
    bias_score = Column(Float, nullable=False)
    safety_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)  # Low, Medium, High
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    response = relationship("Response", back_populates="safety_result")


class RegressionResult(Base):
    __tablename__ = "regression_results"

    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False)
    old_response_id = Column(Integer, ForeignKey("responses.id", ondelete="SET NULL"), nullable=True)
    new_response_id = Column(Integer, ForeignKey("responses.id", ondelete="SET NULL"), nullable=True)
    quality_degradation_score = Column(Float, nullable=False)
    missing_info_score = Column(Float, nullable=False)
    format_change_score = Column(Float, nullable=False)
    regression_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    prompt = relationship("Prompt", foreign_keys=[prompt_id], back_populates="regression_results")
    old_response = relationship("Response", foreign_keys=[old_response_id], back_populates="regression_olds")
    new_response = relationship("Response", foreign_keys=[new_response_id], back_populates="regression_news")


class BugReport(Base):
    __tablename__ = "bug_reports"

    id = Column(Integer, primary_key=True, index=True)
    bug_uuid = Column(String(50), unique=True, index=True, nullable=False)
    severity = Column(String(20), nullable=False)  # Low, Medium, High, Critical
    priority = Column(String(20), nullable=False)  # Low, Medium, High, Urgent
    steps_to_reproduce = Column(Text, nullable=False)
    expected_result = Column(Text, nullable=False)
    actual_result = Column(Text, nullable=False)
    root_cause = Column(Text, nullable=True)
    suggested_fix = Column(Text, nullable=True)
    status = Column(String(20), default="Open", nullable=False)  # Open, In Progress, Resolved
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="bug_reports")
