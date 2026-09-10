"""
Unit & Integration Tests for NIRIKSHAN AI.
Validates anomaly algorithms, risk scoring, data ingestion, and FastAPI endpoints.
"""

import unittest
import json
from backend.database import get_connection
from backend.anomaly_engine.cost_detector import CostAnomalyDetector
from backend.anomaly_engine.timeline_detector import TimelineAnomalyDetector
from backend.anomaly_engine.expenditure_detector import ExpenditureAnomalyDetector
from backend.anomaly_engine.overlap_detector import haversine_distance, OverlapDetector
from backend.anomaly_engine.compliance_rules import ComplianceRuleEngine
from backend.anomaly_engine.risk_scorer import RiskScorer
import backend.main as main_app

class TestNIRIKSHANBackend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = get_connection()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_haversine_distance(self):
        dist = haversine_distance(19.0760, 72.8777, 18.5204, 73.8567)
        self.assertTrue(110 < dist < 140, f"Unexpected distance: {dist}")

    def test_cost_anomaly_detector(self):
        sample_projects = [
            {"work_category": "Community Halls", "sanction_amount": 1200000},
            {"work_category": "Community Halls", "sanction_amount": 1400000},
            {"work_category": "Community Halls", "sanction_amount": 1500000},
        ]
        detector = CostAnomalyDetector(sample_projects)
        norm_res = detector.evaluate({"work_category": "Community Halls", "sanction_amount": 1400000})
        self.assertFalse(norm_res["is_anomaly"])

        outlier_res = detector.evaluate({"work_category": "Community Halls", "sanction_amount": 2900000})
        self.assertTrue(outlier_res["is_anomaly"])
        self.assertTrue(outlier_res["deviation_pct"] > 100)

    def test_timeline_anomaly_detector(self):
        detector = TimelineAnomalyDetector()
        delayed_proj = {
            "sanction_date": "2024-01-01",
            "expected_completion_date": "2025-01-01",
            "status": "DELAYED"
        }
        res = detector.evaluate(delayed_proj)
        self.assertTrue(res["delay_percentage"] > 50)
        self.assertTrue(res["score"] > 60)

    def test_compliance_rules(self):
        engine = ComplianceRuleEngine()
        bad_proj = {
            "sanction_amount": 1000000,
            "expenditure_amount": 1250000,
            "status": "COMPLETED",
            "latitude": 19.0,
            "longitude": 75.0,
            "work_description": "A very long descriptive detail about the project."
        }
        res = engine.evaluate(bad_proj)
        self.assertTrue(res["is_anomaly"])
        self.assertTrue(any("exceeds" in v for v in res["violations"]))

    def test_risk_scorer_weights(self):
        scorer = RiskScorer()
        self.assertEqual(scorer.classify_risk_level(85.0), "CRITICAL")
        self.assertEqual(scorer.classify_risk_level(65.0), "HIGH")
        self.assertEqual(scorer.classify_risk_level(45.0), "MEDIUM")
        self.assertEqual(scorer.classify_risk_level(15.0), "LOW")

    def test_endpoint_health(self):
        res = main_app.health_check()
        self.assertEqual(res["status"], "ok")

    def test_endpoint_dashboard(self):
        data = main_app.get_dashboard_data(conn=self.conn)
        self.assertIn("kpis", data)
        self.assertIn("risk_distribution", data)
        self.assertIn("ai_insights", data)
        kpis = data["kpis"]
        self.assertGreater(kpis["total_projects"], 500)
        self.assertEqual(
            kpis["total_projects"],
            kpis["normal_tolerance_count"] + kpis["projects_requiring_verification"]
        )
        self.assertEqual(
            kpis["normal_tolerance_count"],
            kpis["low_risk_projects"] + kpis["medium_risk_projects"]
        )
        self.assertEqual(
            kpis["projects_requiring_verification"],
            kpis["critical_projects"] + kpis["high_risk_projects"]
        )

    def test_endpoint_projects_list(self):
        data = main_app.list_projects(page=1, page_size=10, search=None, state=None, district=None, category=None, risk_level=None, status=None, sort_by="risk_score", sort_dir="desc", conn=self.conn)
        self.assertIn("items", data)
        self.assertEqual(len(data["items"]), 10)
        self.assertGreaterEqual(data["items"][0]["risk_score"], data["items"][1]["risk_score"])

    def test_endpoint_flagship_project_details(self):
        data = main_app.get_project_details("MPL-DEMO-001", conn=self.conn)
        self.assertEqual(data["project"]["project_id"], "MPL-DEMO-001")
        self.assertIn("risk", data)
        self.assertGreaterEqual(data["risk"]["overall_risk_score"], 80.0)
        self.assertIn(data["risk"]["risk_level"], ["HIGH", "CRITICAL"])
        self.assertIn("similar_projects", data["risk"])
        # Verify non-accusatory overlap dimension name
        factors = [f["dimension"] for f in data["risk"]["contributing_factors"]]
        self.assertIn("Potential Spatial & Description Overlap", factors)

    def test_endpoint_map(self):
        data = main_app.get_map_markers(state=None, risk_level=None, category=None, limit=50, conn=self.conn)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertIn("latitude", data[0])
        self.assertIn("longitude", data[0])

    def test_endpoint_agencies(self):
        data = main_app.get_agencies(conn=self.conn)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertIn("agency_name", data[0])

    def test_endpoint_allocations_real_csv(self):
        data = main_app.get_real_allocations(state=None, conn=self.conn)
        self.assertEqual(data["data_source"], "REAL_GOVT_CSV")
        self.assertEqual(data["total_mps"], 543)
        self.assertGreater(data["total_allocated_limit_inr"], 80000000000)

    def test_endpoint_pdf_report_generation(self):
        resp = main_app.download_investigation_report("MPL-DEMO-001", conn=self.conn)
        self.assertEqual(resp.media_type, "application/pdf")
        self.assertTrue(len(resp.body) > 1000)
        self.assertIn("NIRIKSHAN_Investigation_Dossier_MPL-DEMO-001.pdf", resp.headers["Content-Disposition"])

if __name__ == "__main__":
    unittest.main()
