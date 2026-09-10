# NIRIKSHAN AI (निरीक्षण AI)

> **"From monitoring projects to identifying what needs attention."**  
> *AI-Powered Early-Warning & Decision-Support System for MPLADS Implementation*

**Smart India Hackathon 2026 • Problem Statement SIH26102**  
**Organization:** Ministry of Statistics & Programme Implementation (MoSPI)  
**Scheme:** Members of Parliament Local Area Development Scheme (MPLADS)  

---

## 1. Executive Summary & Core Principle

In large-scale public infrastructure schemes such as MPLADS, auditing thousands of distributed works across 543 Parliamentary constituencies with limited field personnel is a fundamental challenge. Traditional monitoring is manual and retrospective, often discovering cost inflation, timeline overruns, or overlapping works only after funds have been fully disbursed.

**NIRIKSHAN AI** transforms this paradigm by serving as an intelligent triage layer:
> **"We don't replace auditors. We help them know where to look first."**

### Important Ethical & Algorithmic Guardrails
1. **Explainable Triage, Not Accusations:** The system flags projects with quantified metrics as **"Requires verification"** or **"Unusual pattern detected"**; it **never** makes definitive accusations such as "Fraud detected".
2. **Transparent Weights & Open Formulations:** Risk scores (0–100) are not opaque black boxes. Every score is mathematically broken down into itemized cost deviation %, duration delay %, NLP descriptive overlap %, and payment concentration metrics.
3. **No Unauthorized Access:** Built with a clean provider interface (`MPLADSDataProvider`) so future authorized integrations with eSAKSHI can be connected via government APIs without scraping or bypassing authentication.

---

## 2. Data Reality & Integrity Disclosures

### A. Real Allocation Data Ingested
The system directly ingests the official MoSPI allocation dataset:
- **File:** `Allocated Limit for Honble MPs.csv`
- **Scope:** Real expenditure limits for all 543 Parliamentary constituencies across India totaling over **₹83,336 Crores**.
- **Usage:** Ingested into the database table `mp_allocations` for real state-level and constituency-level statutory financial ceiling analysis. The original CSV is preserved unmodified.

### B. Synthetic Project Telemetry for Prototype
Because scheme-level allocation limits do not contain fine-grained project telemetry (milestone completion dates, measurement books, spatial coordinates, payment tranches), NIRIKSHAN AI pairs the real allocation data with **1,000 realistic synthetic MPLADS project records**.
- **Explicit Label:** Every synthetic record is marked internally and displayed on-screen as `data_source = "SYNTHETIC_DEMO"`.
- **Ethics Rule:** No real MP, district magistrate, or implementing agency is represented as fraudulent. Anonymized demo entities (e.g. *"Demo Infrastructure Development Agency"*) are used for intentionally injected anomalous cases.
- **Showcase Demo Flagship:** `MPL-DEMO-001` (*"Construction of Community Hall at Village Khed"*), demonstrating cost deviation (+104%), timeline delay (+83%), and nearby spatial overlap (0.7 km away, 87% descriptive similarity).

---

## 3. Multi-Signal Anomaly Detection Engine

Rather than relying on an opaque machine learning score, NIRIKSHAN AI fuses six independent analytical signals:

