#!/usr/bin/env python3
"""
Collect Scorecard Week 4 Data from Various Systems

This script collects data for the week ending October 24, 2025 from:
- HubSpot (Sales metrics)
- Autotask (Operations metrics)
- Datto Portal (Backup/patch metrics)
- Datto RMM (Device metrics)
- Microsoft 365 (Security Score)

Usage:
    python scripts/collect_scorecard_week4.py
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
import os

# Week 4 date range
WEEK_START = datetime(2025, 10, 18)
WEEK_END = datetime(2025, 10, 24)

# Paths
JSON_PATH = Path("/Users/charles/Projects/qbo-ai/website/data/scorecard-october-2025.json")

def fetch_hubspot_data():
    """
    Fetch sales metrics from HubSpot API

    Metrics to collect:
    - Dials (Jason)
    - Conversations with DM (Jason)
    - FTAs set (Jason)
    - FTA Attended (Jason/Charles)
    - COI Attended (Jason/Charles)
    - MRR Closed (Jason/Charles)
    - COI Created (Josh)
    - COI Attended (Josh)
    - W250 Dials (Charles)
    - W250 Conversations (Charles)
    - W250 FTAs set (Charles)
    """
    # TODO: Implement HubSpot API calls
    # API_KEY = os.getenv('HUBSPOT_API_KEY')
    # endpoint = f'https://api.hubapi.com/...'

    return {
        'dials_jason': None,  # To be implemented
        'conversations_jason': None,
        'ftas_set_jason': None,
        'fta_attended': None,
        'coi_attended': None,
        'mrr_closed': None,
        'coi_created_josh': None,
        'coi_attended_josh': None,
        'w250_dials': None,
        'w250_conversations': None,
        'w250_ftas_set': None
    }

def fetch_autotask_data():
    """
    Fetch operations metrics from Autotask API

    Metrics to collect:
    - Reactive Tickets Opened
    - Reactive Tickets Closed
    - Same day Close percentage
    - Utilization percentage
    - Tickets >7 days old
    - Tickets per endpoint
    - RHEM (Service Noise)
    - Avg Response Time
    - Avg Resolution Time
    - Professional Services Tickets Opened/Closed
    - Tickets Over 30 Days Old
    - TAM metrics
    """
    # TODO: Implement Autotask API calls
    # API_USER = os.getenv('AUTOTASK_API_USER')
    # API_PASS = os.getenv('AUTOTASK_API_PASS')

    return {
        'reactive_tickets_opened': None,
        'reactive_tickets_closed': None,
        'same_day_close': None,
        'utilization': None,
        'tickets_over_7_days': None,
        'tickets_per_endpoint': None,
        'rhem': None,
        'avg_response_time': None,
        'avg_resolution_time': None,
        'prof_services_opened': None,
        'prof_services_closed': None,
        'tickets_over_30_days': None,
        'tam_questions': None,
        'tam_tickets_opened': None,
        'tam_tickets_closed': None
    }

def fetch_datto_portal_data():
    """
    Fetch backup and patch metrics from Datto Portal API

    Metrics to collect:
    - Failed Backups > 48 Hours
    - Failed Backups on Continuity > 7 Days
    - Failed Backups on SAAS > 48 Hours
    - Missing > 5 Patches
    """
    # TODO: Implement Datto Portal API calls

    return {
        'failed_backups_48h': None,
        'failed_backups_continuity': None,
        'failed_backups_saas': None,
        'missing_patches': None
    }

def fetch_datto_rmm_data():
    """
    Fetch device and AV metrics from Datto RMM API

    Metrics to collect:
    - Total Windows 7 Devices
    - Total Windows 10 Devices
    - Total Windows 11 EOL Devices
    - Missing Hosted AV
    """
    # TODO: Implement Datto RMM API calls

    return {
        'windows_7_devices': None,
        'windows_10_devices': None,
        'windows_11_eol_devices': None,
        'missing_hosted_av': None
    }

def fetch_microsoft_data():
    """
    Fetch security score from Microsoft Graph API

    Metrics to collect:
    - TotalCareIT Microsoft Security Score
    """
    # TODO: Implement Microsoft Graph API calls
    # Uses existing Microsoft 365 OAuth

    return {
        'security_score': None
    }

def update_week4_data(data_dict):
    """
    Update the scorecard JSON with week 4 data

    Args:
        data_dict: Dictionary mapping KPI names to values
    """
    with open(JSON_PATH, 'r') as f:
        scorecard = json.load(f)

    # Update each KPI's week 4 value
    for item in scorecard:
        kpi = item['kpi']

        # Find matching key in data_dict
        if kpi in data_dict and data_dict[kpi] is not None:
            # Update the 4th week (index 3)
            if len(item['october_weeks']) >= 4:
                item['october_weeks'][3]['value'] = str(data_dict[kpi])

    # Save updated JSON
    with open(JSON_PATH, 'w') as f:
        json.dump(scorecard, f, indent=2)

    print(f"✅ Updated {JSON_PATH}")

def main():
    """Main collection workflow"""
    print("🔄 Starting Week 4 data collection...")
    print(f"   Week: {WEEK_START.strftime('%Y-%m-%d')} to {WEEK_END.strftime('%Y-%m-%d')}")
    print()

    # Collect from all sources
    print("📊 Collecting HubSpot data...")
    hubspot_data = fetch_hubspot_data()

    print("📊 Collecting Autotask data...")
    autotask_data = fetch_autotask_data()

    print("📊 Collecting Datto Portal data...")
    datto_portal_data = fetch_datto_portal_data()

    print("📊 Collecting Datto RMM data...")
    datto_rmm_data = fetch_datto_rmm_data()

    print("📊 Collecting Microsoft 365 data...")
    microsoft_data = fetch_microsoft_data()

    # Map to scorecard KPI names
    # TODO: Complete mapping once KPI names are confirmed
    kpi_data = {
        # HubSpot metrics
        'Dials': hubspot_data['dials_jason'],
        'Conversations with DM': hubspot_data['conversations_jason'],
        "FTA's set": hubspot_data['ftas_set_jason'],

        # Autotask metrics
        'Reactive Tickets Opened': autotask_data['reactive_tickets_opened'],
        'Reactive Tickets Closed': autotask_data['reactive_tickets_closed'],
        'Same day Close': autotask_data['same_day_close'],

        # Add more mappings here...
    }

    # Update JSON
    print("\n💾 Updating scorecard JSON...")
    update_week4_data(kpi_data)

    print("\n✅ Week 4 data collection complete!")
    print("\nNext steps:")
    print("1. Review updated data in scorecard-october-2025.json")
    print("2. Rebuild HTML: python build_scorecard_2025.py")
    print("3. Deploy: aws s3 cp website/scorecard-complete.html s3://totalcareit.ai/")

if __name__ == '__main__':
    main()
