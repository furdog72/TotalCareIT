# Backend API Setup Guide

## Overview

The TotalCare AI Partner Portal uses a **secure backend API** to access Autotask and HubSpot data. This prevents exposing API credentials in the browser.

**Architecture:**
```
Browser (Partner Portal)
    ↓ HTTPS
Backend API (FastAPI on port 8000)
    ↓ Secure API calls
    ├─→ Autotask API (ROC Board Tickets)
    └─→ HubSpot API (Website Stats)
```

## Why We Need a Backend

**Security Issues with Browser-Only Approach:**
- ❌ API credentials exposed in browser JavaScript (visible to anyone)
- ❌ Users can inspect network traffic and steal credentials
- ❌ No rate limiting or caching
- ❌ No audit logging
- ❌ Cannot filter/sanitize data before sending to frontend

**Benefits of Backend API:**
- ✅ Credentials stored securely on server (environment variables)
- ✅ Users never see API keys or secrets
- ✅ Server-side rate limiting and caching
- ✅ Audit logging of all API requests
- ✅ Can filter sensitive data before sending to browser
- ✅ Single source of truth for API configuration

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Access to Autotask API (read-only user)
- Access to HubSpot API (optional)

## Step 1: Install Dependencies

```bash
cd /Users/charles/Projects/qbo-ai

# Install Python dependencies
pip install -r requirements.txt
```

Required packages (already in requirements.txt):
- `fastapi>=0.104.0` - Web framework
- `uvicorn[standard]>=0.24.0` - ASGI server
- `requests==2.31.0` - HTTP client
- `python-dotenv==1.0.0` - Environment variables
- `pydantic>=2.5.3` - Data validation

## Step 2: Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and configure your credentials:

```bash
# ===== AUTOTASK API CONFIGURATION =====
AUTOTASK_USERNAME=api-readonly@totalcareit.com
AUTOTASK_SECRET=your_actual_secret_here
AUTOTASK_INTEGRATION_CODE=your_integration_code_here

# ROC Board Queue ID (find in Autotask Admin)
AUTOTASK_ROC_BOARD_ID=123456

# ===== HUBSPOT API CONFIGURATION =====
HUBSPOT_API_KEY=your_hubspot_key_here
HUBSPOT_HUB_ID=8752461

# ===== API SERVER CONFIGURATION =====
PORT=8000
ALLOWED_ORIGINS=https://totalcareit.ai,http://localhost:3000
ENVIRONMENT=development
```

### Finding Your ROC Board Queue ID:

1. Log in to Autotask as admin
2. Navigate to: **Admin > Service Desk > Queues**
3. Find and click on "ROC" or "Reactive Services" board
4. Note the **Queue ID** from the URL or board details
5. Add to `.env` file as `AUTOTASK_ROC_BOARD_ID`

## Step 3: Run the Backend API Locally

### Option A: Development Mode (with auto-reload)

```bash
# From project root
python -m uvicorn api.main:app --reload --port 8000
```

### Option B: Production Mode

```bash
python -m api.main
```

### Verify It's Running:

Open in browser or use curl:
```bash
# Health check
curl http://localhost:8000/

# Detailed health
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "checks": {
    "autotask": "configured",
    "hubspot": "configured"
  }
}
```

## Step 4: Test Autotask Integration

### Get ROC Board Tickets:

```bash
# This month's tickets
curl http://localhost:8000/api/autotask/tickets

# Specific date range
curl "http://localhost:8000/api/autotask/tickets?start_date=2025-10-01T00:00:00&end_date=2025-10-31T23:59:59"
```

### Get Activity Summary:

```bash
curl http://localhost:8000/api/autotask/activity
```

### Get Daily Report:

```bash
# Today's report
curl http://localhost:8000/api/autotask/report/daily

# Specific date
curl "http://localhost:8000/api/autotask/report/daily?date=2025-10-23"
```

### Get Monthly Report:

```bash
# Current month
curl http://localhost:8000/api/autotask/report/monthly

# Specific month
curl "http://localhost:8000/api/autotask/report/monthly?year=2025&month=10"
```

## Step 5: Deploy to Production

### Option A: AWS EC2

1. **Launch EC2 Instance:**
   - Amazon Linux 2 or Ubuntu
   - t3.small or larger
   - Security group: Allow port 8000 (or 80/443 with nginx)

2. **Install Dependencies:**
```bash
# Update system
sudo yum update -y  # Amazon Linux
# or
sudo apt update && sudo apt upgrade -y  # Ubuntu

# Install Python 3.9+
sudo yum install python3 python3-pip -y
# or
sudo apt install python3 python3-pip -y

# Clone your project
git clone <your-repo>
cd qbo-ai

# Install Python packages
pip3 install -r requirements.txt
```

3. **Configure Environment:**
```bash
# Copy and edit .env
cp .env.example .env
nano .env  # Add your credentials
```

4. **Run with systemd (recommended):**

Create `/etc/systemd/system/totalcare-api.service`:
```ini
[Unit]
Description=TotalCare AI Partner Portal API
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/qbo-ai
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable totalcare-api
sudo systemctl start totalcare-api
sudo systemctl status totalcare-api
```

