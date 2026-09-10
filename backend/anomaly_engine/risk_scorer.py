"""
Transparent & Explainable Risk Scoring Engine.
Synthesizes multi-dimensional anomaly signals into an auditable 0-100 score with quantified evidence.
"""

from typing import Dict, Any, List
from backend.anomaly_engine.config import RISK_WEIGHTS, RISK_LEVEL_THRESHOLDS

class RiskScorer:
    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or RISK_WEIGHTS

    def classify_risk_level(self, score: float) -> str:
        if score >= 80.0:
            return "CRITICAL"
        elif score >= 60.0:
            return "HIGH"
        elif score >= 30.0:
            return "MEDIUM"
        else:
            return "LOW"

    def determine_recommended_action(self, risk_level: str, factors: List[Dict[str, Any]]) -> str:
        has_overlap = any("overlap" in f.get("dimension", "").lower() for f in factors)
        has_cost = any("cost" in f.get("dimension", "").lower() for f in factors)
        has_compliance = any("compliance" in f.get("dimension", "").lower() for f in factors)

        if risk_level == "CRITICAL":
            if has_overlap:
                return "Prioritize for joint on-site GIS boundary & physical asset verification with implementing agency."
            elif has_compliance:
                return "Prioritize for administrative inquiry & sanction expenditure reconciliation."
            else:
                return "Prioritize for urgent physical inspection and structural rate analysis verification."
        elif risk_level == "HIGH":
            if has_cost:
                return "Prioritize for detailed rate analysis & schedule of rates (SoR) document verification."
            else:
                return "Schedule for targeted milestone audit and measurement book (MB) inspection."
        elif risk_level == "MEDIUM":
            return "Include in routine quarterly district audit sample for physical milestone verification."
        else:
            return "Standard periodic monitoring; progress metrics aligned with scheme benchmarks."

    def generate_explanation_summary(self, project_id: str, factors: List[Dict[str, Any]], risk_level: str) -> str:
        """Generate human-readable audit brief."""
        if not factors or risk_level == "LOW":
            return f"Project {project_id} exhibits normal execution characteristics consistent with regional peer benchmarks."

        factor_phrases = [f["flag_note"] for f in factors[:3]]
        joined = "; ".join(factor_phrases)
        return (
            f"Project {project_id} has been prioritized for verification ({risk_level} Risk) "
            f"primarily because: {joined}. "
            f"These findings indicate potential scope duplication, timeline slippage, or cost variance requiring human auditor review."
        )

    def calculate(
        self,
        project: Dict[str, Any],
        cost_res: Dict[str, Any],
        timeline_res: Dict[str, Any],
        expenditure_res: Dict[str, Any],
        overlap_res: Dict[str, Any],
        agency_res: Dict[str, Any],
        compliance_res: Dict[str, Any]
    ) -> Dict[str, Any]:
        c_score = cost_res["score"]
        t_score = timeline_res["score"]
        e_score = expenditure_res["score"]
        o_score = overlap_res["score"]
        a_score = agency_res["score"]
        comp_score = compliance_res["score"]

        # Weighted composite score
        overall = (
            c_score * self.weights["cost"] +
            t_score * self.weights["timeline"] +
            o_score * self.weights["overlap"] +
            e_score * self.weights["expenditure"] +
            a_score * self.weights["agency"] +
            comp_score * self.weights["compliance"]
        )

        overall = min(100.0, max(0.0, overall))
        risk_level = self.classify_risk_level(overall)

        # Ranked contributing factors
        factors = []
        dimensions = [
            ("Cost Anomaly", c_score, cost_res["flag_note"], cost_res["is_anomaly"]),
            ("Timeline Anomaly", t_score, timeline_res["flag_note"], timeline_res["is_anomaly"]),
            ("Potential Spatial & Description Overlap", o_score, overlap_res["flag_note"], overlap_res["is_anomaly"]),
            ("Expenditure Pattern", e_score, expenditure_res["flag_note"], expenditure_res["is_anomaly"]),
            ("Agency Pattern", a_score, agency_res["flag_note"], agency_res["is_anomaly"]),
            ("Regulatory Compliance", comp_score, compliance_res["flag_note"], compliance_res["is_anomaly"]),
        ]

        # Sort dimensions by severity of score
        dimensions.sort(key=lambda x: x[1], reverse=True)

        for name, score, note, is_anom in dimensions:
            if is_anom or score >= 35.0:
                factors.append({
                    "dimension": name,
                    "score": score,
                    "flag_note": note
                })

        rec_action = self.determine_recommended_action(risk_level, factors)
        explanation = self.generate_explanation_summary(project["project_id"], factors, risk_level)

        evidence = {
            "sanction_amount": float(project.get("sanction_amount", 0.0)),
            "expenditure_amount": float(project.get("expenditure_amount", 0.0)),
            "peer_median_cost": cost_res.get("peer_median"),
            "cost_deviation_pct": cost_res.get("deviation_pct"),
            "expected_months": timeline_res.get("expected_months"),
            "elapsed_months": timeline_res.get("elapsed_months"),
            "delay_percentage": timeline_res.get("delay_percentage"),
            "payment_tranches": expenditure_res.get("num_payments"),
            "utilization_pct": expenditure_res.get("utilization_pct"),
            "agency_projects_count": agency_res.get("total_agency_projects"),
            "agency_cost_premium_pct": agency_res.get("cost_premium_pct"),
            "agency_value_deviation_pct": agency_res.get("cost_premium_pct"),
            "agency_concentration_pct": agency_res.get("district_share_pct"),
            "compliance_violations": compliance_res.get("violations", []),
            "explanation": explanation
        }

        return {
            "overall_risk_score": round(overall, 1),
            "risk_level": risk_level,
            "cost_risk_score": round(c_score, 1),
            "timeline_risk_score": round(t_score, 1),
            "expenditure_risk_score": round(e_score, 1),
            "overlap_risk_score": round(o_score, 1),
            "agency_risk_score": round(a_score, 1),
            "compliance_risk_score": round(comp_score, 1),
            "contributing_factors": factors,
            "evidence": evidence,
            "recommended_action": rec_action,
            "similar_projects": overlap_res.get("similar_projects", [])
        }
