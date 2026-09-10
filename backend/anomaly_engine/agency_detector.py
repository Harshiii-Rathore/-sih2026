"""
Implementing Agency Pattern & Concentration Anomaly Engine.
Evaluates agency market concentration, average project value vs peer agencies, and execution track records.
Uses neutral, objective audit terminology ('Unusual pattern detected', 'Requires review').
"""

from typing import Dict, Any, List
import numpy as np

class AgencyAnomalyDetector:
    def __init__(self, projects: List[Dict[str, Any]]):
        self.agency_stats: Dict[str, Dict[str, Any]] = {}
        self.district_stats: Dict[str, Dict[str, Any]] = {}

        # Aggregate district totals
        dist_projects: Dict[str, List[float]] = {}
        for p in projects:
            dist = p.get("district", "General")
            cost = float(p.get("sanction_amount", 0.0))
            if dist not in dist_projects:
                dist_projects[dist] = []
            dist_projects[dist].append(cost)

        for dist, costs in dist_projects.items():
            self.district_stats[dist] = {
                "total_projects": len(costs),
                "avg_cost": float(np.mean(costs)) if costs else 1.0
            }

        # Aggregate agency metrics
        agency_data: Dict[str, List[Dict[str, Any]]] = {}
        for p in projects:
            agency = p.get("implementing_agency", "District Rural Development Agency")
            if agency not in agency_data:
                agency_data[agency] = []
            agency_data[agency].append(p)

        for agency, works in agency_data.items():
            costs = [float(w.get("sanction_amount", 0.0)) for w in works]
            dist = works[0].get("district", "General")
            state = works[0].get("state", "General")
            delayed_count = sum(1 for w in works if w.get("status") in ("DELAYED", "STALLED"))

            dist_tot = self.district_stats.get(dist, {}).get("total_projects", len(works))
            share_pct = (len(works) / dist_tot * 100.0) if dist_tot > 0 else 10.0
            avg_cost = float(np.mean(costs)) if costs else 0.0
            dist_avg_cost = self.district_stats.get(dist, {}).get("avg_cost", avg_cost)

            cost_premium_pct = ((avg_cost - dist_avg_cost) / dist_avg_cost * 100.0) if dist_avg_cost > 0 else 0.0
            delay_rate_pct = (delayed_count / len(works) * 100.0) if works else 0.0

            self.agency_stats[agency] = {
                "agency_name": agency,
                "district": dist,
                "state": state,
                "total_projects": len(works),
                "total_sanctioned_amount": sum(costs),
                "average_project_value": avg_cost,
                "cost_premium_pct": round(cost_premium_pct, 1),
                "share_pct": round(share_pct, 1),
                "delay_rate_pct": round(delay_rate_pct, 1),
                "delayed_count": delayed_count
            }

    def evaluate(self, project: Dict[str, Any]) -> Dict[str, Any]:
        agency = project.get("implementing_agency", "District Rural Development Agency")
        stats = self.agency_stats.get(agency, {
            "total_projects": 1,
            "average_project_value": float(project.get("sanction_amount", 0.0)),
            "cost_premium_pct": 0.0,
            "share_pct": 5.0,
            "delay_rate_pct": 0.0
        })

        cost_prem = stats["cost_premium_pct"]
        share = stats["share_pct"]
        delay_rate = stats["delay_rate_pct"]

        # Risk scoring
        risk_score = 10.0
        flag_notes = []
        is_anomaly = False

        # Pattern 1: High project concentration in district (> 40% of district projects)
        if share >= 35.0 and stats["total_projects"] >= 8:
            risk_score = max(risk_score, 68.0 + min(25.0, (share - 35.0) * 0.8))
            flag_notes.append(f"High agency concentration: Manages {share:.1f}% of district works ({stats['total_projects']} projects)")
            is_anomaly = True

        # Pattern 2: Significantly higher average project value than district peers
        if cost_prem >= 40.0:
            risk_score = max(risk_score, 62.0 + min(28.0, (cost_prem - 40.0) * 0.5))
            flag_notes.append(f"Agency average project value deviates by {cost_prem:+.1f}% from district benchmark")
            is_anomaly = True

        # Pattern 3: High delay or stalled rate across agency works
        if delay_rate >= 50.0 and stats["total_projects"] >= 4:
            risk_score = max(risk_score, 65.0)
            flag_notes.append(f"Elevated agency delay rate: {delay_rate:.0f}% of projects have exceeded deadlines")
            is_anomaly = True

        if not flag_notes:
            risk_score = 12.0
            flag_notes.append(f"Agency portfolio is diversified across peer group norms ({stats['total_projects']} works)")

        return {
            "score": round(float(risk_score), 1),
            "total_agency_projects": stats["total_projects"],
            "avg_project_value": round(stats["average_project_value"], 2),
            "cost_premium_pct": cost_prem,
            "value_deviation_pct": cost_prem,
            "district_share_pct": share,
            "flag_note": " • ".join(flag_notes),
            "is_anomaly": is_anomaly
        }
