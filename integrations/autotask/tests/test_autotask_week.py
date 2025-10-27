#!/usr/bin/env python3
"""
Test Autotask data for week Oct 18-24, 2025
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

username = os.getenv('AUTOTASK_USERNAME')
secret = os.getenv('AUTOTASK_SECRET')
integration_code = os.getenv('AUTOTASK_INTEGRATION_CODE')
zone_url = os.getenv('AUTOTASK_ZONE_URL')
roc_board_id = os.getenv('AUTOTASK_ROC_BOARD_ID')

print("=" * 80)
print("Autotask Week Data Test (Oct 18-24, 2025)")
print("=" * 80)

headers = {
    'Content-Type': 'application/json',
    'UserName': username,
    'Secret': secret,
    'ApiIntegrationcode': integration_code
}

# Test: Get tickets created in the week
print("\n1️⃣  Tickets created Oct 18-24, 2025...")
try:
    response = requests.post(
        f'{zone_url}/ATServicesRest/V1.0/Tickets/query',
        headers=headers,
        json={
            'filter': [
                {
                    'field': 'createDate',
                    'op': 'gte',
                    'value': '2025-10-18'
                },
                {
                    'field': 'createDate',
                    'op': 'lte',
                    'value': '2025-10-24T23:59:59'
                }
            ],
            'MaxRecords': 100
        },
        timeout=10
    )

    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        tickets = data.get('items', [])
        print(f"   ✅ Found {len(tickets)} tickets created this week")

        for ticket in tickets[:5]:
            print(f"      - #{ticket.get('ticketNumber')}: {ticket.get('title')[:60]}")
            print(f"        Created: {ticket.get('createDate')}")
            print(f"        Queue: {ticket.get('queueID')}")
            print(f"        Status: {ticket.get('status')}")
    else:
        print(f"   ❌ Failed: {response.text[:300]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Get tickets with ROC Board queue
if roc_board_id:
    print(f"\n2️⃣  Tickets in ROC Board queue ({roc_board_id})...")
    try:
        response = requests.post(
            f'{zone_url}/ATServicesRest/V1.0/Tickets/query',
            headers=headers,
            json={
                'filter': [
                    {
                        'field': 'queueID',
                        'op': 'eq',
                        'value': int(roc_board_id)
                    },
                    {
                        'field': 'createDate',
                        'op': 'gte',
                        'value': '2025-10-18'
                    }
                ],
                'MaxRecords': 100
            },
            timeout=10
        )

        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            tickets = data.get('items', [])
            print(f"   ✅ Found {len(tickets)} ROC Board tickets this week")
        else:
            print(f"   ❌ Failed: {response.text[:300]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

# Test 3: Get all queues to see available options
print("\n3️⃣  Available ticket queues...")
try:
    response = requests.post(
        f'{zone_url}/ATServicesRest/V1.0/TicketCategories/query',
        headers=headers,
        json={
            'filter': [],
            'MaxRecords': 50
        },
        timeout=10
    )

    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        queues = data.get('items', [])
        print(f"   ✅ Found {len(queues)} queues:")
        for queue in queues:
            print(f"      - {queue.get('name')} (ID: {queue.get('id')})")
    else:
        print(f"   ❌ Failed: {response.text[:300]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 80)