```
                          ┌───────────────────────────┐
                          │   MPLADS Project Data     │
                          └─────────────┬─────────────┘
                                        │
        ┌───────────────┬───────────────┼───────────────┬───────────────┐
        ▼               ▼               ▼               ▼               ▼
┌───────────────┐┌───────────────┐┌───────────────┐┌───────────────┐┌───────────────┐
│ Cost Anomaly  ││Timeline Delay ││ Spatial & NLP ││  Expenditure  ││Agency Pattern │
│ (Peer IQR/Dev)││(Duration Dev) ││ Overlap (TF-  ││ (Tranches &   ││ Concentration │
│  Weight: 25%  ││  Weight: 20%  ││IDF + Haversine││ Frontloading) ││  Weight: 10%  │
└───────┬───────┘└───────┬───────┘│  Weight: 20%  │└───────┬───────┘└───────┬───────┘
        │               │         └───────┬───────┘        │               │
        │               │                 │                │               │
        └───────────────┴────────┬────────┴────────────────┴───────────────┘
                                 │
                                 ▼
                   ┌───────────────────────────┐
                   │ Deterministic Rule Engine │ (Weight: 10%)
                   └─────────────┬─────────────┘
                                 │
                                 ▼
                   ┌───────────────────────────┐
                   │ Composite Risk Scorer     │
                   │ (0 - 100 Auditable Score) │
                   └─────────────┬─────────────┘
                                 │
                                 ▼
                   ┌───────────────────────────┐
                   │ Explainable AI (XAI)      │
                   │ Evidence + Action Dossier │
                   └───────────────────────────┘
```

### A. Cost Anomaly Engine (Weight: 25%)
- Segments projects by work category (e.g., *Community Halls, Roads, Drinking Water*) and regional cohorts.
- Computes category median, Interquartile Range (IQR), and percentage deviation:
  $$\Delta_{\text{cost}} = \frac{\text{Sanction Amount} - \text{Peer Median}}{\text{Peer Median}} \times 100$$
- Flags projects with statistical cost inflation (+40% to +140% above peer medians).

### B. Timeline Anomaly Engine (Weight: 20%)
- Compares administrative sanction date, scheduled completion deadline, and actual/current elapsed months.
- Computes delay velocity and duration deviation:
  $$\Delta_{\text{duration}} = \frac{\text{Elapsed Months} - \text{Planned Months}}{\text{Planned Months}} \times 100$$
- Detects stalled projects exceeding 1.5× standard completion windows.

### C. NLP Descriptive & Spatial Overlap Engine (Weight: 20%)
- Computes TF-IDF n-gram vectorization and cosine similarity over project titles and work descriptions.
- Calculates Haversine great-circle distance between geospatial coordinates:
  $$d = 2R \arcsin \sqrt{\sin^2 \frac{\Delta \phi}{2} + \cos \phi_1 \cos \phi_2 \sin^2 \frac{\Delta \lambda}{2}}$$
- Identifies projects located within $< 2.0\text{ km}$ with text similarity $> 75\%$ as **"Potential overlap"** to prevent duplicate asset sanctioning on identical footprints.

### D. Expenditure & Payment Pattern Anomaly (Weight: 15%)
- Evaluates fund disbursement timing, tranche release velocities, and utilization rates.
- Flags anomalous patterns such as 100% upfront lump-sum payouts on incomplete infrastructure works, or heavy fund release on stalled projects.

### E. Implementing Agency Concentration (Weight: 10%)
- Evaluates agency market share within districts and average project ticket-size premiums compared to peer district agencies.

### F. Deterministic Compliance Rule Engine (Weight: 10%)
- Executes non-probabilistic statutory checks:
  1. Expenditure exceeding approved administrative sanction ($E > S$).
  2. Completion date preceding sanction date.
  3. Stalled projects with zero physical progress for $> 18$ months.
  4. Geospatial coordinates falling outside statutory Indian boundaries.

### Transparent Risk Level Mapping
| Score Range | Risk Classification | Recommended Auditor Action Protocol |
| :--- | :--- | :--- |
| **80 – 100** | <span style="color:#ef4444;font-weight:bold;">CRITICAL</span> | Prioritize for joint on-site GIS boundary & physical asset verification. |
| **60 – 79** | <span style="color:#f97316;font-weight:bold;">HIGH</span> | Prioritize for detailed rate analysis & schedule of rates (SoR) document verification. |
| **30 – 59** | <span style="color:#f59e0b;font-weight:bold;">MEDIUM</span> | Include in routine quarterly district audit sample for milestone check. |
| **0 – 29** | <span style="color:#10b981;font-weight:bold;">LOW</span> | Standard periodic monitoring; progress metrics aligned with scheme benchmarks. |

---

## 4. Technology Stack

