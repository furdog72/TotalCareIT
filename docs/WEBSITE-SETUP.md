# TotalCare AI Website - Complete Setup Guide

This guide walks you through deploying the TotalCare AI website to AWS with Microsoft 365 authentication.

## Prerequisites

- AWS Account with administrative access
- AWS CLI installed and configured
- Microsoft 365 (Azure AD) admin access
- Domain: totalcareit.ai (already registered)

## Part 1: Azure AD App Registration (Microsoft 365 Login)

### Step 1: Create Azure AD Application

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **New registration**
4. Fill in the details:
   - **Name**: `TotalCare AI Portal`
   - **Supported account types**: `Accounts in this organizational directory only (Single tenant)`
   - **Redirect URI**:
     - Platform: `Single-page application (SPA)`
     - URI: `https://totalcareit.ai/dashboard.html`
5. Click **Register**

### Step 2: Note Your Credentials

After registration, save these values:
- **Application (client) ID**: (e.g., `12345678-1234-1234-1234-123456789012`)
- **Directory (tenant) ID**: (e.g., `87654321-4321-4321-4321-210987654321`)

You'll find these on the app's **Overview** page.

### Step 3: Configure API Permissions

1. In your app, go to **API permissions**
2. Click **Add a permission**
3. Select **Microsoft Graph**
4. Choose **Delegated permissions**
5. Add these permissions:
   - `User.Read`
   - `profile`
   - `openid`
   - `email`
6. Click **Add permissions**
7. Click **Grant admin consent for [Your Organization]**

### Step 4: Configure Authentication

1. Go to **Authentication** in your app
2. Under **Single-page application**, verify redirect URI is set:
   - `https://totalcareit.ai/dashboard.html`
3. For testing, add local redirect URI:
   - `http://localhost:8000/dashboard.html`
4. Under **Implicit grant and hybrid flows**, check:
   - ✅ Access tokens
   - ✅ ID tokens
5. **Save** changes

### Step 5: Update Website Configuration

Edit `website/js/auth.js` and update:

```javascript
const msalConfig = {
    auth: {
        clientId: "YOUR_CLIENT_ID_HERE",  // Replace with Application (client) ID
        authority: "https://login.microsoftonline.com/YOUR_TENANT_ID_HERE",  // Replace with Directory (tenant) ID
        redirectUri: "https://totalcareit.ai/dashboard.html"
    },
    // ...
};
```

## Part 2: AWS S3 Setup

### Step 1: Verify AWS CLI Configuration

```bash
# Check AWS CLI is installed
aws --version

# Verify credentials are configured
aws sts get-caller-identity

# Should output your account details
```

### Step 2: Deploy Using Automated Script

The easiest way to deploy:

```bash
cd /Users/charles/Projects/qbo-ai/website
./deploy.sh
```

This script will:
- Create S3 bucket `totalcareit.ai`
- Configure static website hosting
- Set public access policies
- Enable versioning
- Upload all website files

### Step 3: Manual Deployment (Alternative)

If you prefer manual steps:

```bash
# 1. Create bucket
aws s3 mb s3://totalcareit.ai --region us-east-1

# 2. Configure for static hosting
aws s3 website s3://totalcareit.ai \
    --index-document index.html \
    --error-document index.html

# 3. Allow public access
aws s3api put-public-access-block \
    --bucket totalcareit.ai \
    --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

# 4. Set bucket policy
aws s3api put-bucket-policy \
    --bucket totalcareit.ai \
    --policy file://bucket-policy.json

# 5. Upload files
cd /Users/charles/Projects/qbo-ai/website
aws s3 sync . s3://totalcareit.ai \
    --exclude "*.md" \
    --exclude "*.sh" \
    --exclude "*.json" \
    --exclude ".git/*" \
    --delete
```

### Step 4: Test S3 Website

After deployment, test the S3 website URL:

```
http://totalcareit.ai.s3-website-us-east-1.amazonaws.com
```

Open this URL in your browser to verify the website loads.

## Part 3: Route53 Configuration

### Step 1: Get Hosted Zone ID

