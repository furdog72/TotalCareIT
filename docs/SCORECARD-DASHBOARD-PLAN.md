# Scorecard & PBR Dashboard Implementation Plan

## Overview

This document outlines the plan to create an automated web-based dashboard that displays the TotalCareIT Scorecard 2025 and Performance-Based Reporting (PBR) metrics.

**Goal:** Automatically collect, calculate, and display key performance metrics on a webpage in real-time.

## Scorecard 2025 Metrics Identified

Based on the Scorecard 2025.xlsx file, here are the key metrics tracked:

### 1. **Inside Sales Activity** (Jason)
**Metrics:**
- **Dials** (Goal: 125/week)
- **Conversations with DM** (Decision Maker) (Goal: 13/week)
- **FTAs Set** (First Time Appointments) (Goal: 1/week)

**Data Source:** CRM (HubSpot) + Manual entry
**Calculation:** Weekly count of sales activities

---

### 2. **Outside Sales Activity** (Jason/Charles)
**Metrics:**
- **FTA Attended** (Goal: 1/week)
- **COI Attended** (Center of Influence meetings) (Goal: 1/week)
- **Networking Events** (Goal: 1/week)
- **MRR Closed** (Monthly Recurring Revenue) (Goal: $500/week)

**Data Source:** CRM (HubSpot) + Manual entry
**Calculation:**
- FTA/COI/Events: Count per week
- MRR: Sum of closed deals' MRR value

---

### 3. **Hybrid Sales Activity** (Josh)
**Metrics:**
- **COI Created** (Goal: 2/week)
- **COI Attended** (Goal: 2/week)
- **Networking Events** (Goal: 3/week)

**Data Source:** CRM (HubSpot) + Manual entry
**Calculation:** Weekly count

---

### 4. **Warm 250 Activity** (Charles)
**Metrics:**
- **W250 Dials** (Goal: 25/week)
- **W250 Conversations with DM** (Goal: 6/week)
- **W250 FTAs Set** (Goal: 1/week)

**Data Source:** CRM (HubSpot) - specific list/segment
**Calculation:** Weekly count filtered to "Warm 250" contact list

---

### 5. **Reactive Operations** (Scott) ⭐ **PRIMARY AUTOTASK DATA**
**Metrics:**
- **Reactive Tickets Opened** (tracked weekly)
- **Reactive Tickets Closed** (tracked weekly)
- **Same Day Close Rate** (Goal: 70%)
- **Utilization** (Goal: 60%)

**Data Source:** **AUTOTASK** (Kaseya)
**Calculation:**
- Tickets Opened: Count of new tickets created in week
- Tickets Closed: Count of tickets closed in week
- Same Day Close: `(Tickets closed same day / Total tickets closed) * 100`
- Utilization: `(Billable hours / Total hours worked) * 100`

---

### 6. **Marketing Activity**
**Metrics:**
- Email campaigns sent
- Website traffic
- Lead generation
- Social media engagement

**Data Source:** HubSpot Marketing Hub
**Calculation:** Various marketing metrics from HubSpot

---

### 7. **Financial Metrics**
**Metrics:**
- Revenue
- Expenses
- Profit margin
- Cash flow

**Data Source:** QuickBooks Online
**Calculation:** Financial reports from QBO

---

## Data Sources & API Access

### 1. Autotask (Kaseya) - ⭐ **PRIMARY FOCUS**

**What We Need:**
- Reactive tickets opened (by week)
- Reactive tickets closed (by week)
- Ticket created date/time
- Ticket closed date/time
- Ticket queue (filter for "ROC Board" only)
- Time entries (for utilization calculation)
  - Billable hours
  - Non-billable hours
  - Total hours

**API Setup:**
1. **Already Created:** `api/autotask_service.py` exists
2. **Need to Configure:**
   - `AUTOTASK_USERNAME` - API user (read-only)
   - `AUTOTASK_SECRET` - API secret
   - `AUTOTASK_INTEGRATION_CODE` - Integration code
   - `AUTOTASK_ROC_BOARD_ID` - ROC board queue ID

