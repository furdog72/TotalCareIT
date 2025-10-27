# TotalCare IT Partner Portal

Comprehensive business intelligence platform integrating QuickBooks, HubSpot, Autotask, Datto, LinkedIn, and AWS for automated reporting and analytics.

## Project Structure

```
TotalCareIT/
├── quickbooks/          # QuickBooks Online integration
│   ├── qbo_ai/         # Core QBO package
│   ├── scripts/        # QBO utility scripts
│   ├── examples/       # Usage examples
│   └── tests/          # QBO tests
├── integrations/        # Third-party API integrations
│   ├── hubspot/        # CRM and sales activity tracking
│   ├── autotask/       # PSA and ticket management
│   ├── datto/          # Backup and RMM monitoring
│   ├── linkedin/       # LinkedIn performance tracking
│   └── aws/            # AWS billing and cost management
├── scorecard/          # Weekly scorecard system
│   ├── scripts/        # Data collection and deployment
│   └── data/           # Scorecard data storage
├── website/            # Frontend dashboard
│   ├── css/           # Stylesheets
│   ├── js/            # JavaScript modules
│   └── data/          # JSON data files
├── api/                # Backend API
│   ├── routes/        # API endpoints
│   ├── models/        # Data models
│   └── services/      # Business logic
├── tests/              # Integration tests
├── scripts/            # Utility scripts
├── docs/               # Documentation
└── deployment/         # Deployment configurations
```

## Quick Start

### 1. Environment Setup

```bash
cd /Users/charles/Projects/TotalCareIT

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and configure your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# QuickBooks Online
QBO_CLIENT_ID=your_client_id
QBO_CLIENT_SECRET=your_client_secret
QBO_COMPANY_ID=your_company_id

# HubSpot
HUBSPOT_API_KEY=pat-na1-xxxxx
HUBSPOT_HUB_ID=8752461

# Autotask
AUTOTASK_USERNAME=your_username
AUTOTASK_SECRET=your_secret
AUTOTASK_INTEGRATION_CODE=your_code
AUTOTASK_ZONE_URL=https://webservices3.autotask.net

# Datto
DATTO_API_PUBLIC_KEY=your_public_key
DATTO_API_PRIVATE_KEY=your_private_key
DATTO_PORTAL_URL=https://portal.dattobackup.com
DATTO_RMM_URL=https://vidal-rmm.centrastage.net

# AWS
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# CloudFront
CLOUDFRONT_DISTRIBUTION_ID=EBUCQMMFVHWED
```

### 3. Run Tests

```bash
# Test HubSpot authentication
python quickbooks/tests/test_hubspot_auth.py

# Test Autotask authentication
python quickbooks/tests/test_autotask_auth.py

# Test Datto authentication
python quickbooks/tests/test_datto.py
```

## Components

### QuickBooks Integration

Located in `quickbooks/` - OAuth-based integration with QuickBooks Online for financial data queries.

**Key Files:**
- `qbo_ai/client.py` - Main QBOClient class
- `qbo_ai/config.py` - Configuration management
- `lambda_handler.py` - AWS Lambda deployment

**Usage:**
```python
from quickbooks.qbo_ai import QBOClient

client = QBOClient()
auth_url = client.get_authorization_url()
# ... OAuth flow ...
client.connect(access_token, refresh_token)
results = client.query("SELECT * FROM Customer MAXRESULTS 10")
```

### API Integrations

Each integration is self-contained in `integrations/` with its own service, tests, and README.

#### HubSpot (`integrations/hubspot/`)
- CRM contact management
- Sales activity tracking (dials, conversations, FTAs)
- Deal pipeline analytics

#### Autotask (`integrations/autotask/`)
- PSA ticket tracking
- ROC Board metrics
- Same-day close rate calculations

#### Datto (`integrations/datto/`)
- Backup device monitoring
- RMM agent status
- System health metrics

#### LinkedIn (`integrations/linkedin/`)
- Performance tracking (impressions, profile views)
- Follower growth analytics
- Competitor comparison

#### AWS (`integrations/aws/`)
- Cost Explorer integration
- Billing reports
- Usage metrics

### Scorecard System

Located in `scorecard/` - Automated weekly scorecard generation and deployment.

**Main Script:**
```bash
cd scorecard/scripts
python extract_and_deploy_scorecard.py
```

**What it does:**
1. Collects live data from all API integrations
2. Generates HTML with retractable quarters
3. Deploys to S3 bucket: `totalcareit.ai`
4. Invalidates CloudFront cache

