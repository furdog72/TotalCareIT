# Datto Integration

Backup and RMM integration with Datto.

## Setup
1. Get API keys from Datto Portal
2. Add to `.env`:
   - `DATTO_API_PUBLIC_KEY`
   - `DATTO_API_PRIVATE_KEY`
   - `DATTO_PORTAL_URL`
   - `DATTO_RMM_URL`

## Usage
```python
from integrations.datto.service import DattoService
service = DattoService()
backups = service.get_backup_status()
```
