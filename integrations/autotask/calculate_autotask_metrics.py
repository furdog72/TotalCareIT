#!/usr/bin/env python3
"""
Calculate Autotask ROC Board Metrics for Week Oct 18-24, 2025

Calculates:
- Reactive Tickets Opened
- Reactive Tickets Closed
- Tickets Over 7 Days
- Same Day Close %
- Average Response Time (hours)
- Average Resolution Time (hours)
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load env BEFORE imports
load_dotenv()

from datetime import datetime, timedelta, timezone
import requests

# Week 4: Oct 18-24, 2025 (timezone-aware for comparison with API dates)
WEEK_START = datetime(2025, 10, 18, tzinfo=timezone.utc)
WEEK_END = datetime(2025, 10, 24, 23, 59, 59, tzinfo=timezone.utc)

def get_roc_tickets():
    """Get ROC Board tickets for the week"""
    import os

    username = os.getenv('AUTOTASK_USERNAME')
    secret = os.getenv('AUTOTASK_SECRET')
    integration_code = os.getenv('AUTOTASK_INTEGRATION_CODE')
    zone_url = os.getenv('AUTOTASK_ZONE_URL')
    roc_board_id = int(os.getenv('AUTOTASK_ROC_BOARD_ID'))

    headers = {
        'Content-Type': 'application/json',
        'UserName': username,
        'Secret': secret,
        'ApiIntegrationcode': integration_code
    }

    print(f"\n📊 Fetching ROC Board tickets (Queue ID: {roc_board_id})")
    print(f"   Date range: {WEEK_START.date()} to {WEEK_END.date()}")

    # Get tickets created in the week
    response = requests.post(
        f'{zone_url}/ATServicesRest/V1.0/Tickets/query',
        headers=headers,
        json={
            'filter': [
                {
                    'field': 'queueID',
                    'op': 'eq',
                    'value': roc_board_id
                },
                {
                    'field': 'createDate',
                    'op': 'gte',
                    'value': WEEK_START.strftime('%Y-%m-%d')
                },
                {
                    'field': 'createDate',
                    'op': 'lte',
                    'value': WEEK_END.strftime('%Y-%m-%dT23:59:59')
                }
            ],
            'MaxRecords': 500
        },
        timeout=30
    )

    response.raise_for_status()
    tickets = response.json().get('items', [])

    print(f"   ✅ Found {len(tickets)} tickets")

    return tickets

def calculate_metrics(tickets):
    """Calculate scorecard metrics from tickets"""

    print(f"\n📈 Calculating Metrics...")

    # 1. Reactive Tickets Opened
    tickets_opened = len(tickets)

    # 2. Reactive Tickets Closed (completed in the same week)
    tickets_closed = 0
    for ticket in tickets:
        completed_date = ticket.get('completedDate')
        if completed_date:
            completed_dt = datetime.fromisoformat(completed_date.replace('Z', '+00:00'))
            if WEEK_START <= completed_dt <= WEEK_END:
                tickets_closed += 1

    # 3. Same Day Close %
    same_day_closed = 0
    for ticket in tickets:
        create_date = ticket.get('createDate')
        completed_date = ticket.get('completedDate')

        if create_date and completed_date:
            create_dt = datetime.fromisoformat(create_date.replace('Z', '+00:00'))
            completed_dt = datetime.fromisoformat(completed_date.replace('Z', '+00:00'))

            # Check if closed same day
            if create_dt.date() == completed_dt.date():
                same_day_closed += 1

    same_day_close_pct = round((same_day_closed / tickets_opened * 100), 1) if tickets_opened > 0 else 0

    # 4. Tickets Over 7 Days (still open or took > 7 days to close)
    tickets_over_7_days = 0
    for ticket in tickets:
        create_date = ticket.get('createDate')
        completed_date = ticket.get('completedDate')
        status = ticket.get('status')  # 5 = Complete in Autotask

        if create_date:
            create_dt = datetime.fromisoformat(create_date.replace('Z', '+00:00'))

            if completed_date:
                # Ticket is closed - check if it took > 7 days
                completed_dt = datetime.fromisoformat(completed_date.replace('Z', '+00:00'))
                days_to_close = (completed_dt - create_dt).days
                if days_to_close > 7:
                    tickets_over_7_days += 1
            else:
                # Ticket still open - check if it's been > 7 days
                days_open = (WEEK_END - create_dt).days
                if days_open > 7:
                    tickets_over_7_days += 1

    # 5. Average Response Time (first note/work entry after creation)
    # Note: This requires TimeEntry API calls which may be slow
    # For now, we'll estimate or skip
    avg_response_time = 0  # TODO: Implement if needed

    # 6. Average Resolution Time (time to close)
    resolution_times = []
    for ticket in tickets:
        create_date = ticket.get('createDate')
        completed_date = ticket.get('completedDate')

        if create_date and completed_date:
            create_dt = datetime.fromisoformat(create_date.replace('Z', '+00:00'))
            completed_dt = datetime.fromisoformat(completed_date.replace('Z', '+00:00'))
            resolution_hours = (completed_dt - create_dt).total_seconds() / 3600
            resolution_times.append(resolution_hours)

    avg_resolution_time = round(sum(resolution_times) / len(resolution_times), 1) if resolution_times else 0

    return {
        'Reactive Tickets Opened': tickets_opened,
        'Reactive Tickets Closed': tickets_closed,
        'Tickets Over 7 Days': tickets_over_7_days,
        'Same Day Close %': same_day_close_pct,
        'Average Response Time (hours)': avg_response_time,
        'Average Resolution Time (hours)': avg_resolution_time,
        '_details': {
            'same_day_closed_count': same_day_closed,
            'resolution_times_count': len(resolution_times)
        }
    }

def main():
    """Main execution"""
    print("=" * 80)
    print("Autotask ROC Board Metrics Calculator")
    print(f"Week Ending October 24, 2025")
    print("=" * 80)

    try:
        # Get tickets
        tickets = get_roc_tickets()

        # Calculate metrics
        metrics = calculate_metrics(tickets)

        # Display results
        print("\n" + "=" * 80)
        print("✅ METRICS CALCULATED")
        print("=" * 80)

        for key, value in metrics.items():
            if not key.startswith('_'):
                print(f"\n{key}:")
                print(f"  {value}")

        print("\n" + "=" * 80)
        print("Details:")
        print(f"  Same-day closed count: {metrics['_details']['same_day_closed_count']}")
        print(f"  Tickets with resolution time: {metrics['_details']['resolution_times_count']}")
        print("=" * 80)

        return metrics

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    main()
