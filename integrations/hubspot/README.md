# HubSpot Integration

CRM and sales activity tracking integration with HubSpot.

## Setup
1. Get API token from HubSpot Settings → Integrations → Private Apps
2. Add to `.env`: `HUBSPOT_API_KEY=your_key`

## Usage
```python
from integrations.hubspot.service import HubSpotService
service = HubSpotService()
metrics = service.get_sales_activity_metrics(start_date, end_date)
```
