"""
Expenditure & Payment Anomaly Detection Engine.
Analyzes budget utilization ratios, payment tranche concentration, and velocity.
"""

import json
from typing import Dict, Any, List

class ExpenditureAnomalyDetector:
    def __init__(self):
        pass

    def evaluate(self, project: Dict[str, Any]) -> Dict[str, Any]:
        sanction = float(project.get("sanction_amount", 1.0))
        expenditure = float(project.get("expenditure_amount", 0.0))
        status = project.get("status", "IN_PROGRESS")
        
        # Utilization ratio
        util_ratio = expenditure / sanction if sanction > 0 else 1.0
        util_pct = util_ratio * 100.0

        # Parse payments
        pmt_amounts = project.get("payment_amounts", [])
        if isinstance(pmt_amounts, str):
            try:
                pmt_amounts = json.loads(pmt_amounts)
            except Exception:
                pmt_amounts = []
        
        num_payments = len(pmt_amounts) if pmt_amounts else int(project.get("number_of_payments", 1))

        risk_score = 10.0
        flag_notes = []
        is_anomaly = False

        # Signal 1: Expenditure exceeds sanction
        if expenditure > sanction:
            excess_pct = ((expenditure - sanction) / sanction) * 100.0
            risk_score = min(100.0, 85.0 + excess_pct)
            flag_notes.append(f"Expenditure exceeds sanctioned amount by {excess_pct:.1f}% (₹{expenditure - sanction:,.0f} excess)")
            is_anomaly = True

        # Signal 2: Single lump-sum 100% payout upfront on unfinished work
        elif num_payments == 1 and util_pct >= 95.0 and status in ("IN_PROGRESS", "DELAYED", "STALLED"):
            risk_score = max(risk_score, 82.0)
            flag_notes.append("100% fund disbursement released in a single upfront tranche prior to project completion")
            is_anomaly = True

        # Signal 3: Heavy disbursement on stalled project
        elif status == "STALLED" and util_pct >= 60.0:
            risk_score = max(risk_score, 78.0)
            flag_notes.append(f"High fund utilization ({util_pct:.1f}%) on a work marked as stalled")
            is_anomaly = True

        # Signal 4: Premature high payout relative to progress
        elif status == "SANCTIONED" and util_pct >= 40.0:
            risk_score = max(risk_score, 65.0)
            flag_notes.append(f"Significant payout ({util_pct:.1f}%) released while work remains in initial sanction status")
            is_anomaly = True

        # Signal 5: Unusually concentrated payments
        elif pmt_amounts and len(pmt_amounts) >= 2:
            first_tranche_share = (pmt_amounts[0] / expenditure) * 100.0 if expenditure > 0 else 0
            if first_tranche_share > 85.0 and status in ("IN_PROGRESS", "DELAYED"):
                risk_score = max(risk_score, 60.0)
                flag_notes.append(f"Disbursement heavily front-loaded: {first_tranche_share:.0f}% in first payment")
                is_anomaly = True

        # Normal spend gradient
        if not flag_notes:
            risk_score = min(30.0, max(5.0, (util_pct - 50.0) * 0.4))
            flag_notes.append(f"Standard financial tranche progression ({util_pct:.1f}% disbursed across {num_payments} tranches)")

        return {
            "score": round(float(risk_score), 1),
            "utilization_pct": round(float(util_pct), 1),
            "num_payments": num_payments,
            "flag_note": " • ".join(flag_notes),
            "is_anomaly": is_anomaly
        }
