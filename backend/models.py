from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class MPAllocation(Base):
    __tablename__ = "mp_allocations"

    id = Column(Integer, primary_key=True, index=True)
    sr_no = Column(Integer, nullable=True)
    state = Column(String(100), index=True, nullable=False)
    mp_name = Column(String(200), index=True, nullable=False)
    constituency = Column(String(200), index=True, nullable=False)
    allocated_amount = Column(Float, nullable=False)

class Project(Base):
    __tablename__ = "projects"

    project_id = Column(String(64), primary_key=True, index=True)
    state = Column(String(100), index=True, nullable=False)
    district = Column(String(100), index=True, nullable=False)
    constituency = Column(String(200), index=True, nullable=False)
    mp_name = Column(String(200), index=True, nullable=False)
    work_title = Column(String(300), nullable=False)
    work_description = Column(Text, nullable=False)
    work_category = Column(String(100), index=True, nullable=False)
    sanction_amount = Column(Float, nullable=False)
    expenditure_amount = Column(Float, nullable=False)
    sanction_date = Column(String(32), nullable=False)
    expected_completion_date = Column(String(32), nullable=False)
    actual_completion_date = Column(String(32), nullable=True)
    status = Column(String(50), index=True, nullable=False)  # COMPLETED, IN_PROGRESS, SANCTIONED, DELAYED, STALLED
    implementing_agency = Column(String(200), index=True, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    number_of_payments = Column(Integer, default=1)
    payment_dates = Column(Text, default="[]")  # JSON list
    payment_amounts = Column(Text, default="[]")  # JSON list
    data_source = Column(String(50), default="SYNTHETIC_DEMO", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to risk score
    risk = relationship("ProjectRisk", back_populates="project", uselist=False, cascade="all, delete-orphan")

class ProjectRisk(Base):
    __tablename__ = "project_risks"

    project_id = Column(String(64), ForeignKey("projects.project_id"), primary_key=True)
    overall_risk_score = Column(Float, index=True, nullable=False)  # 0 to 100
    risk_level = Column(String(32), index=True, nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    cost_risk_score = Column(Float, default=0.0)
    timeline_risk_score = Column(Float, default=0.0)
    expenditure_risk_score = Column(Float, default=0.0)
    overlap_risk_score = Column(Float, default=0.0)
    agency_risk_score = Column(Float, default=0.0)
    compliance_risk_score = Column(Float, default=0.0)
    contributing_factors = Column(Text, default="[]")  # JSON list of strings
    evidence = Column(Text, default="{}")  # JSON dict with metrics
    recommended_action = Column(Text, nullable=False)
    similar_projects = Column(Text, default="[]")  # JSON list of similar works
    updated_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="risk")

class Agency(Base):
    __tablename__ = "agencies"

    agency_name = Column(String(200), primary_key=True, index=True)
    district = Column(String(100), index=True, nullable=False)
    state = Column(String(100), index=True, nullable=False)
    total_projects = Column(Integer, default=0)
    total_sanctioned_amount = Column(Float, default=0.0)
    average_project_value = Column(Float, default=0.0)
    high_risk_projects_count = Column(Integer, default=0)
    risk_percentage = Column(Float, default=0.0)
    primary_category = Column(String(100), default="General")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_name = Column(String(100), nullable=False)
    user_role = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)
    project_id = Column(String(64), nullable=True, index=True)
    timestamp = Column(String(50), nullable=False)
    details = Column(Text, nullable=True)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)  # Monitoring Officer, Auditor, Administrator
    department = Column(String(100), nullable=False)
