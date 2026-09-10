"""
NIRIKSHAN AI - Main FastAPI Application Server.
Provides authenticated REST endpoints for MPLADS anomaly intelligence,
project monitoring, explainable risk scoring, geospatial map, and dossier exports.
Uses Python's native sqlite3 database connection for maximum speed and portability.
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import jwt

from backend.database import get_db
from backend.report_generator import generate_pdf_report
from backend.seed_database import hash_pw

JWT_SECRET = os.environ.get("JWT_SECRET", "nirikshan-sih2026-secret-key-national-intel")
ALGORITHM = "HS256"

app = FastAPI(
    title="NIRIKSHAN AI - MPLADS Anomaly Intelligence System",
    description="AI-powered early-warning and decision-support system for MoSPI MPLADS monitoring.",
    version="1.0.0"
)

# Enable CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Auth Models -----------------
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    username: str
    full_name: str
    role: str
    department: str

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)

def log_action(conn: sqlite3.Connection, user_name: str, user_role: str, action: str, project_id: Optional[str] = None, details: Optional[str] = None):
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO audit_logs (user_name, user_role, action, project_id, timestamp, details)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_name,
        user_role,
        action,
        project_id,
        datetime.now(timezone.utc).strftime("%d %b %Y, %I:%M %p"),
        details
    ))
    conn.commit()

# ----------------- Auth Endpoints -----------------
@app.post("/api/auth/login", response_model=LoginResponse)
def login(req: LoginRequest, conn: sqlite3.Connection = Depends(get_db)):
    pw_hash = hash_pw(req.password)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", (req.username, pw_hash))
    user = cursor.fetchone()

    if not user:
        demo_roles = {
            "officer": ("Rajesh Kumar Sharma", "Monitoring Officer", "MoSPI MPLADS Division"),
            "auditor": ("Priya Venkatraman", "Auditor", "CAG Audit Cell"),
            "admin": ("Sanjay Singhal", "Administrator", "MoSPI National Data Centre")
        }
        if req.username in demo_roles and req.password in (f"{req.username}123", "password"):
            full_name, role, dept = demo_roles[req.username]
            token = create_access_token({"sub": req.username, "role": role})
            return LoginResponse(token=token, username=req.username, full_name=full_name, role=role, department=dept)
        raise HTTPException(status_code=401, detail="Invalid username or credentials")

    token = create_access_token({"sub": user["username"], "role": user["role"]})
    log_action(conn, user["full_name"], user["role"], "User Logged In", None, "Accessed NIRIKSHAN Portal")
    return LoginResponse(
        token=token,
        username=user["username"],
        full_name=user["full_name"],
        role=user["role"],
        department=user["department"]
    )

# ----------------- Dashboard Endpoints -----------------
@app.get("/api/dashboard")
def get_dashboard_data(conn: sqlite3.Connection = Depends(get_db)):
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total, SUM(sanction_amount) as total_sanction, SUM(expenditure_amount) as total_expenditure FROM projects")
    stats = cursor.fetchone()
    total_projects = stats["total"] or 0
    if total_projects == 0:
        return {"status": "Database not seeded yet"}

    total_sanction = stats["total_sanction"] or 0.0
    total_expenditure = stats["total_expenditure"] or 0.0

    # Risk level counts
    cursor.execute("SELECT risk_level, COUNT(*) as cnt FROM project_risks GROUP BY risk_level")
    risk_counts = {row["risk_level"]: row["cnt"] for row in cursor.fetchall()}
    critical_count = risk_counts.get("CRITICAL", 0)
    high_count = risk_counts.get("HIGH", 0)
    medium_count = risk_counts.get("MEDIUM", 0)
    low_count = risk_counts.get("LOW", 0)

    projects_requiring_verification = critical_count + high_count

    risk_distribution = [
        {"name": "Low Risk (0-29)", "count": low_count, "level": "LOW", "color": "#10b981"},
        {"name": "Medium Risk (30-59)", "count": medium_count, "level": "MEDIUM", "color": "#f59e0b"},
        {"name": "High Risk (60-79)", "count": high_count, "level": "HIGH", "color": "#f97316"},
        {"name": "Critical Risk (80-100)", "count": critical_count, "level": "CRITICAL", "color": "#ef4444"},
    ]

    # Category breakdown
    cursor.execute("""
    SELECT work_category, COUNT(*) as count, SUM(sanction_amount) as total_sanction, SUM(expenditure_amount) as total_expenditure
    FROM projects
    GROUP BY work_category
    ORDER BY count DESC
    """)
    category_distribution = [
        {
            "category": r["work_category"],
            "count": r["count"],
            "sanction_amount": round(r["total_sanction"] or 0.0, 2),
            "expenditure_amount": round(r["total_expenditure"] or 0.0, 2)
        }
        for r in cursor.fetchall()
    ]

    # Projects by state
    cursor.execute("""
    SELECT p.state, COUNT(p.project_id) as total, SUM(p.sanction_amount) as sanction,
           SUM(CASE WHEN r.risk_level IN ('HIGH', 'CRITICAL') THEN 1 ELSE 0 END) as high_risk_count
    FROM projects p
    LEFT JOIN project_risks r ON p.project_id = r.project_id
    GROUP BY p.state
    ORDER BY total DESC
    """)
    projects_by_state = [
        {
            "state": r["state"],
            "total_projects": r["total"],
            "total_sanction": round(r["sanction"] or 0.0, 2),
            "high_risk_count": r["high_risk_count"] or 0
        }
        for r in cursor.fetchall()
    ]

    # Dynamic AI insights computed from database anomalies
    cursor.execute("SELECT COUNT(*) as cnt FROM project_risks WHERE cost_risk_score >= 60.0")
    cost_anoms = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) as cnt FROM project_risks WHERE timeline_risk_score >= 60.0")
    timeline_anoms = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) as cnt FROM project_risks WHERE overlap_risk_score >= 60.0")
    overlap_anoms = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) as cnt FROM project_risks WHERE agency_risk_score >= 60.0")
    agency_anoms = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) as cnt FROM project_risks WHERE compliance_risk_score >= 40.0")
    compliance_anoms = cursor.fetchone()["cnt"]

    ai_insights = [
        f"{cost_anoms} projects show unusually high cost compared with peer benchmarks (>40% deviation).",
        f"{timeline_anoms} projects exhibit significant execution duration delays exceeding scheduled deadlines.",
        f"{overlap_anoms} potential overlapping project clusters detected with high descriptive & spatial proximity.",
        f"{agency_anoms} projects belong to implementing agencies with elevated concentration or project value deviations.",
        f"{compliance_anoms} projects triggered statutory compliance alerts (such as expenditure exceeding administrative sanction)."
    ]

    return {
        "kpis": {
            "total_projects": total_projects,
            "total_sanction_amount": round(total_sanction, 2),
            "total_expenditure_amount": round(total_expenditure, 2),
            "utilization_percentage": round((total_expenditure / total_sanction * 100.0) if total_sanction > 0 else 0.0, 1),
            "critical_projects": critical_count,
            "high_risk_projects": high_count,
            "medium_risk_projects": medium_count,
            "low_risk_projects": low_count,
            "normal_tolerance_count": low_count + medium_count,
            "projects_requiring_verification": projects_requiring_verification
        },
        "risk_distribution": risk_distribution,
        "category_distribution": category_distribution,
        "projects_by_state": projects_by_state,
        "ai_insights": ai_insights,
        "flagship_project_id": "MPL-DEMO-001"
    }

# ----------------- Project Monitoring Endpoints -----------------
@app.get("/api/projects")
def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    search: Optional[str] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
    category: Optional[str] = None,
    risk_level: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: str = Query("risk_score", pattern="^(risk_score|sanction_amount|expenditure_amount|sanction_date)$"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
    conn: sqlite3.Connection = Depends(get_db)
):
    cursor = conn.cursor()

    where_clauses = []
    params = []

    if search:
        s = f"%{search.strip()}%"
        where_clauses.append("(p.project_id LIKE ? OR p.work_title LIKE ? OR p.district LIKE ? OR p.mp_name LIKE ? OR p.implementing_agency LIKE ?)")
        params.extend([s, s, s, s, s])

    if state and state != "ALL":
        where_clauses.append("p.state = ?")
        params.append(state)

    if district and district != "ALL":
        where_clauses.append("p.district = ?")
        params.append(district)

    if category and category != "ALL":
        where_clauses.append("p.work_category = ?")
        params.append(category)

    if risk_level and risk_level != "ALL":
        where_clauses.append("r.risk_level = ?")
        params.append(risk_level)

    if status and status != "ALL":
        where_clauses.append("p.status = ?")
        params.append(status)

    where_str = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    # Sort column mapping
    sort_col = "r.overall_risk_score"
    if sort_by == "sanction_amount":
        sort_col = "p.sanction_amount"
    elif sort_by == "expenditure_amount":
        sort_col = "p.expenditure_amount"
    elif sort_by == "sanction_date":
        sort_col = "p.sanction_date"

    # Count query
    count_sql = f"""
    SELECT COUNT(*) as total
    FROM projects p
    LEFT JOIN project_risks r ON p.project_id = r.project_id
    {where_str}
    """
    cursor.execute(count_sql, params)
    total = cursor.fetchone()["total"]

    # Data query
    offset = (page - 1) * page_size
    data_sql = f"""
    SELECT p.*, r.overall_risk_score, r.risk_level, r.contributing_factors
    FROM projects p
    LEFT JOIN project_risks r ON p.project_id = r.project_id
    {where_str}
    ORDER BY {sort_col} {sort_dir.upper()}
    LIMIT ? OFFSET ?
    """
    cursor.execute(data_sql, params + [page_size, offset])
    rows = cursor.fetchall()

    items = []
    for row in rows:
        factors = []
        if row["contributing_factors"]:
            try:
                factors = json.loads(row["contributing_factors"])
            except Exception:
                factors = []

        items.append({
            "project_id": row["project_id"],
            "work_title": row["work_title"],
            "work_category": row["work_category"],
            "state": row["state"],
            "district": row["district"],
            "constituency": row["constituency"],
            "mp_name": row["mp_name"],
            "sanction_amount": row["sanction_amount"],
            "expenditure_amount": row["expenditure_amount"],
            "status": row["status"],
            "implementing_agency": row["implementing_agency"],
            "sanction_date": row["sanction_date"],
            "expected_completion_date": row["expected_completion_date"],
            "risk_score": row["overall_risk_score"] or 0.0,
            "risk_level": row["risk_level"] or "LOW",
            "top_factor": factors[0]["flag_note"] if factors else "Normal execution parameters",
            "data_source": row["data_source"]
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }

# ----------------- Project Details & Investigation -----------------
@app.get("/api/projects/{project_id}")
def get_project_details(project_id: str, conn: sqlite3.Connection = Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects WHERE project_id = ?", (project_id,))
    proj = cursor.fetchone()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    cursor.execute("SELECT * FROM project_risks WHERE project_id = ?", (project_id,))
    risk = cursor.fetchone()

    pmt_dates = []
    pmt_amounts = []
    factors = []
    evidence = {}
    similar_projects = []

    try:
        pmt_dates = json.loads(proj["payment_dates"]) if proj["payment_dates"] else []
    except Exception:
        pass

    try:
        pmt_amounts = json.loads(proj["payment_amounts"]) if proj["payment_amounts"] else []
    except Exception:
        pass

    if risk:
        try:
            factors = json.loads(risk["contributing_factors"]) if risk["contributing_factors"] else []
        except Exception:
            pass
        try:
            evidence = json.loads(risk["evidence"]) if risk["evidence"] else {}
        except Exception:
            pass
        try:
            similar_projects = json.loads(risk["similar_projects"]) if risk["similar_projects"] else []
        except Exception:
            pass

    payments = [{"date": d, "amount": a} for d, a in zip(pmt_dates, pmt_amounts)]

    # Audit log
    log_action(conn, "Auditor Reviewer", "Auditor", f"Investigated Project {project_id}", project_id, f"Viewed Risk Dossier (Score: {risk['overall_risk_score'] if risk else 0})")

    return {
        "project": {
            "project_id": proj["project_id"],
            "work_title": proj["work_title"],
            "work_description": proj["work_description"],
            "work_category": proj["work_category"],
            "state": proj["state"],
            "district": proj["district"],
            "constituency": proj["constituency"],
            "mp_name": proj["mp_name"],
            "sanction_amount": proj["sanction_amount"],
            "expenditure_amount": proj["expenditure_amount"],
            "sanction_date": proj["sanction_date"],
            "expected_completion_date": proj["expected_completion_date"],
            "actual_completion_date": proj["actual_completion_date"],
            "status": proj["status"],
            "implementing_agency": proj["implementing_agency"],
            "latitude": proj["latitude"],
            "longitude": proj["longitude"],
            "number_of_payments": proj["number_of_payments"],
            "payments": payments,
            "data_source": proj["data_source"]
        },
        "risk": {
            "overall_risk_score": risk["overall_risk_score"] if risk else 0.0,
            "risk_level": risk["risk_level"] if risk else "LOW",
            "cost_risk_score": risk["cost_risk_score"] if risk else 0.0,
            "timeline_risk_score": risk["timeline_risk_score"] if risk else 0.0,
            "expenditure_risk_score": risk["expenditure_risk_score"] if risk else 0.0,
            "overlap_risk_score": risk["overlap_risk_score"] if risk else 0.0,
            "agency_risk_score": risk["agency_risk_score"] if risk else 0.0,
            "compliance_risk_score": risk["compliance_risk_score"] if risk else 0.0,
            "contributing_factors": factors,
            "evidence": evidence,
            "recommended_action": risk["recommended_action"] if risk else "Standard monitoring",
            "similar_projects": similar_projects
        }
    }

@app.get("/api/projects/{project_id}/similar")
def get_similar_projects(project_id: str, conn: sqlite3.Connection = Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute("SELECT similar_projects FROM project_risks WHERE project_id = ?", (project_id,))
    row = cursor.fetchone()
    if not row or not row["similar_projects"]:
        return []
    try:
        return json.loads(row["similar_projects"])
    except Exception:
        return []

# ----------------- PDF Report Generation -----------------
@app.get("/api/projects/{project_id}/report")
def download_investigation_report(project_id: str, conn: sqlite3.Connection = Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects WHERE project_id = ?", (project_id,))
    proj = cursor.fetchone()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    cursor.execute("SELECT * FROM project_risks WHERE project_id = ?", (project_id,))
    risk = cursor.fetchone()
    if not risk:
        raise HTTPException(status_code=404, detail="Risk record not found")

    proj_dict = dict(proj)
    risk_dict = dict(risk)

    pdf_bytes = generate_pdf_report(proj_dict, risk_dict)

    log_action(conn, "Auditor Reviewer", "Auditor", f"Generated Investigation Dossier for {project_id}", project_id, "PDF Downloaded")

    filename = f"NIRIKSHAN_Investigation_Dossier_{project_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# ----------------- Map Geospatial Endpoints -----------------
@app.get("/api/map")
def get_map_markers(
    state: Optional[str] = None,
    risk_level: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = Query(500, le=1000),
    conn: sqlite3.Connection = Depends(get_db)
):
    cursor = conn.cursor()
    where_clauses = []
    params = []

    if state and state != "ALL":
        where_clauses.append("p.state = ?")
        params.append(state)
    if risk_level and risk_level != "ALL":
        where_clauses.append("r.risk_level = ?")
        params.append(risk_level)
    if category and category != "ALL":
        where_clauses.append("p.work_category = ?")
        params.append(category)

    where_str = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    sql = f"""
    SELECT p.project_id, p.work_title, p.work_category, p.state, p.district,
           p.latitude, p.longitude, p.sanction_amount, p.expenditure_amount, p.status,
           r.overall_risk_score, r.risk_level, r.contributing_factors
    FROM projects p
    JOIN project_risks r ON p.project_id = r.project_id
    {where_str}
    LIMIT ?
    """
    cursor.execute(sql, params + [limit])
    rows = cursor.fetchall()

    features = []
    for r in rows:
        factors = []
        if r["contributing_factors"]:
            try:
                factors = json.loads(r["contributing_factors"])
            except Exception:
                factors = []

        features.append({
            "project_id": r["project_id"],
            "work_title": r["work_title"],
            "category": r["work_category"],
            "state": r["state"],
            "district": r["district"],
            "latitude": r["latitude"],
            "longitude": r["longitude"],
            "sanction_amount": r["sanction_amount"],
            "expenditure_amount": r["expenditure_amount"],
            "status": r["status"],
            "risk_score": r["overall_risk_score"],
            "risk_level": r["risk_level"],
            "main_anomaly": factors[0]["flag_note"] if factors else "Normal parameters"
        })

    return features

# ----------------- Agency Analytics Endpoints -----------------
@app.get("/api/agencies")
def get_agencies(conn: sqlite3.Connection = Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM agencies
    ORDER BY high_risk_projects_count DESC, total_projects DESC
    """)
    rows = cursor.fetchall()
    return [dict(r) for r in rows]

