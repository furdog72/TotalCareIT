"""
Microsoft 365 API Integration
Provides access to Microsoft Graph API for M365 data
"""

import os
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


class Microsoft365Client:
    """
    Microsoft 365 / Graph API Client
    API Docs: https://learn.microsoft.com/en-us/graph/api/overview
    """

    def __init__(
        self,
        tenant_id: str = None,
        client_id: str = None,
        client_secret: str = None
    ):
        self.tenant_id = tenant_id or os.getenv('M365_TENANT_ID')
        self.client_id = client_id or os.getenv('M365_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('M365_CLIENT_SECRET')

        self.base_url = 'https://graph.microsoft.com/v1.0'
        self.auth_url = f'https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token'

        self.access_token = None
        self.token_expires = None

    def is_configured(self) -> bool:
        """Check if Microsoft 365 is configured"""
        return bool(self.tenant_id and self.client_id and self.client_secret)

    def _authenticate(self):
        """Authenticate and get access token"""
        if self.access_token and self.token_expires:
            if datetime.now() < self.token_expires:
                return  # Token still valid

        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'https://graph.microsoft.com/.default'
        }

        try:
            response = requests.post(self.auth_url, data=data, timeout=30)
            response.raise_for_status()
            result = response.json()

            self.access_token = result.get('access_token')
            expires_in = result.get('expires_in', 3600)
            self.token_expires = datetime.now() + timedelta(seconds=expires_in)

        except requests.exceptions.RequestException as e:
            raise Exception(f"Microsoft 365 authentication error: {str(e)}")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Dict = None,
        data: Dict = None
    ) -> Dict:
        """Make API request with error handling"""
        self._authenticate()

        url = f"{self.base_url}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise Exception(f"Microsoft 365 API error: {str(e)}")

    # ===== USERS =====

    def get_users(self, filter: str = None, top: int = 100) -> Dict:
        """
        Get users from Azure AD / Microsoft 365

        Args:
            filter: OData filter string (e.g., "accountEnabled eq true")
            top: Number of results to return

        Returns:
            Dictionary with user data
        """
        endpoint = '/users'
        params = {'$top': top}

        if filter:
            params['$filter'] = filter

        return self._make_request('GET', endpoint, params=params)

    def get_user_by_id(self, user_id: str) -> Dict:
        """Get a specific user by ID or UPN"""
        endpoint = f'/users/{user_id}'
        return self._make_request('GET', endpoint)

    # ===== GROUPS =====

    def get_groups(self, filter: str = None, top: int = 100) -> Dict:
        """
        Get groups from Azure AD

        Args:
            filter: OData filter string
            top: Number of results to return

        Returns:
            Dictionary with group data
        """
        endpoint = '/groups'
        params = {'$top': top}

        if filter:
            params['$filter'] = filter

        return self._make_request('GET', endpoint, params=params)

    def get_group_members(self, group_id: str) -> Dict:
        """Get members of a specific group"""
        endpoint = f'/groups/{group_id}/members'
        return self._make_request('GET', endpoint)

    # ===== LICENSES =====

    def get_subscribed_skus(self) -> Dict:
        """Get subscribed SKUs (licenses) for the tenant"""
        endpoint = '/subscribedSkus'
        return self._make_request('GET', endpoint)

    def get_user_licenses(self, user_id: str) -> Dict:
        """Get licenses assigned to a specific user"""
        endpoint = f'/users/{user_id}/licenseDetails'
        return self._make_request('GET', endpoint)

    # ===== SHAREPOINT =====

    def get_sharepoint_sites(self, search: str = None) -> Dict:
        """
        Get SharePoint sites

        Args:
            search: Search query for sites

        Returns:
            Dictionary with site data
        """
        if search:
            endpoint = f'/sites?search={search}'
        else:
            endpoint = '/sites'

        return self._make_request('GET', endpoint)

    def get_site_lists(self, site_id: str) -> Dict:
        """Get lists from a SharePoint site"""
        endpoint = f'/sites/{site_id}/lists'
        return self._make_request('GET', endpoint)

    # ===== ONEDRIVE =====

    def get_user_drive(self, user_id: str) -> Dict:
        """Get OneDrive for a user"""
        endpoint = f'/users/{user_id}/drive'
        return self._make_request('GET', endpoint)

    def get_drive_items(self, user_id: str, folder_path: str = 'root') -> Dict:
        """
        Get items from a user's OneDrive

        Args:
            user_id: User ID or UPN
            folder_path: Path to folder (default: 'root')

        Returns:
            Dictionary with drive items
        """
        endpoint = f'/users/{user_id}/drive/root:/{folder_path}:/children'
        return self._make_request('GET', endpoint)

    # ===== TEAMS =====

    def get_teams(self) -> Dict:
        """Get all Microsoft Teams in the organization"""
        endpoint = '/groups?$filter=resourceProvisioningOptions/Any(x:x eq \'Team\')'
        return self._make_request('GET', endpoint)

    def get_team_channels(self, team_id: str) -> Dict:
        """Get channels for a specific team"""
        endpoint = f'/teams/{team_id}/channels'
        return self._make_request('GET', endpoint)

    # ===== MAIL =====

    def get_user_messages(
        self,
        user_id: str,
        folder: str = 'inbox',
        top: int = 50
    ) -> Dict:
        """
        Get messages from a user's mailbox

        Args:
            user_id: User ID or UPN
            folder: Folder name (inbox, sentitems, etc.)
            top: Number of messages to return

        Returns:
            Dictionary with message data
        """
        endpoint = f'/users/{user_id}/mailFolders/{folder}/messages'
        params = {'$top': top}
        return self._make_request('GET', endpoint, params=params)

    # ===== CALENDAR =====

    def get_user_calendar_events(
        self,
        user_id: str,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict:
        """
        Get calendar events for a user

        Args:
            user_id: User ID or UPN
            start_date: Start date for events
            end_date: End date for events

        Returns:
            Dictionary with event data
        """
        endpoint = f'/users/{user_id}/calendar/events'
        params = {}

        if start_date and end_date:
            params['$filter'] = (
                f"start/dateTime ge '{start_date.isoformat()}' and "
                f"end/dateTime le '{end_date.isoformat()}'"
            )

        return self._make_request('GET', endpoint, params=params)

    # ===== REPORTS =====

    def get_office365_active_users(self, period: str = 'D30') -> bytes:
        """
        Get Office 365 active user report

        Args:
            period: Reporting period (D7, D30, D90, D180)

        Returns:
            CSV data as bytes
        """
        endpoint = f'/reports/getOffice365ActiveUserDetail(period=\'{period}\')'

        # Reports API returns CSV, not JSON
        self._authenticate()
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.content

    def get_email_activity_counts(self, period: str = 'D30') -> bytes:
        """
        Get email activity count report

        Args:
            period: Reporting period (D7, D30, D90, D180)

        Returns:
            CSV data as bytes
        """
        endpoint = f'/reports/getEmailActivityCounts(period=\'{period}\')'

        self._authenticate()
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.content


class Microsoft365ReportingService:
    """Service for generating reports from Microsoft 365 data"""

    def __init__(self, client: Microsoft365Client = None):
        self.client = client or Microsoft365Client()

    def get_tenant_summary(self) -> Dict:
        """Get tenant summary with users, groups, and licenses"""
        if not self.client.is_configured():
            return {"error": "Microsoft 365 not configured"}

        try:
            users = self.client.get_users()
            groups = self.client.get_groups()
            licenses = self.client.get_subscribed_skus()

            # Count active users
            active_users = len([
                u for u in users.get('value', [])
                if u.get('accountEnabled')
            ])

            # Calculate license usage
            total_licenses = 0
            assigned_licenses = 0
            for sku in licenses.get('value', []):
                enabled = sku.get('prepaidUnits', {}).get('enabled', 0)
                consumed = sku.get('consumedUnits', 0)
                total_licenses += enabled
                assigned_licenses += consumed

            return {
                'users': {
                    'total': len(users.get('value', [])),
                    'active': active_users
                },
                'groups': {
                    'total': len(groups.get('value', []))
                },
                'licenses': {
                    'total': total_licenses,
                    'assigned': assigned_licenses,
                    'available': total_licenses - assigned_licenses
                },
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e)}

    def get_license_details(self) -> Dict:
        """Get detailed license information"""
        if not self.client.is_configured():
            return {"error": "Microsoft 365 not configured"}

        try:
            licenses = self.client.get_subscribed_skus()

            license_details = []
            for sku in licenses.get('value', []):
                sku_part_number = sku.get('skuPartNumber')
                enabled = sku.get('prepaidUnits', {}).get('enabled', 0)
                consumed = sku.get('consumedUnits', 0)

                license_details.append({
                    'name': sku_part_number,
                    'total': enabled,
                    'assigned': consumed,
                    'available': enabled - consumed
                })

            return {
                'licenses': license_details,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e)}


# Dependency injection for FastAPI
def get_microsoft365_client() -> Microsoft365Client:
    """Get Microsoft 365 client instance"""
    return Microsoft365Client()


def get_microsoft365_reporting_service() -> Microsoft365ReportingService:
    """Get Microsoft 365 reporting service instance"""
    return Microsoft365ReportingService()
