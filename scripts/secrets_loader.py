"""
Automatic secrets loading from AWS Secrets Manager

This module provides automatic loading of secrets from AWS Secrets Manager
with fallback to local .env file for development.

Usage:
    from scripts.secrets_loader import load_secrets

    # Automatically loads from AWS Secrets Manager or .env
    load_secrets()

    # Now you can use os.getenv() as normal
    api_key = os.getenv('HUBSPOT_API_KEY')
"""

import os
import boto3
import json
from pathlib import Path
from dotenv import load_dotenv


def load_secrets(secret_name: str = 'totalcareit/api-keys', use_aws: bool = None):
    """
    Load secrets from AWS Secrets Manager or .env file

    Args:
        secret_name: Name of the secret in AWS Secrets Manager
        use_aws: Force AWS or local mode. If None, auto-detect based on AWS credentials

    Returns:
        bool: True if secrets loaded successfully
    """

    # Auto-detect if we should use AWS
    if use_aws is None:
        # Check if running on AWS (Lambda, EC2, etc.) or has AWS credentials
        use_aws = _has_aws_credentials()

    if use_aws:
        print("🔐 Loading secrets from AWS Secrets Manager...")
        return _load_from_aws(secret_name)
    else:
        print("📁 Loading secrets from local .env file...")
        return _load_from_env()


def _has_aws_credentials() -> bool:
    """Check if AWS credentials are available"""
    try:
        # Check environment variables
        if os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY'):
            return True

        # Check if running on EC2/Lambda
        if os.getenv('AWS_EXECUTION_ENV') or os.getenv('AWS_LAMBDA_FUNCTION_NAME'):
            return True

        # Try to get credentials from boto3 (includes ~/.aws/credentials)
        session = boto3.Session()
        credentials = session.get_credentials()
        return credentials is not None
    except Exception:
        return False


def _load_from_aws(secret_name: str) -> bool:
    """Load secrets from AWS Secrets Manager"""
    try:
        client = boto3.client('secretsmanager', region_name='us-east-1')
        response = client.get_secret_value(SecretId=secret_name)
        secret_data = json.loads(response['SecretString'])

        # Set environment variables
        for key, value in secret_data.items():
            os.environ[key] = value

        print(f"✅ Loaded {len(secret_data)} secrets from AWS Secrets Manager")
        return True
    except Exception as e:
        print(f"❌ Failed to load from AWS Secrets Manager: {e}")
        print("   Falling back to local .env file...")
        return _load_from_env()


def _load_from_env() -> bool:
    """Load secrets from local .env file"""
    env_path = Path(__file__).parent.parent / '.env'

    if not env_path.exists():
        print(f"⚠️  No .env file found at: {env_path}")
        print(f"   Run: python scripts/setup_secrets_manager.py download")
        return False

    load_dotenv(env_path)
    print(f"✅ Loaded secrets from {env_path}")
    return True


# Convenience function for direct import
def get_secret(key: str, default: str = None) -> str:
    """
    Get a secret value with automatic loading

    Args:
        key: Environment variable name
        default: Default value if not found

    Returns:
        str: Secret value or default
    """
    # Ensure secrets are loaded
    if not os.getenv(key):
        load_secrets()

    return os.getenv(key, default)
