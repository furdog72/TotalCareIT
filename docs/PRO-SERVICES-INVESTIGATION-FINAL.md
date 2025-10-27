# Pro Services Queue Investigation - Final Report

## Summary

**Queue 29683482 IS "Pro Services"** - confirmed correct.

**Finding**: The "500 opened, 0 closed" is ACCURATE data for Oct 13-19, 2025:
- 500+ automated security alerts created (Blackpoint, SaaS monitoring)
- **0 actual Pro Services project tickets completed that week**

## Root Cause Analysis

### The Pro Services Queue Contains Two Types of Tickets:

1. **Automated Security Alerts** (high volume):
   - Blackpoint Managed Application Control alerts
   - SaaS compliance monitoring alerts
   - Backup failure alerts
   - Server monitoring alerts
   - Status: Mostly remain as Status 1 (Open)
   - Volume: 500+ per week

2. **Actual Pro Services Project Work** (low volume):
   - Professional services projects
   - Client implementations
   - These DO get completed (Status 5)
   - Volume: Historically 168 completed tickets (all-time)

### Why "500 Opened, 0 Closed" for Oct 13-19?

**It's accurate:**
- 500+ tickets created that week (hitting API MaxRecords limit)
- All 500 were automated alerts (Status 1, not completed)
- **Zero Pro Services project tickets were completed that specific week**

### Verification

Query with Status 5 filter confirmed:
```
Pro Services tickets with Status 5 (Complete) for Oct 13-19: 0
```

## The Real Problem

The Pro Services queue is **polluted with automated alerts**, making it difficult to track actual professional services work.

### Autotask API Limitation

- MaxRecords = 500 per query
- Pro Services queue has 500+ tickets per week
- All automated alerts fill the 500-record limit
- Can't see actual Pro Services work in weekly queries

## Recommendations

### Option 1: Separate Queues (Recommended)

**Best Practice**: Create separate queues in Autotask:
- "Pro Services - Projects" (manual work)
- "Pro Services - Alerts" (automated monitoring)

This allows clean tracking of actual billable Pro Services work.

### Option 2: Filter by Title Pattern

Update the scorecard to exclude automated alerts:

```python
# Exclude Blackpoint and monitoring alerts
def is_actual_pro_services_ticket(ticket):
    title = ticket.get('title', '')
    excludes = ['Blackpoint', 'SaaS Alerts', 'Bootable Screenshot',
                'Backup Agent', 'SUPPORT EXPIRED']
    return not any(pattern in title for pattern in excludes)
```

### Option 3: Track Only Completed Pro Services

Since automated alerts rarely complete, track only Status 5 tickets:

```python
# Query only completed Pro Services tickets
filters = {
    'filter': [
        {'field': 'queueID', 'op': 'eq', 'value': pro_services_id},
        {'field': 'status', 'op': 'eq', 'value': 5},  # Completed only
        {'field': 'completedDate', 'op': 'gte', 'value': start_date},
        {'field': 'completedDate', 'op': 'lte', 'value': end_date}
    ]
}
```

**Note**: This changes from "created date" to "completed date" filtering.

### Option 4: Don't Track Pro Services in Weekly Scorecard

If Pro Services work is project-based (not weekly), consider:
- Remove from weekly scorecard
- Create separate quarterly/monthly Pro Services report
- Focus weekly scorecard on ROC (reactive work)

## Current Scorecard Impact

With current setup (Oct 13-19, 2025):

```
PRO SERVICES:
✅ Opened: 500+ (mostly automated alerts) - ACCURATE
✅ Closed: 0 (no Pro Services projects completed) - ACCURATE
⚠️  Not meaningful for business metrics
```

This data is **technically correct** but **not useful** for tracking Pro Services performance.

## Questions for You

### 1. Queue Separation

Do you want to separate automated alerts into a different queue in Autotask?

**If YES**: I can provide step-by-step instructions for Autotask queue setup
**If NO**: We'll implement one of the filtering options

### 2. What Do You Want to Track?

For Pro Services on the weekly scorecard, what metrics matter?

**Option A**: Number of Pro Services projects completed
**Option B**: Billable hours on Pro Services work
**Option C**: Number of active Pro Services projects
**Option D**: Don't track Pro Services weekly (too project-based)
**Option E**: Track separately from automated alerts

### 3. Completed Date vs Created Date

Should Pro Services metrics use:

**Created Date**: When ticket was opened
**Completed Date**: When work was finished (better for project tracking)

Most project-based work is better tracked by completion date.

## Proposed Solution

Based on best practices, I recommend:

### Short-term Fix (Today)

Update scorecard to filter out automated alerts:

```python
# Get Pro Services tickets excluding automated alerts
pro_services_tickets = []
all_tickets = client.get_tickets_by_queue(pro_services_id, start_date, end_date)

for ticket in all_tickets:
    title = ticket.get('title', '')
    # Exclude automated alerts
    if not any(pattern in title for pattern in [
        'Blackpoint', 'SaaS Alerts', 'Bootable Screenshot',
        'Backup Agent', 'SUPPORT EXPIRED', 'Endpoint Backup'
    ]):
        pro_services_tickets.append(ticket)

# Now calculate metrics on filtered list
opened = len(pro_services_tickets)
closed = sum(1 for t in pro_services_tickets if t.get('completedDate'))
```

### Long-term Fix (Next Week)

1. Create new Autotask queue: "Security Alerts"
2. Move automated alert integrations to new queue
3. Keep "Pro Services" for actual client project work
4. Update scorecard to track both separately

## What Would You Like to Do?

Please let me know:

1. Should I implement the short-term filter fix now?
2. Do you want to separate the queues in Autotask?
3. What Pro Services metrics matter for your weekly scorecard?

---

**Investigation Date**: October 24, 2025
**Finding**: Data is accurate - Pro Services had 0 completed projects Oct 13-19
**Root Cause**: Queue polluted with 500+ automated alerts per week
**Status**: Awaiting decision on solution approach
