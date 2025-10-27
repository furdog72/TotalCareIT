# Autotask Setup - Next Steps

## What I Have So Far

From your screenshots, I've configured:

```bash
AUTOTASK_USERNAME=gmhad6lqecgcsaq@totalcareit.com
AUTOTASK_SECRET=5x*Na#B8Jq7$1~gQz0Z@4@eAf
```

## What I Still Need From You

### 1. Integration Vendor Code ⚠️ **REQUIRED**

In your second screenshot, there's an "Integration Vendor" dropdown under "API Tracking Identifier".

**You need to:**
1. In that dropdown, select or create an Integration Vendor
   - If creating new: Name it "TotalCare Partner Portal" or similar
2. Once selected/created, copy the Integration Code
3. Send me that code

**Why needed:** Autotask API requires this for API v1.6+

---

### 2. ROC Board Queue ID ⚠️ **REQUIRED**

We need the Queue ID for your ROC (Reactive Operations Center) board to filter tickets.

**To find it:**
1. In Autotask, go to **Service Desk** → **Queues**
2. Find your "ROC" or "Reactive Operations" queue
3. Click on it
4. The Queue ID will be in the URL or visible in the queue settings
   - Format: Usually a number like `12345678`

**Example URL:**
```
https://ww4.autotask.net/Autotask/AutotaskExtend/ExecuteCommand.aspx?Code=QueueDetail&QueueID=12345678
                                                                                        ^^^^^^^^
                                                                                      This is the ID
```

Send me this Queue ID number.

---

## Dashboard Navigation Issue - What's Wrong

You mentioned clicking items on the left sidebar of https://totalcareit.ai/dashboard.html doesn't work.

**The Issue:**
Most navigation links use hash anchors (`href="#analytics"`, `href="#automations"`, etc.) but those pages don't exist yet.

**Current Navigation:**
- ✅ **Dashboard** → `dashboard.html` (works)
- ✅ **Sales Report** → `sales-report.html` (works)
- ❌ **Analytics** → `#analytics` (doesn't exist)
- ❌ **Automations** → `#automations` (doesn't exist)
- ❌ **AI Models** → `#ai-models` (doesn't exist)
- ❌ **Documents** → `#documents` (doesn't exist)
- ❌ **Settings** → `#settings` (doesn't exist)

**Solutions:**

### Option 1: Create Placeholder Pages (Quick Fix)
I can create simple placeholder pages for each section that say "Coming Soon" so the navigation works.

### Option 2: Create Scorecard Page (Better)
I can create a **Scorecard** page (based on your Scorecard 2025.xlsx) and add it to the navigation:
- `/scorecard.html` - Live scorecard dashboard

### Option 3: Disable Non-Working Links (Temporary)
I can disable or hide the links that don't work yet until we build those pages.

**Which would you prefer?**

---

## Once I Have Integration Code + ROC Board ID

I will:

1. **Complete Autotask Configuration**
   - Add Integration Code to `.env`
   - Add ROC Board ID to `.env`
   - Restart backend server

2. **Test Autotask API**
   ```bash
   curl http://localhost:8000/api/health
   # Should show autotask: "configured"

   curl "http://localhost:8000/api/autotask/tickets?start_date=2025-10-01&end_date=2025-10-24"
   # Should return ROC board tickets
   ```

3. **Build Scorecard Endpoints**
   - `/api/autotask/scorecard/weekly?week=43&year=2025`
   - `/api/autotask/scorecard/quarterly?quarter=4&year=2025`

4. **Create Scorecard Dashboard Page**
   - Real-time metrics from Autotask
   - Weekly/quarterly averages
   - Status indicators (red/yellow/green)
   - Based on your Scorecard 2025.xlsx structure

---

## Summary of Autotask Data We'll Collect

Based on your clarification that Autotask is for **tickets** (not sales):

### Reactive Operations Metrics:
1. **Tickets Opened** - Count of tickets created (filtered to ROC board)
2. **Tickets Closed** - Count of tickets resolved (filtered to ROC board)
3. **Same Day Close Rate** - `(Tickets closed same day / Total closed) × 100%`
4. **Utilization** - `(Billable hours / Total hours worked) × 100%`

### Time Tracking:
- Billable hours (from time entries)
- Non-billable hours
- Total hours worked

All filtered to ROC board only, as you specified.

---

## What to Do Next

**Please provide:**

1. **Integration Vendor Code** (from the dropdown in screenshot #2)
2. **ROC Board Queue ID** (from Autotask Service Desk → Queues)
3. **Dashboard preference:** Which option for fixing navigation?
   - [ ] Option 1: Create placeholder pages
   - [ ] Option 2: Create Scorecard page
   - [ ] Option 3: Disable non-working links

Once I have these, I can:
- Complete Autotask API setup
- Test the connection with real data
- Build the Scorecard dashboard
- Fix the navigation

---

## Questions?

If you have any questions about:
- How to find the Integration Code
- How to find the ROC Board ID
- What data we'll collect from Autotask
- The Scorecard dashboard design

Just let me know!
