"""
QuickBooks Online API Client
"""

import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from quickbooks import QuickBooks

# Load .env from project root
project_root = Path(__file__).parent.parent
load_dotenv(project_root / '.env')


class QBOClient:
    """
    Main client for interacting with QuickBooks Online API
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        environment: Optional[str] = None,
        company_id: Optional[str] = None,
    ):
        """
        Initialize QBO Client

        Args:
            client_id: QuickBooks app client ID
            client_secret: QuickBooks app client secret
            redirect_uri: OAuth redirect URI
            environment: 'sandbox' or 'production'
            company_id: QuickBooks company/realm ID
        """
        self.client_id = client_id or os.getenv("QBO_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("QBO_CLIENT_SECRET")
        self.redirect_uri = redirect_uri or os.getenv("QBO_REDIRECT_URI")
        self.environment = environment or os.getenv("QBO_ENVIRONMENT", "sandbox")
        self.company_id = company_id or os.getenv("QBO_COMPANY_ID")

        self.auth_client = None
        self.qb_client = None

    def get_authorization_url(self) -> str:
        """
        Get the authorization URL for OAuth flow

        Returns:
            Authorization URL string
        """
        self.auth_client = AuthClient(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            environment=self.environment,
        )

        auth_url = self.auth_client.get_authorization_url(
            scopes=[Scopes.ACCOUNTING]
        )

        return auth_url

    def get_bearer_token(self, auth_code: str, realm_id: str) -> dict:
        """
        Exchange authorization code for bearer token

        Args:
            auth_code: Authorization code from OAuth callback
            realm_id: Company ID from OAuth callback

        Returns:
            Token information dictionary
        """
        if not self.auth_client:
            self.auth_client = AuthClient(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                environment=self.environment,
            )

        self.auth_client.get_bearer_token(auth_code, realm_id=realm_id)
        self.company_id = realm_id

        return {
            'access_token': self.auth_client.access_token,
            'refresh_token': self.auth_client.refresh_token,
            'realm_id': realm_id,
        }

    def connect(self, access_token: str, refresh_token: str):
        """
        Connect to QuickBooks with existing tokens

        Args:
            access_token: OAuth access token
            refresh_token: OAuth refresh token
        """
        if not self.company_id:
            raise ValueError("Company ID (realm_id) is required")

        # Initialize auth client if not already done
        if not self.auth_client:
            self.auth_client = AuthClient(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                environment=self.environment,
            )

        # Set the tokens
        self.auth_client.access_token = access_token
        self.auth_client.refresh_token = refresh_token

        self.qb_client = QuickBooks(
            auth_client=self.auth_client,
            refresh_token=refresh_token,
            company_id=self.company_id,
        )

    def query(self, entity: str, where: Optional[str] = None, limit: int = 100) -> list:
        """
        Execute a query against QuickBooks

        Args:
            entity: Entity type (e.g., 'Customer', 'Invoice', 'Account')
            where: Optional WHERE clause
            limit: Maximum number of results

        Returns:
            List of results
        """
        if not self.qb_client:
            raise RuntimeError("Not connected. Call connect() first.")

        query_string = f"SELECT * FROM {entity}"
        if where:
            query_string += f" WHERE {where}"
        query_string += f" MAXRESULTS {limit}"

        results = self.qb_client.query(query_string)
        return results
