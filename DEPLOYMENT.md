# TotalCareIT Partner Portal - Production Deployment

## Deployment Date
October 30, 2025

## Production Status: ✅ LIVE AND OPERATIONAL

---

## Production URLs

### Frontend
- **Website**: https://totalcareit.ai
- **Sales Report**: https://totalcareit.ai/sales-report.html

### Backend API
- **Base URL**: https://api.totalcareit.ai
- **Health Check**: https://api.totalcareit.ai/api/health
- **Sales Metrics**: https://api.totalcareit.ai/api/hubspot/sales-metrics

---

## Infrastructure

### EC2 Instance
- **Instance ID**: i-0074616043c23e4f7
- **Public IP**: 98.84.165.255
- **Instance Type**: t3.small
- **OS**: Ubuntu 22.04 LTS
- **Region**: us-east-1
- **VPC**: vpc-02e7cc580a35e6423
- **Security Group**: totalcareit-api-sg (ports 22, 80, 443)

### DNS Configuration
- **Domain**: api.totalcareit.ai
- **Hosted Zone**: Z00878113C25HN2DXVKVS
- **Record Type**: A
- **Value**: 98.84.165.255
- **TTL**: 300 seconds

### SSL Certificate
- **Provider**: Let's Encrypt
- **Certificate**: api.totalcareit.ai
- **Expiry Date**: January 28, 2026 (89 days remaining)
- **Auto-Renewal**: Enabled via certbot.timer
- **Next Renewal Check**: Daily at 01:08 UTC

### Frontend Hosting
- **S3 Bucket**: s3://totalcareit.ai
- **CloudFront Distribution**: EBUCQMMFVHWED
- **CloudFront Domain**: d33hpqeu07nz4u.cloudfront.net
- **SSL**: CloudFront certificate for totalcareit.ai

---

## API Configuration

### Service Details
- **Service Name**: totalcareit-api.service
- **Working Directory**: /var/www/totalcareit-api/api
- **Python Script**: main_simple.py
- **Port**: 8000 (internal)
- **User**: ubuntu
- **Auto-Start**: Enabled
- **Auto-Restart**: Enabled (10s delay)

### Environment Variables
Located in: `/var/www/totalcareit-api/api/.env`

**Note**: The production .env file contains all API credentials. For security reasons, actual credentials are not included in this documentation. Reference the local `.env` file or AWS Secrets Manager for credential values.

```
HUBSPOT_ACCESS_TOKEN=<hubspot_access_token>
HUBSPOT_HUB_ID=<hubspot_hub_id>
AUTOTASK_USERNAME=<autotask_username>
AUTOTASK_SECRET=<autotask_secret>
AUTOTASK_INTEGRATION_CODE=<autotask_integration_code>
DATTO_API_PUBLIC_KEY=<datto_public_key>
DATTO_API_PRIVATE_KEY=<datto_private_key>
CONNECTWISE_CPQ_PUBLIC_KEY=<connectwise_public_key>
CONNECTWISE_CPQ_PRIVATE_KEY=<connectwise_private_key>
ALLOWED_ORIGINS=https://totalcareit.ai,http://localhost:3000
PORT=8000
```

**To retrieve actual credentials:**
```bash
# Copy from local .env file
cat /Users/charles/Projects/TotalCareIT/.env

# Or access on production server
ssh -i ~/.ssh/totalcareit-api-key.pem ubuntu@98.84.165.255
cat /var/www/totalcareit-api/api/.env
```

### CORS Configuration
- **Allowed Origins**:
  - https://totalcareit.ai (production)
  - http://localhost:3000 (development)
- **Allowed Methods**: GET, POST, OPTIONS
- **Allowed Headers**: Content-Type
- **Credentials**: Supported

### Nginx Configuration
- **Config File**: /etc/nginx/sites-available/api.totalcareit.ai
- **Reverse Proxy**: Port 80/443 → localhost:8000
- **SSL**: Managed by Certbot
- **CORS Headers**: Added in nginx configuration

---

## Current API Endpoints

### Health Check
```
GET https://api.totalcareit.ai/api/health
```
Response:
```json
{
  "status": "healthy",
  "checks": {
    "hubspot": "configured"
  }
}
```

