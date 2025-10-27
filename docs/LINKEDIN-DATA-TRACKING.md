# LinkedIn Performance Data Tracking

Automated system for tracking LinkedIn performance metrics over time with monthly snapshots and weekly updates.

## Overview

The LinkedIn Performance tracking system collects and stores:
- **Monthly Snapshots**: Captured on the 1st of each month
- **Weekly Updates**: Captured every Saturday for the current month
- **Historical Comparison**: View trends across the last 6 months

## Data Structure

### Storage Location
All data is stored in: `/Users/charles/Projects/qbo-ai/data/linkedin/`

### Files
- `monthly_snapshots.json` - All monthly snapshots (1st of each month)
- `weekly_updates.json` - All weekly updates (every Saturday)
- `current_month.json` - Quick access to latest weekly update

### Data Format

**Monthly Snapshot** (collected on 1st of month):
```json
{
  "2025-01": {
    "month": "2025-01",
    "snapshot_date": "2025-01-01",
    "collected_at": "2025-01-01T00:00:00",
    "profiles": {
      "charles": { metrics },
      "jason": { metrics }
    },
    "company": { metrics }
  }
}
```

**Weekly Update** (collected every Saturday):
```json
{
  "2025-01": [
    {
      "week_ending": "2025-01-04",
      "month": "2025-01",
      "collected_at": "2025-01-04T00:00:00",
      "profiles": {
        "charles": { metrics },
        "jason": { metrics }
      },
      "company": { metrics }
    }
  ]
}
```

## Automation Setup

### Cron Jobs

Add these entries to cron to automate data collection:

```bash
# Edit crontab
crontab -e
```

Add these lines:

```cron
# LinkedIn Monthly Snapshot - 1st of each month at 12:00 AM
0 0 1 * * /Users/charles/Projects/qbo-ai/scripts/linkedin_monthly_snapshot.sh >> /Users/charles/Projects/qbo-ai/logs/linkedin_monthly.log 2>&1

# LinkedIn Weekly Update - Every Saturday at 12:00 AM
0 0 * * 6 /Users/charles/Projects/qbo-ai/scripts/linkedin_weekly_update.sh >> /Users/charles/Projects/qbo-ai/logs/linkedin_weekly.log 2>&1
```

### Create Log Directory

```bash
mkdir -p /Users/charles/Projects/qbo-ai/logs
```

## Manual Data Collection

### Collect Monthly Snapshot

```bash
cd /Users/charles/Projects/qbo-ai
source .venv/bin/activate
python -m api.linkedin_data_tracker monthly
```

### Collect Weekly Update

```bash
cd /Users/charles/Projects/qbo-ai
source .venv/bin/activate
python -m api.linkedin_data_tracker weekly
```

### View Dashboard Data

```bash
cd /Users/charles/Projects/qbo-ai
source .venv/bin/activate
python -m api.linkedin_data_tracker dashboard
```

## Environment Configuration

Add these to your `.env` file:

```bash
# LinkedIn Company ID
LINKEDIN_COMPANY_ID=your_company_id

# Competitor Company IDs (comma-separated)
LINKEDIN_COMPETITOR_IDS=competitor1_id,competitor2_id,competitor3_id
```

## API Integration

### Dashboard Endpoint

The LinkedIn Performance dashboard will fetch data from:

```
GET /api/linkedin/dashboard-data
```

This returns:
- Current month real-time data (latest weekly update)
- Historical data (last 6 monthly snapshots)
- Weekly trend for current month

### Example Response

```json
{
  "current": {
    "week_ending": "2025-01-25",
    "profiles": {
      "charles": {
        "post_impressions": 4287,
        "profile_views": 847,
        "followers": 1923,
        "search_appearances": 456,
        "connections": 2847
      },
      "jason": { ... }
    },
    "company": { ... }
  },
  "historical": {
    "months": ["2025-01", "2024-12", "2024-11", ...],
    "snapshots": { ... }
  },
  "weekly_trend": {
    "month": "2025-01",
    "weekly_updates": [ ... ]
  },
  "last_updated": "2025-01-25T12:00:00"
}
```

## Dashboard Features

The LinkedIn Performance dashboard shows:

1. **Current Month (Real-Time)**
   - Latest weekly update (updated every Saturday)
   - Current values for all metrics

2. **Historical Comparison**
   - Monthly snapshots from previous months
   - Trend charts showing growth over time
   - Month-over-month percentage changes

3. **Weekly Trend**
   - Week-by-week progression for current month
   - Shows how metrics are trending within the month

## Testing

### Test Monthly Snapshot Collection

```bash
cd /Users/charles/Projects/qbo-ai
source .venv/bin/activate
python -c "from api.linkedin_data_tracker import LinkedInDataTracker; tracker = LinkedInDataTracker(); print(tracker.collect_monthly_snapshot())"
```

### Test Weekly Update Collection

```bash
cd /Users/charles/Projects/qbo-ai
source .venv/bin/activate
python -c "from api.linkedin_data_tracker import LinkedInDataTracker; tracker = LinkedInDataTracker(); print(tracker.collect_weekly_update())"
```

## Troubleshooting

### No Data Appearing

1. Check if data directory exists:
   ```bash
   ls -la /Users/charles/Projects/qbo-ai/data/linkedin/
   ```

2. Check log files:
   ```bash
   tail -f /Users/charles/Projects/qbo-ai/logs/linkedin_weekly.log
   tail -f /Users/charles/Projects/qbo-ai/logs/linkedin_monthly.log
   ```

3. Verify LinkedIn API credentials in `.env`:
   ```bash
   cat /Users/charles/Projects/qbo-ai/.env | grep LINKEDIN
   ```

### Cron Jobs Not Running

1. Check cron service status:
   ```bash
   # macOS
   sudo launchctl list | grep cron
   ```

2. Check crontab entries:
   ```bash
   crontab -l
   ```

3. Test scripts manually:
   ```bash
   /Users/charles/Projects/qbo-ai/scripts/linkedin_weekly_update.sh
   /Users/charles/Projects/qbo-ai/scripts/linkedin_monthly_snapshot.sh
   ```

## Data Retention

- Monthly snapshots: Keep all (unlimited retention)
- Weekly updates: Keep current month + last 3 months
- Automatic cleanup runs on 1st of each month

## Backup

Monthly snapshots and weekly data should be backed up regularly:

```bash
# Backup to OneDrive
cp -r /Users/charles/Projects/qbo-ai/data/linkedin ~/OneDrive\ -\ Prevailing\ Networks\ Inc.\ dba\ TotalCareIT/LinkedIn_Performance_Backups/$(date +%Y-%m-%d)
```

## Future Enhancements

- [ ] Email alerts for significant metric changes
- [ ] Automated competitor tracking
- [ ] PDF report generation
- [ ] Integration with other marketing metrics
- [ ] Machine learning trend predictions
