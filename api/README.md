# TotalCareIT Partner Portal API

Backend API server for securely accessing multiple business systems.

## Features

- **HubSpot Integration**: CRM data, contacts, deals, calls, meetings, sales metrics
- **Autotask PSA Integration**: Service desk tickets, time entries, reporting
- **Datto Commerce**: Sales opportunities, quotes, product catalog
- **Datto RMM**: Device management, alerts, sites, monitoring
- **ConnectWise Manage**: Tickets, opportunities, time tracking, agreements
- **Microsoft 365**: Users, groups, licenses, SharePoint, Teams
- **Health Check**: Monitor API configuration and connectivity
- **Unified API**: All integrations through one secure endpoint

## Quick Start

### 1. Install Dependencies

```bash
cd api
pip3 install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env and add your API credentials
```

### 3. Get HubSpot Access Token

1. Go to HubSpot Settings → Integrations → Private Apps
2. Create a new private app with these scopes:
   - `crm.objects.contacts.read`
   - `crm.objects.deals.read`
   - `crm.objects.companies.read`
   - `sales-email-read`
3. Copy the access token to `.env`

### 4. Run the API Server

```bash
python3 main.py
```

The API will start at `http://localhost:8000`

## API Endpoints

### Health Check
- `GET /` - Basic health check
- `GET /api/health` - Detailed health check with service status

### HubSpot Endpoints
- `GET /api/hubspot/crm/summary` - CRM summary statistics
- `GET /api/hubspot/contacts/recent` - Recently created contacts
- `GET /api/hubspot/deals/pipeline` - Sales pipeline by stage
- `GET /api/hubspot/sales-metrics` - **Sales report metrics** (calls, meetings, funnel)
- `GET /api/hubspot/analytics` - Website analytics
- `GET /api/hubspot/forms` - Form submission stats

### Autotask Endpoints
- `GET /api/autotask/tickets` - Get tickets with date filtering
- `GET /api/autotask/activity` - Get activity summary
- `GET /api/autotask/report/daily` - Daily ticket report
- `GET /api/autotask/report/monthly` - Monthly ticket report

## Testing the API

```bash
# Health check
curl http://localhost:8000/api/health

# Get sales metrics (requires HubSpot token)
curl http://localhost:8000/api/hubspot/sales-metrics
```

## Deployment

### AWS EC2 / DigitalOcean Droplet

1. Install Python 3.9+
2. Clone repository
3. Install dependencies
4. Configure environment variables in `/etc/environment` or `.env`
5. Run with systemd service or supervisor

### Example systemd service

```ini
[Unit]
Description=TotalCareIT Partner Portal API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/totalcareit-api
Environment="PATH=/var/www/totalcareit-api/venv/bin"
ExecStart=/var/www/totalcareit-api/venv/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name api.totalcareit.ai;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Updating Frontend to Use API

Update `/website/js/sales-report.js`:

```javascript
// Change this:
// const useAutotaskData = false;

// To this:
const apiClient = new BackendAPIClient();
const salesAdapter = new SalesReportAdapter(apiClient);

async function loadData() {
    const data = await salesAdapter.getSalesData();
    updateDashboard(data);
}
```

## Security Notes

- **Never expose API credentials in frontend code**
- Use environment variables for all sensitive data
- Enable CORS only for trusted origins
- Consider adding authentication for production
- Use HTTPS in production (configure SSL certificate)

## Troubleshooting

### HubSpot API Errors

- Verify access token is valid
- Check token has required scopes
- Ensure HubSpot account is active

### CORS Issues

- Add frontend domain to `ALLOWED_ORIGINS` in `.env`
- Verify frontend is using correct API URL

### Connection Refused

- Ensure API server is running
- Check firewall rules allow port 8000
- Verify `AUTOTASK_BASE_URL` is correct

## Support

For issues, contact TotalCareIT support or check the main repository documentation.
