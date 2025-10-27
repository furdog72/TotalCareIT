# TotalCare IT - Quick Start Guide

## Your API Keys Are Now Securely Stored! ✅

All 24 API keys have been uploaded to **AWS Secrets Manager** and can be accessed from any machine.

### Quick Commands

```bash
# Download secrets to any machine
python scripts/setup_secrets_manager.py download

# View secrets (masked for security)
python scripts/setup_secrets_manager.py view

# Upload new/updated secrets
python scripts/setup_secrets_manager.py upload
```

## Setting Up on a New Machine

### 1. Clone Repository
```bash
git clone https://github.com/furdog72/TotalCareIT.git
cd TotalCareIT
```

### 2. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Download Secrets from AWS
```bash
python scripts/setup_secrets_manager.py download
```

### 4. Test Integration
```bash
# Test HubSpot
python integrations/hubspot/tests/test_hubspot_auth.py

# Test Autotask
python integrations/autotask/tests/test_autotask_auth.py

# Test Datto
python integrations/datto/tests/test_datto.py
```

## Project Structure

```
TotalCareIT/
├── quickbooks/          # QuickBooks Online integration
├── integrations/        # API integrations
│   ├── hubspot/        # HubSpot CRM
│   ├── autotask/       # Autotask PSA
│   ├── datto/          # Datto backup/RMM
│   ├── linkedin/       # LinkedIn analytics
│   └── aws/            # AWS billing
├── scorecard/          # Weekly scorecard system
├── website/            # Frontend dashboard
├── api/                # Backend API
├── scripts/            # Utility scripts
└── docs/               # Documentation
```

## Common Tasks

### Deploy Updated Scorecard
```bash
source .venv/bin/activate
python scorecard/scripts/extract_and_deploy_scorecard.py
```

### Update Website
```bash
aws s3 sync website/ s3://totalcareit.ai/ --delete
aws cloudfront create-invalidation --distribution-id EBUCQMMFVHWED --paths "/*"
```

### Collect Weekly Data
```bash
source .venv/bin/activate
cd scorecard/scripts
python collect_scorecard_week_oct24.py
```

## Security Notes

### ✅ Your Secrets Are Stored In:
- **AWS Secrets Manager** (encrypted, centralized)
- **Secret Name:** `totalcareit/api-keys`
- **Region:** `us-east-1`
- **Account:** `848549168478`

### ⚠️ Important:
- **Never commit `.env` to git** (already in `.gitignore`)
- Delete local `.env` file after uploading to AWS
- Use `python scripts/setup_secrets_manager.py download` to retrieve on new machines
- Cost: ~$0.40/month for AWS Secrets Manager

## Documentation

- **Setup Guide:** [README.md](README.md)
- **Secure Credentials:** [docs/SECURE-CREDENTIALS-GUIDE.md](docs/SECURE-CREDENTIALS-GUIDE.md)
- **API Verification:** [docs/API-VERIFICATION-GUIDE.md](docs/API-VERIFICATION-GUIDE.md)
- **Reorganization Plan:** [docs/REORGANIZATION_PLAN.md](docs/REORGANIZATION_PLAN.md)

## Support

- **GitHub:** https://github.com/furdog72/TotalCareIT
- **Website:** https://totalcareit.ai
- **CloudFront:** Distribution ID `EBUCQMMFVHWED`

## What's Different Now?

### Before:
- ❌ API keys stored on local computer in `.env` file
- ❌ Had to manually copy `.env` to each machine
- ❌ No central management
- ❌ Risk of losing credentials

### After:
- ✅ API keys encrypted in AWS Secrets Manager
- ✅ Download from anywhere with AWS credentials
- ✅ Central management and rotation
- ✅ Audit logging via CloudTrail
- ✅ No local storage needed

---

**Last Updated:** October 27, 2025
**Repository:** https://github.com/furdog72/TotalCareIT
**Secrets ARN:** `arn:aws:secretsmanager:us-east-1:848549168478:secret:totalcareit/api-keys-cDFDA8`
