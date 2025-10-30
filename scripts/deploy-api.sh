#!/bin/bash

# TotalCareIT API - Automated AWS Deployment Script
# This script deploys the backend API to AWS EC2

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}TotalCareIT API - AWS Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Configuration
AWS_PROFILE="default"
AWS_REGION="us-east-1"
INSTANCE_TYPE="t3.small"
HOSTED_ZONE_ID="Z05865843LXBEZ6UMEIY7"
DOMAIN="api.totalcareit.ai"
KEY_NAME="totalcareit-api-key"
SECURITY_GROUP_NAME="totalcareit-api-sg"

# Get the latest Ubuntu 22.04 LTS AMI
echo -e "${YELLOW}Finding latest Ubuntu 22.04 LTS AMI...${NC}"
AMI_ID=$(aws ec2 describe-images \
    --owners 099720109477 \
    --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
    --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
    --output text \
    --profile $AWS_PROFILE \
    --region $AWS_REGION)

echo -e "${GREEN}✓ Using AMI: $AMI_ID${NC}"

# Create key pair if it doesn't exist
echo ""
echo -e "${YELLOW}Checking SSH key pair...${NC}"
if aws ec2 describe-key-pairs --key-names $KEY_NAME --profile $AWS_PROFILE --region $AWS_REGION >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Key pair $KEY_NAME already exists${NC}"
else
    echo -e "${YELLOW}Creating new key pair...${NC}"
    aws ec2 create-key-pair \
        --key-name $KEY_NAME \
        --query 'KeyMaterial' \
        --output text \
        --profile $AWS_PROFILE \
        --region $AWS_REGION > ~/.ssh/$KEY_NAME.pem
    chmod 400 ~/.ssh/$KEY_NAME.pem
    echo -e "${GREEN}✓ Key pair created and saved to ~/.ssh/$KEY_NAME.pem${NC}"
fi

# Create security group if it doesn't exist
echo ""
echo -e "${YELLOW}Checking security group...${NC}"
SECURITY_GROUP_ID=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=$SECURITY_GROUP_NAME" \
    --query 'SecurityGroups[0].GroupId' \
    --output text \
    --profile $AWS_PROFILE \
    --region $AWS_REGION 2>/dev/null || echo "")

if [ "$SECURITY_GROUP_ID" = "None" ] || [ -z "$SECURITY_GROUP_ID" ]; then
    echo -e "${YELLOW}Creating security group...${NC}"

    # Get default VPC
    VPC_ID=$(aws ec2 describe-vpcs \
        --filters "Name=is-default,Values=true" \
        --query 'Vpcs[0].VpcId' \
        --output text \
        --profile $AWS_PROFILE \
        --region $AWS_REGION)

    SECURITY_GROUP_ID=$(aws ec2 create-security-group \
        --group-name $SECURITY_GROUP_NAME \
        --description "Security group for TotalCareIT API" \
        --vpc-id $VPC_ID \
        --query 'GroupId' \
        --output text \
        --profile $AWS_PROFILE \
        --region $AWS_REGION)

    # Add rules
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp --port 22 --cidr 0.0.0.0/0 \
        --profile $AWS_PROFILE --region $AWS_REGION

    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp --port 80 --cidr 0.0.0.0/0 \
        --profile $AWS_PROFILE --region $AWS_REGION

    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp --port 443 --cidr 0.0.0.0/0 \
        --profile $AWS_PROFILE --region $AWS_REGION

    echo -e "${GREEN}✓ Security group created: $SECURITY_GROUP_ID${NC}"
else
    echo -e "${GREEN}✓ Security group already exists: $SECURITY_GROUP_ID${NC}"
fi

# Create user data script for EC2 initialization
echo ""
echo -e "${YELLOW}Preparing EC2 user data script...${NC}"
cat > /tmp/user-data.sh <<'USERDATA'
#!/bin/bash
set -e

# Update system
apt-get update
apt-get upgrade -y

# Install dependencies
apt-get install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git

# Create application directory
mkdir -p /var/www/totalcareit-api
cd /var/www/totalcareit-api

# Create placeholder until we deploy
echo "API deployment in progress" > index.html

echo "EC2 instance initialized successfully" > /var/log/user-data-complete.log
USERDATA

# Launch EC2 instance
echo ""
echo -e "${YELLOW}Launching EC2 instance...${NC}"
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --security-group-ids $SECURITY_GROUP_ID \
    --user-data file:///tmp/user-data.sh \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=TotalCareIT-API},{Key=Project,Value=TotalCareIT}]" \
    --query 'Instances[0].InstanceId' \
    --output text \
    --profile $AWS_PROFILE \
    --region $AWS_REGION)

echo -e "${GREEN}✓ Instance launched: $INSTANCE_ID${NC}"

# Wait for instance to be running
echo ""
echo -e "${YELLOW}Waiting for instance to be running...${NC}"
aws ec2 wait instance-running \
    --instance-ids $INSTANCE_ID \
    --profile $AWS_PROFILE \
    --region $AWS_REGION

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text \
    --profile $AWS_PROFILE \
    --region $AWS_REGION)

echo -e "${GREEN}✓ Instance running with IP: $PUBLIC_IP${NC}"

# Update Route53 DNS
echo ""
echo -e "${YELLOW}Updating DNS for $DOMAIN...${NC}"
cat > /tmp/dns-change.json <<EOF
{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "$DOMAIN",
      "Type": "A",
      "TTL": 300,
      "ResourceRecords": [{"Value": "$PUBLIC_IP"}]
    }
  }]
}
EOF

aws route53 change-resource-record-sets \
    --hosted-zone-id $HOSTED_ZONE_ID \
    --change-batch file:///tmp/dns-change.json \
    --profile $AWS_PROFILE >/dev/null

echo -e "${GREEN}✓ DNS updated: $DOMAIN → $PUBLIC_IP${NC}"

# Wait for SSH to be available
echo ""
echo -e "${YELLOW}Waiting for SSH to be available (this may take 2-3 minutes)...${NC}"
for i in {1..60}; do
    if ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -i ~/.ssh/$KEY_NAME.pem ubuntu@$PUBLIC_IP "echo 'SSH Ready'" 2>/dev/null; then
        echo -e "${GREEN}✓ SSH connection established${NC}"
        break
    fi
    echo -n "."
    sleep 5
done
echo ""

# Save deployment info
cat > /tmp/deployment-info.txt <<EOF
========================================
TotalCareIT API Deployment Information
========================================

Instance ID: $INSTANCE_ID
Public IP: $PUBLIC_IP
Domain: $DOMAIN
SSH Key: ~/.ssh/$KEY_NAME.pem

SSH Command:
  ssh -i ~/.ssh/$KEY_NAME.pem ubuntu@$PUBLIC_IP

Next Steps:
1. Wait 2-3 minutes for the instance to finish initialization
2. SSH into the server
3. Run the deployment script: ~/deploy-api-code.sh
4. Configure API credentials in /var/www/totalcareit-api/.env

========================================
EOF

cat /tmp/deployment-info.txt

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}EC2 Instance Deployed Successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Instance ID:${NC} $INSTANCE_ID"
echo -e "${YELLOW}Public IP:${NC} $PUBLIC_IP"
echo -e "${YELLOW}Domain:${NC} $DOMAIN"
echo ""
echo -e "${YELLOW}SSH Command:${NC}"
echo -e "  ssh -i ~/.ssh/$KEY_NAME.pem ubuntu@$PUBLIC_IP"
echo ""
echo -e "${YELLOW}Deployment info saved to:${NC} /tmp/deployment-info.txt"
echo ""