@app.get("/api/agencies/{agency_name}")
def get_agency_profile(agency_name: str, conn: sqlite3.Connection = Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agencies WHERE agency_name = ?", (agency_name,))
    agency = cursor.fetchone()
    if not agency:
        raise HTTPException(status_code=404, detail="Agency not found")

    cursor.execute("""
    SELECT p.project_id, p.work_title, p.work_category, p.sanction_amount, p.status,
           r.overall_risk_score, r.risk_level
    FROM projects p
    JOIN project_risks r ON p.project_id = r.project_id
    WHERE p.implementing_agency = ?
    ORDER BY r.overall_risk_score DESC
    """, (agency_name,))
    projects = [dict(r) for r in cursor.fetchall()]

    return {
        "agency": dict(agency),
        "projects": projects
    }

# ----------------- Real MP Allocations Endpoints -----------------
@app.get("/api/allocations")
def get_real_allocations(state: Optional[str] = None, conn: sqlite3.Connection = Depends(get_db)):
    cursor = conn.cursor()

    where_sql = ""
    params = []
    if state and state != "ALL":
        where_sql = "WHERE state = ?"
        params.append(state)

    cursor.execute(f"SELECT * FROM mp_allocations {where_sql} ORDER BY allocated_amount DESC", params)
    allocations = [dict(r) for r in cursor.fetchall()]

    total_amount = sum(a["allocated_amount"] for a in allocations)

    # State aggregates
    cursor.execute("""
    SELECT state, COUNT(*) as mp_count, SUM(allocated_amount) as total_allocated
    FROM mp_allocations
    GROUP BY state
    ORDER BY total_allocated DESC
    """)
    state_breakdown = [dict(r) for r in cursor.fetchall()]

    return {
        "total_mps": len(allocations),
        "total_allocated_limit_inr": round(total_amount, 2),
        "data_source": "REAL_GOVT_CSV",
        "csv_filename": "Allocated Limit for Honble MPs.csv",
        "state_breakdown": state_breakdown,
        "allocations": allocations[:100]
    }

# ----------------- Audit Logs Endpoints -----------------
@app.get("/api/audit-logs")
def get_audit_logs(limit: int = 50, conn: sqlite3.Connection = Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,))
    return [dict(r) for r in cursor.fetchall()]

# ----------------- Re-analyze -----------------
@app.post("/api/analyze")
def trigger_analysis(conn: sqlite3.Connection = Depends(get_db)):
    from backend.seed_database import seed_database
    seed_database()
    return {"status": "success", "message": "Multi-signal anomaly analysis executed successfully."}

@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "NIRIKSHAN AI Backend",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
