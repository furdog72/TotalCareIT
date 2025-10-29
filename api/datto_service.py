"""
Datto API Integration
Supports both Datto Commerce (Portal) and Datto RMM APIs
"""

import os
import requests
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class DattoCommerceClient:
    """
    Datto Commerce API Client (formerly Autotask PSA Quotes/Opportunities)
    API Docs: https://portal.datto.com/api-docs
    """

    def __init__(
        self,
        api_key: str = None,
        api_secret: str = None,
        base_url: str = None
    ):
        self.api_key = api_key or os.getenv('DATTO_COMMERCE_API_KEY')
        self.api_secret = api_secret or os.getenv('DATTO_COMMERCE_API_SECRET')
        self.base_url = base_url or os.getenv(
            'DATTO_COMMERCE_BASE_URL',
            'https://api.datto.com/v1'
        )

        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

    def is_configured(self) -> bool:
        """Check if Datto Commerce is configured"""
        return bool(self.api_key and self.api_secret)

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Dict = None,
        data: Dict = None
    ) -> Dict:
        """Make API request with error handling"""
        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise Exception(f"Datto Commerce API error: {str(e)}")

    def get_opportunities(self, status: str = 'open') -> Dict:
        """
        Get sales opportunities from Datto Commerce

        Args:
            status: 'open', 'won', 'lost', or 'all'

        Returns:
            Dictionary with opportunities data
        """
        params = {}
        if status != 'all':
            params['status'] = status

        return self._make_request('GET', '/opportunities', params=params)

    def get_quotes(self, status: str = 'active') -> Dict:
        """
        Get quotes from Datto Commerce

        Args:
            status: 'active', 'approved', 'expired', or 'all'

        Returns:
            Dictionary with quotes data
        """
        params = {}
        if status != 'all':
            params['status'] = status

        return self._make_request('GET', '/quotes', params=params)

    def get_products(self) -> Dict:
        """Get product catalog from Datto Commerce"""
        return self._make_request('GET', '/products')

    def get_customers(self) -> Dict:
        """Get customers from Datto Commerce"""
        return self._make_request('GET', '/customers')


class DattoRMMClient:
    """
    Datto RMM API Client (formerly Autotask Endpoint Management)
    API Docs: https://rmm.datto.com/help/api
    """

    def __init__(
        self,
        api_key: str = None,
        api_secret: str = None,
        region: str = None
    ):
        self.api_key = api_key or os.getenv('DATTO_RMM_API_KEY')
        self.api_secret = api_secret or os.getenv('DATTO_RMM_API_SECRET')
        self.region = region or os.getenv('DATTO_RMM_REGION', 'us')

        # Region-specific base URLs
        region_urls = {
            'us': 'https://pinotage-api.centrastage.net',
            'eu': 'https://merlot-api.centrastage.net',
            'ap': 'https://concord-api.centrastage.net'
        }
        self.base_url = region_urls.get(self.region, region_urls['us'])

        self.access_token = None
        self.token_expires = None

    def is_configured(self) -> bool:
        """Check if Datto RMM is configured"""
        return bool(self.api_key and self.api_secret)

    def _authenticate(self):
        """Authenticate and get access token"""
        if self.access_token and self.token_expires:
            if datetime.now() < self.token_expires:
                return  # Token still valid

        url = f"{self.base_url}/auth/oauth/token"
        data = {
            'grant_type': 'password',
            'username': self.api_key,
            'password': self.api_secret
        }

        try:
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            result = response.json()

            self.access_token = result.get('access_token')
            expires_in = result.get('expires_in', 3600)
            self.token_expires = datetime.now() + timedelta(seconds=expires_in)

        except requests.exceptions.RequestException as e:
            raise Exception(f"Datto RMM authentication error: {str(e)}")

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
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
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
            raise Exception(f"Datto RMM API error: {str(e)}")

    def get_devices(self, site_id: str = None) -> Dict:
        """
        Get devices/endpoints from Datto RMM

        Args:
            site_id: Optional site ID to filter devices

        Returns:
            Dictionary with devices data
        """
        endpoint = '/api/v2/account/devices'
        params = {}
        if site_id:
            params['siteUid'] = site_id

        return self._make_request('GET', endpoint, params=params)

    def get_alerts(self, resolved: bool = False) -> Dict:
        """
        Get alerts from Datto RMM

        Args:
            resolved: Include resolved alerts

        Returns:
            Dictionary with alerts data
        """
        endpoint = '/api/v2/account/alerts'
        params = {'resolved': str(resolved).lower()}

        return self._make_request('GET', endpoint, params=params)

    def get_sites(self) -> Dict:
        """Get all sites/customers from Datto RMM"""
        endpoint = '/api/v2/account/sites'
        return self._make_request('GET', endpoint)

    def get_components(self, device_id: str) -> Dict:
        """
        Get components for a specific device

        Args:
            device_id: Device UID

        Returns:
            Dictionary with component data
        """
        endpoint = f'/api/v2/account/devices/{device_id}/components'
        return self._make_request('GET', endpoint)

    def get_audit_events(self, start_date: datetime = None, end_date: datetime = None) -> Dict:
        """
        Get audit events from Datto RMM

        Args:
            start_date: Start date for audit events
            end_date: End date for audit events

        Returns:
            Dictionary with audit events
        """
        endpoint = '/api/v2/audit/event'
        params = {}

        if start_date:
            params['startDate'] = start_date.isoformat()
        if end_date:
            params['endDate'] = end_date.isoformat()

        return self._make_request('GET', endpoint, params=params)


