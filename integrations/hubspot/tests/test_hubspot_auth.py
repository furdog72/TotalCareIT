#!/usr/bin/env python3
"""
Test HubSpot Authentication
Identifies what type of auth is configured and what's failing
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('HUBSPOT_API_KEY')
hub_id = os.getenv('HUBSPOT_HUB_ID')

print("=" * 80)
print("HubSpot Authentication Test")
print("=" * 80)

print(f"\n📋 Current Configuration:")
print(f"   API Key: {api_key[:30]}..." if api_key else "   API Key: NOT SET")
print(f"   Hub ID: {hub_id}")

# Identify key type
if not api_key:
    print("\n❌ PROBLEM: No API key configured in .env file")
    print("\n💡 SOLUTION: You need to set up HubSpot API access")
    print("   Since you don't have Private Apps, you have these options:")
    print("   1. Use OAuth 2.0 (requires app setup)")
    print("   2. Check if you have access to create Private Apps")
    print("   3. Use a different authentication method")
    exit(1)

print(f"\n🔍 API Key Type Analysis:")
if api_key.startswith('pat-'):
    print(f"   Type: Private App Access Token")
    print(f"   Status: This requires a Private App to exist in HubSpot")
    print(f"   ⚠️  You mentioned no Private App exists!")
elif api_key.startswith('CU'):
    print(f"   Type: Legacy API Key (hapikey)")
    print(f"   Status: Being deprecated by HubSpot")
else:
    print(f"   Type: Unknown format")

print("\n" + "=" * 80)
print("Testing API Endpoints...")
print("=" * 80)

# Test 1: Legacy API key format
print("\n1️⃣  Testing with Legacy API Key format (hapikey)...")
response1 = requests.get(
    'https://api.hubapi.com/crm/v3/owners',
    params={'hapikey': api_key}
)
print(f"   Status: {response1.status_code}")
if response1.status_code == 200:
    print("   ✅ Legacy API key works!")
    owners = response1.json()
    print(f"   Found {len(owners.get('results', []))} owners")
    for owner in owners.get('results', [])[:3]:
        print(f"      - {owner.get('email')} ({owner.get('firstName')} {owner.get('lastName')})")
else:
    print(f"   ❌ Failed: {response1.text[:200]}")

# Test 2: Bearer token format (Private App)
print("\n2️⃣  Testing with Bearer Token format (Private App)...")
response2 = requests.get(
    'https://api.hubapi.com/crm/v3/owners',
    headers={
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
)
print(f"   Status: {response2.status_code}")
if response2.status_code == 200:
    print("   ✅ Bearer token works!")
    owners = response2.json()
    print(f"   Found {len(owners.get('results', []))} owners")
    for owner in owners.get('results', [])[:3]:
        print(f"      - {owner.get('email')} ({owner.get('firstName')} {owner.get('lastName')})")
else:
    print(f"   ❌ Failed: {response2.text[:200]}")

# Test 3: Check account access
print("\n3️⃣  Testing account endpoint...")
response3 = requests.get(
    f'https://api.hubapi.com/account-info/v3/details',
    headers={
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
)
print(f"   Status: {response3.status_code}")
if response3.status_code == 200:
    print("   ✅ Account access works!")
    account = response3.json()
    print(f"   Portal ID: {account.get('portalId')}")
    print(f"   Time Zone: {account.get('timeZone')}")
else:
    print(f"   ❌ Failed: {response3.text[:200]}")

print("\n" + "=" * 80)
print("Diagnosis & Next Steps")
print("=" * 80)

if response1.status_code == 200:
    print("\n✅ GOOD NEWS: Legacy API key authentication works!")
    print("\n📝 ACTION: Update hubspot_service.py to use hapikey parameter instead of Bearer token")
    print("   File: api/hubspot_service.py:41-46")
    print("   Change from: Authorization: Bearer {api_key}")
    print("   Change to: URL parameter ?hapikey={api_key}")
elif response2.status_code == 200:
    print("\n✅ GOOD NEWS: Bearer token works!")
    print("   This means you DO have a Private App (or valid OAuth token)")
    print("   The token might have been created by someone else.")
elif response1.status_code == 401 and response2.status_code == 401:
    print("\n❌ PROBLEM: API key is invalid or expired")
    print("\n💡 SOLUTIONS:")
    print("   Option 1: Get access to create a Private App")
    print("      - Ask account admin to grant you permission")
    print("      - Settings → Integrations → Private Apps → Create")
    print()
    print("   Option 2: Use existing OAuth integration")
    print("      - Check if there's a connected app under Integrations")
    print("      - Get the OAuth token from that app")
    print()
    print("   Option 3: Use API Key (if available)")
    print("      - Settings → Integrations → API Key")
    print("      - This might not be available in newer HubSpot accounts")
else:
    print("\n⚠️  UNEXPECTED: Check the error messages above for details")

print("\n" + "=" * 80)
