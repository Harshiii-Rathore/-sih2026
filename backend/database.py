"""
Database Access Layer for NIRIKSHAN AI using Python standard sqlite3.
Zero external dependency, fast, robust, and clean SQL structure.
"""

import os
import sqlite3
from typing import Generator

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BACKEND_DIR, "nirikshan.db")

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. MP Allocations Table (from real CSV)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mp_allocations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sr_no INTEGER,
        state TEXT NOT NULL,
        mp_name TEXT NOT NULL,
        constituency TEXT NOT NULL,
        allocated_amount REAL NOT NULL
    );
    """)

    # 2. Projects Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        project_id TEXT PRIMARY KEY,
        state TEXT NOT NULL,
        district TEXT NOT NULL,
        constituency TEXT NOT NULL,
        mp_name TEXT NOT NULL,
        work_title TEXT NOT NULL,
        work_description TEXT NOT NULL,
        work_category TEXT NOT NULL,
        sanction_amount REAL NOT NULL,
        expenditure_amount REAL NOT NULL,
        sanction_date TEXT NOT NULL,
        expected_completion_date TEXT NOT NULL,
        actual_completion_date TEXT,
        status TEXT NOT NULL,
        implementing_agency TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        number_of_payments INTEGER DEFAULT 1,
        payment_dates TEXT DEFAULT '[]',
        payment_amounts TEXT DEFAULT '[]',
        data_source TEXT DEFAULT 'SYNTHETIC_DEMO',
        created_at TEXT NOT NULL
    );
    """)

    # 3. Project Risks Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS project_risks (
        project_id TEXT PRIMARY KEY,
        overall_risk_score REAL NOT NULL,
        risk_level TEXT NOT NULL,
        cost_risk_score REAL DEFAULT 0.0,
        timeline_risk_score REAL DEFAULT 0.0,
        expenditure_risk_score REAL DEFAULT 0.0,
        overlap_risk_score REAL DEFAULT 0.0,
        agency_risk_score REAL DEFAULT 0.0,
        compliance_risk_score REAL DEFAULT 0.0,
        contributing_factors TEXT DEFAULT '[]',
        evidence TEXT DEFAULT '{}',
        recommended_action TEXT NOT NULL,
        similar_projects TEXT DEFAULT '[]',
        updated_at TEXT NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
    );
    """)

    # 4. Agencies Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agencies (
        agency_name TEXT PRIMARY KEY,
        district TEXT NOT NULL,
        state TEXT NOT NULL,
        total_projects INTEGER DEFAULT 0,
        total_sanctioned_amount REAL DEFAULT 0.0,
        average_project_value REAL DEFAULT 0.0,
        high_risk_projects_count INTEGER DEFAULT 0,
        risk_percentage REAL DEFAULT 0.0,
        primary_category TEXT DEFAULT 'General'
    );
    """)

    # 5. Audit Logs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT NOT NULL,
        user_role TEXT NOT NULL,
        action TEXT NOT NULL,
        project_id TEXT,
        timestamp TEXT NOT NULL,
        details TEXT
    );
    """)

    # 6. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL,
        department TEXT NOT NULL
    );
    """)

    # Create Indexes for fast filtering & search
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_proj_state ON projects(state);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_proj_district ON projects(district);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_proj_category ON projects(work_category);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_proj_status ON projects(status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_risk_score ON project_risks(overall_risk_score);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_risk_level ON project_risks(risk_level);")

    conn.commit()
    conn.close()
