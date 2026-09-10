"""
Cost Anomaly Detection Engine.
Calculates peer median, IQR, and statistical deviation for project sanction amounts.
"""

from typing import Dict, Any, List
import numpy as np

class CostAnomalyDetector:
    def __init__(self, projects: List[Dict[str, Any]]):
        self.peer_groups: Dict[str, List[float]] = {}
        self.peer_stats: Dict[str, Dict[str, float]] = {}

        # Group sanction amounts by work_category
        for p in projects:
            cat = p.get("work_category", "Other Eligible Works")
            amount = float(p.get("sanction_amount", 0.0))
            if cat not in self.peer_groups:
                self.peer_groups[cat] = []
            self.peer_groups[cat].append(amount)

        # Precompute robust statistics per category
        for cat, amounts in self.peer_groups.items():
            arr = np.array(amounts)
            median = float(np.median(arr))
            q25 = float(np.percentile(arr, 25))
            q75 = float(np.percentile(arr, 75))
            iqr = q75 - q25
            self.peer_stats[cat] = {
                "median": median,
                "q25": q25,
                "q75": q75,
                "iqr": iqr if iqr > 0 else (median * 0.25),
                "count": len(amounts)
            }

    def evaluate(self, project: Dict[str, Any]) -> Dict[str, Any]:
        cat = project.get("work_category", "Other Eligible Works")
        amount = float(project.get("sanction_amount", 0.0))
        stats = self.peer_stats.get(cat, {
            "median": amount if amount > 0 else 1.0,
            "q25": amount * 0.8,
            "q75": amount * 1.2,
            "iqr": amount * 0.4,
            "count": 1
        })

        median = stats["median"] if stats["median"] > 0 else 1.0
        deviation_pct = ((amount - median) / median) * 100.0

        # Calculate risk score 0 - 100
        if deviation_pct <= 10.0:
            risk_score = max(0.0, deviation_pct * 1.5)  # 0 to 15
        elif deviation_pct <= 35.0:
            risk_score = 15.0 + ((deviation_pct - 10.0) / 25.0) * 25.0  # 15 to 40
        elif deviation_pct <= 70.0:
            risk_score = 40.0 + ((deviation_pct - 35.0) / 35.0) * 30.0  # 40 to 70
        elif deviation_pct <= 110.0:
            risk_score = 70.0 + ((deviation_pct - 70.0) / 40.0) * 20.0  # 70 to 90
        else:
            excess = min(deviation_pct - 110.0, 100.0)
            risk_score = min(100.0, 90.0 + (excess / 100.0) * 10.0)

        # Determine qualitative flag
        if deviation_pct >= 80.0:
            flag_note = f"Cost is {deviation_pct:+.1f}% above category median (₹{median:,.0f})"
        elif deviation_pct >= 40.0:
            flag_note = f"Cost is {deviation_pct:+.1f}% higher than peer average (₹{median:,.0f})"
        elif deviation_pct <= -50.0:
            flag_note = f"Cost is {abs(deviation_pct):.1f}% unusually lower than category median"
        else:
            flag_note = "Cost is aligned with peer benchmarks"

        return {
            "score": round(float(risk_score), 1),
            "deviation_pct": round(float(deviation_pct), 1),
            "peer_median": round(float(median), 2),
            "peer_count": stats["count"],
            "flag_note": flag_note,
            "is_anomaly": deviation_pct >= 40.0
        }
