# How to Find ROC Queue ID in Autotask

## Quick Method (Easiest)

### Step 1: Go to ROC Queue
1. In Autotask, click **"My Workspace & Queues"** (you're already there based on your screenshot)
2. In the left sidebar under **"All"**, click on **"ROC (57)"**

### Step 2: Look at the URL
When you click on "ROC", the URL in your browser will change to something like:

```
https://ww4.autotask.net/Autotask/ServiceDesk/Tickets.aspx?queueID=29682934
                                                                   ^^^^^^^^
                                                               This is the Queue ID!
```

**The number after `queueID=` is what we need!**

Copy that number and send it to me.

---

## Alternative Method (If URL doesn't show it)

### Option A: Check Queue Settings
1. In Autotask, go to **Admin** → **Service Desk** → **Queues**
2. Find "ROC" in the list
3. Click on it to view details
4. The Queue ID should be displayed in the queue details

### Option B: Use Autotask API Documentation
1. Go to Autotask Help/API documentation
2. Look for TicketQueues endpoint
3. The Queue ID is the numeric identifier for the queue

---

## What I Need

Just send me the number from the URL (the `queueID` value).

Example:
- If URL is `...queueID=29682934`, send me: `29682934`
- If URL is `...queueID=12345678`, send me: `12345678`

I'll add it to the `.env` file as:
```bash
AUTOTASK_ROC_BOARD_ID=29682934
```

---

## Why We Need This

The ROC Board Queue ID allows us to filter tickets to only show:
- Tickets from the ROC (Reactive Operations Center) board
- NOT tickets from other boards like Sales, Pro Services, etc.

This ensures the Scorecard metrics are accurate and only show reactive service tickets.

---

## Once You Send It

I will:
1. Add it to `.env`
2. Test the Autotask API to retrieve real ROC ticket data
3. Build the Scorecard dashboard showing:
   - Tickets opened/closed per week
   - Same-day close rate
   - Utilization
   - Weekly and quarterly averages

---

**Just click on "ROC (57)" in your sidebar and copy the `queueID` number from the URL!** 🎯