### Sales Metrics (HubSpot)
```
GET https://api.totalcareit.ai/api/hubspot/sales-metrics
```
Response:
```json
{
  "success": true,
  "data": {
    "callsMade": 127,
    "conversationsHad": 89,
    "appointmentsScheduled": 34,
    "outboundCalls": 98,
    "inboundCalls": 29,
    "emailConversations": 45,
    "meetingConversations": 44,
    "prospects": 250,
    "contacted": 195,
    "qualified": 78,
    "proposal": 42,
    "closedWon": 18
  },
  "timestamp": "2025-10-30T13:51:49.628224"
}
```

**Note**: Currently returns sample data. Real HubSpot API integration pending.

---

## Frontend Integration

### Backend API Client
- **File**: /js/backend-api-client.js
- **Class**: BackendAPIClient
- **Adapter**: SalesReportAdapter

### API Detection
The frontend automatically detects and uses the production API when:
1. Page loads from https://totalcareit.ai
2. Backend API health check succeeds
3. HubSpot configuration is detected

### Data Source Priority
1. **Backend API (HubSpot)** - Preferred
2. **Autotask API** - Fallback (legacy)
3. **Sample Data** - Final fallback

---

## Management Commands

### SSH Access
```bash
ssh -i ~/.ssh/totalcareit-api-key.pem ubuntu@98.84.165.255
```

### Service Management
```bash
# Check service status
sudo systemctl status totalcareit-api

# Start service
sudo systemctl start totalcareit-api

# Stop service
sudo systemctl stop totalcareit-api

# Restart service
sudo systemctl restart totalcareit-api

# View real-time logs
sudo journalctl -u totalcareit-api -f

# View recent logs
sudo journalctl -u totalcareit-api -n 100
```

### Code Updates
```bash
# SSH to server
ssh -i ~/.ssh/totalcareit-api-key.pem ubuntu@98.84.165.255

# Navigate to project
cd /var/www/totalcareit-api

# Pull latest code
git pull

# Restart service
sudo systemctl restart totalcareit-api

# Verify service started
sudo systemctl status totalcareit-api
```

### SSL Certificate Management
```bash
# Check certificate status
sudo certbot certificates

# Test renewal (dry run)
sudo certbot renew --dry-run

# Force renewal
sudo certbot renew

# Reload nginx after renewal
sudo systemctl reload nginx
```

### Website Deployment
```bash
# From local machine
cd /Users/charles/Projects/TotalCareIT/website

# Sync to S3
aws s3 sync . s3://totalcareit.ai/ --exclude ".DS_Store" --exclude "*.md" --profile default

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id EBUCQMMFVHWED --paths "/*" --profile default

# Check invalidation status
aws cloudfront list-invalidations --distribution-id EBUCQMMFVHWED --profile default
```

---

## Testing

### API Endpoints
```bash
# Health check
curl https://api.totalcareit.ai/api/health

# Sales metrics
curl https://api.totalcareit.ai/api/hubspot/sales-metrics

# Test CORS
curl -I -X OPTIONS https://api.totalcareit.ai/api/hubspot/sales-metrics \
  -H "Origin: https://totalcareit.ai" \
  -H "Access-Control-Request-Method: GET"
```

### Frontend
1. Open https://totalcareit.ai/sales-report.html
2. Open browser developer console (F12)
3. Look for these log messages:
   - ✅ Backend API client initialized
   - ✅ Backend API configured with HubSpot
   - ✅ Using HubSpot data from Backend API

---

## Known Issues & Limitations

### Current Limitations
1. **Sample Data**: API currently returns hardcoded sample data
2. **Limited Endpoints**: Only health check and sales-metrics endpoints active
3. **No Real HubSpot Integration**: HubSpot API calls not yet implemented

### Pending Work
1. **Implement Real HubSpot API Integration**
   - Update main_simple.py to call actual HubSpot API
   - Use configured access token
   - Parse real HubSpot data

2. **Fix Full API Implementation**
   - Resolve FastAPI dependency injection issues in main.py
   - Fix service files (autotask_service.py, hubspot_service.py, etc.)
   - Enable all planned endpoints

3. **Add Additional Endpoints**
   - Autotask PSA integration
   - Datto Commerce integration
   - Datto RMM integration
   - ConnectWise Manage integration
   - Microsoft 365 integration

---

## Deployment Scripts