**API Endpoints Needed:**
- `/api/autotask/tickets` - Get tickets with date range filter
- `/api/autotask/activity` - Get time entries for utilization
- `/api/autotask/report/daily` - Daily metrics
- `/api/autotask/report/weekly` - Weekly metrics (for Scorecard)

**See:** [AUTOTASK-SETUP.md](AUTOTASK-SETUP.md) for detailed setup instructions

---

### 2. HubSpot - ✅ **ALREADY CONFIGURED**

**What We Have:**
- CRM data (contacts, deals, companies)
- Forms and submissions
- Website analytics (limited on Starter tier)

**What We Need for Scorecard:**
- Custom activities tracking:
  - Dials (call logging)
  - Conversations with DM (call outcomes)
  - FTAs set (meeting scheduling)
  - COI meetings attended
  - Networking events attended
- Deal tracking with MRR field
- Contact segmentation ("Warm 250" list)

**API Status:** ✅ Fully configured and tested
**Credentials:** Already in `.env`

**Custom Fields Needed in HubSpot:**
- Deal: `monthly_recurring_revenue` (MRR)
- Activity: `activity_type` (Dial, Conversation, FTA, COI, Networking)
- Contact: `warm_250_status` (boolean or list membership)

---

### 3. QuickBooks Online - ✅ **ALREADY CONFIGURED**

**What We Need:**
- Revenue (monthly/quarterly)
- Expenses (monthly/quarterly)
- Profit & Loss statements
- Cash flow data

**API Status:** ✅ OAuth configured, connection working
**Credentials:** Already in `.env`

**QBO Entities to Query:**
- `Invoice` - for revenue
- `Bill`, `Expense` - for expenses
- `Account` - for P&L accounts
- `ProfitAndLoss` report

---

### 4. Manual Entry (Future Enhancement)

Some metrics may require manual entry initially:
- Networking events attended
- COI meetings created/attended
- W250 specific activities (if not tagged in HubSpot)

**Solution:** Create simple web form for weekly data entry
**Location:** `/scorecard/manual-entry` page

---

## Autotask API Setup Steps

### Step 1: Create API User (You'll Do This)

1. **Login to Autotask**
   - Go to https://ww4.autotask.net (or your zone)

2. **Create Read-Only API User**
   - Admin → Resources (Users)
   - Add New → API User
   - Username: `api-readonly@totalcareit.com`
   - Security Level: **API User (System)** with READ-ONLY permissions

3. **Generate API Credentials**
   - Go to Admin → API Users
   - Select the user
   - Generate Integration Code
   - Generate API Secret

4. **Find ROC Board Queue ID**
   - Service Desk → Queues
   - Find "ROC" or "Reactive Operations" queue
   - Note the Queue ID (visible in URL or queue settings)

### Step 2: Configure Environment Variables

Add to `.env`:
```bash
# ===== AUTOTASK API CONFIGURATION =====
AUTOTASK_USERNAME=api-readonly@totalcareit.com
AUTOTASK_SECRET=your_secret_here
AUTOTASK_INTEGRATION_CODE=your_integration_code_here
AUTOTASK_ROC_BOARD_ID=1234567
```

### Step 3: Test API Connection

```bash
# Start backend server
source .venv/bin/activate
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000

# Test health check
curl http://localhost:8000/api/health

# Test Autotask tickets
curl "http://localhost:8000/api/autotask/tickets?start_date=2025-10-01&end_date=2025-10-24"
```

---

##Dashboard Design

### Page: `/scorecard` or `/dashboard/scorecard`

**Layout:**

