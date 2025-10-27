# API Integration Verification Guide

This guide will help you verify and fix the API integrations for the TotalCare IT Partner Portal scorecard data collection.

---

## 1. HubSpot API Verification

### Current Configuration
- **API Key**: Stored in `.env` as `HUBSPOT_API_KEY`
- **Hub ID**: `8752461`
- **Authentication Type**: Bearer Token (OAuth 2.0)

### How to Verify HubSpot Access

#### Option A: Using Private Apps (Recommended)

1. **Go to HubSpot Settings**:
   - Login to HubSpot: https://app.hubspot.com/login
   - Click the settings icon (gear) in the top right
   - Navigate to: **Integrations** → **Private Apps**

2. **Check if Private Apps exist**:
   - If you see "No private apps yet", you'll need to create one
   - If apps exist, look for one named something like "TotalCare IT API" or "Partner Portal"

3. **Create a New Private App** (if needed):
   - Click **Create a private app**
   - Name: `TotalCare IT Partner Portal`
   - Description: `API access for partner portal scorecard metrics`

4. **Configure Scopes** (Required permissions):
   - Go to the **Scopes** tab
   - Select these scopes:
     - ✅ `crm.objects.contacts.read` - Read contacts
     - ✅ `crm.objects.deals.read` - Read deals
     - ✅ `crm.objects.owners.read` - Read owners/users
     - ✅ `crm.objects.companies.read` - Read companies
     - ✅ `sales-email-read` - Read email activity
     - ✅ `crm.objects.contacts.write` - Write contacts (for lifecycle stage tracking)

5. **Get the Access Token**:
   - Click **Create app** or **Show token**
   - Copy the access token (starts with `pat-na1-` or similar)
   - This is your `HUBSPOT_API_KEY`

6. **Find Your Hub ID**:
   - Look at your HubSpot URL: `https://app.hubspot.com/contacts/8752461/...`
   - The number after `/contacts/` is your Hub ID
   - Or go to Settings → Account Setup → Account Defaults

#### Option B: Using OAuth Apps (Alternative)

If you're using a full OAuth app instead of Private Apps:

1. Go to Settings → Integrations → **Connected Apps**
2. Look for "TotalCare IT" or custom app
3. Verify it has the required scopes listed above
4. You may need to use OAuth flow instead of API key

### Testing HubSpot API

Run this test command:
```bash
cd /Users/charles/Projects/qbo-ai
source .venv/bin/activate

# Test the API key
python3 << 'EOF'
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('HUBSPOT_API_KEY')
hub_id = os.getenv('HUBSPOT_HUB_ID')

print(f"Testing HubSpot API...")
print(f"Hub ID: {hub_id}")
print(f"API Key: {api_key[:20]}...")

# Test API call
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

response = requests.get(
    'https://api.hubapi.com/crm/v3/owners',
    headers=headers
)

print(f"\nStatus Code: {response.status_code}")
if response.status_code == 200:
    print("✅ HubSpot API is working!")
    owners = response.json()
    print(f"Found {len(owners.get('results', []))} owners")
else:
    print(f"❌ Error: {response.text}")
EOF
```

### Updating the API Key

If you get a new API key, update it:
```bash
# Edit .env file
nano .env

# Update this line:
HUBSPOT_API_KEY=pat-na1-YOUR-NEW-TOKEN-HERE
```

---

## 2. Autotask API Verification

### Current Configuration
- **Username**: `gmhad6lqecgcsaq@totalcareit.com`
- **Secret**: `5x*Na#B8Jq7$1~gQz0Z@4@eAf`
- **Integration Code**: `4AJTYIXNQC6KBJ4VEBDLG6RRAAP`
- **Zone URL**: `https://webservices3.autotask.net`

### How to Verify Autotask Access

1. **Login to Autotask PSA**:
   - Go to: https://ww3.autotask.net/
   - Login with your TotalCare IT credentials

2. **Navigate to API Settings**:
   - Click on **Admin** (top menu)
   - Go to **Resources (Users)** → **Resources (Users)**
   - Find the API user: `gmhad6lqecgcsaq@totalcareit.com`

3. **Verify API User**:
   - Check if the user is active
   - Verify it has "API User" security level
   - Check password/secret hasn't expired

4. **Check Integration Code**:
   - Go to Admin → **Extensions** → **API**
   - Look for your integration: "TotalCare IT Partner Portal"
   - Copy the Integration Code (Tracking Identifier)

5. **Verify Zone URL**:
   - The zone URL should match your Autotask instance
   - Common zones:
     - `https://webservices.autotask.net` (US zone)
     - `https://webservices2.autotask.net`
     - `https://webservices3.autotask.net`
     - `https://webservices4.autotask.net`

### Testing Autotask API

Run this test command:
```bash
cd /Users/charles/Projects/qbo-ai
source .venv/bin/activate

python3 << 'EOF'
import os
import requests
from dotenv import load_dotenv

load_dotenv()

username = os.getenv('AUTOTASK_USERNAME')
secret = os.getenv('AUTOTASK_SECRET')
integration_code = os.getenv('AUTOTASK_INTEGRATION_CODE')
zone_url = os.getenv('AUTOTASK_ZONE_URL')

print(f"Testing Autotask API...")
print(f"Username: {username}")
print(f"Zone URL: {zone_url}")

headers = {
    'Content-Type': 'application/json',
    'UserName': username,
    'Secret': secret,
    'ApiIntegrationcode': integration_code
}

# Test API call - get version info
response = requests.get(
    f'{zone_url}/ATServicesRest/V1.0/Companies/query',
    headers=headers,
    json={
        'filter': [{'field': 'CompanyName', 'op': 'contains', 'value': 'TotalCare'}]
    }
)

print(f"\nStatus Code: {response.status_code}")
if response.status_code == 200:
    print("✅ Autotask API is working!")
    data = response.json()
    print(f"Response: {data}")
else:
    print(f"❌ Error: {response.text}")
EOF
```