- **Frontend:**
  - React 19 + TypeScript + Vite
  - Tailwind CSS v4 (Clean, national intelligence dashboard styling)
  - Recharts (Risk distribution histogram, regional density, category breakdown)
  - Leaflet (Interactive India geospatial surveillance map)
  - Lucide React (Government portal iconography)
- **Backend:**
  - Python 3.14 + FastAPI
  - Python native `sqlite3` database engine with parameterized SQL queries (Zero external ORM startup overhead, seamless future PostgreSQL migration path)
  - Scikit-learn (`TfidfVectorizer`, `cosine_similarity`) & NumPy
  - PyJWT (Role-based authentication)
  - ReportLab (Formal MoSPI-styled PDF investigation dossier generator)

---

## 5. Hackathon 2-Minute Demo Flow

The prototype is optimized for an impactful, flawless demo before judges:

```
[1. LOGIN] ────────► [2. DASHBOARD] ────────► [3. MONITORING]
Select "Auditor"      Inspect 1,000 works,     Default sorted by
Role (1-Click)        Live AI Insights, KPIs   Risk Score (Desc)
                            │
                            ▼
[6. PDF DOSSIER] ◄─── [5. DETAILS] ◄──────── [4. FLAGSHIP CASE]
1-Click MoSPI         "Why Was This Flagged?"  Click MPL-DEMO-001
Official Report PDF   +104% Cost, +83% Time,   (Score 80.3 CRITICAL)
                      0.7 km Overlap (87%)
```

1. **Login Screen:** Click the pre-filled **"Auditor (CAG Audit)"** button for instantaneous role-based entry.
2. **Dashboard:** Judge sees 1,000 monitored works, total sanction (₹1,924+ Cr), live dynamic AI insights, risk distribution histogram, and state breakdown.
3. **Flagship Demo Banner:** Click **"Investigate Case"** on `MPL-DEMO-001`.
4. **Explainable AI (XAI) Breakdown:**
   - **Cost Anomaly:** Project Cost ₹29.0L vs Peer Category Median ₹14.2L (+104.2% deviation).
   - **Timeline Anomaly:** 22 months elapsed vs 12 months scheduled (+83.3% delay).
   - **Potential Overlap:** Similar work (*"New Community Hall Construction near Village Khed"*) found 0.7 km away with 87% similarity.
   - **Disbursement Pattern:** 100% upfront single lump-sum payout.
   - **Recommended Action:** *"Prioritize for joint on-site GIS boundary & physical asset verification with implementing agency."*
5. **Similar Works Comparison Table:** Demonstrates peer projects side-by-side.
6. **Geospatial Map:** Switch to **Geospatial Map** tab to see color-coded risk markers across India and click markers for instant telemetry inspection.
7. **Agency Analytics:** Switch to **Agency Analytics** tab to view concentration risks.
8. **Real MP Limits:** Switch to **Real MP Limits** tab to view all 543 real MPs from `Allocated Limit for Honble MPs.csv`.
9. **AI Pipeline:** Switch to **AI Risk Engine** tab to present the 9-stage algorithmic pipeline to technical judges.
10. **Generate PDF Report:** Click **"Generate Official Investigation Report (PDF)"** to download a print-ready audit dossier.

---

## 6. Project Directory Structure