### Local Scripts

#### Deploy API Infrastructure
```bash
/Users/charles/Projects/TotalCareIT/scripts/deploy-api.sh
```
Creates EC2 instance, security groups, and DNS records.

#### Deploy API Code
```bash
/Users/charles/Projects/TotalCareIT/scripts/deploy-api-code-to-server.sh
```
Deploys code to server, sets up systemd service and nginx.

### Server-Side Files
- **Systemd Service**: /etc/systemd/system/totalcareit-api.service
- **Nginx Config**: /etc/nginx/sites-available/api.totalcareit.ai
- **API Code**: /var/www/totalcareit-api/api/
- **Environment**: /var/www/totalcareit-api/api/.env

---

## Monitoring

### Health Check
```bash
# Check if API is responding
curl -f https://api.totalcareit.ai/api/health || echo "API is down!"
```

### Service Status
```bash
# On server
sudo systemctl is-active totalcareit-api
sudo systemctl is-enabled totalcareit-api
```

### Logs
```bash
# Real-time logs
sudo journalctl -u totalcareit-api -f

# Recent errors
sudo journalctl -u totalcareit-api -p err -n 50

# All logs from today
sudo journalctl -u totalcareit-api --since today
```

### Certificate Expiry
```bash
# Check certificate expiration
sudo certbot certificates | grep "Expiry Date"

# Check auto-renewal timer
sudo systemctl status certbot.timer
```

---

## Security

### SSH Key
- **Location**: ~/.ssh/totalcareit-api-key.pem
- **Permissions**: 400 (read-only for owner)
- **Created**: October 30, 2025

### API Credentials
- **Location**: /var/www/totalcareit-api/api/.env
- **Permissions**: 600 (readable by ubuntu user only)
- **Storage**: Also backed up in AWS Secrets Manager (planned)

### Security Group Rules
- **Port 22**: SSH (restricted to your IP recommended)
- **Port 80**: HTTP (redirect to HTTPS)
- **Port 443**: HTTPS (public)

---

## Troubleshooting

### API Not Responding
```bash
# 1. Check if service is running
sudo systemctl status totalcareit-api

# 2. Check recent logs
sudo journalctl -u totalcareit-api -n 50

# 3. Check if port is listening
sudo netstat -tlnp | grep 8000

# 4. Test locally on server
curl http://localhost:8000/api/health

# 5. Restart service
sudo systemctl restart totalcareit-api
```

### SSL Certificate Issues
```bash
# 1. Check certificate status
sudo certbot certificates

# 2. Test renewal
sudo certbot renew --dry-run

# 3. Check nginx config
sudo nginx -t

# 4. Reload nginx
sudo systemctl reload nginx
```

### Website Not Loading
```bash
# 1. Check CloudFront distribution
aws cloudfront get-distribution --id EBUCQMMFVHWED --profile default

# 2. Check S3 bucket
aws s3 ls s3://totalcareit.ai/ --profile default

# 3. Create cache invalidation
aws cloudfront create-invalidation --distribution-id EBUCQMMFVHWED --paths "/*" --profile default
```

---

## Backup & Recovery

### EC2 Instance Backup
```bash
# Create AMI from running instance
aws ec2 create-image --instance-id i-0074616043c23e4f7 --name "totalcareit-api-backup-$(date +%Y%m%d)" --profile default
```

### Code Backup
- **Primary**: GitHub repository
- **Server**: /var/www/totalcareit-api (git repository)

### Configuration Backup
```bash
# Backup .env file
scp -i ~/.ssh/totalcareit-api-key.pem ubuntu@98.84.165.255:/var/www/totalcareit-api/api/.env /tmp/totalcareit-api-production.env
```

---

## Contact & Support

For issues or questions:
- **Email**: ai@totalcareit.com
- **GitHub**: https://github.com/totalcareit (if applicable)
- **Documentation**: This file

---

## Version History

### v2.0.0 - October 30, 2025
- ✅ Production deployment to AWS EC2
- ✅ SSL certificate installed (Let's Encrypt)
- ✅ API accessible at https://api.totalcareit.ai
- ✅ Frontend integrated with backend API
- ✅ Health check and sales metrics endpoints live
- ⚠️ Currently using sample data (real HubSpot integration pending)

---

*Last Updated: October 30, 2025*
