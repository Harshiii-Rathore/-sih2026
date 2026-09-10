"""
Database Seeding Script for NIRIKSHAN AI (SIH26102).
Ingests real allocation limits, creates ~1,000 realistic synthetic projects,
calculates multi-signal anomaly metrics, and seeds the SQLite database.
"""

import os
import sys
import json
import random
import hashlib
from datetime import datetime, timedelta

# Add workspace root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import get_connection, init_db, DB_PATH
from backend.data_provider import DemoDataProvider
from backend.anomaly_engine.cost_detector import CostAnomalyDetector
from backend.anomaly_engine.timeline_detector import TimelineAnomalyDetector
from backend.anomaly_engine.expenditure_detector import ExpenditureAnomalyDetector
from backend.anomaly_engine.overlap_detector import OverlapDetector
from backend.anomaly_engine.agency_detector import AgencyAnomalyDetector
from backend.anomaly_engine.compliance_rules import ComplianceRuleEngine
from backend.anomaly_engine.risk_scorer import RiskScorer

def hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

STATE_GEO = {
    "Maharashtra": {"districts": ["Pune", "Nagpur", "Nashik", "Thane", "Amravati", "Aurangabad", "Solapur"], "lat": 19.75, "lon": 75.71},
    "Uttar Pradesh": {"districts": ["Lucknow", "Varanasi", "Kanpur", "Gorakhpur", "Agra", "Prayagraj", "Meerut"], "lat": 26.84, "lon": 80.94},
    "Tamil Nadu": {"districts": ["Chennai", "Coimbatore", "Madurai", "Salem", "Tiruchirappalli", "Vellore"], "lat": 11.12, "lon": 78.65},
    "Bihar": {"districts": ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Darbhanga", "Purnea"], "lat": 25.09, "lon": 85.31},
    "Karnataka": {"districts": ["Bangalore Urban", "Mysore", "Belgaum", "Dharwad", "Mangalore", "Gulbarga"], "lat": 15.31, "lon": 75.71},
    "Rajasthan": {"districts": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Bikaner", "Ajmer", "Sikar"], "lat": 27.02, "lon": 74.21},
    "Gujarat": {"districts": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar"], "lat": 22.25, "lon": 71.19},
    "West Bengal": {"districts": ["Kolkata", "Howrah", "North 24 Parganas", "Hooghly", "Murshidabad", "Bardhaman"], "lat": 22.98, "lon": 87.85},
    "Kerala": {"districts": ["Thiruvananthapuram", "Ernakulam", "Kozhikode", "Thrissur", "Malappuram", "Kollam"], "lat": 10.85, "lon": 76.27},
    "Madhya Pradesh": {"districts": ["Bhopal", "Indore", "Gwalior", "Jabalpur", "Ujjain", "Sagar"], "lat": 22.97, "lon": 78.65},
    "Odisha": {"districts": ["Bhubaneswar", "Cuttack", "Sambalpur", "Balasore", "Berhampur", "Puri"], "lat": 20.95, "lon": 85.09},
    "Delhi": {"districts": ["New Delhi", "North Delhi", "South Delhi", "East Delhi", "West Delhi"], "lat": 28.61, "lon": 77.20}
}

CATEGORIES = [
    "Community Halls",
    "Roads",
    "Drinking Water",
    "Sanitation",
    "Education",
    "Healthcare",
    "Street Lighting",
    "Drainage",
    "Public Utilities",
    "Sports Facilities",
    "Public Infrastructure"
]

CATEGORY_BENCHMARKS = {
    "Community Halls": (1200000, 1600000),      # ~14 Lakhs
    "Roads": (2500000, 4500000),                # ~35 Lakhs
    "Drinking Water": (600000, 1100000),         # ~8.5 Lakhs
    "Sanitation": (500000, 900000),              # ~7 Lakhs
    "Education": (1500000, 2800000),             # ~21 Lakhs
    "Healthcare": (1800000, 3200000),            # ~25 Lakhs
    "Street Lighting": (400000, 800000),         # ~6 Lakhs
    "Drainage": (1200000, 2200000),              # ~17 Lakhs
    "Public Utilities": (800000, 1500000),       # ~11.5 Lakhs
    "Sports Facilities": (1400000, 2500000),     # ~19.5 Lakhs
    "Public Infrastructure": (2000000, 4000000)  # ~30 Lakhs
}

WORK_TITLES = {
    "Community Halls": [
        "Construction of Multi-purpose Community Hall at {loc}",
        "Development of Samajik Kalyan Kendra Hall at {loc}",
        "Erection of Community Activity Centre and Pavilion at {loc}",
        "Construction of Public Gathering Hall with Solar Lighting at {loc}"
    ],
    "Roads": [
        "Construction of Concrete CC Road from Main Market to {loc}",
        "Bituminous Road Upgradation and Culvert Strengthening near {loc}",
        "Paver Block Road Laying and Side Berm Widening at {loc}",
        "Link Road Improvement Connecting Rural Habitation to {loc}"
    ],
    "Drinking Water": [
        "Installation of Solar-Powered RO Water Purification Plant at {loc}",
        "Deep Tube Well Boring with Overhead Water Storage Tank at {loc}",
        "Piped Drinking Water Supply Line Augmentation at {loc}",
        "Community Drinking Water Filtration Unit Setup at {loc}"
    ],
    "Sanitation": [
        "Construction of Modern Community Public Toilet Block at {loc}",
        "Setup of Decentralized Solid Waste Segregation Shed at {loc}",
        "Installation of Bio-Toilets with Soak Pit System at {loc}",
        "Sanitation Complex with Handwashing Station at {loc}"
    ],
    "Education": [
        "Construction of Additional Classrooms & Computer Lab at {loc}",
        "Upgradation of Government Higher Secondary School Building at {loc}",
        "Setup of Smart Classroom Equipment and Library at {loc}",
        "Development of Science Laboratory and Study Hall at {loc}"
    ],
    "Healthcare": [
        "Construction of Primary Health Sub-Centre Building at {loc}",
        "Procurement and Installation of Advanced Medical Diagnostic Equipment for {loc}",
        "Establishment of Mother and Child Care Wellness Wing at {loc}",
        "Mobile Health Clinic Stationing and Dispensary Upgradation at {loc}"
    ],
    "Street Lighting": [
        "Installation of 60W Solar LED Street Lights across {loc}",
        "High-Mast Tower Lighting Erection at Commercial Junction of {loc}",
        "Energy-Efficient Smart Street Illumination Project at {loc}",
        "Installation of Semi-High Mast Light Poles at {loc}"
    ],
    "Drainage": [
        "Construction of Underground Storm Water Drainage Channel at {loc}",
        "Reinforced Covered Pucca Nallah Construction near {loc}",
        "Drainage Desilting and Masonry Wall Retaining Structure at {loc}",
        "Construction of Village Effluent Disposal Open Drain at {loc}"
    ],
    "Public Utilities": [
        "Construction of Crematorium / Shmashan Ghat Shed and Facilities at {loc}",
        "Setup of Covered Rural Haat / Farmer Market Platform at {loc}",
        "Public Passenger Bus Shelter with Seating and Roof at {loc}",
        "Development of Senior Citizen Recreation Park Facility at {loc}"
    ],
    "Sports Facilities": [
        "Development of Rural Sports Ground with Running Track at {loc}",
        "Construction of Open Gym Facility and Volleyball Court at {loc}",
        "Synthetic Badminton Court and Spectator Gallery at {loc}",
        "Sports Training Equipment and Youth Fitness Pavilion at {loc}"
    ],
    "Public Infrastructure": [
        "Construction of Over-Bridge Footpath and Retaining Barrier at {loc}",
        "Development of Riverfront Ghat Retaining Wall & Steps at {loc}",
        "Public Boundary Wall and Fencing around Government Land at {loc}",
        "Multi-Purpose Administrative Transit Room Facility at {loc}"
    ]
}

AGENCIES = [
    "District Rural Development Agency (DRDA)",
    "Public Works Department (PWD - Division 1)",
    "Rural Water Supply & Sanitation Department (RWSSD)",
    "District Urban Development Cell (DUDC)",
    "Zila Parishad Engineering Wing",
    "Municipal Corporation Public Works",
    "State Infrastructure Development Corp (SIDC)",
    "Demo Infrastructure Development Agency (Anonymized)",
    "Apex Civil Constructions Ltd (Demo)",
    "Regional Vikas Parishad (Demo)"
]

def generate_payment_schedule(sanction_amount: float, status: str, is_anom: bool = False):
    if is_anom:
        return 1, ["2024-10-15"], [sanction_amount]

    if status == "SANCTIONED":
        return 0, [], []
    elif status == "IN_PROGRESS":
        num_tranches = random.choice([1, 2])
        p1 = round(sanction_amount * random.uniform(0.3, 0.45), 2)
        if num_tranches == 1:
            return 1, ["2025-02-10"], [p1]
        else:
            p2 = round(sanction_amount * random.uniform(0.25, 0.35), 2)
            return 2, ["2025-02-10", "2025-07-15"], [p1, p2]
    elif status in ("COMPLETED", "DELAYED"):
        num_tranches = random.choice([3, 4])
        p1 = round(sanction_amount * 0.35, 2)
        p2 = round(sanction_amount * 0.35, 2)
        p3 = round(sanction_amount * (0.25 if num_tranches == 4 else 0.30), 2)
        dates = ["2024-06-15", "2024-11-20", "2025-04-10"]
        amounts = [p1, p2, p3]
        if num_tranches == 4:
            dates.append("2025-09-05")
            amounts.append(round(sanction_amount * 0.05, 2))
        return num_tranches, dates, amounts
    else:  # STALLED
        p1 = round(sanction_amount * 0.40, 2)
        return 1, ["2024-05-12"], [p1]

def seed_database():
    print(f"Initializing database at: {DB_PATH}")
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except Exception:
            pass

    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Ingest Real Allocation CSV
    print("Ingesting 'Allocated Limit for Honble MPs.csv' into 'mp_allocations'...")
    provider = DemoDataProvider()
    allocations_data = provider.get_mp_allocations()
    print(f"Parsed {len(allocations_data)} real MP records from uploaded CSV.")

    alloc_rows = [
        (item["sr_no"], item["state"], item["mp_name"], item["constituency"], item["allocated_amount"])
        for item in allocations_data
    ]
    cursor.executemany(
        "INSERT INTO mp_allocations (sr_no, state, mp_name, constituency, allocated_amount) VALUES (?, ?, ?, ?, ?)",
        alloc_rows
    )
    conn.commit()
    print("Real MP Allocation limit table successfully populated.")

    # 2. Seed Default Users
    print("Creating demo user accounts...")
    user_rows = [
        ("officer", hash_pw("officer123"), "Rajesh Kumar Sharma", "Monitoring Officer", "MoSPI MPLADS Division"),
        ("auditor", hash_pw("auditor123"), "Priya Venkatraman", "Auditor", "CAG Audit Cell"),
        ("admin", hash_pw("admin123"), "Sanjay Singhal", "Administrator", "MoSPI National Data Centre")
    ]
    cursor.executemany(
        "INSERT INTO users (username, password_hash, full_name, role, department) VALUES (?, ?, ?, ?, ?)",
        user_rows
    )
    conn.commit()

    # 3. Generate Projects
    print("Synthesizing ~1,000 realistic project records...")
    random.seed(42)
    raw_projects = []

    # Flagship 001
    flagship_p1 = {
        "project_id": "MPL-DEMO-001",
        "state": "Maharashtra",
        "district": "Pune",
        "constituency": "SHIRUR",
        "mp_name": "Demo MP (Anonymized for Evaluation)",
        "work_title": "Construction of Community Hall at Village Khed",
        "work_description": "Construction of Community Hall with public seating, stage area, sanitation facilities, and electrification at Gram Panchayat grounds, Ward 4, Village Khed",
        "work_category": "Community Halls",
        "sanction_amount": 2900000.0,
        "expenditure_amount": 2840000.0,
        "sanction_date": "2024-11-10",
        "expected_completion_date": "2025-11-10",
        "actual_completion_date": None,
        "status": "DELAYED",
        "implementing_agency": "Demo Infrastructure Development Agency (Anonymized)",
        "latitude": 18.8412,
        "longitude": 73.9125,
        "number_of_payments": 1,
        "payment_dates": json.dumps(["2024-12-05"]),
        "payment_amounts": json.dumps([2840000.0]),
        "data_source": "SYNTHETIC_DEMO"
    }
    raw_projects.append(flagship_p1)

    # Paired Flagship 002
    flagship_p2 = {
        "project_id": "MPL-DEMO-002",
        "state": "Maharashtra",
        "district": "Pune",
        "constituency": "SHIRUR",
        "mp_name": "Demo MP (Anonymized for Evaluation)",
        "work_title": "New Community Hall Construction near Village Khed",
        "work_description": "Construction of Community Hall with public seating, stage area, sanitation facilities, and electrification near Gram Panchayat grounds, Ward 4, Village Khed",
        "work_category": "Community Halls",
        "sanction_amount": 1420000.0,
        "expenditure_amount": 1390000.0,
        "sanction_date": "2024-08-15",
        "expected_completion_date": "2025-08-15",
        "actual_completion_date": "2025-08-25",
        "status": "COMPLETED",
        "implementing_agency": "Zila Parishad Engineering Wing",
        "latitude": 18.8462,
        "longitude": 73.9165,
        "number_of_payments": 3,
        "payment_dates": json.dumps(["2024-08-10", "2024-12-05", "2025-08-20"]),
        "payment_amounts": json.dumps([500000.0, 500000.0, 420000.0]),
        "data_source": "SYNTHETIC_DEMO"
    }
    raw_projects.append(flagship_p2)

    # Flagship 003
    flagship_p3 = {
        "project_id": "MPL-DEMO-003",
        "state": "Maharashtra",
        "district": "Pune",
        "constituency": "SHIRUR",
        "mp_name": "Demo MP (Anonymized for Evaluation)",
        "work_title": "Community Activity Hall Construction at Manchar",
        "work_description": "Standard Community Hall with multipurpose activity space and drinking water connection at Manchar Block",
        "work_category": "Community Halls",
        "sanction_amount": 1380000.0,
        "expenditure_amount": 1350000.0,
        "sanction_date": "2024-05-10",
        "expected_completion_date": "2025-05-10",
        "actual_completion_date": "2025-06-12",
        "status": "COMPLETED",
        "implementing_agency": "Public Works Department (PWD - Division 1)",
        "latitude": 18.9950,
        "longitude": 73.9390,
        "number_of_payments": 3,
        "payment_dates": json.dumps(["2024-06-15", "2024-11-20", "2025-06-12"]),
        "payment_amounts": json.dumps([480000.0, 480000.0, 390000.0]),
        "data_source": "SYNTHETIC_DEMO"
    }
    raw_projects.append(flagship_p3)

    states = list(STATE_GEO.keys())

    for i in range(4, 1001):
        pid = f"MPL-DEMO-{i:04d}"
        state = random.choice(states)
        geo = STATE_GEO[state]
        district = random.choice(geo["districts"])
        category = random.choice(CATEGORIES)
        loc_name = f"{district} Sector {random.randint(1, 18)}"

        title_template = random.choice(WORK_TITLES[category])
        work_title = title_template.format(loc=loc_name)
        work_desc = (
            f"Official MPLADS development initiative: {work_title}. "
            f"Executed to provide durable public infrastructure and community utility assets for local residents under statutory guidelines."
        )

        min_cost, max_cost = CATEGORY_BENCHMARKS[category]
        base_cost = random.uniform(min_cost, max_cost)

        lat = geo["lat"] + random.uniform(-0.4, 0.4)
        lon = geo["lon"] + random.uniform(-0.4, 0.4)

        status = random.choice(["COMPLETED", "COMPLETED", "IN_PROGRESS", "IN_PROGRESS", "SANCTIONED", "DELAYED"])
        start_year = random.choice([2023, 2024, 2025])
        start_month = random.randint(1, 12)
        sanction_dt = datetime(start_year, start_month, random.randint(1, 28))
        planned_months = random.randint(8, 16)
        expected_dt = sanction_dt + timedelta(days=planned_months * 30)

        actual_dt = None
        if status == "COMPLETED":
            actual_dt = expected_dt + timedelta(days=random.randint(-20, 45))

        agency = random.choice(AGENCIES)
        mp_name = f"Hon'ble MP ({district} Constituency - Demo Entity)"

        # Planned intentional anomaly triggers (~22% rate)
        anomaly_type = None
        if i % 18 == 0:
            anomaly_type = "COST_OUTLIER"
        elif i % 23 == 0:
            anomaly_type = "OVERLAP_PAIR"
        elif i % 29 == 0:
            anomaly_type = "STALLED_SPEND"
        elif i % 37 == 0:
            anomaly_type = "EXCESS_EXPENDITURE"
        elif i % 43 == 0:
            anomaly_type = "TIMELINE_SLIPPAGE"

        if anomaly_type == "COST_OUTLIER":
            sanction_amount = round(base_cost * random.uniform(1.85, 2.30), 2)
            expenditure_amount = round(sanction_amount * random.uniform(0.75, 0.95), 2)
            num_pmt, p_dates, p_amts = generate_payment_schedule(sanction_amount, status, is_anom=False)

        elif anomaly_type == "OVERLAP_PAIR":
            sanction_amount = round(base_cost * random.uniform(0.9, 1.1), 2)
            expenditure_amount = round(sanction_amount * random.uniform(0.7, 0.9), 2)
            prev = raw_projects[-1]
            lat = prev["latitude"] + random.uniform(-0.005, 0.005)
            lon = prev["longitude"] + random.uniform(-0.005, 0.005)
            work_title = f"Upgradation & {prev['work_title']}"
            work_desc = f"Additional development and {prev['work_description']}"
            category = prev["work_category"]
            district = prev["district"]
            state = prev["state"]
            num_pmt, p_dates, p_amts = generate_payment_schedule(sanction_amount, status, is_anom=False)

        elif anomaly_type == "STALLED_SPEND":
            sanction_amount = round(base_cost, 2)
            expenditure_amount = round(sanction_amount * 0.88, 2)
            status = "STALLED"
            num_pmt, p_dates, p_amts = 1, ["2024-04-10"], [expenditure_amount]

        elif anomaly_type == "EXCESS_EXPENDITURE":
            sanction_amount = round(base_cost, 2)
            expenditure_amount = round(sanction_amount * random.uniform(1.15, 1.25), 2)
            num_pmt, p_dates, p_amts = 3, ["2024-05-10", "2024-11-15", "2025-06-20"], [
                round(sanction_amount * 0.4, 2),
                round(sanction_amount * 0.4, 2),
                round(expenditure_amount - sanction_amount * 0.8, 2)
            ]

        elif anomaly_type == "TIMELINE_SLIPPAGE":
            sanction_amount = round(base_cost, 2)
            expenditure_amount = round(sanction_amount * 0.65, 2)
            status = "DELAYED"
            sanction_dt = datetime(2023, 5, 10)
            expected_dt = sanction_dt + timedelta(days=240)
            num_pmt, p_dates, p_amts = generate_payment_schedule(sanction_amount, status, is_anom=False)

        else:
            sanction_amount = round(base_cost * random.uniform(0.85, 1.15), 2)
            if status == "COMPLETED":
                expenditure_amount = round(sanction_amount * random.uniform(0.92, 0.99), 2)
            elif status == "IN_PROGRESS":
                expenditure_amount = round(sanction_amount * random.uniform(0.30, 0.65), 2)
            elif status == "SANCTIONED":
                expenditure_amount = 0.0
            else:
                expenditure_amount = round(sanction_amount * random.uniform(0.50, 0.80), 2)
            num_pmt, p_dates, p_amts = generate_payment_schedule(sanction_amount, status, is_anom=False)

        raw_projects.append({
            "project_id": pid,
            "state": state,
            "district": district,
            "constituency": f"{district.upper()} CONSTITUENCY",
            "mp_name": mp_name,
            "work_title": work_title,
            "work_description": work_desc,
            "work_category": category,
            "sanction_amount": sanction_amount,
            "expenditure_amount": expenditure_amount,
            "sanction_date": sanction_dt.strftime("%Y-%m-%d"),
            "expected_completion_date": expected_dt.strftime("%Y-%m-%d"),
            "actual_completion_date": actual_dt.strftime("%Y-%m-%d") if actual_dt else None,
            "status": status,
            "implementing_agency": agency,
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "number_of_payments": num_pmt,
            "payment_dates": json.dumps(p_dates),
            "payment_amounts": json.dumps(p_amts),
            "data_source": "SYNTHETIC_DEMO"
        })

    # Insert projects
    now_str = datetime.utcnow().isoformat()
    project_insert_rows = [
        (
            p["project_id"], p["state"], p["district"], p["constituency"], p["mp_name"],
            p["work_title"], p["work_description"], p["work_category"],
            p["sanction_amount"], p["expenditure_amount"],
            p["sanction_date"], p["expected_completion_date"], p["actual_completion_date"],
            p["status"], p["implementing_agency"], p["latitude"], p["longitude"],
            p["number_of_payments"], p["payment_dates"], p["payment_amounts"],
            p["data_source"], now_str
        )
        for p in raw_projects
    ]

    cursor.executemany("""
    INSERT INTO projects (
        project_id, state, district, constituency, mp_name,
        work_title, work_description, work_category,
        sanction_amount, expenditure_amount,
        sanction_date, expected_completion_date, actual_completion_date,
        status, implementing_agency, latitude, longitude,
        number_of_payments, payment_dates, payment_amounts,
        data_source, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, project_insert_rows)
    conn.commit()
    print("Projects inserted.")

    # 4. Multi-signal Anomaly Execution
    print("Running Multi-Signal Anomaly Detection Engine...")
    cost_detector = CostAnomalyDetector(raw_projects)
    timeline_detector = TimelineAnomalyDetector()
    expenditure_detector = ExpenditureAnomalyDetector()
    overlap_detector = OverlapDetector(raw_projects)
    agency_detector = AgencyAnomalyDetector(raw_projects)
    compliance_engine = ComplianceRuleEngine()
    risk_scorer = RiskScorer()

    print("Computing NLP text similarity matrix and GIS spatial proximity...")
    overlap_results = overlap_detector.evaluate_all()
    print("Overlap detection complete.")

    risk_insert_rows = []
    high_critical_count = 0

    for p in raw_projects:
        pid = p["project_id"]
        c_res = cost_detector.evaluate(p)
        t_res = timeline_detector.evaluate(p)
        e_res = expenditure_detector.evaluate(p)
        o_res = overlap_results.get(pid, {
            "score": 5.0,
            "similar_projects": [],
            "flag_note": "No spatial overlap detected",
            "is_anomaly": False
        })
        a_res = agency_detector.evaluate(p)
        comp_res = compliance_engine.evaluate(p)

        score_res = risk_scorer.calculate(p, c_res, t_res, e_res, o_res, a_res, comp_res)

        if score_res["risk_level"] in ("HIGH", "CRITICAL"):
            high_critical_count += 1

        risk_insert_rows.append((
            pid,
            score_res["overall_risk_score"],
            score_res["risk_level"],
            score_res["cost_risk_score"],
            score_res["timeline_risk_score"],
            score_res["expenditure_risk_score"],
            score_res["overlap_risk_score"],
            score_res["agency_risk_score"],
            score_res["compliance_risk_score"],
            json.dumps(score_res["contributing_factors"]),
            json.dumps(score_res["evidence"]),
            score_res["recommended_action"],
            json.dumps(score_res["similar_projects"]),
            now_str
        ))

    cursor.executemany("""
    INSERT INTO project_risks (
        project_id, overall_risk_score, risk_level,
        cost_risk_score, timeline_risk_score, expenditure_risk_score,
        overlap_risk_score, agency_risk_score, compliance_risk_score,
        contributing_factors, evidence, recommended_action, similar_projects, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, risk_insert_rows)
    conn.commit()
    print(f"Risk scoring complete. {high_critical_count} projects prioritized for verification.")

    # 5. Populate Agencies
    agency_insert_rows = []
    for agency_name, stats in agency_detector.agency_stats.items():
        agency_pids = [p["project_id"] for p in raw_projects if p["implementing_agency"] == agency_name]
        high_risk_n = sum(1 for r in risk_insert_rows if r[0] in agency_pids and r[2] in ("HIGH", "CRITICAL"))
        risk_pct = round((high_risk_n / len(agency_pids) * 100.0) if agency_pids else 0.0, 1)

        agency_insert_rows.append((
            agency_name,
            stats["district"],
            stats["state"],
            stats["total_projects"],
            round(stats["total_sanctioned_amount"], 2),
            round(stats["average_project_value"], 2),
            high_risk_n,
            risk_pct,
            "Public Infrastructure"
        ))

    cursor.executemany("""
    INSERT INTO agencies (
        agency_name, district, state, total_projects,
        total_sanctioned_amount, average_project_value,
        high_risk_projects_count, risk_percentage, primary_category
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, agency_insert_rows)
    conn.commit()

    # 6. Audit Log
    cursor.execute("""
    INSERT INTO audit_logs (user_name, user_role, action, project_id, timestamp, details)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "System AI Engine",
        "Automated Ingestion Process",
        "Full Anomaly Detection & Ingestion Pass Executed",
        None,
        datetime.utcnow().strftime("%d %b %Y, %I:%M %p"),
        "Ingested real MP allocations and completed multi-signal anomaly evaluation across 1,000 projects."
    ))
    conn.commit()

    # Verify MPL-DEMO-001
    cursor.execute("SELECT * FROM project_risks WHERE project_id = 'MPL-DEMO-001'")
    demo1 = cursor.fetchone()
    print(f"\n=======================================================")
    print(f"FLAGSHIP DEMO SHOWCASE VERIFICATION: MPL-DEMO-001")
    print(f"Overall Risk Score: {demo1['overall_risk_score']} / 100 ({demo1['risk_level']})")
    print(f"Cost Score: {demo1['cost_risk_score']}, Timeline Score: {demo1['timeline_risk_score']}, Overlap Score: {demo1['overlap_risk_score']}")
    print(f"Recommended Action: {demo1['recommended_action']}")
    print(f"Evidence factors: {demo1['contributing_factors']}")
    print(f"=======================================================\n")

    conn.close()
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