```
sih2026/
├── Allocated Limit for Honble MPs.csv   # Real MoSPI MP limits CSV (543 MPs, ₹83,336+ Cr)
├── README.md                           # Comprehensive documentation & architecture guide
│
├── backend/                            # FastAPI Python Backend
│   ├── database.py                     # SQLite3 connection & table schema DDL
│   ├── models.py                       # Entity model specifications
│   ├── data_provider.py                # Decoupled MPLADSDataProvider abstraction
│   ├── seed_database.py                # Ingestion, synthetic generator & anomaly runner
│   ├── report_generator.py             # ReportLab PDF investigation dossier builder
│   ├── main.py                         # REST API endpoints & JWT authentication
│   ├── nirikshan.db                    # Ingested SQLite database
│   ├── anomaly_engine/                 # Independent multi-signal anomaly modules
│   │   ├── config.py                   # Configurable risk scoring weights & thresholds
│   │   ├── cost_detector.py            # Peer category median & IQR deviation calculus
│   │   ├── timeline_detector.py        # Execution duration & delay velocity calculus
│   │   ├── expenditure_detector.py     # Tranche concentration & frontload analysis
│   │   ├── overlap_detector.py         # TF-IDF Cosine similarity & Haversine distance
│   │   ├── agency_detector.py          # Implementing agency concentration analysis
│   │   ├── compliance_rules.py         # Deterministic regulatory rule engine
│   │   └── risk_scorer.py              # Composite weighted scoring & XAI synthesis
│   └── tests/                          # Automated backend test suite
│       └── test_backend.py             # 13 unit & integration tests
│
└── frontend/                           # React 19 + TypeScript + Tailwind v4 Portal
    ├── package.json                    # Frontend dependencies
    ├── vite.config.ts                  # Vite build configuration
    ├── tsconfig.app.json               # TypeScript compiler options
    └── src/
        ├── types.ts                    # TypeScript interface definitions
        ├── api.ts                      # REST API client
        ├── index.css                   # Tailwind v4 & Leaflet styling
        ├── App.tsx                     # Main navigation and state controller
        ├── components/
        │   ├── Navbar.tsx              # Official MoSPI header & role switcher
        │   ├── RiskBadge.tsx           # Color-coded risk level indicator
        │   ├── MetricCard.tsx          # Analytics KPI card component
        │   └── AuditLogModal.tsx       # Live audit trail modal
        └── pages/
            ├── LoginPage.tsx           # Role-based login with 1-click demo presets
            ├── DashboardPage.tsx       # Executive overview & dynamic AI insights
            ├── ProjectMonitoringPage.tsx # Searchable/filterable project triage grid
            ├── ProjectDetailPage.tsx   # Deep-dive XAI investigation dossier
            ├── MapView.tsx             # Interactive Leaflet geospatial map
            ├── AgencyAnalyticsPage.tsx # Implementing agency performance profiler
            ├── RealAllocationsPage.tsx # Real CSV MP limit explorer
            └── AiPipelinePage.tsx      # Interactive AI pipeline architecture
```

---

## 7. How to Run Locally

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Node.js 18+ and npm

### 1. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Seed the database (ingests CSV, generates 1,000 projects, runs anomaly engine)
python3 -m backend.seed_database

# Start FastAPI backend server
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
Backend API will be live at `http://localhost:8000`.  
Swagger interactive documentation available at `http://localhost:8000/docs`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend Web Portal will be live at `http://localhost:5173`.

### 3. Run Automated Tests
```bash
python3 -m unittest backend/tests/test_backend.py
```
*(All 13 tests execute in under 40 milliseconds)*

---

## 8. Credentials for Demo

| Role | Username | Password | Notes |
| :--- | :--- | :--- | :--- |
| **Auditor** | `auditor` | `auditor123` | Recommended for hackathon demo (Full audit dossier access) |
| **Monitoring Officer** | `officer` | `officer123` | MoSPI Division review mode |
| **Administrator** | `admin` | `admin123` | Data Centre supervision mode |

*(Pre-filled 1-click buttons are available on the Login screen).*

---

## 9. Future Scope & Production Roadmap
- **Authorized eSAKSHI Integration:** Connect `AuthorizedESAKSHIDataProvider` with MoSPI's official OAuth2/mTLS API endpoints upon administrative clearance.
- **Satellite Remote Sensing:** Ingest Sentinel-2 multispectral imagery to verify physical asset construction footprints over time.
- **Graph Neural Networks (GNN):** Expand implementing agency pattern detection into entity relationship graph analysis to detect circular sub-contracting networks.
- **Offline Mobile Triage App:** Lightweight mobile application for district revenue officers to conduct on-site physical geotagging without continuous network connectivity.
