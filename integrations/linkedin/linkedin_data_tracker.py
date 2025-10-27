"""
LinkedIn Performance Data Tracker
Manages historical snapshots and weekly updates for LinkedIn performance metrics
"""

import json
import os
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional
from .linkedin_performance import LinkedInPerformanceAPI


class LinkedInDataTracker:
    """Track and store LinkedIn performance data over time"""

    def __init__(self, data_dir: str = "data/linkedin"):
        """
        Initialize the data tracker

        Args:
            data_dir: Directory to store LinkedIn performance data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # File paths
        self.monthly_snapshots_file = self.data_dir / "monthly_snapshots.json"
        self.weekly_data_file = self.data_dir / "weekly_updates.json"
        self.current_month_file = self.data_dir / "current_month.json"

        # Initialize API
        self.api = LinkedInPerformanceAPI()

    def collect_monthly_snapshot(self, target_date: Optional[date] = None) -> Dict:
        """
        Collect monthly snapshot on the 1st of the month

        Args:
            target_date: Date for the snapshot (defaults to today)

        Returns:
            Dictionary with snapshot data
        """
        if target_date is None:
            target_date = date.today()

        # Format: YYYY-MM (e.g., "2025-01")
        month_key = target_date.strftime("%Y-%m")

        print(f"📸 Collecting monthly snapshot for {month_key}...")

        # Collect data for all profiles
        snapshot = {
            "month": month_key,
            "snapshot_date": target_date.isoformat(),
            "collected_at": datetime.now().isoformat(),
            "profiles": {
                "charles": self.api.get_individual_metrics("Charles R. Berry, II", days=30),
                "jason": self.api.get_individual_metrics("Jason Snow", days=30),
            },
            "company": self._get_company_snapshot(),
        }

        # Load existing snapshots
        snapshots = self._load_monthly_snapshots()

        # Add or update this month's snapshot
        snapshots[month_key] = snapshot

        # Save back to file
        self._save_monthly_snapshots(snapshots)

        print(f"✅ Monthly snapshot saved for {month_key}")
        return snapshot

    def collect_weekly_update(self, target_date: Optional[date] = None) -> Dict:
        """
        Collect weekly update (run every Saturday)

        Args:
            target_date: Date for the update (defaults to today)

        Returns:
            Dictionary with weekly data
        """
        if target_date is None:
            target_date = date.today()

        # Format: YYYY-MM-DD (e.g., "2025-01-25")
        week_key = target_date.isoformat()
        current_month = target_date.strftime("%Y-%m")

        print(f"📊 Collecting weekly update for {week_key}...")

        # Collect current week data (last 7 days)
        weekly_data = {
            "week_ending": week_key,
            "month": current_month,
            "collected_at": datetime.now().isoformat(),
            "profiles": {
                "charles": self.api.get_individual_metrics("Charles R. Berry, II", days=7),
                "jason": self.api.get_individual_metrics("Jason Snow", days=7),
            },
            "company": self._get_company_weekly_data(),
        }

        # Load existing weekly updates
        weekly_updates = self._load_weekly_updates()

        # Add this week's update
        if current_month not in weekly_updates:
            weekly_updates[current_month] = []

        # Check if we already have data for this week
        existing_week_idx = None
        for idx, update in enumerate(weekly_updates[current_month]):
            if update["week_ending"] == week_key:
                existing_week_idx = idx
                break

        if existing_week_idx is not None:
            # Update existing week
            weekly_updates[current_month][existing_week_idx] = weekly_data
        else:
            # Add new week
            weekly_updates[current_month].append(weekly_data)

        # Sort by week_ending
        weekly_updates[current_month].sort(key=lambda x: x["week_ending"])

        # Save back to file
        self._save_weekly_updates(weekly_updates)

        # Update current month file for quick access
        self._update_current_month(weekly_data)

        print(f"✅ Weekly update saved for {week_key}")
        return weekly_data

    def get_historical_comparison(self, months_back: int = 6) -> Dict:
        """
        Get historical data for comparison

        Args:
            months_back: Number of months to include in comparison

        Returns:
            Dictionary with historical comparison data
        """
        snapshots = self._load_monthly_snapshots()

        # Get the last N months
        sorted_months = sorted(snapshots.keys(), reverse=True)[:months_back]

        historical_data = {
            "months": sorted_months,
            "snapshots": {month: snapshots[month] for month in sorted_months},
        }

        return historical_data

    def get_current_month_trend(self) -> Dict:
        """
        Get weekly trend for the current month

        Returns:
            Dictionary with weekly updates for current month
        """
        current_month = date.today().strftime("%Y-%m")
        weekly_updates = self._load_weekly_updates()

        return {
            "month": current_month,
            "weekly_updates": weekly_updates.get(current_month, []),
        }

    def get_dashboard_data(self) -> Dict:
        """
        Get all data needed for the LinkedIn Performance dashboard

        Returns:
            Complete dataset for dashboard display
        """
        current_month_data = self._load_current_month()
        historical_data = self.get_historical_comparison(months_back=6)
        weekly_trend = self.get_current_month_trend()

        return {
            "current": current_month_data,
            "historical": historical_data,
            "weekly_trend": weekly_trend,
            "last_updated": datetime.now().isoformat(),
        }

    # Private helper methods

    def _get_company_snapshot(self) -> Dict:
        """Get company page snapshot data"""
        company_id = os.getenv('LINKEDIN_COMPANY_ID', '')

        return {
            "followers": self.api.get_company_followers(company_id),
            "engagement": self.api.get_company_engagement(company_id, days=30),
            "posts": self.api.get_company_post_count(company_id, days=30),
            "competitor_comparison": self._get_competitor_snapshot(),
        }

    def _get_company_weekly_data(self) -> Dict:
        """Get company page weekly data"""
        company_id = os.getenv('LINKEDIN_COMPANY_ID', '')

        return {
            "followers": self.api.get_company_followers(company_id),
            "engagement": self.api.get_company_engagement(company_id, days=7),
            "posts": self.api.get_company_post_count(company_id, days=7),
        }

    def _get_competitor_snapshot(self) -> Dict:
        """Get competitor comparison data"""
        company_id = os.getenv('LINKEDIN_COMPANY_ID', '')
        competitor_ids = os.getenv('LINKEDIN_COMPETITOR_IDS', '').split(',')
        competitor_ids = [c.strip() for c in competitor_ids if c.strip()]

        if not competitor_ids:
            return {}

        return self.api.compare_with_competitors(company_id, competitor_ids, days=30)

    def _load_monthly_snapshots(self) -> Dict:
        """Load monthly snapshots from file"""
        if not self.monthly_snapshots_file.exists():
            return {}

        with open(self.monthly_snapshots_file, 'r') as f:
            return json.load(f)

    def _save_monthly_snapshots(self, snapshots: Dict):
        """Save monthly snapshots to file"""
        with open(self.monthly_snapshots_file, 'w') as f:
            json.dump(snapshots, f, indent=2)

    def _load_weekly_updates(self) -> Dict:
        """Load weekly updates from file"""
        if not self.weekly_data_file.exists():
            return {}

        with open(self.weekly_data_file, 'r') as f:
            return json.load(f)

    def _save_weekly_updates(self, updates: Dict):
        """Save weekly updates to file"""
        with open(self.weekly_data_file, 'w') as f:
            json.dump(updates, f, indent=2)

    def _load_current_month(self) -> Dict:
        """Load current month data from file"""
        if not self.current_month_file.exists():
            return {}

        with open(self.current_month_file, 'r') as f:
            return json.load(f)

    def _update_current_month(self, weekly_data: Dict):
        """Update current month file with latest weekly data"""
        with open(self.current_month_file, 'w') as f:
            json.dump(weekly_data, f, indent=2)


def run_monthly_snapshot():
    """Run monthly snapshot collection (for cron job on 1st of month)"""
    tracker = LinkedInDataTracker()
    snapshot = tracker.collect_monthly_snapshot()
    print(f"Monthly snapshot complete: {json.dumps(snapshot, indent=2)}")
    return snapshot


def run_weekly_update():
    """Run weekly update collection (for cron job every Saturday)"""
    tracker = LinkedInDataTracker()
    update = tracker.collect_weekly_update()
    print(f"Weekly update complete: {json.dumps(update, indent=2)}")
    return update


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "monthly":
            run_monthly_snapshot()
        elif sys.argv[1] == "weekly":
            run_weekly_update()
        elif sys.argv[1] == "dashboard":
            tracker = LinkedInDataTracker()
            data = tracker.get_dashboard_data()
            print(json.dumps(data, indent=2))
        else:
            print("Usage: python linkedin_data_tracker.py [monthly|weekly|dashboard]")
    else:
        print("Usage: python linkedin_data_tracker.py [monthly|weekly|dashboard]")
