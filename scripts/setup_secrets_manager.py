#!/usr/bin/env python3
"""
Setup and manage secrets in AWS Secrets Manager

This script helps you:
1. Store API keys securely in AWS Secrets Manager
2. Retrieve secrets for local development
3. Rotate secrets when needed
"""

import boto3
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def create_secret(secret_name: str, secret_data: dict):
    """Create or update a secret in AWS Secrets Manager"""
    client = boto3.client('secretsmanager', region_name='us-east-1')

    try:
        # Try to create the secret
        response = client.create_secret(
            Name=secret_name,
            Description='TotalCare IT API credentials',
            SecretString=json.dumps(secret_data)
        )
        print(f"✅ Created secret: {secret_name}")
        print(f"   ARN: {response['ARN']}")
        return response
    except client.exceptions.ResourceExistsException:
        # Secret already exists, update it
        response = client.update_secret(
            SecretId=secret_name,
            SecretString=json.dumps(secret_data)
        )
        print(f"✅ Updated secret: {secret_name}")
        print(f"   ARN: {response['ARN']}")
        return response
    except Exception as e:
        print(f"❌ Error creating/updating secret: {e}")
        raise


def get_secret(secret_name: str) -> dict:
    """Retrieve a secret from AWS Secrets Manager"""
    client = boto3.client('secretsmanager', region_name='us-east-1')

    try:
        response = client.get_secret_value(SecretId=secret_name)
        secret_data = json.loads(response['SecretString'])
        print(f"✅ Retrieved secret: {secret_name}")
        return secret_data
    except client.exceptions.ResourceNotFoundException:
        print(f"❌ Secret not found: {secret_name}")
        return None
    except Exception as e:
        print(f"❌ Error retrieving secret: {e}")
        raise


def generate_env_file(secret_data: dict, output_path: str = '.env'):
    """Generate .env file from secret data"""
    env_content = []

    # QuickBooks
    if 'QBO_CLIENT_ID' in secret_data:
        env_content.append(f"QBO_CLIENT_ID={secret_data['QBO_CLIENT_ID']}")
    if 'QBO_CLIENT_SECRET' in secret_data:
        env_content.append(f"QBO_CLIENT_SECRET={secret_data['QBO_CLIENT_SECRET']}")
    if 'QBO_COMPANY_ID' in secret_data:
        env_content.append(f"QBO_COMPANY_ID={secret_data['QBO_COMPANY_ID']}")
    if 'QBO_REDIRECT_URI' in secret_data:
        env_content.append(f"QBO_REDIRECT_URI={secret_data['QBO_REDIRECT_URI']}")
    if 'QBO_ENVIRONMENT' in secret_data:
        env_content.append(f"QBO_ENVIRONMENT={secret_data['QBO_ENVIRONMENT']}")

    env_content.append("")

    # HubSpot
    if 'HUBSPOT_API_KEY' in secret_data:
        env_content.append(f"HUBSPOT_API_KEY={secret_data['HUBSPOT_API_KEY']}")
    if 'HUBSPOT_HUB_ID' in secret_data:
        env_content.append(f"HUBSPOT_HUB_ID={secret_data['HUBSPOT_HUB_ID']}")

    env_content.append("")

    # Autotask
    if 'AUTOTASK_USERNAME' in secret_data:
        env_content.append(f"AUTOTASK_USERNAME={secret_data['AUTOTASK_USERNAME']}")
    if 'AUTOTASK_SECRET' in secret_data:
        env_content.append(f"AUTOTASK_SECRET={secret_data['AUTOTASK_SECRET']}")
    if 'AUTOTASK_INTEGRATION_CODE' in secret_data:
        env_content.append(f"AUTOTASK_INTEGRATION_CODE={secret_data['AUTOTASK_INTEGRATION_CODE']}")
    if 'AUTOTASK_ZONE_URL' in secret_data:
        env_content.append(f"AUTOTASK_ZONE_URL={secret_data['AUTOTASK_ZONE_URL']}")

    env_content.append("")

    # Datto
    if 'DATTO_API_PUBLIC_KEY' in secret_data:
        env_content.append(f"DATTO_API_PUBLIC_KEY={secret_data['DATTO_API_PUBLIC_KEY']}")
    if 'DATTO_API_PRIVATE_KEY' in secret_data:
        env_content.append(f"DATTO_API_PRIVATE_KEY={secret_data['DATTO_API_PRIVATE_KEY']}")
    if 'DATTO_PORTAL_URL' in secret_data:
        env_content.append(f"DATTO_PORTAL_URL={secret_data['DATTO_PORTAL_URL']}")
    if 'DATTO_RMM_URL' in secret_data:
        env_content.append(f"DATTO_RMM_URL={secret_data['DATTO_RMM_URL']}")

    env_content.append("")

    # CloudFront
    if 'CLOUDFRONT_DISTRIBUTION_ID' in secret_data:
        env_content.append(f"CLOUDFRONT_DISTRIBUTION_ID={secret_data['CLOUDFRONT_DISTRIBUTION_ID']}")

    # Write to file
    with open(output_path, 'w') as f:
        f.write('\n'.join(env_content))

    print(f"✅ Generated .env file at: {output_path}")


def upload_from_env_file(env_path: str = '.env', secret_name: str = 'totalcareit/api-keys'):
    """Upload secrets from existing .env file to AWS Secrets Manager"""
    if not Path(env_path).exists():
        print(f"❌ .env file not found at: {env_path}")
        return

    secret_data = {}

    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                secret_data[key.strip()] = value.strip()

    print(f"\n📦 Found {len(secret_data)} secrets in {env_path}")
    print(f"🔐 Uploading to AWS Secrets Manager: {secret_name}\n")

    create_secret(secret_name, secret_data)

    print(f"\n✅ Successfully uploaded secrets!")
    print(f"\n⚠️  IMPORTANT: You can now delete your local .env file for security")
    print(f"   To retrieve secrets later, run: python scripts/setup_secrets_manager.py download")


def download_secrets(secret_name: str = 'totalcareit/api-keys', output_path: str = '.env'):
    """Download secrets from AWS Secrets Manager and create .env file"""
    print(f"\n🔐 Retrieving secrets from AWS Secrets Manager: {secret_name}\n")

    secret_data = get_secret(secret_name)

    if secret_data:
        generate_env_file(secret_data, output_path)
        print(f"\n✅ Successfully downloaded secrets to {output_path}")
        print(f"\n⚠️  Remember: Never commit .env to git!")
    else:
        print(f"\n❌ Failed to retrieve secrets")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Manage API secrets in AWS Secrets Manager')
    parser.add_argument('action', choices=['upload', 'download', 'view'],
                       help='Action to perform')
    parser.add_argument('--secret-name', default='totalcareit/api-keys',
                       help='Name of the secret in AWS Secrets Manager')
    parser.add_argument('--env-file', default='.env',
                       help='Path to .env file')

    args = parser.parse_args()

    if args.action == 'upload':
        upload_from_env_file(args.env_file, args.secret_name)
    elif args.action == 'download':
        download_secrets(args.secret_name, args.env_file)
    elif args.action == 'view':
        secret_data = get_secret(args.secret_name)
        if secret_data:
            print(f"\n📋 Secret contents:")
            for key in sorted(secret_data.keys()):
                # Mask the value for security
                masked_value = secret_data[key][:4] + '*' * (len(secret_data[key]) - 4) if len(secret_data[key]) > 4 else '****'
                print(f"   {key}: {masked_value}")