5. **Setup Nginx Reverse Proxy (optional but recommended):**

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

Then setup SSL with Let's Encrypt:
```bash
sudo certbot --nginx -d api.totalcareit.ai
```

### Option B: AWS Lambda + API Gateway

1. **Package for Lambda:**
```bash
pip install -t lambda_package -r requirements.txt
cp -r api lambda_package/
cd lambda_package
zip -r ../totalcare-api-lambda.zip .
```

2. **Create Lambda Function:**
   - Runtime: Python 3.9+
   - Handler: `api.main.handler`
   - Environment variables: Add all from `.env`
   - Upload `totalcare-api-lambda.zip`

3. **Create API Gateway:**
   - Type: HTTP API
   - Integration: Lambda function
   - Custom domain: api.totalcareit.ai

### Option C: Docker (Recommended)

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api ./api
COPY .env .env

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t totalcare-api .
docker run -p 8000:8000 --env-file .env totalcare-api
```

## Step 6: Update Frontend Configuration

The frontend will automatically detect the environment and connect to the appropriate API URL:

- **Production:** `https://api.totalcareit.ai`
- **Development:** `http://localhost:8000`

No code changes needed! The `backend-api-client.js` handles this automatically.

## Step 7: Update DNS

Add DNS record for API subdomain:

**Route53 Configuration:**
```
Type: A Record
Name: api.totalcareit.ai
Value: <EC2-IP-ADDRESS>
TTL: 300
```

Or use ALB/CloudFront:
```
Type: CNAME
Name: api.totalcareit.ai
Value: <load-balancer-dns>
TTL: 300
```

## Step 8: Update CORS Configuration

Edit `api/main.py` to update allowed origins:

```python
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'https://totalcareit.ai,http://localhost:3000').split(',')
```

In `.env`:
```bash
ALLOWED_ORIGINS=https://totalcareit.ai,https://www.totalcareit.ai
```

## API Endpoints Reference

### Health & Status
- `GET /` - Health check
- `GET /api/health` - Detailed health with service status

### Autotask (ROC Board Tickets)
- `GET /api/autotask/tickets` - Get ROC board tickets
  - Query params: `start_date`, `end_date` (ISO format)
- `GET /api/autotask/activity` - Get activity summary
  - Query params: `start_date`, `end_date`
- `GET /api/autotask/report/daily` - Daily report
  - Query param: `date` (ISO format)
- `GET /api/autotask/report/monthly` - Monthly report
  - Query params: `year`, `month`

### HubSpot
- `GET /api/hubspot/crm/summary` - CRM summary (contacts, deals, companies counts)
- `GET /api/hubspot/contacts/recent` - Recent contacts
  - Query param: `limit` (default: 10)
- `GET /api/hubspot/deals/pipeline` - Sales pipeline grouped by stage
- `GET /api/hubspot/analytics` - Website analytics (page views, sessions)
- `GET /api/hubspot/forms` - Form submission statistics

## Troubleshooting

### Backend Won't Start

**Error: "Autotask credentials not configured"**
- Check `.env` file exists
- Verify all required variables are set
- Ensure no quotes around values in `.env`

**Error: "Port 8000 already in use"**
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9

# Or use different port
PORT=8001 python -m api.main
```

### API Returns Errors

**401 Unauthorized from Autotask:**
- Verify AUTOTASK_USERNAME is correct (email format)
- Check AUTOTASK_SECRET is current password
- Confirm AUTOTASK_INTEGRATION_CODE is valid

**No Tickets Returned:**
- Verify AUTOTASK_ROC_BOARD_ID is correct
- Check date range (tickets may not exist for that period)
- Confirm API user has read access to tickets

### Frontend Can't Connect

**CORS errors in browser:**
- Add frontend domain to ALLOWED_ORIGINS
- Restart backend after changing .env

**Connection refused:**
- Verify backend is running: `curl http://localhost:8000/`
- Check firewall rules (EC2 security group)
- Confirm correct URL in frontend

## Security Best Practices

1. **Never commit `.env` file** - Add to `.gitignore`
2. **Rotate credentials regularly** - Every 90 days
3. **Use HTTPS in production** - Setup SSL certificate
4. **Implement rate limiting** - Add middleware if needed
5. **Monitor API logs** - Watch for unusual activity
6. **Use read-only Autotask user** - Minimize permissions
7. **Keep dependencies updated** - `pip list --outdated`

## Monitoring

### Logs

View logs in real-time:
```bash
# Systemd
sudo journalctl -u totalcare-api -f

# Docker
docker logs -f <container-id>

# Direct
tail -f /var/log/totalcare-api.log
```

### Metrics

Add monitoring with:
- AWS CloudWatch (for EC2/Lambda)
- Prometheus + Grafana
- Datadog
- New Relic

## Support

For issues:
- Backend API: Check logs first
- Autotask integration: Review AUTOTASK-SETUP.md
- Frontend: Check browser console for errors

## Next Steps

1. Deploy backend to production server
2. Setup `api.totalcareit.ai` DNS record
3. Configure SSL certificate
4. Test from production frontend
5. Monitor logs for errors
6. Setup automated backups (if storing any data)
