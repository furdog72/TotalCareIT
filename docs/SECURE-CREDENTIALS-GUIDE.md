# Secure Credentials Management Guide

This guide shows you how to securely store API keys in AWS Secrets Manager so they can be accessed from anywhere without storing them on your computer.

## Why AWS Secrets Manager?

✅ **Encrypted storage** - Keys encrypted at rest and in transit
✅ **Access from anywhere** - Use credentials on any machine with AWS access
✅ **Automatic rotation** - Support for rotating credentials
✅ **Audit logging** - Track who accessed which secrets when
✅ **No local storage** - Never store sensitive keys on your computer
✅ **Free tier** - First 30 days free, then $0.40/secret/month

## Quick Start

### Step 1: Upload Your Current .env File to AWS

If you have an existing `.env` file with your API keys:

```bash
cd /Users/charles/Projects/TotalCareIT

# Upload all secrets from .env to AWS Secrets Manager
python scripts/setup_secrets_manager.py upload

# After successful upload, delete your local .env file for security
rm .env
```

### Step 2: Download Secrets on Any Machine

On any machine with AWS credentials configured:

```bash
cd /Users/charles/Projects/TotalCareIT

# Download secrets from AWS and create .env file
python scripts/setup_secrets_manager.py download

# View secrets (masked for security)
python scripts/setup_secrets_manager.py view
```

### Step 3: Use Automatic Loading in Your Code

Update your scripts to use the secrets loader:

```python
# Instead of this:
from dotenv import load_dotenv
load_dotenv()

# Use this:
from scripts.secrets_loader import load_secrets
load_secrets()  # Automatically uses AWS or local .env

# Then use environment variables as normal
import os
api_key = os.getenv('HUBSPOT_API_KEY')
```

## Detailed Usage

### Upload Secrets to AWS

```bash
# Upload from .env file
python scripts/setup_secrets_manager.py upload

# Upload from custom file
python scripts/setup_secrets_manager.py upload --env-file /path/to/.env

# Use custom secret name
python scripts/setup_secrets_manager.py upload --secret-name my-company/api-keys
```

### Download Secrets from AWS

```bash
# Download to .env
python scripts/setup_secrets_manager.py download

# Download to custom file
python scripts/setup_secrets_manager.py download --env-file /path/to/.env

# Download specific secret
python scripts/setup_secrets_manager.py download --secret-name my-company/api-keys
```

### View Secrets (Masked)

```bash
# View all secrets (values are masked for security)
python scripts/setup_secrets_manager.py view

# Example output:
# 📋 Secret contents:
#    AUTOTASK_INTEGRATION_CODE: ABC1****
#    AUTOTASK_SECRET: sec_****
#    AUTOTASK_USERNAME: api@****
#    HUBSPOT_API_KEY: pat-****
```

## Automatic Loading

The `secrets_loader` module automatically detects where to load secrets from:

### On AWS (EC2, Lambda, etc.)
Automatically loads from AWS Secrets Manager using IAM role

### On Developer Machine with AWS CLI
Automatically loads from AWS Secrets Manager using `~/.aws/credentials`

### On Machine Without AWS Credentials
Falls back to local `.env` file

### Example Usage in Scripts

```python
from scripts.secrets_loader import load_secrets

# Load secrets (auto-detects AWS or local)
load_secrets()

# Now use environment variables
import os
hubspot_key = os.getenv('HUBSPOT_API_KEY')
qbo_client_id = os.getenv('QBO_CLIENT_ID')
```

## Security Best Practices

### ✅ DO:
- Store all API keys in AWS Secrets Manager
- Delete local `.env` files after uploading to AWS
- Use IAM roles for EC2/Lambda instead of access keys
- Rotate credentials regularly
- Use least-privilege IAM policies
- Enable AWS CloudTrail for audit logs

### ❌ DON'T:
- Commit `.env` files to git (already in `.gitignore`)
- Share AWS access keys via email/Slack
- Store credentials in code comments or documentation
- Use the same credentials across environments
- Give everyone access to production secrets

## AWS IAM Permissions Required

To use Secrets Manager, your AWS user/role needs these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue",
                "secretsmanager:CreateSecret",
                "secretsmanager:UpdateSecret",
                "secretsmanager:DescribeSecret"
            ],
            "Resource": "arn:aws:secretsmanager:us-east-1:*:secret:totalcareit/*"
        }
    ]
}
```

## Setting Up New Machines

### 1. Clone Repository
```bash
git clone https://github.com/furdog72/TotalCareIT.git
cd TotalCareIT
```

### 2. Set Up Python Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure AWS Credentials
```bash
# Option A: Use AWS CLI
aws configure

# Option B: Use environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

### 4. Download Secrets
```bash
# Download from AWS Secrets Manager
python scripts/setup_secrets_manager.py download
```

### 5. Test
```bash
# Test HubSpot
python integrations/hubspot/tests/test_hubspot_auth.py

# Test Autotask
python integrations/autotask/tests/test_autotask_auth.py
```

## Troubleshooting

### Error: "Unable to locate credentials"

**Problem:** AWS credentials not configured

**Solution:**
```bash
# Configure AWS CLI
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

### Error: "Secret not found"

**Problem:** Secret doesn't exist in AWS Secrets Manager

**Solution:**
```bash
# Upload secrets first
python scripts/setup_secrets_manager.py upload
```

### Error: "Access Denied"

**Problem:** Your AWS user doesn't have Secrets Manager permissions

**Solution:** Ask AWS admin to add the IAM policy shown above

### Secrets Work Locally But Not on AWS

**Problem:** EC2/Lambda role doesn't have Secrets Manager permissions

**Solution:** Add IAM policy to the EC2 instance role or Lambda execution role

## Cost Estimate

AWS Secrets Manager pricing (as of 2025):
- **First 30 days:** FREE
- **After 30 days:** $0.40 per secret per month
- **API calls:** $0.05 per 10,000 API calls

**Example for TotalCare IT:**
- 1 secret (totalcareit/api-keys)
- ~100 API calls/month
- **Total:** ~$0.40/month

## Migration Plan

### Phase 1: Upload to AWS (Today)
1. Upload current `.env` to AWS Secrets Manager
2. Test downloading on same machine
3. Keep local `.env` as backup for now

### Phase 2: Update Code (This Week)
1. Update all scripts to use `secrets_loader`
2. Test all integrations still work
3. Deploy updated code

### Phase 3: Remove Local Storage (After Testing)
1. Delete local `.env` files
2. Update onboarding docs
3. Train team on new process

## Alternative Options

If you prefer not to use AWS Secrets Manager:

### Option 2: 1Password CLI
- Good for team sharing
- Requires 1Password subscription
- Costs $7.99/user/month

### Option 3: HashiCorp Vault
- Self-hosted option
- More complex setup
- Good for multi-cloud

### Option 4: Azure Key Vault
- If you prefer Azure
- Similar pricing to AWS

**Recommendation:** Use AWS Secrets Manager since you're already using AWS for hosting.

## Support

For issues or questions:
1. Check [AWS Secrets Manager documentation](https://docs.aws.amazon.com/secretsmanager/)
2. Review this guide's troubleshooting section
3. Check AWS CloudTrail logs for access issues
4. Contact AWS Support if needed

## Quick Reference

```bash
# Upload secrets
python scripts/setup_secrets_manager.py upload

# Download secrets
python scripts/setup_secrets_manager.py download

# View secrets (masked)
python scripts/setup_secrets_manager.py view

# Use in code
from scripts.secrets_loader import load_secrets
load_secrets()
```
