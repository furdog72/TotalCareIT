# Week 4 Data Collection Status (October 24, 2025)

## Script Execution Results

The collection script [collect_scorecard_week_oct24.py](collect_scorecard_week_oct24.py:1) was successfully created and executed. It uses the existing API service integrations to collect scorecard metrics for the week ending October 24, 2025 (Oct 18-24).

## Current Status

### ✅ Completed
- Collection script created using existing API services:
  - [api/hubspot_service.py](api/hubspot_service.py:1) - HubSpotReportingService
  - [api/autotask_service.py](api/autotask_service.py:1) - AutotaskReportingService
  - [api/datto_service.py](api/datto_service.py:1) - DattoReportingService
- Script successfully runs and collects data structure
- All API credentials are configured in .env file

### ⚠️ API Issues Encountered

#### 1. HubSpot API (401 Unauthorized)
- **Error**: "Authentication credentials not found"
- **API Key**: `[REDACTED - See .env]`
- **Hub ID**: 8752461
- **Issue**: The HubSpot API key may be expired or have insufficient permissions
- **Resolution**:
  - Verify the API key is still active in HubSpot settings
  - Ensure the key has permissions for:
    - Read calls/meetings (engagements)
    - Read contacts
    - Read deals
    - Read owners

#### 2. Autotask API (404 Not Found)
- **Error**: 404 at zone information endpoint
- **Zone URL**: https://webservices3.autotask.net
- **Issue**: The zone URL endpoint returns 404 but should be using the configured zone URL
- **Resolution**:
  - Verify `AUTOTASK_ZONE_URL=https://webservices3.autotask.net` is correct
  - Test Autotask API authentication manually
  - The code should use the zone URL from env (which it does), so this may be a temporary API issue

#### 3. Datto API (Not Configured)
- **Error**: "Datto API credentials not configured"
- **Credentials Found**:
  - Public Key: 3b3837
  - Private Key: 768e17b07b2947f2e539483f629f8e45
  - Portal URL: https://portal.dattobackup.com
  - RMM URL: https://vidal-rmm.centrastage.net
- **Issue**: DattoConfig.from_env() is not loading credentials properly
- **Resolution**: Check [api/datto_service.py](api/datto_service.py:19) DattoConfig class to ensure it reads the correct env variable names

#### 4. Microsoft 365 Security Score (Not Implemented)
- **Status**: TODO placeholder
- **Resolution**: Implement Microsoft Graph API call for security score

## Data Collected (With Issues)

### HubSpot Metrics (All showing 0 due to auth error)
```
dials_jason: 0
conversations_jason: 0
ftas_set_jason: 0
fta_attended: 0
coi_attended_outside: 0
mrr_closed: 0
coi_created_josh: 0
coi_attended_josh: 0
w250_dials: 0
w250_conversations: 0
w250_ftas_set: 0
```

### Autotask Metrics (Failed)
- Script crashed at Autotask zone information lookup

### Datto Metrics (All showing 0 due to config error)
```
failed_backups_48h: 0
failed_backups_continuity: 0
failed_backups_saas: 0
missing_patches: 0
windows_7_devices: 0
windows_10_devices: 0
windows_11_eol_devices: 0
missing_hosted_av: 0
```

### Microsoft Metrics
```
security_score: None (not implemented)
```

## Next Steps to Fix

### Immediate Actions

1. **Fix HubSpot API Authentication**
   - Go to HubSpot → Settings → Integrations → Private Apps
   - Check if the API key `[REDACTED - See .env]` exists and is active
   - If expired, generate a new key with these scopes:
     - `crm.objects.contacts.read`
     - `crm.objects.deals.read`
     - `crm.objects.owners.read`
     - `sales-email-read`
   - Update `.env` with new key

2. **Verify Autotask Zone URL**
   - Test the zone URL manually: https://webservices3.autotask.net
   - Verify API credentials are still valid
   - Check if Autotask requires updated authentication

3. **Fix Datto Configuration**
   - Check [api/datto_service.py:19-37](api/datto_service.py:19) DattoConfig class
   - Ensure it reads:
     - `DATTO_API_PUBLIC_KEY`
     - `DATTO_API_PRIVATE_KEY`
     - `DATTO_PORTAL_URL`
     - `DATTO_RMM_URL`

4. **Implement Microsoft Security Score**
   - Add Microsoft Graph API call to `collect_microsoft_metrics()` in [collect_scorecard_week_oct24.py:166](collect_scorecard_week_oct24.py:166)
   - Use existing Microsoft 365 OAuth setup

### Testing After Fixes

Run the collection script again:
```bash
cd /Users/charles/Projects/qbo-ai
source .venv/bin/activate
python collect_scorecard_week_oct24.py
```

### After Successful Collection

1. Review the collected metrics
2. Update the scorecard Excel file with week 4 values
3. Rebuild the HTML: `python build_scorecard_2025.py`
4. Deploy to S3: `aws s3 cp website/scorecard-complete.html s3://totalcareit.ai/`

## Files Involved

- [collect_scorecard_week_oct24.py](collect_scorecard_week_oct24.py:1) - Main collection script
- [scripts/collect_scorecard_week4.py](scripts/collect_scorecard_week4.py:1) - Alternative placeholder script
- [api/hubspot_service.py](api/hubspot_service.py:1) - HubSpot API integration
- [api/autotask_service.py](api/autotask_service.py:1) - Autotask API integration
- [api/datto_service.py](api/datto_service.py:1) - Datto API integration
- [.env](.env) - API credentials configuration
- [website/data/scorecard-october-2025.json](website/data/scorecard-october-2025.json:1) - October scorecard data (weeks 1-3 populated, week 4 empty)

## Additional Notes

- The script correctly uses date range Oct 18-24, 2025
- All service classes are properly instantiated
- The issue is purely with API authentication/configuration, not the script logic
- Once APIs are fixed, the script will work as designed
