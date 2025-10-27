#!/usr/bin/env python3
"""
Test HubSpot sales activity metrics for scorecard
"""
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, '/Users/charles/Projects/qbo-ai')

from api.hubspot_service import get_hubspot_reporting_service

# Load environment
load_dotenv()

# Test week: October 18-24, 2025
week_start = datetime(2025, 10, 18, 0, 0, 0)
week_end = datetime(2025, 10, 24, 23, 59, 59)

print("Testing HubSpot Sales Activity Metrics")
print("=" * 80)
print(f"Week: {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}")
print()

# Get HubSpot service
try:
    service = get_hubspot_reporting_service()

    # Test 1: Get all owners
    print("1. Getting HubSpot Owners (Sales Reps)...")
    print("-" * 40)
    client = service.client
    owners_response = client.get_owners()
    owners = owners_response.get('results', [])

    print(f"Found {len(owners)} owners:")
    for owner in owners:
        print(f"  - {owner.get('firstName', '')} {owner.get('lastName', '')} ({owner.get('email', '')})")
        print(f"    ID: {owner.get('id')}")
    print()

    # Test 2: Get sales activity for Jason
    print("2. Sales Activity Metrics for Jason")
    print("-" * 40)
    jason_metrics = service.get_sales_activity_metrics(
        start_date=week_start,
        end_date=week_end,
        owner_email='jason@totalcareit.com'  # Adjust based on actual email
    )

    print(f"  Dials: {jason_metrics.get('dials', 0)}")
    print(f"  Conversations with DM: {jason_metrics.get('conversations_with_dm', 0)}")
    print(f"  FTAs Set: {jason_metrics.get('ftas_set', 0)}")
    print(f"  MRR Closed: ${jason_metrics.get('mrr_closed', 0)}")
    if 'error' in jason_metrics:
        print(f"  Error: {jason_metrics['error']}")
    print()

    # Test 3: Get sales activity for Charles
    print("3. Sales Activity Metrics for Charles")
    print("-" * 40)
    charles_metrics = service.get_sales_activity_metrics(
        start_date=week_start,
        end_date=week_end,
        owner_email='charles@totalcareit.com'  # Adjust based on actual email
    )

    print(f"  Dials (W250): {charles_metrics.get('dials', 0)}")
    print(f"  Conversations with DM: {charles_metrics.get('conversations_with_dm', 0)}")
    print(f"  FTAs Set: {charles_metrics.get('ftas_set', 0)}")
    print(f"  MRR Closed: ${charles_metrics.get('mrr_closed', 0)}")
    if 'error' in charles_metrics:
        print(f"  Error: {charles_metrics['error']}")
    print()

    # Test 4: Get all sales activity (no owner filter)
    print("4. Sales Activity Metrics for All")
    print("-" * 40)
    all_metrics = service.get_sales_activity_metrics(
        start_date=week_start,
        end_date=week_end
    )

    print(f"  Total Dials: {all_metrics.get('dials', 0)}")
    print(f"  Total Conversations with DM: {all_metrics.get('conversations_with_dm', 0)}")
    print(f"  Total FTAs Set: {all_metrics.get('ftas_set', 0)}")
    print(f"  Total MRR Closed: ${all_metrics.get('mrr_closed', 0)}")
    if 'error' in all_metrics:
        print(f"  Error: {all_metrics['error']}")
    print()

    print("=" * 80)
    print("✓ HubSpot sales activity integration test complete!")

except Exception as e:
    print(f"❌ Error testing HubSpot integration: {e}")
    import traceback
    traceback.print_exc()