class DattoReportingService:
    """Service for generating reports from Datto data"""

    def __init__(
        self,
        commerce_client: DattoCommerceClient = None,
        rmm_client: DattoRMMClient = None
    ):
        self.commerce = commerce_client or DattoCommerceClient()
        self.rmm = rmm_client or DattoRMMClient()

    def get_sales_summary(self) -> Dict:
        """Get sales summary from Datto Commerce"""
        if not self.commerce.is_configured():
            return {"error": "Datto Commerce not configured"}

        try:
            opportunities = self.commerce.get_opportunities(status='all')
            quotes = self.commerce.get_quotes(status='all')

            return {
                'opportunities': {
                    'total': len(opportunities.get('items', [])),
                    'open': len([o for o in opportunities.get('items', []) if o.get('status') == 'open']),
                    'won': len([o for o in opportunities.get('items', []) if o.get('status') == 'won']),
                    'lost': len([o for o in opportunities.get('items', []) if o.get('status') == 'lost'])
                },
                'quotes': {
                    'total': len(quotes.get('items', [])),
                    'active': len([q for q in quotes.get('items', []) if q.get('status') == 'active']),
                    'approved': len([q for q in quotes.get('items', []) if q.get('status') == 'approved'])
                },
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e)}

    def get_rmm_summary(self) -> Dict:
        """Get RMM summary from Datto RMM"""
        if not self.rmm.is_configured():
            return {"error": "Datto RMM not configured"}

        try:
            devices = self.rmm.get_devices()
            alerts = self.rmm.get_alerts(resolved=False)
            sites = self.rmm.get_sites()

            return {
                'devices': {
                    'total': len(devices.get('devices', [])),
                    'online': len([d for d in devices.get('devices', []) if d.get('online')]),
                    'offline': len([d for d in devices.get('devices', []) if not d.get('online')])
                },
                'alerts': {
                    'total': len(alerts.get('alerts', [])),
                    'critical': len([a for a in alerts.get('alerts', []) if a.get('priority') == 'critical']),
                    'warning': len([a for a in alerts.get('alerts', []) if a.get('priority') == 'warning'])
                },
                'sites': {
                    'total': len(sites.get('sites', []))
                },
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e)}


# Dependency injection for FastAPI
def get_datto_commerce_client() -> DattoCommerceClient:
    """Get Datto Commerce client instance"""
    return DattoCommerceClient()


def get_datto_rmm_client() -> DattoRMMClient:
    """Get Datto RMM client instance"""
    return DattoRMMClient()


def get_datto_reporting_service() -> DattoReportingService:
    """Get Datto reporting service instance"""
    return DattoReportingService()
