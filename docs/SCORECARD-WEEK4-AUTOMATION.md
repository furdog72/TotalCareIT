# Scorecard Week 4 Automated Data Collection

## Overview

Week 4 (Oct 24, 2025) data needs to be collected automatically from various systems. This document outlines the data sources and required API integrations.

## Current Status

✅ **Weeks 1-3 Completed** - Extracted from Scorecard 2025.xlsx
⏳ **Week 4 Pending** - Needs automated collection setup

## Data Sources by Metric

### HubSpot (Jason/Charles Sales Metrics)

**Inside Sales Activity:**
- Dials (Jason) - Goal: 125
- Conversations with DM (Jason) - Goal: 13
- FTAs set (Jason) - Goal: 1

**Outside Sales Activity:**
- FTA Attended (Jason/Charles) - Goal: 1
- COI Attended (Jason/Charles) - Goal: 1
- Networking Events (Jason/Charles) - Goal: 1 (Manual)
- MRR Closed (Jason/Charles) - Goal: 500

**Hybrid Sales Activity:**
- COI Created (Josh) - Goal: 2
- COI Attended (Josh) - Goal: 2
- Networking Events (Josh) - Goal: 3

**W250 Activity:**
- W250 Dials (Charles) - Goal: 25
- W250 Conversations with DM (Charles) - Goal: 6
- W250 FTAs set (Charles) - Goal: 1

### Autotask (Scott's Reactive Operations)

**Reactive Operations:**
- Reactive Tickets Opened (Scott)
- Reactive Tickets Closed (Scott)
- Same day Close (Scott) - Goal: 0.7
- Utilization (Scott) - Goal: 0.6
- Tickets >7 days old (ROC) - Goal: 2
- Tickets Opened/IT 360 endpoint/month (Scott) - Goal: 0.5
- RHEM (Service Noise) (Scott) - Goal: 0.25
- Avg Response Time/Ticket (Scott) - Goal: 0.5
- Avg Resolution Time/Ticket (Scott) - Goal: 0.5

**Professional Services:**
- Professional Services Tickets Opened
- Professional Services Tickets Closed
- Tickets Over 30 Days Old - Goal: 7

**TAM:**
- # of Questions Answered (Joe)
- TAM Tickets Opened (Joe)
- TAM Tickets Closed (Joe)

### Datto Portal (Centralized Services)

**Backup Metrics:**
- Failed Backups > 48 Hours (50) - Goal: 0
- Failed Backups on Continuity > 7 Days - Goal: 0.2
- Failed Backups on SAAS > 48 Hours - Goal: 0.02

**Patch Metrics:**
- Missing > 5 Patches - Goal: 0.05

### Datto RMM (Windows Devices & AV)

**Windows Devices:**
- Total Windows 7 Devices (Charles) - Goal: 0
- Total Windows 10 Devices - Goal: 0
- Total Windows 11 EOL Devices - Goal: 0

**Antivirus:**
- Missing Hosted AV - Goal: 0.02

### Microsoft 365 (Security)

**Security Score:**
- TotalCareIT Microsoft Security Score (Joe) - Goal: 0.6

### Manual Entry (No API)

**Manual Metrics:**
- Reviews Complete (Charles) - Goal: 1
- Some networking events

## Required API Credentials

### HubSpot
- API Key or OAuth token
- Endpoint: `https://api.hubapi.com/`
- Documentation: https://developers.hubspot.com/docs/api/overview

### Autotask
- API Username/Password or API Integration Code
- Endpoint: `https://webservices.autotask.net/`
- Documentation: https://ww4.autotask.net/help/DeveloperHelp/Content/APIs/REST/API_Calls.htm

### Datto
- Portal API credentials
- RMM API credentials
- Endpoint: Varies by product
- Documentation: https://www.datto.com/api

### Microsoft 365
- Microsoft Graph API
- App Registration with appropriate permissions
- Endpoint: `https://graph.microsoft.com/`
- Documentation: https://docs.microsoft.com/en-us/graph/

## Implementation Plan

### Phase 1: API Setup (Immediate)
1. Gather API credentials for all systems
2. Test API connectivity
3. Document API endpoints and data formats

### Phase 2: Data Collection Script (Week 1)
1. Create `collect_scorecard_week4.py` script
2. Implement data fetchers for each system:
   - `fetch_hubspot_data()`
   - `fetch_autotask_data()`
   - `fetch_datto_portal_data()`
   - `fetch_datto_rmm_data()`
   - `fetch_microsoft_data()`
3. Map API data to scorecard KPIs
4. Update `scorecard-october-2025.json` week 4 values

### Phase 3: Automation (Week 2)
1. Create weekly cron job to run collection script
2. Set up error handling and logging
3. Create notification system for failures
4. Implement data validation

### Phase 4: Testing & Deployment (Week 3)
1. Test with week 4 data
2. Verify accuracy against manual counts
3. Deploy to production
4. Document for future weeks

## Next Steps

**Immediate Actions:**
1. Provide API credentials for:
   - HubSpot
   - Autotask
   - Datto Portal
   - Datto RMM
   - Microsoft 365 (if needed)

2. Run initial API tests to verify connectivity

3. Create mapping document showing:
   - Which API endpoint provides which KPI
   - Data transformation rules
   - Calculation formulas

## Script Template

A placeholder script has been created at:
`/Users/charles/Projects/qbo-ai/scripts/collect_scorecard_week4.py`

This script needs to be populated with:
- API credential configuration
- Data fetching logic for each system
- KPI calculation logic
- JSON update logic

## Questions to Answer

1. **HubSpot**: Which deals/contacts should be counted for each metric?
2. **Autotask**: What date range defines "week 4"? (Oct 18-24?)
3. **Datto**: Which endpoints/devices should be included?
4. **Calculations**: How are percentages calculated (e.g., RHEM, utilization)?

## Files Created

- ✅ `/Users/charles/Projects/qbo-ai/website/data/scorecard-october-2025.json` - Week 4 placeholder added
- ✅ `/Users/charles/Projects/qbo-ai/build_scorecard_2025.py` - HTML builder for 2025
- ✅ `/Users/charles/Projects/qbo-ai/SCORECARD-WEEK4-AUTOMATION.md` - This file
- ⏳ `/Users/charles/Projects/qbo-ai/scripts/collect_scorecard_week4.py` - To be created

## Support

For questions or issues:
- Check API documentation links above
- Review existing scorecard Excel formulas
- Contact system administrators for API access