```bash
# List all hosted zones
aws route53 list-hosted-zones

# Find the zone ID for totalcareit.ai
aws route53 list-hosted-zones \
    --query "HostedZones[?Name=='totalcareit.ai.'].Id" \
    --output text
```

Save this Zone ID (e.g., `Z1234567890ABC`)

### Step 2: Update DNS Records

**IMPORTANT**: The existing Route53 configuration includes Microsoft 365 email records. We need to ADD the website records WITHOUT removing the email configuration.

#### Option A: Using AWS Console (Recommended for Safety)

1. Go to [Route53 Console](https://console.aws.amazon.com/route53)
2. Click **Hosted zones** → **totalcareit.ai**
3. Click **Create record**
4. Create an **A record**:
   - **Record name**: (leave blank for root domain)
   - **Record type**: A - Routes traffic to an IPv4 address
   - **Alias**: Yes
   - **Route traffic to**: Alias to S3 website endpoint
   - **Region**: US East (N. Virginia) [us-east-1]
   - **S3 endpoint**: s3-website-us-east-1.amazonaws.com
   - Click **Create records**

5. Create a **CNAME record** for www:
   - **Record name**: www
   - **Record type**: CNAME
   - **Value**: totalcareit.ai
   - **TTL**: 300
   - Click **Create records**

#### Option B: Using CLI (Advanced)

First, verify your current records:

```bash
aws route53 list-resource-record-sets \
    --hosted-zone-id YOUR_ZONE_ID \
    --query "ResourceRecordSets[?Name=='totalcareit.ai.']"
```

Then update (this will replace the A record):

```bash
aws route53 change-resource-record-sets \
    --hosted-zone-id YOUR_ZONE_ID \
    --change-batch file://route53-website-config.json
```

### Step 3: Verify DNS Propagation

```bash
# Check DNS resolution
dig totalcareit.ai
dig www.totalcareit.ai

# Or use nslookup
nslookup totalcareit.ai
```

DNS changes can take 5-60 minutes to propagate globally.

### Step 4: Test Website

Once DNS propagates, visit:
- http://totalcareit.ai
- http://www.totalcareit.ai

## Part 4: CloudFront + HTTPS (Recommended)

For production, you should use CloudFront with HTTPS.

### Step 1: Request SSL Certificate

1. Go to [AWS Certificate Manager](https://console.aws.amazon.com/acm) in **us-east-1** region
2. Click **Request certificate**
3. Choose **Request a public certificate**
4. Add domain names:
   - `totalcareit.ai`
   - `www.totalcareit.ai`
5. Choose **DNS validation**
6. Click **Request**
7. Add the CNAME records to Route53 as instructed (for validation)
8. Wait for certificate status to become **Issued** (5-30 minutes)

### Step 2: Create CloudFront Distribution

1. Go to [CloudFront Console](https://console.aws.amazon.com/cloudfront)
2. Click **Create distribution**
3. Configure:
   - **Origin domain**: `totalcareit.ai.s3-website-us-east-1.amazonaws.com`
   - **Origin path**: (leave blank)
   - **Name**: `TotalCare AI S3`
   - **Viewer protocol policy**: Redirect HTTP to HTTPS
   - **Allowed HTTP methods**: GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE
   - **Cache policy**: CachingOptimized
   - **Alternate domain names (CNAMEs)**:
     - `totalcareit.ai`
     - `www.totalcareit.ai`
   - **Custom SSL certificate**: (select your certificate)
   - **Default root object**: `index.html`
4. Click **Create distribution**
5. Wait for distribution to deploy (10-20 minutes)
6. Save the **Distribution domain name** (e.g., `d123abc456def.cloudfront.net`)

### Step 3: Update Route53 for CloudFront

Update your A records to point to CloudFront:

1. Go to Route53 → totalcareit.ai hosted zone
2. Edit the A record for `totalcareit.ai`:
   - **Alias**: Yes
   - **Route traffic to**: Alias to CloudFront distribution
   - **Distribution**: (select your distribution)
3. Update the www CNAME or create an A record alias as well

### Step 4: Configure CloudFront Error Pages

1. In your CloudFront distribution, go to **Error pages**
2. Create custom error response:
   - **HTTP error code**: 403
   - **Customize error response**: Yes
   - **Response page path**: `/index.html`
   - **HTTP response code**: 200
3. Repeat for error code 404

### Step 5: Test HTTPS

Visit:
- https://totalcareit.ai
- https://www.totalcareit.ai

## Part 5: Testing Microsoft 365 Login

### Step 1: Test Authentication Flow

1. Visit https://totalcareit.ai
2. Click **Client Portal** button
3. Click **Sign in with Microsoft 365**
4. You should be redirected to Microsoft login
5. Enter your Microsoft 365 credentials
6. After successful login, you should be redirected to the dashboard

### Step 2: Verify Dashboard Access

1. Check that your name and email appear in the sidebar
2. Try clicking different navigation items
3. Test the logout button

### Step 3: Troubleshooting

If login fails:

1. **Check browser console** (F12) for errors
2. **Verify Azure AD configuration**:
   - Redirect URI matches exactly
   - API permissions are granted
   - App is enabled
3. **Check auth.js configuration**:
   - Client ID is correct
   - Tenant ID is correct
   - Redirect URI matches Azure AD

Common errors:
- `AADSTS50011`: Redirect URI mismatch
- `AADSTS65001`: User didn't consent
- `AADSTS7000215`: Invalid client secret (shouldn't need one for SPA)

## Part 6: Post-Deployment

### Update Website Content

To update the website after making changes:

```bash
cd /Users/charles/Projects/qbo-ai/website

# Sync changes to S3
aws s3 sync . s3://totalcareit.ai \
    --exclude "*.md" \
    --exclude "*.sh" \
    --exclude "*.json" \
    --delete

# If using CloudFront, invalidate cache
aws cloudfront create-invalidation \
    --distribution-id YOUR_DISTRIBUTION_ID \
    --paths "/*"
```

### Enable Logging

For S3 access logs:

```bash
aws s3api put-bucket-logging \
    --bucket totalcareit.ai \
    --bucket-logging-status file://logging-config.json
```

For CloudFront logs:
1. Go to CloudFront distribution settings
2. Edit **Logging**
3. Enable logging
4. Choose an S3 bucket for logs

### Set Up Monitoring

1. Go to CloudWatch
2. Set up alarms for:
   - S3 bucket requests
   - CloudFront 4xx/5xx errors
   - CloudFront cache hit ratio

## Security Checklist

- ✅ HTTPS enabled (via CloudFront)
- ✅ S3 bucket policy restricts to GetObject only
- ✅ Azure AD authentication configured
- ✅ Redirect URIs validated
- ✅ API permissions limited to minimum required
- ✅ Session storage (not localStorage) for tokens
- ✅ No client secrets in frontend code
- ⚠️ Consider adding CSP headers via CloudFront
- ⚠️ Consider adding WAF rules for protection

## Troubleshooting

### Website Not Loading

1. Check S3 bucket policy allows public read
2. Verify DNS records in Route53
3. Test S3 website endpoint directly
4. Check browser console for errors

### Microsoft 365 Login Not Working

1. Verify Azure AD app configuration
2. Check redirect URIs match exactly
3. Ensure API permissions are granted
4. Check browser console for MSAL errors
5. Verify users have access to the app

### Certificate Issues

1. Certificate must be in us-east-1 for CloudFront
2. Domain validation must be complete
3. Certificate must include all domain names (root + www)

## Costs Estimate

- **S3**: ~$0.50-2/month (for small traffic)
- **CloudFront**: ~$1-5/month (first 50GB free for 12 months)
- **Route53**: $0.50/month per hosted zone + query charges
- **Total**: ~$2-8/month

## Next Steps

1. **Add Real Content**: Populate dashboard with actual company data
2. **Implement API**: Build backend API for dashboard data
3. **Analytics**: Add Google Analytics or similar
4. **SEO**: Add meta tags, sitemap.xml, robots.txt
5. **Email Integration**: Configure contact form to send emails
6. **Monitoring**: Set up uptime monitoring (e.g., UptimeRobot)

## Support

If you encounter issues:
1. Check the README.md in the website folder
2. Review AWS CloudWatch logs
3. Check Azure AD sign-in logs
4. Contact TotalCare IT support

---

**Deployment Date**: 2025-01-23
**Version**: 1.0.0
