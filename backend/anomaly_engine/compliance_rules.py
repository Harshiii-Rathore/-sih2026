"""
Compliance & Regulatory Rule Engine.
Executes deterministic, non-probabilistic checks against statutory MPLADS norms.
"""

from datetime import datetime
from typing import Dict, Any, List

class ComplianceRuleEngine:
    def __init__(self):
        pass

    def _parse_date(self, d_str: str):
        if not d_str:
            return None
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                return datetime.strptime(d_str.strip(), fmt)
            except ValueError:
                continue
        return None

    def evaluate(self, project: Dict[str, Any]) -> Dict[str, Any]:
        violations: List[str] = []
        risk_penalty = 0.0

        sanction = float(project.get("sanction_amount", 0.0))
        expenditure = float(project.get("expenditure_amount", 0.0))
        status = project.get("status", "IN_PROGRESS")
        lat = float(project.get("latitude", 0.0))
        lon = float(project.get("longitude", 0.0))

        s_date = self._parse_date(project.get("sanction_date"))
        e_date = self._parse_date(project.get("expected_completion_date"))
        a_date = self._parse_date(project.get("actual_completion_date"))

        # Rule 1: Expenditure > Sanction
        if expenditure > sanction:
            violations.append(f"Financial Compliance: Expenditure (₹{expenditure:,.0f}) exceeds approved administrative sanction (₹{sanction:,.0f})")
            risk_penalty += 45.0

        # Rule 2: Inverted or invalid dates
        if s_date and e_date and e_date < s_date:
            violations.append("Date Integrity: Scheduled completion date precedes administrative sanction date")
            risk_penalty += 35.0

        if s_date and a_date and a_date < s_date:
            violations.append("Date Integrity: Actual completion recorded prior to sanction date")
            risk_penalty += 40.0

        # Rule 3: Geo-coordinate validation (India bounds roughly lat 6-37, lon 68-98)
        if not (6.0 <= lat <= 38.0 and 68.0 <= lon <= 98.0):
            violations.append(f"GIS Compliance: Missing or out-of-boundary geospatial coordinates ({lat}, {lon})")
            risk_penalty += 25.0

        # Rule 4: Mandatory descriptive attributes
        desc = project.get("work_description", "").strip()
        if len(desc) < 15:
            violations.append("Metadata Compliance: Insufficient or missing project scope documentation")
            risk_penalty += 20.0

        # Rule 5: Unusually long stalled/sanctioned status without progress
        if status == "STALLED" and expenditure == 0.0 and s_date:
            ref_date = datetime(2026, 9, 10)
            months_elapsed = (ref_date - s_date).days / 30.4
            if months_elapsed > 18:
                violations.append(f"Execution Compliance: Zero financial/physical progress for {months_elapsed:.0f} months since sanction")
                risk_penalty += 30.0

        # Base score
        compliance_risk_score = min(100.0, risk_penalty if violations else 5.0)

        flag_note = " • ".join(violations) if violations else "All statutory guidelines & data completeness checks passed"

        return {
            "score": round(compliance_risk_score, 1),
            "violations_count": len(violations),
            "violations": violations,
            "flag_note": flag_note,
            "is_anomaly": len(violations) > 0
        }
