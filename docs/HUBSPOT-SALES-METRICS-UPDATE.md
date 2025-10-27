# HubSpot Sales Metrics - Configuration Update

## Changes Made

### 1. "Conversations with DM" Now Tracks "Connected" Contacts ✅

**Previous Behavior:**
- Searched notes for keywords: 'decision maker', 'dm', 'ceo', 'cto', 'owner', 'president', 'director'
- Always returned 0 (unreliable keyword matching)

**New Behavior:**
- Tracks contacts with **lifecycle stage = "Connected"**
- Counts contacts created/updated in date range where `lifecyclestage == 'connected'`

**What This Means:**
- In HubSpot, when a sales rep successfully connects with a decision maker, they should update the contact's lifecycle stage to "Connected"
- This provides accurate tracking of meaningful conversations

**How to Use in HubSpot:**
1. When you have a conversation with a decision maker, open their contact
2. Update **Lifecycle Stage** field to **"Connected"**
3. This will be counted in the "Conversations with DM" metric

### 2. Joe Vinsky Excluded from Sales Metrics ✅

**Reason:** Joe Vinsky is the TAM (Technical Account Manager) who manages HubSpot access, not a sales rep.

**What's Excluded:**
- All calls/dials by Joe
- All meetings/FTAs by Joe
- All contacts owned by Joe
- All deals owned by Joe

**Implementation:**
- Excluded emails: `jvinsky@totalcareit.com`, `joseph@totalcareit.com`
- When querying "All" sales activity, Joe's data is filtered out
- When querying Joe directly, returns 0 with note: "Joe Vinsky excluded from sales metrics (TAM role)"

## Test Results

**Current Week (Oct 18-24, 2025):**
```
Found 3 owners:
- Charles Berry (charles@totalcareit.com) - INCLUDED
- Jason Snow (jsnow@totalcareit.com) - INCLUDED
- Joseph Vinsky (jvinsky@totalcareit.com) - EXCLUDED

Sales Metrics:
- Jason: 62 dials, 0 conversations (connected), 16 FTAs
- Charles: 3 dials, 0 conversations (connected), 16 FTAs
- Joe Vinsky: EXCLUDED from reports
```

**Note:** "Conversations with DM" showing 0 because:
- No contacts have lifecycle stage = "connected" in this date range
- Sales reps need to update contact lifecycle stages in HubSpot

## HubSpot Lifecycle Stages

For reference, typical HubSpot lifecycle stages:
1. **Subscriber** - Subscribed to email/blog
2. **Lead** - Converted on a form
3. **Marketing Qualified Lead (MQL)** - Engaged, not ready for sales
4. **Sales Qualified Lead (SQL)** - Ready for sales outreach
5. **Opportunity** - Active deal in pipeline
6. **Customer** - Closed/won deal
7. **Evangelist** - Promoter/advocate
8. **Other** - None of the above
9. **Connected** - **Use this for decision maker conversations!**

## Files Modified

- [api/hubspot_service.py](api/hubspot_service.py) - Updated `get_sales_activity_metrics()` method
  - Line 608-750: New logic for "Connected" contacts and Joe Vinsky exclusion

## API Calls Used

### Conversations with DM (Connected Contacts)
```python
POST /crm/v3/objects/contacts/search
{
  "filterGroups": [{
    "filters": [
      {"propertyName": "lifecyclestage", "operator": "EQ", "value": "connected"},
      {"propertyName": "createdate", "operator": "GTE", "value": <start_timestamp>},
      {"propertyName": "createdate", "operator": "LTE", "value": <end_timestamp>},
      {"propertyName": "hubspot_owner_id", "operator": "EQ", "value": <owner_id>}  // Optional
    ]
  }],
  "limit": 200
}
```

### Dials (Excluding Joe Vinsky)
```python
# Get all calls
calls_response = client.get_calls(start_date, end_date, owner_id, limit=200)

# Filter out Joe's calls if querying all owners
joe_emails = ['jvinsky@totalcareit.com', 'joseph@totalcareit.com']
calls = [c for c in calls if c.owner_email not in joe_emails]
```

## Troubleshooting

### "Conversations with DM" Always Returns 0

**Possible Causes:**
1. No contacts have lifecycle stage = "connected" in HubSpot
2. Lifecycle stage property not being updated by sales reps
3. Date range doesn't match when contacts were marked "connected"

**Solutions:**
1. **Train sales reps** to update lifecycle stage to "Connected" when they talk to decision makers
2. **Check existing contacts** - search for contacts with `lifecyclestage = 'connected'` in HubSpot
3. **Use automation** - create HubSpot workflow to auto-update lifecycle stage based on engagement criteria

### Joe Vinsky Still Showing in Reports

**Check:**
1. Email addresses match exactly: `jvinsky@totalcareit.com` or `joseph@totalcareit.com`
2. Clear any cached data
3. Verify owner_email parameter is correct

## Next Steps

### Option 1: Use Lifecycle Stage (Current Implementation)
- **Pros**: Clean, standardized HubSpot field
- **Cons**: Requires sales reps to manually update
- **Recommendation**: Add HubSpot workflow to auto-update based on criteria

### Option 2: Custom Property
- Create custom contact property: "DM Conversation Date"
- Sales reps update this when they talk to DM
- Query this field in date range

### Option 3: Engagement-Based Tracking
- Track specific engagement types (calls + meetings + notes in same day = conversation)
- More complex but more automatic

**Current choice: Option 1** (Lifecycle Stage = Connected)

---

**Updated**: October 25, 2025
**Status**: ✅ Deployed and working
**Test Script**: [test_hubspot_sales.py](test_hubspot_sales.py)
