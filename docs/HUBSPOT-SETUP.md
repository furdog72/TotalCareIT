# HubSpot API Setup Guide

## Overview

The TotalCare AI Partner Portal integrates with HubSpot to provide:

- **CRM Data**: Contacts, Deals, Companies
- **Analytics**: Website traffic, page views, sessions
- **Forms**: Submission statistics
- **Sales Pipeline**: Deal stages and values

**Note:** This integration uses HubSpot's REST API (v3) with a Private App Access Token.

## Prerequisites

- HubSpot account (Marketing Hub, Sales Hub, or CMS Hub)
- Admin access to HubSpot account
- Hub ID (Portal ID) - find at Settings > Account Defaults

## Step 1: Create a Private App

HubSpot Private Apps provide secure API access without OAuth flow.

### 1. Navigate to Private Apps

1. Log in to your HubSpot account
2. Click the **Settings** icon (⚙️) in the top navigation
3. In the left sidebar, navigate to **Integrations > Private Apps**
4. Click **Create a private app**

### 2. Configure Basic Info

**Name:** `TotalCare Partner Portal API`

**Description:**
```
Backend API integration for TotalCare Partner Portal.
Provides read-only access to CRM data, analytics, and forms
for the sales reporting dashboard.
```

**Logo:** Upload TotalCareIT logo (optional)

### 3. Set Scopes (Permissions)

Click the **Scopes** tab and enable the following **READ** permissions:

#### CRM Scopes:
- ✅ `crm.objects.contacts.read` - Read contacts
- ✅ `crm.objects.companies.read` - Read companies
- ✅ `crm.objects.deals.read` - Read deals

#### Analytics Scopes:
- ✅ `analytics.read` - Read website analytics
- ✅ `content.read` - Read pages (for analytics)

#### Forms Scopes:
- ✅ `forms` - Read forms and submissions

#### Conversations Scopes (for chat widget):
- ✅ `conversations.read` - Read conversations

**Security Note:** Only grant READ permissions. Never grant WRITE access unless absolutely necessary.

### 4. Create the App

1. Review the permissions
2. Click **Create app**
3. Read the warning about access token security
4. Click **Continue creating**

### 5. Copy Access Token

**IMPORTANT:** The access token is shown **only once**. Copy it immediately.

1. Click **Show token**
2. Copy the token (starts with `pat-na1-...`)
3. Store it securely in your password manager
4. Click **Done**

## Step 2: Find Your Hub ID

Your Hub ID (also called Portal ID) is needed for some API calls.

### Method 1: Account Settings

1. In HubSpot, go to **Settings** (⚙️)
2. Navigate to **Account Defaults**
3. Your Hub ID is displayed at the top

**Example:** Hub ID: `8752461`

### Method 2: URL

Your Hub ID is in the HubSpot URL:
```
https://app.hubspot.com/reports-dashboard/8752461/view/12345
                                        ^^^^^^^^
                                        Hub ID
```

## Step 3: Configure Environment Variables

Add the following to your `.env` file:

```bash
# ===== HUBSPOT API CONFIGURATION =====
HUBSPOT_API_KEY=pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
HUBSPOT_HUB_ID=8752461
```

**Replace:**
- `HUBSPOT_API_KEY`: Your Private App access token (from Step 1.5)
- `HUBSPOT_HUB_ID`: Your Hub ID (from Step 2)

## Step 4: Verify Integration

### Test Backend API Connection

Start your backend API server:
```bash
python -m uvicorn api.main:app --reload --port 8000
```

Test the health check:
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "checks": {
    "autotask": "configured",
    "hubspot": "configured"
  }
}
```

### Test HubSpot Endpoints

#### CRM Summary
```bash
curl http://localhost:8000/api/hubspot/crm/summary
```

Expected response:
```json
{
  "success": true,
  "data": {
    "contacts_count": 150,
    "deals_count": 45,
    "companies_count": 30
  },
  "timestamp": "2025-10-24T..."
}
```

#### Recent Contacts
```bash
curl http://localhost:8000/api/hubspot/contacts/recent?limit=5
```

#### Sales Pipeline
```bash
curl http://localhost:8000/api/hubspot/deals/pipeline
```

#### Website Analytics
```bash
curl http://localhost:8000/api/hubspot/analytics
```

#### Form Statistics
```bash
curl http://localhost:8000/api/hubspot/forms
```

## Step 5: Install Chat Widget

The HubSpot chat widget is already configured in your website code.

### Verify Widget Code

In `website/dashboard.html` and `website/sales-report.html`:

```html
<!-- HubSpot Chat Widget -->
<script type="text/javascript" id="hs-script-loader" async defer src="//js.hs-scripts.com/8752461.js"></script>
```

**Update** the Hub ID (`8752461`) if using a different account.

### Configure Chat Settings

1. In HubSpot, navigate to **Conversations > Chatflows**
2. Create or edit your chatflow
3. Set **Targeting**:
   - **URL contains:** `totalcareit.ai/dashboard`
   - **OR URL contains:** `totalcareit.ai/sales-report`
4. **Availability:** Set your team's working hours
5. **Customize:** Brand colors, welcome message, etc.

## HubSpot API Endpoints Reference

### CRM Summary
**Endpoint:** `GET /api/hubspot/crm/summary`

**Response:**
```json
{
  "success": true,
  "data": {
    "contacts_count": 150,
    "deals_count": 45,
    "companies_count": 30,
    "total_deal_value": 125000.00
  },
  "timestamp": "2025-10-24T12:34:56"
}
```

### Recent Contacts
**Endpoint:** `GET /api/hubspot/contacts/recent?limit=10`

**Parameters:**
- `limit` (optional): Number of contacts to return (default: 10, max: 100)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "12345",
      "firstname": "John",
      "lastname": "Doe",
      "email": "john.doe@example.com",
      "company": "Acme Inc",
      "createdate": "2025-10-20T10:30:00Z",
      "lastmodifieddate": "2025-10-23T15:45:00Z"
    }
  ],
  "timestamp": "2025-10-24T12:34:56"
}
```

