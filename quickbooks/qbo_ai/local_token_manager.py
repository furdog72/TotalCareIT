"""
Local Token Manager for QuickBooks Online OAuth
Handles token lifecycle for local development with automatic refresh
"""

import os
import json
from typing import Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes


class LocalTokenManager:
    """
    Manages QuickBooks OAuth tokens locally with automatic refresh
    """

    def __init__(self, token_file: str = ".qbo_tokens"):
        """
        Initialize LocalTokenManager

        Args:
            token_file: Path to the token file
        """
        self.token_file = Path(token_file)
        self.tokens: Optional[Dict] = None
        self.auth_client: Optional[AuthClient] = None
        self.last_refresh: Optional[datetime] = None

        # Load tokens on initialization
        if self.tokens_exist():
            self._load_tokens()

    def _load_tokens(self) -> Dict:
        """
        Load tokens from local file

        Returns:
            Dictionary containing token data
        """
        tokens = {}

        if self.token_file.exists():
            # Read token file
            with open(self.token_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        tokens[key.lower()] = value

            # Map to expected keys
            self.tokens = {
                'access_token': tokens.get('access_token', ''),
                'refresh_token': tokens.get('refresh_token', ''),
                'realm_id': tokens.get('realm_id', ''),
                'client_id': os.getenv('QBO_CLIENT_ID'),
                'client_secret': os.getenv('QBO_CLIENT_SECRET'),
                'redirect_uri': os.getenv('QBO_REDIRECT_URI', 'http://localhost:8000/callback'),
                'environment': os.getenv('QBO_ENVIRONMENT', 'sandbox')  # Default to sandbox for local dev
            }

            self.last_refresh = datetime.now()
            return self.tokens
        else:
            raise RuntimeError(f"Token file {self.token_file} not found")

    def _save_tokens(self) -> None:
        """
        Save updated tokens to local file
        """
        if not self.tokens:
            return

        # Write tokens to file
        with open(self.token_file, 'w') as f:
            f.write(f"ACCESS_TOKEN={self.tokens.get('access_token', '')}\n")
            f.write(f"REFRESH_TOKEN={self.tokens.get('refresh_token', '')}\n")
            f.write(f"REALM_ID={self.tokens.get('realm_id', '')}\n")

    def tokens_exist(self) -> bool:
        """
        Check if tokens file exists

        Returns:
            True if tokens file exists, False otherwise
        """
        return self.token_file.exists()

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
            print("Refreshing QuickBooks tokens...")

            # Initialize auth client if needed
            if not self.auth_client:
                self.auth_client = self._initialize_auth_client()

            # Refresh the token
            self.auth_client.refresh()

            # Update our token storage
            self.tokens["access_token"] = self.auth_client.access_token
            self.tokens["refresh_token"] = self.auth_client.refresh_token
            self.last_refresh = datetime.now()

            # Save updated tokens to file
            self._save_tokens()

            print("Tokens refreshed successfully")
            return self.tokens

        except Exception as e:
            raise RuntimeError(f"Failed to refresh tokens: {str(e)}")

    def get_valid_tokens(self) -> Dict:
        """
        Get valid tokens, refreshing if necessary

        Returns:
            Dictionary containing valid tokens
        """
        # Load tokens if not already loaded
        if not self.tokens:
            self._load_tokens()

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