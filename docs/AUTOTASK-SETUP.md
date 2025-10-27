# Autotask Integration Setup Guide

This guide explains how to configure the Autotask by Kaseya integration for the TotalCare AI Partner Portal sales reporting.

## Overview

The Autotask integration provides real-time sales reporting data including:
- Phone calls made (inbound/outbound)
- Conversations had (calls + meetings)
- Appointments scheduled
- Sales pipeline/funnel metrics
- Recent activity tracking

## Security Architecture

The integration is designed with security in mind:

**Current Implementation (Browser-based):**
- Credentials stored in browser localStorage
- API calls made directly from browser
- Suitable for trusted partner portal users

**Recommended Production Implementation:**
- Backend API proxy between browser and Autotask
- Credentials stored securely on server (encrypted vault/env variables)
- Rate limiting and caching on server side
- Browser makes requests to your API, which proxies to Autotask

## Step 1: Create Autotask API User

1. Log in to your Autotask instance as an administrator
2. Navigate to **Admin > Resources/Users (HR) > Resources/Users**
3. Click **New** to create a new resource

### Configure API User:

**User Details:**
- First Name: `API`
- Last Name: `User - Read Only` (or similar)
- Email: `api-readonly@totalcareit.com` (use your domain)
- Security Level: Select **"API User (system)"** or create custom read-only level

**Security Level Configuration (Recommended):**
For read-only access, create a custom security level:
1. Go to **Admin > Features & Settings > Application-Wide (Shared) Features > Security > Security Levels**
2. Copy the "API User (system)" security level
3. Name it "API User - Read Only"
4. Remove write/delete permissions, keep only read permissions for:
   - Companies
   - Contacts
   - Opportunities
   - Activities/Tasks
   - Tickets (optional)
   - Time Entries (optional)
   - Appointments

**API Integration Code:**
1. While viewing the API user, note the **Username** (email address)
2. Set a strong **Password/Secret**
3. Generate an **API Integration Code**:
   - Go to **Admin > Extensions & Integrations > API Management**
   - Create a new integration code or use existing one
   - Note the integration code

## Step 2: Test API Access

You can test the API credentials using curl:

```bash
# Get zone information
curl -X GET "https://webservices.autotask.net/ATServicesRest/V1.0/zoneInformation" \
  -H "UserName: api-readonly@totalcareit.com" \
  -H "Content-Type: application/json"

# This should return your zone URL like: "https://webservices1.autotask.net"
```

## Step 3: Configure Integration in Partner Portal

1. Log in to the Partner Portal: https://totalcareit.ai/partner-login.html
2. Navigate to **Sales Report**
3. Click **Configure Autotask** in the yellow banner
4. Enter your credentials:
   - **API Username**: The email address of your API user
   - **API Secret**: The password for your API user
   - **Integration Code**: Your API integration tracking code
5. Click **Test Connection** to verify
6. Click **Save & Connect** to start using live data

## Available API Endpoints

The integration uses the following Autotask REST API endpoints:

### Read-Only Queries:
- `POST /Tickets/query` - Ticket/service desk data
- `POST /TimeEntries/query` - Time tracking data
- `POST /Companies/query` - Client companies
- `POST /Contacts/query` - Contact information
- `POST /Tasks/query` - Activities (calls, meetings, emails)
- `POST /Opportunities/query` - Sales pipeline
- `POST /Appointments/query` - Scheduled appointments
- `POST /Contracts/query` - Contract information

### Data Mapping:

**Phone Calls:**
- Source: Tasks with `actionType = 4` (Phone Call)
- Outbound: `direction = 1` or description contains "outbound"
- Inbound: `direction = 2` or description contains "inbound"

**Conversations:**
- Calls: Tasks with `actionType = 4`
- Meetings: Tasks with `actionType = 6` or `actionType = 7`
- Emails: Tasks with `actionType = 3`

**Appointments:**
- Source: Appointments entity
- Filtered by `startDateTime >= today`

**Sales Funnel:**
- Source: Opportunities entity
- Stages:
  - Prospects: All opportunities
  - Contacted: `stage >= 1`
  - Qualified: `stage >= 2`
  - Proposal: `stage >= 3`
  - Closed Won: `stage = 5`

## Troubleshooting

### Connection Failed

**Error: "Zone info request failed: 401"**
- Check that username is correct (must be email address)
- Verify password/secret is correct
- Ensure API user security level includes API access

**Error: "Failed to initialize"**
- Verify integration code is correct
- Check that API user is active (not disabled)
- Confirm network can reach webservices.autotask.net

### No Data Showing

**Data appears as "--" or zero:**
- Check date range filter (default is "This Month")
- Verify API user has read permissions for relevant entities
- Check browser console (F12) for error messages
- Confirm Opportunities/Tasks/Appointments exist for selected period

### Rate Limiting

Autotask API has rate limits. If you encounter rate limit errors:
- Reduce refresh frequency
- Implement caching (5-minute cache already included)
- Consider backend API proxy for production use

## Data Refresh

**Automatic:**
- Data is cached for 5 minutes to reduce API calls
- Click "Refresh" button to force reload

**Manual:**
- Change date range filter
- Reload the page
- Click "Refresh" button

## Security Best Practices

1. **Use Read-Only API User:**
   - Create dedicated API user with minimal permissions
   - Never use admin account for API access

2. **Rotate Credentials Regularly:**
   - Change API secret every 90 days
   - Update integration in portal when changed

3. **Monitor API Usage:**
   - Review Autotask API logs regularly
   - Watch for unusual access patterns

4. **Production Deployment:**
   - Implement backend API proxy (see architecture notes)
   - Store credentials in secure vault (AWS Secrets Manager, etc.)
   - Add rate limiting and request monitoring
   - Implement audit logging

## Files Involved

- `js/autotask-config.js` - API configuration and endpoints
- `js/autotask-client.js` - API client for making requests
- `js/autotask-sales-adapter.js` - Data transformation for sales metrics
- `js/sales-report.js` - Main sales report page logic
- `sales-report.html` - Sales report UI with Autotask configuration modal

## Support

For issues with:
- **Autotask API**: Contact Kaseya/Autotask support
- **Portal Integration**: Contact TotalCare IT support
- **API Documentation**: https://www.autotask.net/help/DeveloperHelp/

## API Reference

**Autotask REST API Documentation:**
https://www.autotask.net/help/DeveloperHelp/Content/APIs/REST/REST_API_Home.htm

**Authentication:**
https://ww1.autotask.net/help/developerhelp/content/apis/REST/General_Topics/REST_Security_Auth.htm
