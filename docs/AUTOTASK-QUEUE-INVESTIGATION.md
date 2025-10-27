# Autotask Queue Investigation Results

## Summary

Investigation revealed that the queue IDs do NOT match the expected queue names. The "Pro Services" queue is actually automated security alerts, not manual service tickets.

## Queue Identification

Based on ticket title analysis:

| Queue ID | Actual Content | Previous Label | Status |
|----------|----------------|----------------|--------|
| 29683482 | **Security Alerts** (Blackpoint, SaaS Alerts) | Pro Services | ❌ Wrong |
| 29683483 | **ROC Board** (Manual tickets) | ROC | ✅ Correct |
| 29683479 | **Sales/Support** (Manual tickets) | Sales | ✅ Likely Correct |
| 29683490 | **TAM** (Monthly TAM tickets) | TAM | ✅ Correct |
| 29683484 | **Monitoring Alerts** (Backup jobs, server issues) | Unknown | Unknown |

## Detailed Analysis

### Queue 29683482 - Security Alerts (NOT Pro Services)

**Total Tickets**: 500 (hitting API limit)

**Sample Titles**:
- `[Blackpoint][TotalCareIT][Managed Application Control][Rule Hit]`
- `SaaS Alerts - TotalCareIT - scottadmin@totalcareit.com - System Compli...`
- `SaaS Alerts - TotalCareIT - scottadmin@totalcareit.com - System Compli...`

**Characteristics**:
- All Status 1 (New/Open)
- None have completedDate
- Automated security monitoring tickets
- Very high volume (500+ per week)
- Likely auto-created by Blackpoint and SaaS monitoring tools

**Conclusion**: This is an automated alert queue, not Pro Services.

### Queue 29683483 - ROC Board ✅

**Total Tickets**: 73 (for Oct 13-19)

**Sample Titles**:
- `CrewHu Test`
- `Your account has been accessed from a new IP address`
- `We detected synchronization errors in your directory`

**Characteristics**:
- Status 5 (Complete): 70 tickets
- Status 8: 2 tickets
- Status 28: 1 ticket
- 70 tickets have completedDate
- Manual reactive support tickets

**Conclusion**: Correctly identified as ROC board.

### Queue 29683479 - Sales/Support ✅

**Total Tickets**: 246 (currently open)

**Sample Titles**:
- `Test Ticket - Can you see me?`
- `RE: [External][Filevine] Pending request: Outlook Calendar Sync`
- `MFA setup`

**Characteristics**:
- Mix of sales and support inquiries
- Currently open (not closed)
- Likely correct identification

**Conclusion**: Appears to be Sales/Support queue.

### Queue 29683490 - TAM ✅

**Total Tickets**: 500 (hitting API limit)

**Sample Titles**:
- `Monthy TAM, CCVFD`
- `Monthly TAM, 8-Koi`
- `Monthly TAM, Small Clients`

**Characteristics**:
- Recurring monthly TAM tickets
- One per client per month
- High volume due to all-time history

**Conclusion**: Correctly identified as TAM queue.

### Queue 29683484 - Monitoring Alerts

**Total Tickets**: 500 (hitting API limit)

**Sample Titles**:
- `Critical services are not running on the server : EMFSVR`
- `Long running Veritas backup jobs`
- `Long running Veritas backup jobs`

**Characteristics**:
- Automated monitoring alerts
- Server and backup monitoring
- High volume

**Conclusion**: Another automated alert queue.

## Root Cause of "500 Opened, 0 Closed"

Queue 29683482 (labeled as "Pro Services") contains:
- **Automated security alerts** from Blackpoint and SaaS monitoring
- All tickets have **Status 1** (New/Open)
- None have **completedDate** field populated
- These alerts are likely:
  - Auto-created by security tools
  - Auto-closed or dismissed without setting completedDate
  - Or left open indefinitely as informational

**This is NOT a bug** - it's the expected behavior for an automated alert queue.

## Status Code Meanings

Based on ROC ticket analysis:

| Status Code | Meaning | Has completedDate? |
|-------------|---------|-------------------|
| 1 | New/Open | No |
| 5 | Complete | Yes |
| 8 | Unknown | No |
| 28 | Unknown | No |

## Recommendations

### 1. Find Real Pro Services Queue

The current "Pro Services" queue (29683482) is actually security alerts. You need to:

**Option A**: Ask your team which queue contains actual Pro Services tickets
**Option B**: Look in Autotask UI sidebar for the Pro Services queue name
**Option C**: We can query more queues to find it

Which queue should we be tracking for **actual professional services project work**?

### 2. Exclude Alert Queues from Scorecard

Queues to potentially exclude:
- **29683482** - Security Alerts (Blackpoint, SaaS)
- **29683484** - Monitoring Alerts (Server, Backup)

These automated alerts aren't meaningful for scorecard tracking.

### 3. Update Queue Mappings

Suggested new mappings:

```bash
# Correctly identified queues
AUTOTASK_ROC_BOARD_ID=29683483
AUTOTASK_TAM_ID=29683490
AUTOTASK_SALES_ID=29683479

# Need to find
AUTOTASK_PRO_SERVICES_ID=???  # NOT 29683482

# Alert queues (exclude from scorecard)
AUTOTASK_SECURITY_ALERTS_ID=29683482
AUTOTASK_MONITORING_ALERTS_ID=29683484
```

### 4. Query All Queues

Would you like me to query ALL queue IDs to help you find the real Pro Services queue?

We can:
1. Get a list of all queues from Autotask
2. Sample tickets from each
3. Identify which one contains Pro Services work

## Next Steps

Please provide:

1. **Pro Services Queue**: What is the actual Pro Services queue in your Autotask workspace?
   - Go to Autotask → My Workspace & Queues
   - Look for "Pro Services" or "Professional Services" or "Projects"
   - Click on it and send me a screenshot or the queue name

2. **Should we exclude alert queues?** Should security and monitoring alerts be removed from the scorecard?

3. **Do you want to track alerts separately?** Should we create a separate dashboard for security alert metrics?

## Current Scorecard Status

With current queue assignments (Oct 13-19, 2025):

```
ROC Board: 73 opened, 70 closed, 62.9% same-day ✅
Security Alerts: 500 opened, 0 closed ❌ (Wrong queue)
TAM: 15 opened, 15 closed ✅
Sales: 246 currently open ✅
```

---

**Investigation Date**: October 24, 2025
**Issue**: Queue 29683482 is automated security alerts, NOT Pro Services
**Action Required**: Identify correct Pro Services queue ID
