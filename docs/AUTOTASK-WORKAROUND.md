# Autotask API Workaround - Zone Issue

## Problem

The Autotask zone information endpoint (`/ATServicesRest/V1.0/zoneInformation`) is returning 404, which means either:
1. The API version has changed
2. The endpoint structure is different
3. Authentication needs to be different

## Your Zone

Based on your URL `https://ww3.autotask.net/...`, you are on **Zone 3 (ww3)**.

## Workaround Solutions

### Option 1: Use Queue Name Instead of Queue ID (RECOMMENDED)

Instead of filtering by Queue ID, we can filter tickets by queue name "ROC".

**Advantages:**
- Don't need to find the Queue ID
- Works immediately
- More flexible (if queue name changes, easy to update)

**I can implement this now** - just confirm the exact queue name is "ROC".

---

### Option 2: Find Queue ID via Autotask UI

**Steps:**
1. In Autotask, go to **Admin** (gear icon)
2. Click **Service Desk (Configuration)**
3. Click **Queues**
4. Find "ROC" in the list
5. Click on it
6. Look for "Queue ID" or "ID" field in the details

**Send me that ID number.**

---

### Option 3: Contact Autotask Support

If the API endpoint has changed, Autotask support can provide:
- Current API documentation URL
- Correct zone information endpoint
- Sample API calls for your version

---

### Option 4: Use Tickets API Without Queue Filter (TEMPORARY)

We can query ALL tickets and filter ROC tickets in the code based on other fields:
- Ticket category
- Ticket type
- Custom fields

**Not ideal** - would return more data than needed.

---

## My Recommendation

**Let's use Option 1** - filter by queue name "ROC" instead of Queue ID.

This will work immediately and we can get the Scorecard dashboard built.

### Implementation:

Instead of:
```python
filters = {
    "filter": [
        {"field": "queueID", "op": "eq", "value": 123456}
    ]
}
```

We'll use:
```python
filters = {
    "filter": [
        {"field": "queueName", "op": "eq", "value": "ROC"}
    ]
}
```

---

## Next Steps

**Please confirm:**
1. The exact name of your ROC queue (is it exactly "ROC" or something else like "ROC Board", "ROC Queue", etc.?)
2. Should we proceed with queue name filtering?

Once confirmed, I'll:
1. Update the Autotask service to use ww3 zone hardcoded
2. Modify ticket queries to filter by queue name
3. Test retrieving ROC tickets
4. Build the Scorecard endpoints

---

## Alternative: Check Autotask API Version

Your Autotask might be using a different API version. Can you check:
1. **Admin → Integrations & Extensions**
2. Look for API version information
3. It might be using v2.0 instead of v1.0

If you can find the API version, send it to me and I'll update the code accordingly.
