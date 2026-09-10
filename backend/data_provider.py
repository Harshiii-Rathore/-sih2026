"""
Data Provider Abstraction Layer for NIRIKSHAN AI.
Decouples data sourcing from analytics logic so future authorized eSAKSHI API
integrations can replace the demo provider seamlessly without scraping or unauthorized access.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
import os
import csv

class MPLADSDataProvider(ABC):
    """Abstract base class defining contract for MPLADS data ingestion."""

    @abstractmethod
    def get_mp_allocations(self) -> List[Dict[str, Any]]:
        """Retrieve MP and constituency limit allocations."""
        pass

    @abstractmethod
    def get_projects(self) -> List[Dict[str, Any]]:
        """Retrieve project-level execution and payment records."""
        pass

class DemoDataProvider(MPLADSDataProvider):
    """
    Demo Provider combining:
    1. Real MoSPI MP Allocations from 'Allocated Limit for Honble MPs.csv'
    2. High-fidelity synthetic project records explicitly labeled 'SYNTHETIC_DEMO'
    """

    def __init__(self, csv_path: str = None):
        if csv_path is None:
            # Default to root directory file
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.csv_path = os.path.join(root_dir, "Allocated Limit for Honble MPs.csv")
        else:
            self.csv_path = csv_path

    def get_mp_allocations(self) -> List[Dict[str, Any]]:
        allocations = []
        if not os.path.exists(self.csv_path):
            return allocations

        with open(self.csv_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sr_no_str = row.get("Sr. No.", "").strip()
                if not sr_no_str or sr_no_str.lower() == "grand total":
                    continue
                try:
                    sr_no = int(sr_no_str)
                except ValueError:
                    sr_no = None

                amount_str = row.get("Allocated AMOUNT ( ₹ )", "").replace(",", "").strip()
                try:
                    amount = float(amount_str) if amount_str else 0.0
                except ValueError:
                    amount = 0.0

                allocations.append({
                    "sr_no": sr_no,
                    "state": row.get("State", "").strip(),
                    "mp_name": row.get("Hon'ble Members of Parliaments", "").strip(),
                    "constituency": row.get("Constituency", "").strip(),
                    "allocated_amount": amount
                })
        return allocations

    def get_projects(self) -> List[Dict[str, Any]]:
        # Projects are populated via the synthetic generator during seed_database
        return []

class AuthorizedESAKSHIDataProvider(MPLADSDataProvider):
    """
    Production extension point: Future authorized integration with eSAKSHI
    using government-issued API credentials and mutual TLS.
    """

    def __init__(self, api_endpoint: str, client_cert_path: str = None):
        self.api_endpoint = api_endpoint
        self.client_cert_path = client_cert_path

    def get_mp_allocations(self) -> List[Dict[str, Any]]:
        raise NotImplementedError("eSAKSHI production endpoint requires authorized government ministry credentials.")

    def get_projects(self) -> List[Dict[str, Any]]:
        raise NotImplementedError("eSAKSHI production endpoint requires authorized government ministry credentials.")
