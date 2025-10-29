# Backend API Deployment Guide

## Overview

The TotalCareIT Partner Portal Backend API has been fully developed and is ready for deployment. This document provides step-by-step instructions for deploying the API to production.

## What's Been Completed

### 1. Backend API Infrastructure ✅

**Location**: `/Users/charles/Projects/TotalCareIT/api/`

#### Core Files Created:
- ✅ `main.py` - FastAPI application with all endpoints
- ✅ `hubspot_service.py` - HubSpot API integration service
- ✅ `autotask_service.py` - Autotask PSA integration service (placeholder)
- ✅ `requirements.txt` - Python dependencies
- ✅ `.env.example` - Environment variable template
- ✅ `README.md` - Complete documentation

#### Key Features:
- **Health Check Endpoints**: `/api/health` with service status
- **HubSpot Endpoints**:
  - `/api/hubspot/crm/summary` - CRM statistics
  - `/api/hubspot/contacts/recent` - Recent contacts
  - `/api/hubspot/deals/pipeline` - Sales pipeline
  - `/api/hubspot/sales-metrics` - **Sales report metrics** (formatted for dashboard)
  - `/api/hubspot/analytics` - Website analytics
  - `/api/hubspot/forms` - Form submission stats
- **CORS Middleware**: Configured for totalcareit.ai
- **Error Handling**: Comprehensive error handling and logging
- **Security**: Credentials stored in environment variables

### 2. Frontend Integration ✅

**Files Updated**:
- ✅ `website/js/backend-api-client.js` - API client with HubSpot support
- ✅ `website/js/sales-report.js` - Updated to use Backend API first
- ✅ `website/sales-report.html` - Includes backend-api-client.js

**Deployment Status**:
- ✅ Deployed to S3: `s3://totalcareit.ai/`
- ✅ CloudFront cache invalidated

#### Integration Logic:
1. **Primary**: Try Backend API (HubSpot data)
2. **Fallback 1**: Try Autotask (if configured)
3. **Fallback 2**: Use sample data

## Deployment Steps

### Step 1: Choose Hosting Platform

**Recommended Options**:
1. **AWS EC2** (t3.micro or t3.small)
2. **DigitalOcean Droplet** ($6-12/month)
3. **Heroku** (easy deployment, higher cost)
4. **AWS Lambda + API Gateway** (serverless, pay-per-use)

**For this guide, we'll use AWS EC2.**

### Step 2: Set Up Server

#### Launch EC2 Instance:
```bash
# Instance Type: t3.small (2 vCPU, 2GB RAM)
# OS: Ubuntu 22.04 LTS
# Security Group: Allow HTTP (80), HTTPS (443), SSH (22)
```

#### Connect to Server:
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

#### Install Dependencies:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.9+
sudo apt install python3 python3-pip python3-venv -y

# Install Nginx
sudo apt install nginx -y

# Install certbot for SSL
sudo apt install certbot python3-certbot-nginx -y
```

### Step 3: Deploy API Code

#### Create Application Directory:
```bash
sudo mkdir -p /var/www/totalcareit-api
sudo chown ubuntu:ubuntu /var/www/totalcareit-api
cd /var/www/totalcareit-api
```

#### Upload API Files:
```bash
# From your local machine:
cd /Users/charles/Projects/TotalCareIT/api
rsync -avz --exclude '.env' --exclude '__pycache__' . ubuntu@your-ec2-ip:/var/www/totalcareit-api/
```

#### Set Up Python Virtual Environment:
```bash
cd /var/www/totalcareit-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

#### Create Production .env File:
```bash
sudo nano /var/www/totalcareit-api/.env
```

#### Add Configuration:
```env
# Server Configuration
PORT=8000
ALLOWED_ORIGINS=https://totalcareit.ai,https://www.totalcareit.ai

# HubSpot API Configuration
HUBSPOT_ACCESS_TOKEN=your_hubspot_access_token_here

# Autotask PSA Configuration (Optional)
AUTOTASK_API_INTEGRATION_CODE=your_integration_code
AUTOTASK_USERNAME=your_username
AUTOTASK_SECRET=your_api_secret
AUTOTASK_BASE_URL=https://webservices.autotask.net/ATServicesRest
```

#### Secure the .env File:
```bash
sudo chmod 600 /var/www/totalcareit-api/.env
```

### Step 5: Get HubSpot Access Token

1. **Log in to HubSpot**: https://app.hubspot.com/
2. **Navigate to**: Settings → Integrations → Private Apps
3. **Create New Private App**:
   - Name: "TotalCareIT Partner Portal API"
   - Description: "Backend API for partner portal sales reporting"
4. **Add Required Scopes**:
   - `crm.objects.contacts.read`
   - `crm.objects.deals.read`
   - `crm.objects.companies.read`
   - `crm.objects.owners.read`
   - `sales-email-read`
5. **Generate Access Token**
6. **Copy Token** to `.env` file

### Step 6: Test API Locally

```bash
cd /var/www/totalcareit-api
source venv/bin/activate
python3 main.py
```

**Test Endpoints**:
```bash
# Health check
curl http://localhost:8000/api/health

# Sales metrics (should return real HubSpot data)
curl http://localhost:8000/api/hubspot/sales-metrics
```