```
┌─────────────────────────────────────────────────────────────┐
│  TotalCareIT Scorecard 2025                    Week: 43/52  │
│  ══════════════════════════════════════════════════════════ │
│                                                               │
│  📈 INSIDE SALES (Jason)                            Q4 2025  │
│  ┌─────────────┬──────┬────────┬───────┬──────────────────┐ │
│  │ Metric      │ Goal │ This W │ Last W│ Q4 Avg           │ │
│  ├─────────────┼──────┼────────┼───────┼──────────────────┤ │
│  │ Dials       │ 125  │  101   │  70   │ 86 (🔴 Below)   │ │
│  │ Convos w/DM │  13  │   21   │  16   │ 14.5 (✅ Above) │ │
│  │ FTAs Set    │   1  │    0   │   1   │ 0.5 (🔴 Below)  │ │
│  └─────────────┴──────┴────────┴───────┴──────────────────┘ │
│                                                               │
│  🎯 OUTSIDE SALES (Jason/Charles)                            │
│  ┌─────────────┬──────┬────────┬───────┬──────────────────┐ │
│  │ FTA Attended│   1  │    1   │   1   │ 0.67 (🟡 On)    │ │
│  │ COI Attended│   1  │    2   │   3   │ 2.33 (✅ Above) │ │
│  │ Networking  │   1  │    3   │   7   │ 4 (✅ Above)    │ │
│  │ MRR Closed  │ $500 │   $0   │   $0  │ $0 (🔴 Below)   │ │
│  └─────────────┴──────┴────────┴───────┴──────────────────┘ │
│                                                               │
│  ⚙️ REACTIVE OPERATIONS (Scott) - AUTOTASK DATA              │
│  ┌─────────────────────┬──────┬────────┬───────┬──────────┐ │
│  │ Metric              │ Goal │ This W │ Last W│ Q4 Avg   │ │
│  ├─────────────────────┼──────┼────────┼───────┼──────────┤ │
│  │ Tickets Opened      │  --  │   69   │  78   │ 76.5     │ │
│  │ Tickets Closed      │  --  │   79   │  59   │ 76       │ │
│  │ Same Day Close Rate │  70% │  53%   │  49%  │ 58% 🔴   │ │
│  │ Utilization         │  60% │  63%   │  55%  │ 59% 🟡   │ │
│  └─────────────────────┴──────┴────────┴───────┴──────────┘ │
│                                                               │
│  📊 QUARTERLY SUMMARY                                         │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ • Total Deals: 18 ($97,743.96)                           ││
│  │ • Closed Won: 2  |  Closed Lost: 13  |  In Progress: 3  ││
│  │ • HubSpot Contacts: 5+ recent                            ││
│  │ • Forms: 20 (0 submissions)                              ││
│  └──────────────────────────────────────────────────────────┘│
│                                                               │
│  [View Details] [Export PDF] [Historical Data]               │
└─────────────────────────────────────────────────────────────┘
```

### Status Indicators:
- ✅ **Green** - Meeting or exceeding goal
- 🟡 **Yellow** - Within 10% of goal
- 🔴 **Red** - Below goal by >10%

---

## Implementation Steps

### Phase 1: Autotask Integration (CURRENT FOCUS)

**Week 1:**
1. ✅ Review existing Autotask service code
2. ⏳ **YOU: Create Autotask API user and get credentials**
3. ⏳ Configure `.env` with Autotask credentials
4. ⏳ Test Autotask API connection
5. ⏳ Verify ROC board ticket filtering works

**Week 2:**
6. Create weekly metrics endpoints for Autotask data
7. Implement same-day close calculation
8. Implement utilization calculation
9. Create data aggregation for weekly/quarterly views

### Phase 2: HubSpot Custom Fields & Activities

**Week 3:**
10. Create custom activity types in HubSpot
11. Set up "Warm 250" contact list/tag
12. Add MRR custom field to deals
13. Test activity logging via API

### Phase 3: Frontend Dashboard

**Week 4:**
14. Create `/scorecard` page HTML/CSS
15. Create scorecard JavaScript client
16. Connect to backend APIs
17. Implement real-time data display
18. Add status indicators (red/yellow/green)

### Phase 4: QuickBooks Financial Integration

**Week 5:**
19. Add financial metrics to scorecard
20. Create P&L summary widget
21. Revenue/expense trending

### Phase 5: Manual Entry & Enhancements

**Week 6:**
22. Create manual entry form (if needed)
23. Add export to PDF functionality
24. Add historical data viewer
25. Set up automated email reports

---

## API Endpoints Architecture

### Autotask Endpoints (To Be Created)

