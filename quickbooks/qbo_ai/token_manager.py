"""
Token Manager for QuickBooks Online OAuth
Handles token lifecycle including loading from AWS Secrets Manager and automatic refresh
"""

import json
import os
from typing import Dict, Optional
from datetime import datetime, timedelta
import boto3
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes


class TokenManager:
    """
    Manages QuickBooks OAuth tokens with automatic refresh
    """

    def __init__(
        self,
        secret_name: Optional[str] = None,
        region_name: Optional[str] = None,
        secrets_client: Optional[boto3.client] = None,
    ):
        """
        Initialize TokenManager

        Args:
            secret_name: Name of the secret in AWS Secrets Manager
            region_name: AWS region for Secrets Manager
            secrets_client: Optional pre-configured boto3 secrets manager client
        """
        self.secret_name = secret_name or os.getenv(
            "QBO_SECRET_NAME", "qbo-ai/tokens"
        )
        self.region_name = region_name or os.getenv("AWS_REGION", "us-east-1")

        # Use provided client or create new one
        self.secrets_client = secrets_client or boto3.client(
            "secretsmanager", region_name=self.region_name
        )

        # Token data
        self.tokens: Optional[Dict] = None
        self.auth_client: Optional[AuthClient] = None
        self.last_refresh: Optional[datetime] = None

        # Load tokens on initialization
        self._load_tokens()

    def _load_tokens(self) -> Dict:
        """
        Load tokens from AWS Secrets Manager

        Returns:
            Dictionary containing token data
        """
        try:
            response = self.secrets_client.get_secret_value(SecretId=self.secret_name)
            self.tokens = json.loads(response["SecretString"])
            self.last_refresh = datetime.now()
            return self.tokens
        except Exception as e:
            raise RuntimeError(
                f"Failed to load tokens from Secrets Manager: {str(e)}"
            )

    def _save_tokens(self) -> None:
        """
        Save updated tokens back to AWS Secrets Manager
        """
        try:
            self.secrets_client.update_secret(
                SecretId=self.secret_name, SecretString=json.dumps(self.tokens)
            )
        except Exception as e:
            raise RuntimeError(f"Failed to save tokens to Secrets Manager: {str(e)}")

    def tokens_exist(self) -> bool:
        """
        Check if tokens are available

        Returns:
            True if tokens are loaded, False otherwise
        """
        return self.tokens is not None and 'access_token' in self.tokens

    def _initialize_auth_client(self) -> AuthClient:
        """
        Initialize Intuit AuthClient with current credentials

        Returns:
            Configured AuthClient instance
        """
        if not self.tokens:
            raise RuntimeError("Tokens not loaded")

        auth_client = AuthClient(
            client_id=self.tokens.get("client_id"),
            client_secret=self.tokens.get("client_secret"),
            redirect_uri=self.tokens.get("redirect_uri", "http://localhost:8000/callback"),
            environment=self.tokens.get("environment", "production"),
        )

        # Set existing tokens
        auth_client.access_token = self.tokens.get("access_token")
        auth_client.refresh_token = self.tokens.get("refresh_token")

        return auth_client

    def _is_token_expired(self) -> bool:
        """
        Check if access token is likely expired

        QuickBooks access tokens expire after 1 hour.
        We'll consider it expired if it's been more than 55 minutes since last refresh
        to provide a safety margin.

        Returns:
            True if token is likely expired
        """
        if not self.last_refresh:
            return True

        # Consider expired after 55 minutes (5 minute safety margin)
        expiry_threshold = timedelta(minutes=55)
        return datetime.now() - self.last_refresh > expiry_threshold

    def refresh_tokens(self) -> Dict:
        """
        Refresh access token using refresh token

        Returns:
            Updated token dictionary
        """
        try:
            # Initialize auth client if needed
            if not self.auth_client:
                self.auth_client = self._initialize_auth_client()

            # Refresh the token
            self.auth_client.refresh()

            # Update our token storage
            self.tokens["access_token"] = self.auth_client.access_token
            self.tokens["refresh_token"] = self.auth_client.refresh_token
            self.last_refresh = datetime.now()

            # Save updated tokens to Secrets Manager
            self._save_tokens()

            return self.tokens

        except Exception as e:
            raise RuntimeError(f"Failed to refresh tokens: {str(e)}")

    def get_valid_tokens(self) -> Dict:
        """
        Get valid tokens, refreshing if necessary

        Returns:
            Dictionary containing valid tokens
        """
        # Check if tokens need refresh
        if self._is_token_expired():
            self.refresh_tokens()

        return self.tokens

    def get_access_token(self) -> str:
        """
        Get valid access token, refreshing if necessary

        Returns:
            Valid access token string
        """
        tokens = self.get_valid_tokens()
        return tokens.get("access_token")

    def get_refresh_token(self) -> str:
        """
        Get refresh token

        Returns:
            Refresh token string
        """
        if not self.tokens:
            self._load_tokens()
        return self.tokens.get("refresh_token")

    def get_realm_id(self) -> str:
        """
        Get QuickBooks company/realm ID

        Returns:
            Realm ID string
        """
        if not self.tokens:
            self._load_tokens()
        return self.tokens.get("realm_id")

    def get_environment(self) -> str:
        """
        Get QuickBooks environment (sandbox or production)

        Returns:
            Environment string
        """
        if not self.tokens:
            self._load_tokens()
        return self.tokens.get("environment", "production")

    def reload_from_secrets_manager(self) -> Dict:
        """
        Force reload tokens from Secrets Manager
        Useful if tokens were updated externally

        Returns:
            Reloaded token dictionary
        """
        return self._load_tokens()
