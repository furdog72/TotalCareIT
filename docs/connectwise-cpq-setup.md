# ConnectWise CPQ API Setup Guide

## Overview

ConnectWise CPQ (formerly Quosal) API integration for pulling Pro Services opportunities, quotes, and pipeline data into the Partner Portal PBR (Pro Services Board).

## Requirements

- ConnectWise CPQ **Premium** license (Basic and Standard licenses do NOT support APIs)
- Administrator permissions in ConnectWise CPQ
- Python 3.7+ with `requests` library

## Step 1: Generate API Keys

1. **Log into ConnectWise CPQ** with an administrator account

2. **Navigate to Settings:**
   - Click **Settings** in the top menu
   - Go to **Organization Setup**
   - Click **API Keys**

3. **Grant Admin Permissions** (if not already admin):
   - Go to **Settings** > **Organization Setup** > **My User**
   - Check the **Is Administrator** checkbox
   - Save

4. **Generate API Key:**
   - In the API Keys section, enter a description: "TotalCareIT Partner Portal"
   - Click **Generate Key**
   - A pop-up window will display:
     - **Public API Key** (keep this safe)
     - **Private API Key** (keep this VERY safe - shown only once!)

5. **Save the keys** - you won't be able to see the private key again!

## Step 2: Find Your Access Key

Your **Access Key** is your CPQ subdomain followed by `_azure`.

**Example:**
- If your CPQ URL is: `https://totalcareit.quosal.com`
- Your subdomain is: `totalcareit`
- Your Access Key is: `totalcareit_azure`

**To find it:**
1. Log into ConnectWise CPQ
2. Look at your browser URL: `https://[YOUR-SUBDOMAIN].quosal.com`
3. Access Key = `[YOUR-SUBDOMAIN]_azure`

## Step 3: Add Credentials to .env File

Open `/Users/charles/Projects/TotalCareIT/.env` and add:

```bash
# ConnectWise CPQ API Configuration
# Get from: Settings > Organization Setup > API Keys in CPQ
# Requires CPQ Premium license
CONNECTWISE_CPQ_PUBLIC_KEY=your_public_key_here
CONNECTWISE_CPQ_PRIVATE_KEY=your_private_key_here
CONNECTWISE_CPQ_ACCESS_KEY=yourcompany_azure  # Your CPQ subdomain + _azure
```

**Example (with fake keys):**
```bash
CONNECTWISE_CPQ_PUBLIC_KEY=8f7a6b5c4d3e2f1a
CONNECTWISE_CPQ_PRIVATE_KEY=a1b2c3d4e5f6g7h8i9j0
CONNECTWISE_CPQ_ACCESS_KEY=totalcareit_azure
```

## Step 4: Test the Connection

Run the test script:

```bash
cd /Users/charles/Projects/TotalCareIT
python3 api/connectwise_cpq.py
```

**Expected Output (if successful):**
```
🔧 Testing ConnectWise CPQ API connection...

📊 Fetching Pro Services pipeline (last 30 days)...

✅ Pipeline Metrics:
   Total Opportunities: 15
   Total Value: $234,500.00
   Open: 8 ($125,000.00)
   Won: 5 ($89,500.00)
   Lost: 2 ($20,000.00)

📋 Recent Opportunities:
   - Network Upgrade (Acme Corp): $45,000.00 - Open
   - Migration Project (XYZ Inc): $32,500.00 - Won
   - Security Assessment (Tech Co): $15,000.00 - Open
   [...]

📋 Fetching Pro Services backlog...

✅ Found 8 open opportunities

🔴 Oldest opportunities:
   - Legacy System Migration (ABC Company): 45 days old - $67,000.00
   - Cloud Infrastructure Setup (123 Corp): 32 days old - $28,500.00
   [...]
```

**If you see errors:**

❌ **Missing credentials:**
```
❌ Missing CPQ credentials in .env file

Please add:
CONNECTWISE_CPQ_PUBLIC_KEY=your_public_key
CONNECTWISE_CPQ_PRIVATE_KEY=your_private_key
CONNECTWISE_CPQ_ACCESS_KEY=your_subdomain_azure
```
→ **Fix:** Add credentials to .env file (Step 3 above)

❌ **401 Unauthorized:**
```
❌ CPQ API Error: 401 Client Error: Unauthorized
```
→ **Fix:** Check that your Public/Private keys are correct. They may have been copied incorrectly or expired.

❌ **404 Not Found:**
```
❌ CPQ API Error: 404 Client Error: Not Found
```
→ **Fix:** Your Access Key is wrong. Verify your subdomain and ensure you added `_azure` suffix.

❌ **403 Forbidden:**
```
❌ CPQ API Error: 403 Client Error: Forbidden
```
→ **Fix:** Your user doesn't have API access. Verify:
  - You have a CPQ Premium license (not Basic or Standard)
  - Your user has Administrator permissions

## Step 5: API Usage in Code

### Import the client:
```python
from api.connectwise_cpq import ConnectWiseCPQ

cpq = ConnectWiseCPQ()
```

### Get pipeline metrics:
```python
# Get last 30 days of opportunities
pipeline = cpq.get_pro_services_pipeline(days=30)

print(f"Open Opportunities: {pipeline['open_opportunities']}")
print(f"Open Value: ${pipeline['open_value']:,.2f}")
print(f"Won this month: {pipeline['won_opportunities']} (${pipeline['won_value']:,.2f})")
```

