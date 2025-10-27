#!/usr/bin/env python3
"""
Test Autotask API Authentication
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

username = os.getenv('AUTOTASK_USERNAME')
secret = os.getenv('AUTOTASK_SECRET')
integration_code = os.getenv('AUTOTASK_INTEGRATION_CODE')
zone_url = os.getenv('AUTOTASK_ZONE_URL')

print("=" * 80)
print("Autotask API Authentication Test")
print("=" * 80)

print(f"\n📋 Current Configuration:")
print(f"   Username: {username}")
print(f"   Secret: {'*' * 10}{secret[-5:] if secret else 'NOT SET'}")
print(f"   Integration Code: {integration_code}")
print(f"   Zone URL: {zone_url}")
print(f"   Zone URL type: {type(zone_url)}, length: {len(zone_url) if zone_url else 0}, truthy: {bool(zone_url)}")

if not zone_url:
    print("\n❌ PROBLEM: Zone URL is not set or empty")
    exit(1)

print("\n" + "=" * 80)
print("Testing Autotask API...")
print("=" * 80)

headers = {
    'Content-Type': 'application/json',
    'UserName': username,
    'Secret': secret,
    'ApiIntegrationcode': integration_code
}

# Test 1: Query Companies
print("\n1️⃣  Testing Companies query...")
try:
    response = requests.post(
        f'{zone_url}/ATServicesRest/V1.0/Companies/query',
        headers=headers,
        json={
            'filter': [
                {
                    'field': 'companyName',
                    'op': 'contains',
                    'value': 'TotalCare'
                }
            ]
        },
        timeout=10
    )

    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Companies query works!")
        data = response.json()
        print(f"   Found {len(data.get('items', []))} companies")
        for company in data.get('items', [])[:3]:
            print(f"      - {company.get('companyName')} (ID: {company.get('id')})")
    else:
        print(f"   ❌ Failed: {response.text[:300]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Query Tickets (recent)
print("\n2️⃣  Testing Tickets query...")
try:
    response = requests.post(
        f'{zone_url}/ATServicesRest/V1.0/Tickets/query',
        headers=headers,
        json={
            'filter': [
                {
                    'field': 'createDate',
                    'op': 'gte',
                    'value': '2025-10-01'
                }
            ],
            'MaxRecords': 10
        },
        timeout=10
    )

    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Tickets query works!")
        data = response.json()
        print(f"   Found {len(data.get('items', []))} tickets")
        for ticket in data.get('items', [])[:3]:
            print(f"      - Ticket #{ticket.get('ticketNumber')}: {ticket.get('title')[:50]}")
    else:
        print(f"   ❌ Failed: {response.text[:300]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Get queue information
print("\n3️⃣  Testing Queue information...")
roc_board_id = os.getenv('AUTOTASK_ROC_BOARD_ID')
print(f"   ROC Board Queue ID: {roc_board_id}")

if roc_board_id:
    try:
        response = requests.get(
            f'{zone_url}/ATServicesRest/V1.0/TicketCategories/{roc_board_id}',
            headers=headers,
            timeout=10
        )

        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Queue info retrieved!")
            data = response.json()
            print(f"   Queue: {data.get('item', {})}")
        else:
            print(f"   ❌ Failed: {response.text[:300]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
else:
    print("   ⚠️  ROC_BOARD_QUEUE_ID not configured")

print("\n" + "=" * 80)
print("Diagnosis")
print("=" * 80)

if zone_url and username and secret and integration_code:
    print("\n✅ All credentials are configured")
    print("\n📝 Next: Check the test results above to see if API calls work")
else:
    print("\n❌ Missing credentials - check your .env file")

print("\n" + "=" * 80)
