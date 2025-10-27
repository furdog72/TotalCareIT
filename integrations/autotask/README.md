# Autotask PSA Integration

Professional Services Automation integration for ticket tracking.

## Setup
1. Get API credentials from Autotask
2. Add to `.env`:
   - `AUTOTASK_USERNAME`
   - `AUTOTASK_SECRET`
   - `AUTOTASK_INTEGRATION_CODE`
   - `AUTOTASK_ZONE_URL`

## Usage
```python
from integrations.autotask.service import AutotaskService
service = AutotaskService()
tickets = service.get_roc_board_tickets(start_date, end_date)
```
