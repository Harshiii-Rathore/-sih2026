"""
Timeline Anomaly Detection Engine.
Calculates project duration deviations, delay velocities, and stalled project risk.
"""

from datetime import datetime
from typing import Dict, Any

REFERENCE_DATE = datetime(2026, 9, 10)  # Hackathon reference timeline anchor

class TimelineAnomalyDetector:
    def __init__(self):
        pass

    def _parse_date(self, d_str: str) -> datetime:
        if not d_str:
            return REFERENCE_DATE
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                return datetime.strptime(d_str.strip(), fmt)
            except ValueError:
                continue
        return REFERENCE_DATE

    def evaluate(self, project: Dict[str, Any]) -> Dict[str, Any]:
        s_date = self._parse_date(project.get("sanction_date", "2024-01-01"))
        e_date = self._parse_date(project.get("expected_completion_date", "2025-01-01"))
        
        status = project.get("status", "IN_PROGRESS")
        act_date_str = project.get("actual_completion_date")
        if act_date_str and status == "COMPLETED":
            end_point = self._parse_date(act_date_str)
        else:
            end_point = REFERENCE_DATE

        # Duration in months (approx 30.4 days per month)
        expected_days = max(30, (e_date - s_date).days)
        expected_months = round(expected_days / 30.4, 1)

        elapsed_days = max(30, (end_point - s_date).days)
        elapsed_months = round(elapsed_days / 30.4, 1)

        # Deviation percentage
        deviation_pct = ((elapsed_months - expected_months) / expected_months) * 100.0

        # Risk scoring
        if status == "COMPLETED":
            if deviation_pct <= 10.0:
                risk_score = 5.0
            elif deviation_pct <= 30.0:
                risk_score = 25.0
            elif deviation_pct <= 60.0:
                risk_score = 55.0
            else:
                risk_score = min(85.0, 60.0 + (deviation_pct - 60.0) * 0.5)
        elif status == "STALLED":
            risk_score = min(100.0, max(75.0, 75.0 + deviation_pct * 0.3))
        else:  # IN_PROGRESS or DELAYED
            if deviation_pct <= 0.0:
                risk_score = max(5.0, 15.0 + deviation_pct * 0.2)
            elif deviation_pct <= 30.0:
                risk_score = 20.0 + (deviation_pct / 30.0) * 25.0  # 20 to 45
            elif deviation_pct <= 65.0:
                risk_score = 45.0 + ((deviation_pct - 30.0) / 35.0) * 30.0  # 45 to 75
            else:
                risk_score = min(100.0, 75.0 + ((deviation_pct - 65.0) / 50.0) * 25.0)

        # Qualitative note
        if deviation_pct >= 60.0:
            flag_note = f"Execution duration ({elapsed_months:.0f} mo) is {deviation_pct:+.1f}% beyond scheduled deadline ({expected_months:.0f} mo)"
        elif deviation_pct >= 25.0:
            flag_note = f"Project delayed by {deviation_pct:+.1f}% against planned duration"
        elif status == "STALLED":
            flag_note = f"Work has stalled with no progress recorded for {elapsed_months:.0f} months"
        else:
            flag_note = "Timeline execution within standard tolerances"

        return {
            "score": round(float(risk_score), 1),
            "expected_months": expected_months,
            "elapsed_months": elapsed_months,
            "delay_percentage": round(float(deviation_pct), 1),
            "flag_note": flag_note,
            "is_anomaly": deviation_pct >= 50.0 or status == "STALLED"
        }
