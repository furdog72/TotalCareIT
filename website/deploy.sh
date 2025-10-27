#!/bin/bash

# Deployment script for TotalCare AI website
# This script deploys the website to AWS S3 and configures Route53

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BUCKET_NAME="totalcareit.ai"
REGION="us-east-1"
PROFILE="${AWS_PROFILE:-default}"

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}TotalCare AI Website Deployment${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    echo "Please install AWS CLI: https://aws.amazon.com/cli/"
    exit 1
fi

# Check AWS credentials
echo -e "${YELLOW}Checking AWS credentials...${NC}"
if ! aws sts get-caller-identity --profile "$PROFILE" &> /dev/null; then
    echo -e "${RED}Error: AWS credentials not configured${NC}"
    echo "Please run: aws configure --profile $PROFILE"
    exit 1
fi
echo -e "${GREEN}✓ AWS credentials verified${NC}"
echo ""

# Step 1: Create S3 bucket if it doesn't exist
echo -e "${YELLOW}Step 1: Checking S3 bucket...${NC}"
if aws s3 ls "s3://$BUCKET_NAME" --profile "$PROFILE" 2>&1 | grep -q 'NoSuchBucket'; then
    echo "Creating bucket $BUCKET_NAME..."
    aws s3 mb "s3://$BUCKET_NAME" --region "$REGION" --profile "$PROFILE"
    echo -e "${GREEN}✓ Bucket created${NC}"
else
    echo -e "${GREEN}✓ Bucket already exists${NC}"
fi
echo ""

# Step 2: Configure bucket for static website hosting
echo -e "${YELLOW}Step 2: Configuring static website hosting...${NC}"
aws s3 website "s3://$BUCKET_NAME" \
    --index-document index.html \
    --error-document index.html \
    --profile "$PROFILE"
echo -e "${GREEN}✓ Static website hosting configured${NC}"
echo ""

# Step 3: Set bucket policy for public access
echo -e "${YELLOW}Step 3: Setting bucket policy for public access...${NC}"
aws s3api put-public-access-block \
    --bucket "$BUCKET_NAME" \
    --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false" \
    --profile "$PROFILE"

aws s3api put-bucket-policy \
    --bucket "$BUCKET_NAME" \
    --policy file://bucket-policy.json \
    --profile "$PROFILE"
echo -e "${GREEN}✓ Bucket policy set${NC}"
echo ""

# Step 4: Enable versioning (optional but recommended)
echo -e "${YELLOW}Step 4: Enabling versioning...${NC}"
aws s3api put-bucket-versioning \
    --bucket "$BUCKET_NAME" \
    --versioning-configuration Status=Enabled \
    --profile "$PROFILE"
echo -e "${GREEN}✓ Versioning enabled${NC}"
echo ""

# Step 5: Upload website files
echo -e "${YELLOW}Step 5: Uploading website files...${NC}"
aws s3 sync . "s3://$BUCKET_NAME" \
    --profile "$PROFILE" \
    --exclude "*.md" \
    --exclude "*.sh" \
    --exclude "bucket-policy.json" \
    --exclude "route53-website-config.json" \
    --exclude ".git/*" \
    --exclude ".DS_Store" \
    --delete \
    --cache-control "public, max-age=3600"

# Set longer cache for static assets
aws s3 cp "s3://$BUCKET_NAME/css/" "s3://$BUCKET_NAME/css/" \
    --recursive \
    --metadata-directive REPLACE \
    --cache-control "public, max-age=604800" \
    --profile "$PROFILE"

aws s3 cp "s3://$BUCKET_NAME/js/" "s3://$BUCKET_NAME/js/" \
    --recursive \
    --metadata-directive REPLACE \
    --cache-control "public, max-age=604800" \
    --profile "$PROFILE"

echo -e "${GREEN}✓ Files uploaded${NC}"
echo ""

# Step 6: Get website URL
WEBSITE_URL="http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo -e "Website URL: ${YELLOW}$WEBSITE_URL${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Configure Route53 to point totalcareit.ai to the S3 bucket"
echo "   Run: aws route53 change-resource-record-sets --hosted-zone-id YOUR_ZONE_ID --change-batch file://route53-website-config.json"
echo ""
echo "2. Set up CloudFront distribution for HTTPS (recommended)"
echo "   - Create CloudFront distribution with S3 origin"
echo "   - Request SSL certificate in ACM for totalcareit.ai"
echo "   - Update Route53 to point to CloudFront"
echo ""
echo "3. Configure Microsoft 365 authentication"
echo "   - Update js/auth.js with Azure AD credentials"
echo "   - Add redirect URIs in Azure AD app registration"
echo ""
echo -e "${GREEN}For detailed instructions, see README.md${NC}"