```
GET /api/autotask/scorecard/weekly?week=43&year=2025
Response: {
  "week": 43,
  "year": 2025,
  "start_date": "2025-10-20",
  "end_date": "2025-10-26",
  "metrics": {
    "tickets_opened": 69,
    "tickets_closed": 79,
    "same_day_close_rate": 0.53,
    "utilization": 0.63,
    "billable_hours": 125.5,
    "total_hours": 199.2
  }
}

GET /api/autotask/scorecard/quarterly?quarter=4&year=2025
Response: {
  "quarter": 4,
  "year": 2025,
  "weeks": [...],
  "avg_metrics": {
    "tickets_opened_avg": 76.5,
    "tickets_closed_avg": 76,
    "same_day_close_rate_avg": 0.58,
    "utilization_avg": 0.59
  }
}
```

### HubSpot Endpoints (To Be Created)

```
GET /api/hubspot/scorecard/sales-activity?week=43&year=2025
Response: {
  "jason": {
    "dials": 101,
    "conversations_dm": 21,
    "ftas_set": 0
  },
  "charles": {
    "w250_dials": 14,
    "w250_conversations": 4,
    "w250_ftas": 1
  },
  "josh": {
    "coi_created": 0,
    "coi_attended": 0,
    "networking_events": 0
  }
}

GET /api/hubspot/scorecard/mrr-closed?start_date=2025-10-20&end_date=2025-10-26
Response: {
  "total_mrr": 0,
  "deals_closed": 0,
  "deals": []
}
```

---

## Questions to Answer

Before proceeding, please help clarify:

### 1. **Autotask API Access**
- Do you already have an API user created in Autotask?
- Can you create a read-only API user and get credentials?
- Do you know the ROC Board Queue ID?

### 2. **Metric Calculations**
- **Same Day Close Rate:** Is this tickets created AND closed on the same calendar day?
- **Utilization:** Is this `billable_hours / total_hours_worked`? Or different formula?
- **MRR Closed:** Should this be sum of all closed deals' MRR, or only new MRR (not renewals)?

### 3. **HubSpot Activities**
- Are dials, conversations, FTAs currently logged in HubSpot? Or manually tracked?
- Do you have a "Warm 250" list/segment in HubSpot?
- Do deals have an MRR field?

### 4. **Dashboard Preferences**
- Should the dashboard update in real-time or daily?
- Who should have access? (Only authenticated partners, or public?)
- Do you want PDF export functionality?

---

## Next Steps - Action Required

### Immediate (This Week):

**YOU:**
1. **Create Autotask API User**
   - Follow [AUTOTASK-SETUP.md](AUTOTASK-SETUP.md)
   - Send me the credentials to add to `.env`

2. **Find ROC Board ID**
   - In Autotask, go to your ROC/Reactive queue
   - Send me the Queue ID

3. **Answer Metric Calculation Questions**
   - Clarify same-day close and utilization formulas
   - Confirm HubSpot field status

**ME:**
Once you provide credentials:
1. Configure Autotask in `.env`
2. Test API connection
3. Build weekly metrics endpoints
4. Start frontend dashboard development

---

## Files & Documentation

**Existing:**
- [api/autotask_service.py](api/autotask_service.py) - Autotask API client (already created)
- [api/hubspot_service.py](api/hubspot_service.py) - HubSpot API client (✅ working)
- [AUTOTASK-SETUP.md](AUTOTASK-SETUP.md) - Step-by-step Autotask setup guide
- [HUBSPOT-SETUP.md](HUBSPOT-SETUP.md) - HubSpot setup guide (✅ complete)

**To Be Created:**
- `api/scorecard_service.py` - Scorecard calculation logic
- `website/scorecard.html` - Dashboard frontend
- `website/js/scorecard.js` - Dashboard JavaScript
- `website/css/scorecard.css` - Dashboard styling
- `SCORECARD-METRICS.md` - Detailed metric definitions

---

## Summary

**Goal:** Automated Scorecard 2025 dashboard displaying real-time KPIs

**Primary Data Source:** Autotask (for Reactive Operations metrics)

**Status:**
- ✅ HubSpot API integrated and tested
- ✅ QuickBooks OAuth configured
- ⏳ **Autotask API needs credentials** ← **BLOCKER**
- ⏳ Dashboard frontend not started

**Next Action:** **You provide Autotask API credentials, and I'll build the rest!**

---

**Questions? Let me know what metrics you'd like clarified, and I can explain the data sources and calculations in detail.**