### Get backlog (all open opportunities):
```python
backlog = cpq.get_pro_services_backlog()

for opp in backlog:
    print(f"{opp['name']} - {opp['age_days']} days old - ${opp['value']:,.2f}")
```

### Get specific opportunity:
```python
opportunity = cpq.get_opportunity_by_id(12345)

print(f"Name: {opportunity['name']}")
print(f"Client: {opportunity['clientName']}")
print(f"Value: ${opportunity['totalValue']}")
print(f"Status: {opportunity['status']}")
print(f"Close Date: {opportunity['closeDate']}")
```

### Search opportunities:
```python
results = cpq.search_opportunities("network upgrade")

for opp in results:
    print(f"{opp['name']} - {opp['clientName']}")
```

## Available Methods

### Opportunities
- `get_opportunities(status=None, start_date=None, end_date=None)` - Get all opportunities with filters
- `get_opportunity_by_id(opportunity_id)` - Get detailed opportunity info
- `search_opportunities(search_term)` - Search for opportunities

### Quotes
- `get_quotes(status=None, client_name=None)` - Get all quotes
- `get_quote_by_id(quote_id)` - Get detailed quote with line items

### Products & Clients
- `get_products()` - Get all products from catalog
- `get_clients()` - Get all clients

### Pro Services Specific
- `get_pro_services_pipeline(days=30)` - Get pipeline metrics for PBR dashboard
- `get_pro_services_backlog()` - Get all open opportunities sorted by age

## Integration with Pro Services PBR

The Pro Services PBR (Professional Services Board) can now pull data from ConnectWise CPQ to display:

1. **Pipeline Value**: Total value of open opportunities
2. **Backlog Age**: How long opportunities have been open
3. **Win Rate**: Percentage of opportunities won vs lost
4. **Recent Wins**: Recently closed-won opportunities
5. **At-Risk Opportunities**: Opportunities open longer than 45 days

**To add to PBR dashboard**, edit the Pro Services PBR page and add:

```javascript
// Fetch pipeline data
async function loadCPQPipeline() {
    const response = await fetch('/api/cpq/pipeline');
    const data = await response.json();

    // Update dashboard metrics
    document.getElementById('pipeline-value').textContent = `$${data.open_value.toLocaleString()}`;
    document.getElementById('open-count').textContent = data.open_opportunities;
    document.getElementById('won-count').textContent = data.won_opportunities;

    // Display backlog table
    renderBacklogTable(data.opportunities);
}
```

## API Rate Limits

ConnectWise CPQ API has rate limits (exact limits not publicly documented). Best practices:

- Cache results when possible (don't fetch same data repeatedly)
- Use specific date ranges to limit result set size
- Implement exponential backoff if you receive 429 (Too Many Requests) errors

## Troubleshooting

### "No opportunities returned"

**Possible causes:**
- Date range is too narrow (try wider range)
- No opportunities exist in that status
- Opportunities are in a different status than you're filtering for

**Solution:** Try without filters first:
```python
all_opps = cpq.get_opportunities()
print(f"Total opportunities: {len(all_opps)}")
```

### "Connection timeout"

**Cause:** Network issue or CPQ servers slow

**Solution:** Increase timeout in `connectwise_cpq.py`:
```python
response = requests.request(
    method=method,
    url=url,
    headers=self.headers,
    params=params,
    json=data,
    timeout=60  # Increase from 30 to 60 seconds
)
```

### "SSL Certificate Error"

**Cause:** Corporate firewall or proxy

**Solution (temporary, for testing only):**
```python
response = requests.request(
    method=method,
    url=url,
    headers=self.headers,
    params=params,
    json=data,
    timeout=30,
    verify=False  # WARNING: Only use for testing!
)
```

## Security Best Practices

1. **Never commit .env file to git** (already in .gitignore)
2. **Use environment variables** - don't hardcode keys in scripts
3. **Rotate API keys** every 6-12 months
4. **Use read-only API user** if possible (not currently supported by CPQ)
5. **Monitor API usage** for suspicious activity

## API Documentation

Official ConnectWise CPQ API documentation is available at:
**https://developer.connectwise.com/**

(Requires ConnectWise Developer Network account - free registration)

Key endpoints used:
- `/apiservice/opportunities` - List and search opportunities
- `/apiservice/opportunities/{id}` - Get specific opportunity
- `/apiservice/quotes` - List quotes
- `/apiservice/quotes/{id}` - Get specific quote with line items
- `/apiservice/products` - Product catalog
- `/apiservice/clients` - Client list

## Support

If you encounter issues:

1. **Check ConnectWise CPQ Status:** https://status.connectwise.com/
2. **Review API Logs:** Check console output for detailed error messages
3. **Verify Credentials:** Double-check Public Key, Private Key, and Access Key
4. **Check License:** Confirm you have CPQ Premium (not Basic/Standard)
5. **Contact ConnectWise Support:** If API issues persist

---

**Last Updated:** October 29, 2024
**Author:** Claude Code
**File:** `/Users/charles/Projects/TotalCareIT/api/connectwise_cpq.py`
