"""
Configuration parameters and risk weights for NIRIKSHAN AI.
All weights and thresholds are transparently exposed and configurable.
"""

from typing import Dict

# Configurable Risk Scoring Weights (Must sum to 1.0)
RISK_WEIGHTS: Dict[str, float] = {
    "cost": 0.25,          # Peer median & IQR budget deviation
    "timeline": 0.20,      # Planned vs actual duration & delay velocity
    "overlap": 0.20,       # NLP similarity + Haversine spatial proximity
    "expenditure": 0.15,   # Payment timing, concentration, spend ratio
    "agency": 0.10,        # Concentration of works & average project value vs peers
    "compliance": 0.10,    # Deterministic sanity & regulatory checks
}

# Risk Level Categorization Thresholds (0 to 100)
RISK_LEVEL_THRESHOLDS = {
    "LOW": (0.0, 29.99),
    "MEDIUM": (30.0, 59.99),
    "HIGH": (60.0, 79.99),
    "CRITICAL": (80.0, 100.0)
}

# Overlap & Spatial Thresholds
MAX_OVERLAP_DISTANCE_KM = 3.0       # Max distance to consider for potential spatial overlap
OVERLAP_TEXT_SIMILARITY_MIN = 0.60  # Minimum TF-IDF cosine similarity for flagging overlap

# Cost Anomaly Thresholds
COST_MODERATE_DEV_PCT = 25.0       # 25% above peer median
COST_HIGH_DEV_PCT = 50.0           # 50% above peer median
COST_CRITICAL_DEV_PCT = 85.0       # 85%+ above peer median

# Timeline Anomaly Thresholds
TIMELINE_MODERATE_DELAY_PCT = 25.0 # 25% delay
TIMELINE_HIGH_DELAY_PCT = 50.0     # 50% delay
TIMELINE_CRITICAL_DELAY_PCT = 80.0 # 80%+ delay
