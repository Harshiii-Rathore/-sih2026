"""
NLP + GIS Spatial Duplicate & Overlap Detection Engine.
Uses TF-IDF Cosine Similarity and Haversine distance to identify potential overlapping works.
Strictly labels findings as 'Potential overlap' (not fraud).
"""

import math
from typing import Dict, Any, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points on the earth in km."""
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

class OverlapDetector:
    def __init__(self, projects: List[Dict[str, Any]]):
        self.projects = projects
        self.project_ids = [p["project_id"] for p in projects]
        self.corpus = [
            f"{p.get('work_title', '')} {p.get('work_description', '')} {p.get('work_category', '')}"
            for p in projects
        ]
        
        # Fit TF-IDF Vectorizer
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=2500,
            min_df=1
        )
        if self.corpus:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus)
        else:
            self.tfidf_matrix = None

    def evaluate_all(self) -> Dict[str, Dict[str, Any]]:
        """Compute pairwise similarities and return overlap metrics for all projects."""
        results: Dict[str, Dict[str, Any]] = {}
        if self.tfidf_matrix is None or len(self.projects) == 0:
            return results

        n = len(self.projects)
        # Process in batches if large, or full matrix for ~1,000 projects (1000x1000 is tiny, ~8MB in RAM)
        sim_matrix = cosine_similarity(self.tfidf_matrix)

        for i in range(n):
            p1 = self.projects[i]
            pid1 = p1["project_id"]
            lat1 = float(p1.get("latitude", 0.0))
            lon1 = float(p1.get("longitude", 0.0))
            cat1 = p1.get("work_category", "")

            top_similar: List[Dict[str, Any]] = []
            max_overlap_risk = 5.0
            flag_note = "No spatial or descriptive overlap detected within 5 km radius"
            is_anomaly = False

            # Check neighbors
            for j in range(n):
                if i == j:
                    continue
                p2 = self.projects[j]
                pid2 = p2["project_id"]
                lat2 = float(p2.get("latitude", 0.0))
                lon2 = float(p2.get("longitude", 0.0))
                cat2 = p2.get("work_category", "")

                # Text similarity from matrix
                text_sim = float(sim_matrix[i, j])
                
                # Spatial distance
                dist_km = haversine_distance(lat1, lon1, lat2, lon2)

                # If reasonably nearby (< 15 km) and noticeable text similarity (> 0.40)
                if dist_km <= 15.0 and text_sim >= 0.40:
                    top_similar.append({
                        "project_id": pid2,
                        "work_title": p2.get("work_title", ""),
                        "category": cat2,
                        "distance_km": round(dist_km, 2),
                        "text_similarity_pct": round(text_sim * 100.0, 1),
                        "sanction_amount": float(p2.get("sanction_amount", 0.0)),
                        "status": p2.get("status", "")
                    })

                # Overlap risk scoring rules:
                # 1. Close proximity (< 2 km) + High similarity (> 0.70) -> Critical / High
                if dist_km <= 2.0 and text_sim >= 0.70:
                    score = min(98.0, 75.0 + (text_sim * 20.0) + max(0.0, (2.0 - dist_km) * 10.0))
                    if score > max_overlap_risk:
                        max_overlap_risk = score
                        flag_note = f"Potential Spatial & Description Overlap: Candidate match with similar work '{p2.get('work_title', '')}' found {dist_km:.1f} km away (Similarity: {text_sim*100:.0f}%). Candidate match requiring verification. This is not evidence of duplicate work."
                        is_anomaly = True

                # 2. Proximity (< 4 km) + Moderate-high similarity (> 0.60)
                elif dist_km <= 4.0 and text_sim >= 0.60:
                    score = min(78.0, 50.0 + (text_sim * 20.0) + (4.0 - dist_km) * 5.0)
                    if score > max_overlap_risk:
                        max_overlap_risk = score
                        flag_note = f"Candidate match detected {dist_km:.1f} km away with {text_sim*100:.0f}% descriptive similarity. Candidate match requiring verification. This is not evidence of duplicate work."
                        is_anomaly = True

                # 3. Same category within 1.0 km even with lower text similarity
                elif cat1 == cat2 and dist_km <= 1.0 and text_sim >= 0.50:
                    score = 65.0
                    if score > max_overlap_risk:
                        max_overlap_risk = score
                        flag_note = f"Same category project located {dist_km:.1f} km away; candidate match requiring verification. This is not evidence of duplicate work."
                        is_anomaly = True

            # Sort similar works by similarity score descending
            top_similar.sort(key=lambda x: (x["text_similarity_pct"], -x["distance_km"]), reverse=True)

            results[pid1] = {
                "score": round(float(max_overlap_risk), 1),
                "similar_projects": top_similar[:5],  # Top 5
                "flag_note": flag_note,
                "is_anomaly": is_anomaly
            }

        return results