**Data Storage:**
- Historical data: `website/data/scorecard-2025.json`
- Deployed URL: https://totalcareit.ai/scorecard.html

### Website Dashboard

Located in `website/` - Static frontend hosted on S3 + CloudFront.

**Pages:**
- `dashboard.html` - Main dashboard
- `scorecard.html` - Weekly scorecard
- `linkedin-performance.html` - LinkedIn analytics
- `aws-billing.html` - AWS cost tracking

**Deployment:**
```bash
aws s3 sync website/ s3://totalcareit.ai/ --delete
aws cloudfront create-invalidation --distribution-id EBUCQMMFVHWED --paths "/*"
```

## Common Tasks

### Collect Weekly Scorecard Data

```bash
source .venv/bin/activate
cd scorecard/scripts
python collect_scorecard_week_oct24.py
```

### Deploy Updated Scorecard

```bash
source .venv/bin/activate
python scorecard/scripts/extract_and_deploy_scorecard.py
```

### Calculate Autotask Metrics

```bash
source .venv/bin/activate
python integrations/autotask/calculate_autotask_metrics.py
```

### Test API Authentication

```bash
# Test all APIs
python quickbooks/tests/test_hubspot_auth.py
python quickbooks/tests/test_autotask_auth.py
python quickbooks/tests/test_datto.py
```

## Development Guidelines

### Adding New Integration

1. Create folder: `integrations/your_api/`
2. Add service file: `integrations/your_api/service.py`
3. Create tests: `integrations/your_api/tests/`
4. Add README: `integrations/your_api/README.md`
5. Create `__init__.py` for package imports

### Code Style

- Use type hints for function parameters and returns
- Follow PEP 8 style guidelines
- Add docstrings for all classes and functions
- Use Pydantic for configuration models
- Load environment variables with `python-dotenv`

### Configuration Management

- All secrets in `.env` file (never commit)
- Use Pydantic models for config validation
- Load `.env` BEFORE importing any modules
- Provide `.env.example` for documentation

### Testing

- Test authentication separately from data collection
- Use `python-dotenv` to load test credentials
- Mock external API calls when appropriate
- Verify error handling for expired tokens

## Deployment

### AWS S3 + CloudFront

The website is deployed to S3 and served via CloudFront:

- **Bucket:** `totalcareit.ai`
- **CloudFront Distribution:** `EBUCQMMFVHWED`
- **URL:** https://totalcareit.ai

**Deploy Command:**
```bash
aws s3 sync website/ s3://totalcareit.ai/ --delete
aws cloudfront create-invalidation --distribution-id EBUCQMMFVHWED --paths "/*"
```

### AWS Lambda (QuickBooks)

QuickBooks integration can run as Lambda function:

```bash
cd quickbooks
zip -r function.zip lambda_handler.py qbo_ai/
aws lambda update-function-code --function-name qbo-integration --zip-file fileb://function.zip
```

## Troubleshooting

### API Authentication Errors

**Issue:** 401 Unauthorized from HubSpot/Autotask
**Solution:** Ensure `load_dotenv()` is called BEFORE importing service modules

```python
from dotenv import load_dotenv
load_dotenv()  # MUST be before other imports

from integrations.hubspot.service import HubSpotClient
```

### CloudFront Cache Issues

**Issue:** Updated website not showing
**Solution:** Create cache invalidation

```bash
aws cloudfront create-invalidation \
  --distribution-id EBUCQMMFVHWED \
  --paths "/*"
```

### Timezone Errors

**Issue:** `can't compare offset-naive and offset-aware datetimes`
**Solution:** Always use timezone-aware datetime objects

```python
from datetime import datetime, timezone

# Correct
dt = datetime(2025, 10, 24, tzinfo=timezone.utc)

# Incorrect
dt = datetime(2025, 10, 24)  # naive
```

## Documentation

Additional documentation available in `docs/`:

- `REORGANIZATION_PLAN.md` - Project structure decisions
- `API-VERIFICATION-GUIDE.md` - API setup instructions
- Integration-specific READMEs in each `integrations/` folder

## Support

For issues or questions:
1. Check the API-VERIFICATION-GUIDE.md for authentication issues
2. Review integration-specific README files
3. Verify `.env` configuration
4. Check CloudWatch logs for Lambda functions

## License

Proprietary - TotalCare IT Internal Use Only
