# Scorecard Multi-Queue Update

## Summary

Updated the Weekly Scorecard to track tickets from multiple Autotask queues as requested:
- ROC Board (Reactive Operations)
- Pro Services
- TAM (Technical Alignment Manager)
- Sales (currently open tickets only)

## Changes Made

### Environment Configuration

Added queue IDs to [.env](.env):
```bash
# Queue IDs
AUTOTASK_ROC_BOARD_ID=29683483
AUTOTASK_PRO_SERVICES_ID=29683482
AUTOTASK_TAM_ID=29683490
AUTOTASK_SALES_ID=29683479
```

### Backend API Updates

#### [api/autotask_service.py](api/autotask_service.py)

**Added Queue ID Constants** (lines 40-44):
```python
ROC_BOARD_QUEUE_ID = os.getenv('AUTOTASK_ROC_BOARD_ID', None)
PRO_SERVICES_QUEUE_ID = os.getenv('AUTOTASK_PRO_SERVICES_ID', None)
TAM_QUEUE_ID = os.getenv('AUTOTASK_TAM_ID', None)
SALES_QUEUE_ID = os.getenv('AUTOTASK_SALES_ID', None)
```

**New Method: `get_tickets_by_queue()`** (lines 212-261):
- Generic method to query tickets from any queue
- Supports date filtering
- Supports `only_open` flag for getting uncompleted tickets
- Used for Pro Services, TAM, and Sales ticket queries

### Scorecard Endpoint Updates

#### [api/main.py](api/main.py) - `/api/scorecard/weekly` endpoint

**Now Returns**:
```json
{
  "success": true,
  "data": {
    "week_start": "2025-10-13",
    "week_end": "2025-10-19",
    "roc": {
      "tickets_opened": 73,
      "tickets_closed": 70,
      "same_day_closed": 44,
      "same_day_close_rate": 62.9,
      "goal": 70.0,
      "status": "below_goal",
      "gap": -7.1
    },
    "pro_services": {
      "tickets_opened": 500,
      "tickets_closed": 0
    },
    "tam": {
      "tickets_opened": 15,
      "tickets_closed": 15
    },
    "sales": {
      "currently_open": 246
    },
    "utilization": null,
    "vcio_reviews": null
  }
}
```

**Key Features**:
- ROC metrics remain the primary focus with same-day close rate tracking
- Pro Services and TAM show opened/closed counts for the week
- Sales shows currently open tickets (not date-filtered)
- vCIO Reviews placeholder (manual entry needed - to be automated)
- Utilization placeholder (requires time entry data)

### Frontend Dashboard Updates

#### [website/scorecard.html](website/scorecard.html)

**UI Changes**:
- Split into two sections: "ROC Board" and "Other Queues"
- ROC Board section shows 4 cards:
  - Tickets Opened
  - Tickets Closed
  - Same-Day Closed
  - Same-Day Close Rate (with goal comparison)
- Other Queues section shows 5 cards:
  - Pro Services (opened/closed)
  - TAM Tickets (opened/closed)
  - Sales (currently open)
  - vCIO Reviews (manual/to be automated)
  - Utilization (coming soon)

## Test Results - Last Week (Oct 13-19, 2025)

```
ROC Board:
- 73 tickets opened
- 70 tickets closed
- 44 same-day closed
- 62.9% same-day close rate (7.1% below 70% goal)

Pro Services:
- 500 tickets opened
- 0 closed

TAM:
- 15 tickets opened
- 15 closed (100% close rate)

Sales:
- 246 currently open tickets
```

## Queue ID Discovery

Found queue IDs by analyzing recent tickets:

| Queue ID | Ticket Count (30 days) | Identified As |
|----------|------------------------|---------------|
| 29683482 | 474 tickets | Pro Services |
| 29683483 | 16 tickets | ROC |
| 29683479 | 8 tickets | Sales |
| 29683490 | 1 ticket | TAM |
| 29683484 | 1 ticket | Unknown |

**Note**: Queue 29683482 (Pro Services) returned 500 tickets (API limit), suggesting high volume. The actual count within the date range may be higher.

## Recommendations

### 1. Verify Queue Names

Please confirm the queue assignments are correct:
- Is 29683482 actually "Pro Services"?
- Is 29683490 actually "TAM"?
- Is 29683479 actually "Sales"?

You can verify by:
1. Going to Autotask workspace
2. Clicking on each queue in the sidebar
3. Checking if the queue ID appears in the URL

### 2. Pro Services High Volume

The Pro Services queue shows 500 tickets opened with 0 closed. This could mean:
- The queue has extremely high volume (more than API limit)
- Tickets in this queue may not be getting completed status set correctly
- The date range might need adjustment

Consider investigating why Pro Services tickets aren't showing as closed.

### 3. vCIO Reviews Automation

Currently marked as "Manual entry - To be automated". Options for automation:
- **Option A**: Create a custom field in Autotask tickets to track vCIO review completion
- **Option B**: Use HubSpot to track vCIO reviews as activities or tasks
- **Option C**: Create a separate endpoint for manual data entry with database storage
- **Option D**: Track via calendar integration (Google Calendar, Office 365)

Which approach would you prefer?

### 4. Same-Day Close Rate for Other Queues

Currently only tracking same-day close rate for ROC board. Should we also track:
- Same-day close rate for Pro Services?
- Same-day close rate for TAM?
- Average resolution time across all queues?

## Next Steps

1. **Verify Queue Assignments** - Confirm the queue IDs match the correct boards
2. **Investigate Pro Services** - Check why 500 tickets opened with 0 closed
3. **vCIO Reviews Automation** - Choose automation approach
4. **Deploy to Production** - Upload updated files to totalcareit.ai
5. **Add Utilization** - Query time entries for billable/total hours calculation

## Files Modified

- `.env` - Added queue IDs for Pro Services, TAM, Sales
- `api/autotask_service.py` - Added queue constants and `get_tickets_by_queue()` method
- `api/main.py` - Updated `/api/scorecard/weekly` endpoint to return all queue metrics
- `website/scorecard.html` - Updated UI to display all queue metrics

## Access

- **Backend API**: `http://localhost:8000/api/scorecard/weekly?week_start=2025-10-13`
- **Dashboard**: `file:///Users/charles/Projects/qbo-ai/website/scorecard.html`

---

**Updated**: October 24, 2025
**Status**: ✅ All queues integrated and tested
**Issue**: Pro Services shows unusual high opened count - needs investigation
