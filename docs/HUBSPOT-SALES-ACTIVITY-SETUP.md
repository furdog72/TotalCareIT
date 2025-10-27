# HubSpot Sales Activity Integration - Setup Guide

## Overview

The HubSpot integration has been enhanced to track sales activity metrics for the scorecard:
- **Dials** (phone calls made)
- **Conversations with DM** (decision maker conversations)
- **FTAs Set** (First Time Appointments scheduled)
- **MRR Closed** (Monthly Recurring Revenue from closed deals)

## Current Status

✅ **Code Implemented**: Sales activity tracking methods added to `api/hubspot_service.py`
❌ **API Scopes Missing**: HubSpot Private App needs additional permissions
❌ **Not Tested with Real Data**: Awaiting scope configuration

## Required HubSpot API Scopes

The current HubSpot **Legacy App** "totalcare.ai partner portal" (App ID: 22607238) uses API Key: `[REDACTED - See .env]`

### Scopes to Add:
- ✅ **Owners** - Read/Write access to identify sales reps (Jason, Charles)
- ✅ **Engagements** - Read/Write access for calls, meetings, notes
- ✅ **Webhooks** (optional) - For real-time updates instead of polling

### Already Have (from previous integration):
- ✅ Contacts - Read/Write
- ✅ Deals - Read/Write
- ✅ Companies - Read/Write
- ✅ Forms - Read access

## How to Add Scopes (Legacy Apps)

**NOTE**: HubSpot uses **Legacy Apps** (not Private Apps) for this integration.

1. **Go to HubSpot Legacy App Settings**:
   - Login to HubSpot: https://app.hubspot.com
   - Navigate to: **Settings → Integrations → Connected Apps**
   - Or direct link: https://app.hubspot.com/integrations-settings/{hubId}/installed
   - Find app: **"totalcare.ai partner portal"** (App ID: 22607238)

2. **Update Scopes**:
   - Click on the app
   - Click "Edit" or "Manage Scopes"
   - Enable these scopes:
     - ✅ **Owners** (crm.objects.owners.read)
     - ✅ **Engagements** (for calls, meetings, notes)
     - ✅ **Timeline Events** (if available)
     - ✅ **Webhooks** (optional - for real-time updates)

3. **Save Changes**:
   - The API key remains the same: `[REDACTED - See .env]`
   - Scopes activate immediately

## Implementation Details

### New Methods Added

#### `HubSpotClient` (api/hubspot_service.py)

```python
# Engagement tracking
get_calls(start_date, end_date, owner_id, limit)      # Phone calls/dials
get_meetings(start_date, end_date, owner_id, limit)   # FTAs/appointments
get_notes(start_date, end_date, owner_id, limit)      # Conversation notes
get_owners()                                            # Sales rep list
```

#### `HubSpotReportingService`

```python
get_sales_activity_metrics(start_date, end_date, owner_email)
# Returns:
# - dials: Count of phone calls
# - conversations_with_dm: Notes mentioning DM keywords
# - ftas_set: Meetings scheduled
# - mrr_closed: MRR from closed won deals
```

### Data Mapping for Scorecard

| Scorecard Metric | HubSpot Data Source | Notes |
|-----------------|---------------------|-------|
| **Inside Sales - Dials** | Calls (Jason) | `owner_email='jason@totalcareit.com'` |
| **Inside Sales - Conversations** | Notes (Jason) | Notes containing "decision maker", "dm", "ceo", etc. |
| **Inside Sales - FTAs Set** | Meetings (Jason) | Scheduled meetings/appointments |
| **Outside Sales - MRR Closed** | Deals (closedwon) | Sum of `mrr` or `amount` property |
| **Warm 250 - W250 Dials** | Calls (Charles) | `owner_email='charles@totalcareit.com'` |
| **Warm 250 - W250 Conversations** | Notes (Charles) | Notes with DM keywords |
| **Warm 250 - W250 FTAs Set** | Meetings (Charles) | Scheduled meetings |

### Test Script

Test the integration after adding scopes:

```bash
cd /Users/charles/Projects/qbo-ai
source .venv/bin/activate
PYTHONPATH=/Users/charles/Projects/qbo-ai:$PYTHONPATH python test_hubspot_sales.py
```

## Next Steps

1. **Add Missing Scopes** to HubSpot Private App (see above)
2. **Verify Owner Emails**:
   - Jason's HubSpot email: `jason@totalcareit.com` (verify actual email)
   - Charles's HubSpot email: `charles@totalcareit.com` (verify actual email)
3. **Test Integration** using `test_hubspot_sales.py`
4. **Integrate into Scorecard** data fetching

## Alternative: Manual Data Entry

If HubSpot doesn't have engagement data (calls, meetings, notes), we can:
1. **Use custom properties** on contacts/deals to track these metrics
2. **Create a manual data entry interface** for weekly scorecard updates
3. **Import from other tools** (phone system logs, calendar, etc.)

## Datto Integration

For **Centralized Services** metrics, we'll need Datto Portal/RMM API integration.

**Datto API Status**: Not yet implemented
**Required Metrics**:
- Failed Backups > 48 Hours
- Failed Backups on Continuity > 7 Days
- Failed Backups on SAAS > 48 Hours
- Missing > 5 Patches
- Total Windows 7/10/11 Devices
- Missing Hosted AV
- Microsoft Security Score

**Action Needed**: User to provide Datto API credentials or confirm manual data entry.
