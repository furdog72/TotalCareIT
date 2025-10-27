# AWS Resources for QuickBooks AI Agent

## AWS Account
- **Account ID**: 032880537692
- **Profile**: tci
- **Region**: us-west-2

## EC2 Resources

### Instance
- **Instance ID**: i-0b4108b6b93733500
- **Instance Type**: t3.small
- **AMI**: ami-0e15691111f1b646d (Amazon Linux 2023)
- **Name**: qbo-ai-server
- **Environment**: production

### Networking
- **Elastic IP**: 34.209.45.194
- **Allocation ID**: eipalloc-030cf1472f02c4d06
- **Association ID**: eipassoc-07c20e2b6b7d39211
- **Security Group**: sg-0a36bbfd5c6db283f (qbo-ai-sg)
  - Port 22: SSH access (0.0.0.0/0)
  - Port 8000: FastAPI application (0.0.0.0/0)

### IAM Resources
- **EC2 Role**: qbo-ai-ec2-role
  - ARN: arn:aws:iam::032880537692:role/qbo-ai-ec2-role
  - Attached Policy: SecretsManagerReadWrite
- **Instance Profile**: qbo-ai-ec2-profile
  - ARN: arn:aws:iam::032880537692:instance-profile/qbo-ai-ec2-profile

### SSH Access
- **Key Pair Name**: qbo-ai-key
- **Key File**: qbo-ai-key.pem (stored locally)
- **SSH Command**: `ssh -i qbo-ai-key.pem ec2-user@34.209.45.194`

## Secrets Manager
- **Secret Name**: qbo-ai/tokens
- **Secret ARN**: arn:aws:secretsmanager:us-west-2:032880537692:secret:qbo-ai/tokens-tSN8dU
- **Contents**:
  - access_token
  - refresh_token
  - token_expiry
  - company_id

## Application Access

### Web Interface
- **URL**: http://34.209.45.194:8000
- **API Base**: http://34.209.45.194:8000/api
- **Health Check**: http://34.209.45.194:8000/health

### API Endpoints
- **AI Analysis**: POST http://34.209.45.194:8000/api/analyze
- **Query Entities**: POST http://34.209.45.194:8000/api/query/{entity}
- **Legacy Lambda Compatibility**: POST http://34.209.45.194:8000/api

## QuickBooks OAuth Configuration

### Redirect URI for Production
Add this to your QuickBooks app settings:
- **Redirect URI**: http://34.209.45.194:8000/callback

### IP Allowlist
For production QuickBooks access, add this IP to your allowlist:
- **Static IP**: 34.209.45.194

## Deployment

### Quick Deploy
```bash
./deploy_to_ec2.sh
```

### Manual Deployment
```bash
# SSH to server
ssh -i qbo-ai-key.pem ec2-user@34.209.45.194

# Navigate to app directory
cd /opt/qbo-ai

# Pull latest code (if using git)
git pull

# Install dependencies
python3.11 -m pip install -r requirements.txt

# Restart service
sudo systemctl restart qbo-ai

# Check status
sudo systemctl status qbo-ai

# View logs
sudo journalctl -u qbo-ai -f
```

## Service Management

### Systemd Service
- **Service Name**: qbo-ai
- **Service File**: /etc/systemd/system/qbo-ai.service
- **Working Directory**: /opt/qbo-ai
- **User**: ec2-user
- **Port**: 8000

### Common Commands
```bash
# Start service
sudo systemctl start qbo-ai

# Stop service
sudo systemctl stop qbo-ai

# Restart service
sudo systemctl restart qbo-ai

# Check status
sudo systemctl status qbo-ai

# Enable auto-start on boot
sudo systemctl enable qbo-ai

# View logs
sudo journalctl -u qbo-ai -f

# View last 100 lines of logs
sudo journalctl -u qbo-ai -n 100
```

## Environment Configuration

### Environment Variables
Location: `/opt/qbo-ai/.env`

Required variables:
```
QBO_CLIENT_ID=your_client_id
QBO_CLIENT_SECRET=your_client_secret
QBO_REDIRECT_URI=http://34.209.45.194:8000/callback
QBO_ENVIRONMENT=sandbox
AWS_DEFAULT_REGION=us-west-2
ANTHROPIC_API_KEY=your_anthropic_key
```

## Monitoring

### CloudWatch Logs
- **Log Group**: /aws/ec2/qbo-ai
- **Log Stream**: i-0b4108b6b93733500

### Health Check
```bash
curl http://34.209.45.194:8000/health
```

## Backup and Recovery

### Create AMI Backup
```bash
aws ec2 create-image \
  --instance-id i-0b4108b6b93733500 \
  --name "qbo-ai-backup-$(date +%Y%m%d)" \
  --description "Backup of QBO AI server" \
  --profile tci
```

### Secrets Backup
```bash
aws secretsmanager get-secret-value \
  --secret-id qbo-ai/tokens \
  --profile tci \
  --query SecretString \
  --output text > tokens-backup.json
```

## Cost Optimization

### Instance Type
- Current: t3.small ($0.0208/hour)
- For testing: t3.micro ($0.0104/hour)
- For production: t3.medium ($0.0416/hour)

### Stop/Start Instance
```bash
# Stop instance (keeps Elastic IP)
aws ec2 stop-instances --instance-ids i-0b4108b6b93733500 --profile tci

# Start instance
aws ec2 start-instances --instance-ids i-0b4108b6b93733500 --profile tci
```

## Cleanup (if needed)

### Terminate Resources
```bash
# WARNING: This will permanently delete resources

# Disassociate and release Elastic IP
aws ec2 disassociate-address --association-id eipassoc-07c20e2b6b7d39211 --profile tci
aws ec2 release-address --allocation-id eipalloc-030cf1472f02c4d06 --profile tci

# Terminate instance
aws ec2 terminate-instances --instance-ids i-0b4108b6b93733500 --profile tci

# Delete security group (after instance is terminated)
aws ec2 delete-security-group --group-id sg-0a36bbfd5c6db283f --profile tci

# Delete IAM resources
aws iam remove-role-from-instance-profile --instance-profile-name qbo-ai-ec2-profile --role-name qbo-ai-ec2-role --profile tci
aws iam delete-instance-profile --instance-profile-name qbo-ai-ec2-profile --profile tci
aws iam detach-role-policy --role-name qbo-ai-ec2-role --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite --profile tci
aws iam delete-role --role-name qbo-ai-ec2-role --profile tci

# Delete key pair
aws ec2 delete-key-pair --key-name qbo-ai-key --profile tci
rm qbo-ai-key.pem
```