---

## 3. Datto API Verification

### Current Configuration
- **Public Key**: `3b3837`
- **Private Key**: `768e17b07b2947f2e539483f629f8e45`
- **Portal URL**: `https://portal.dattobackup.com`
- **RMM URL**: `https://vidal-rmm.centrastage.net`

### How to Verify Datto Access

#### Datto Backup (BCDR) Portal

1. **Login to Datto Portal**:
   - Go to: https://portal.dattobackup.com
   - Login with TotalCare IT Datto credentials

2. **Navigate to API Settings**:
   - Click on your name (top right)
   - Go to **XML API Settings** or **API Credentials**

3. **Get API Keys**:
   - **Public Key**: Should be visible
   - **Private Key**: May need to regenerate if lost
   - Copy both keys

#### Datto RMM (formerly Autotask Endpoint Management)

1. **Login to Datto RMM**:
   - Go to: https://vidal-rmm.centrastage.net
   - Login with TotalCare IT credentials

2. **Navigate to API Settings**:
   - Click **Settings** (gear icon)
   - Go to **API** section

3. **Get API Credentials**:
   - Look for API Access settings
   - Copy API URL and credentials

### Testing Datto API

Run this test command:
```bash
cd /Users/charles/Projects/qbo-ai
source .venv/bin/activate

python3 << 'EOF'
import os
import requests
import hmac
import hashlib
from dotenv import load_dotenv

load_dotenv()

public_key = os.getenv('DATTO_API_PUBLIC_KEY')
private_key = os.getenv('DATTO_API_PRIVATE_KEY')
portal_url = os.getenv('DATTO_PORTAL_URL')

print(f"Testing Datto Backup API...")
print(f"Public Key: {public_key}")
print(f"Portal URL: {portal_url}")

# Test API call (example endpoint)
# Note: Datto uses HMAC authentication
# This is a simplified test - actual implementation may vary

response = requests.get(
    f'{portal_url}/api/v1/bcdr/device',
    auth=(public_key, private_key)
)

print(f"\nStatus Code: {response.status_code}")
if response.status_code == 200:
    print("✅ Datto API is working!")
    print(f"Response: {response.json()}")
else:
    print(f"❌ Error: {response.text}")
EOF
```

### Check Datto Config Loading

The error said "Datto API credentials not configured". Let's check the config class:

```bash
cd /Users/charles/Projects/qbo-ai
grep -A 20 "class DattoConfig" api/datto_service.py
```

Make sure the `from_env()` method reads these environment variables:
- `DATTO_API_PUBLIC_KEY`
- `DATTO_API_PRIVATE_KEY`
- `DATTO_PORTAL_URL`
- `DATTO_RMM_URL`

---

## 4. Microsoft 365 Security Score

### Current Status
Not yet implemented. This requires Microsoft Graph API.

### How to Set Up

1. **Register App in Azure AD**:
   - Go to: https://portal.azure.com
   - Navigate to **Azure Active Directory** → **App registrations**
   - Click **New registration**
   - Name: `TotalCare IT Partner Portal`

2. **Configure API Permissions**:
   - Go to **API permissions**
   - Add permission → **Microsoft Graph** → **Application permissions**
   - Add: `SecurityEvents.Read.All`
   - Click **Grant admin consent**

3. **Get Credentials**:
   - Go to **Certificates & secrets**
   - Create a **New client secret**
   - Copy the **Client ID** and **Client Secret**
   - Also copy your **Tenant ID** from Overview page

4. **Add to .env**:
```bash
MICROSOFT_TENANT_ID=your-tenant-id
MICROSOFT_CLIENT_ID=your-client-id
MICROSOFT_CLIENT_SECRET=your-client-secret
```

---

## Summary Checklist

Use this checklist to verify each integration:

- [ ] **HubSpot**
  - [ ] Private App created with required scopes
  - [ ] Access token copied to .env as `HUBSPOT_API_KEY`
  - [ ] Hub ID verified in .env as `HUBSPOT_HUB_ID`
  - [ ] Test API call succeeds (200 response)

- [ ] **Autotask**
  - [ ] API user active and not expired
  - [ ] Integration code verified
  - [ ] Zone URL correct for your instance
  - [ ] Test API call succeeds (200 response)

- [ ] **Datto Backup**
  - [ ] API keys verified in portal
  - [ ] Public/Private keys in .env
  - [ ] Config class loads keys properly
  - [ ] Test API call succeeds (200 response)

- [ ] **Datto RMM**
  - [ ] API credentials verified
  - [ ] RMM URL correct in .env
  - [ ] Test API call succeeds (200 response)

- [ ] **Microsoft 365**
  - [ ] Azure AD app registered
  - [ ] Graph API permissions granted
  - [ ] Credentials in .env
  - [ ] Implementation completed

---

## After Verification

Once all APIs are verified and working:

1. **Re-run the collection script**:
```bash
cd /Users/charles/Projects/qbo-ai
source .venv/bin/activate
python collect_scorecard_week_oct24.py
```

2. **Verify data collection**:
   - Check that all metrics show real values (not 0)
   - Review the output for any remaining errors

3. **Update scorecard**:
   - Copy the collected values to the Excel file
   - Rebuild the HTML
   - Deploy to S3

---

## Need Help?

If you encounter issues:

1. Check the error messages carefully
2. Verify all credentials are correct and not expired
3. Ensure the API users/apps have proper permissions
4. Test each API individually using the test commands above
5. Check firewall/network settings if connection fails