If successful, press `Ctrl+C` to stop the server.

### Step 7: Create Systemd Service

#### Create Service File:
```bash
sudo nano /etc/systemd/system/totalcareit-api.service
```

#### Add Configuration:
```ini
[Unit]
Description=TotalCareIT Partner Portal API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/var/www/totalcareit-api
Environment="PATH=/var/www/totalcareit-api/venv/bin"
EnvironmentFile=/var/www/totalcareit-api/.env
ExecStart=/var/www/totalcareit-api/venv/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Enable and Start Service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable totalcareit-api
sudo systemctl start totalcareit-api
sudo systemctl status totalcareit-api
```

#### Check Logs:
```bash
sudo journalctl -u totalcareit-api -f
```

### Step 8: Configure Nginx Reverse Proxy

#### Create Nginx Configuration:
```bash
sudo nano /etc/nginx/sites-available/api.totalcareit.ai
```

#### Add Configuration:
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

        # CORS headers (if needed)
        add_header 'Access-Control-Allow-Origin' 'https://totalcareit.ai' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Content-Type' always;
    }
}
```

#### Enable Site:
```bash
sudo ln -s /etc/nginx/sites-available/api.totalcareit.ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 9: Configure DNS

**Add A Record**:
- **Type**: A
- **Name**: api.totalcareit.ai
- **Value**: Your EC2 instance public IP
- **TTL**: 300

**Wait for DNS propagation** (5-30 minutes)

### Step 10: Set Up SSL Certificate

```bash
# Get SSL certificate from Let's Encrypt
sudo certbot --nginx -d api.totalcareit.ai

# Follow prompts to complete setup
# Choose: Redirect HTTP to HTTPS
```

**Test Auto-Renewal**:
```bash
sudo certbot renew --dry-run
```

### Step 11: Verify Deployment

#### Test API Endpoints:
```bash
# Health check
curl https://api.totalcareit.ai/api/health

# Sales metrics
curl https://api.totalcareit.ai/api/hubspot/sales-metrics
```

#### Test from Frontend:
1. Open browser to: https://totalcareit.ai/sales-report.html
2. Open Developer Console (F12)
3. Look for console logs:
   - "Backend API client initialized"
   - "Backend API configured with HubSpot"
   - "Using HubSpot data from Backend API"
4. Verify sales metrics are displaying real data (not sample data)

### Step 12: Monitoring and Maintenance

#### View API Logs:
```bash
sudo journalctl -u totalcareit-api -f
```

#### Restart API:
```bash
sudo systemctl restart totalcareit-api
```

#### Update API Code:
```bash
cd /var/www/totalcareit-api
git pull  # or rsync from local
sudo systemctl restart totalcareit-api
```

## Security Checklist

- ✅ `.env` file has secure permissions (600)
- ✅ HubSpot access token stored in environment variables only
- ✅ CORS configured for trusted origins only
- ✅ HTTPS enabled with Let's Encrypt SSL certificate
- ✅ Firewall configured (AWS Security Group)
- ✅ SSH key authentication enabled
- ⚠️ TODO: Add API authentication/authorization if needed
- ⚠️ TODO: Set up CloudWatch monitoring (AWS)
- ⚠️ TODO: Configure log rotation

## Troubleshooting

### API Not Starting

**Check Service Status**:
```bash
sudo systemctl status totalcareit-api
sudo journalctl -u totalcareit-api -n 50
```

**Common Issues**:
- Missing environment variables in `.env`
- Invalid HubSpot access token
- Port 8000 already in use
- Python dependencies not installed

### HubSpot API Errors

**Error: "Unauthorized" or "401"**
- Verify access token is correct
- Check token hasn't expired
- Ensure required scopes are granted

**Error: "Rate Limit Exceeded"**
- HubSpot free tier has API limits
- Add caching to reduce API calls
- Upgrade HubSpot plan if needed

### CORS Issues

**Frontend Can't Access API**:
- Verify `ALLOWED_ORIGINS` in `.env`
- Check nginx CORS headers
- Ensure using HTTPS (not HTTP)

### SSL Certificate Issues

**Certificate Not Renewing**:
```bash
sudo certbot renew --force-renewal
sudo systemctl reload nginx
```

## Alternative: AWS Lambda Deployment

For serverless deployment, see: [AWS Lambda Deployment Guide](./AWS_LAMBDA_DEPLOYMENT.md)

## Cost Estimate

### AWS EC2 Hosting:
- **Instance**: t3.small @ $0.0208/hour = ~$15/month
- **Storage**: 20GB EBS @ $0.10/GB = $2/month
- **Data Transfer**: ~$1/month (low traffic)
- **Total**: ~$18/month

### DigitalOcean Droplet:
- **Basic Droplet**: $6-12/month (all-inclusive)

## Support

For issues or questions:
- API Documentation: [README.md](./api/README.md)
- HubSpot API Docs: https://developers.hubspot.com/docs/api/overview
- FastAPI Docs: https://fastapi.tiangolo.com/

---

**Backend API Status**: ✅ Ready for Production Deployment

**Next Steps**:
1. Deploy to production server
2. Configure HubSpot access token
3. Test endpoints
4. Verify frontend integration