### Sales Pipeline
**Endpoint:** `GET /api/hubspot/deals/pipeline`

**Response:**
```json
{
  "success": true,
  "data": {
    "pipeline_name": "Sales Pipeline",
    "stages": [
      {
        "stage": "Appointment Scheduled",
        "deal_count": 12,
        "total_value": 35000.00
      },
      {
        "stage": "Qualified to Buy",
        "deal_count": 8,
        "total_value": 45000.00
      },
      {
        "stage": "Presentation Scheduled",
        "deal_count": 5,
        "total_value": 30000.00
      },
      {
        "stage": "Closed Won",
        "deal_count": 3,
        "total_value": 15000.00
      }
    ],
    "total_deals": 28,
    "total_value": 125000.00
  },
  "timestamp": "2025-10-24T12:34:56"
}
```

### Website Analytics
**Endpoint:** `GET /api/hubspot/analytics`

**Response:**
```json
{
  "success": true,
  "data": {
    "total_page_views": 5420,
    "total_sessions": 1250,
    "total_contacts": 150,
    "new_contacts_this_month": 23,
    "form_submissions": 45,
    "average_session_duration": 180
  },
  "timestamp": "2025-10-24T12:34:56"
}
```

### Form Statistics
**Endpoint:** `GET /api/hubspot/forms`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "form_id": "abc123",
      "form_name": "Contact Us",
      "submissions": 120,
      "conversion_rate": 0.12
    },
    {
      "form_id": "def456",
      "form_name": "Request Demo",
      "submissions": 45,
      "conversion_rate": 0.08
    }
  ],
  "timestamp": "2025-10-24T12:34:56"
}
```

## Troubleshooting

### Error: "HubSpot API not configured"

**Cause:** Missing or invalid environment variables.

**Fix:**
1. Check `.env` file exists
2. Verify `HUBSPOT_API_KEY` is set
3. Restart backend server after changing `.env`

### Error: 401 Unauthorized

**Cause:** Invalid access token.

**Fix:**
1. Verify token format: `pat-na1-...`
2. Check token hasn't been regenerated in HubSpot
3. Ensure Private App is not deleted or disabled

### Error: 403 Forbidden

**Cause:** Missing scopes/permissions.

**Fix:**
1. In HubSpot, go to **Settings > Integrations > Private Apps**
2. Click on "TotalCare Partner Portal API"
3. Go to **Scopes** tab
4. Enable required permissions (see Step 1.3)
5. Click **Save**

### No Data Returned

**Possible Causes:**
- HubSpot account has no data yet
- Scopes not properly set
- API rate limiting

**Fix:**
1. Check HubSpot has contacts/deals/companies
2. Verify all scopes are enabled
3. Check backend logs for rate limit errors: `journalctl -u totalcare-api -f`

### Chat Widget Not Appearing

**Possible Causes:**
- Hub ID incorrect in script tag
- Chatflow not published
- Targeting rules excluding your page

**Fix:**
1. Verify Hub ID in `<script>` tag matches your account
2. In HubSpot Chatflows, ensure chatflow is **Live**
3. Check targeting rules include your URLs
4. Clear browser cache

## Security Best Practices

1. **Never commit access token** - Keep in `.env` only
2. **Rotate tokens regularly** - Every 6 months
3. **Use read-only scopes** - Minimize permissions
4. **Monitor API usage** - Check HubSpot API logs
5. **Limit access** - Only grant to necessary team members
6. **Use HTTPS in production** - Never HTTP for API calls

## Rate Limits

HubSpot API has rate limits to prevent abuse:

### API Rate Limits (Private Apps)
- **10 requests per second** per integration
- **Daily limit:** Based on subscription tier
  - Free: 250,000 requests/day
  - Starter: 500,000 requests/day
  - Professional: 1,000,000 requests/day
  - Enterprise: Custom

### Backend Caching

The backend API implements caching to reduce HubSpot API calls:
- **CRM data:** 5-minute cache
- **Analytics:** 5-minute cache
- **Forms:** 5-minute cache

This ensures you stay well within rate limits while providing fresh data.

## Monitoring

### View Private App Activity

1. In HubSpot, go to **Settings > Integrations > Private Apps**
2. Click on "TotalCare Partner Portal API"
3. Click the **Logs** tab
4. View recent API requests, errors, and rate limit usage

### Backend Logs

Monitor backend API logs for errors:

```bash
# Systemd service
sudo journalctl -u totalcare-api -f

# Docker
docker logs -f totalcare-api

# Direct
tail -f /var/log/totalcare-api.log
```

## Next Steps

1. ✅ Create Private App in HubSpot
2. ✅ Configure environment variables
3. ✅ Test API endpoints
4. ✅ Configure chat widget targeting
5. 🔲 Deploy backend to production
6. 🔲 Test from production frontend
7. 🔲 Monitor API usage in HubSpot
8. 🔲 Set up alerts for API errors

## Additional Resources

- [HubSpot API Documentation](https://developers.hubspot.com/docs/api/overview)
- [Private Apps Guide](https://developers.hubspot.com/docs/api/private-apps)
- [API Rate Limits](https://developers.hubspot.com/docs/api/usage-details)
- [Chatflows Documentation](https://knowledge.hubspot.com/chatflows/create-a-live-chat)

## Support

For issues with HubSpot integration:
1. Check backend logs first
2. Verify Private App is active
3. Test endpoints with curl
4. Check HubSpot API logs
5. Review this guide's troubleshooting section
