"""
ConnectWise Manage API Integration
Replaces and expands on connectwise_cpq.py
"""

import os
import requests
import base64
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


class ConnectWiseManageClient:
    """
    ConnectWise Manage API Client
    API Docs: https://developer.connectwise.com/Products/Manage/REST
    """

    def __init__(
        self,
        company_id: str = None,
        public_key: str = None,
        private_key: str = None,
        client_id: str = None,
        base_url: str = None
    ):
        self.company_id = company_id or os.getenv('CONNECTWISE_COMPANY_ID')
        self.public_key = public_key or os.getenv('CONNECTWISE_PUBLIC_KEY')
        self.private_key = private_key or os.getenv('CONNECTWISE_PRIVATE_KEY')
        self.client_id = client_id or os.getenv('CONNECTWISE_CLIENT_ID')

        # Base URL - typically https://api-na.myconnectwise.net for North America
        self.base_url = base_url or os.getenv(
            'CONNECTWISE_BASE_URL',
            'https://api-na.myconnectwise.net'
        )

        # Create authorization header
        auth_string = f"{self.company_id}+{self.public_key}:{self.private_key}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')

        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {auth_b64}',
            'clientId': self.client_id
        }

    def is_configured(self) -> bool:
        """Check if ConnectWise is configured"""
        return bool(
            self.company_id and
            self.public_key and
            self.private_key and
            self.client_id
        )

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
            raise Exception(f"ConnectWise API error: {str(e)}")

    # ===== SERVICE TICKETS =====

    def get_tickets(
        self,
        status: str = None,
        board_id: int = None,
        company_id: int = None,
        page: int = 1,
        page_size: int = 100
    ) -> List[Dict]:
        """
        Get service tickets

        Args:
            status: Filter by status (e.g., 'Open', 'Closed')
            board_id: Filter by service board ID
            company_id: Filter by company ID
            page: Page number
            page_size: Items per page

        Returns:
            List of ticket dictionaries
        """
        endpoint = '/v4_6_release/apis/3.0/service/tickets'
        params = {
            'page': page,
            'pageSize': page_size
        }

        # Build conditions string for filtering
        conditions = []
        if status:
            conditions.append(f"status/name='{status}'")
        if board_id:
            conditions.append(f"board/id={board_id}")
        if company_id:
            conditions.append(f"company/id={company_id}")

        if conditions:
            params['conditions'] = ' AND '.join(conditions)

        return self._make_request('GET', endpoint, params=params)

    def get_ticket_by_id(self, ticket_id: int) -> Dict:
        """Get a specific ticket by ID"""
        endpoint = f'/v4_6_release/apis/3.0/service/tickets/{ticket_id}'
        return self._make_request('GET', endpoint)

    # ===== COMPANIES =====

    def get_companies(
        self,
        page: int = 1,
        page_size: int = 100
    ) -> List[Dict]:
        """
        Get companies/customers

        Args:
            page: Page number
            page_size: Items per page

        Returns:
            List of company dictionaries
        """
        endpoint = '/v4_6_release/apis/3.0/company/companies'
        params = {
            'page': page,
            'pageSize': page_size
        }
        return self._make_request('GET', endpoint, params=params)

    def get_company_by_id(self, company_id: int) -> Dict:
        """Get a specific company by ID"""
        endpoint = f'/v4_6_release/apis/3.0/company/companies/{company_id}'
        return self._make_request('GET', endpoint)

    # ===== OPPORTUNITIES =====

    def get_opportunities(
        self,
        status: str = None,
        probability: int = None,
        page: int = 1,
        page_size: int = 100
    ) -> List[Dict]:
        """
        Get sales opportunities

        Args:
            status: Filter by status (e.g., 'Open', 'Won', 'Lost')
            probability: Filter by probability percentage
            page: Page number
            page_size: Items per page

        Returns:
            List of opportunity dictionaries
        """
        endpoint = '/v4_6_release/apis/3.0/sales/opportunities'
        params = {
            'page': page,
            'pageSize': page_size
        }

        conditions = []
        if status:
            conditions.append(f"status/name='{status}'")
        if probability is not None:
            conditions.append(f"probability>={probability}")

        if conditions:
            params['conditions'] = ' AND '.join(conditions)

        return self._make_request('GET', endpoint, params=params)

    def get_opportunity_by_id(self, opportunity_id: int) -> Dict:
        """Get a specific opportunity by ID"""
        endpoint = f'/v4_6_release/apis/3.0/sales/opportunities/{opportunity_id}'
        return self._make_request('GET', endpoint)

    # ===== AGREEMENTS (RECURRING SERVICES) =====

    def get_agreements(
        self,
        company_id: int = None,
        page: int = 1,
        page_size: int = 100
    ) -> List[Dict]:
        """
        Get agreements/contracts

        Args:
            company_id: Filter by company ID
            page: Page number
            page_size: Items per page

        Returns:
            List of agreement dictionaries
        """
        endpoint = '/v4_6_release/apis/3.0/finance/agreements'
        params = {
            'page': page,
            'pageSize': page_size
        }

        if company_id:
            params['conditions'] = f"company/id={company_id}"

        return self._make_request('GET', endpoint, params=params)

    # ===== TIME ENTRIES =====

    def get_time_entries(
        self,
        start_date: datetime = None,
        end_date: datetime = None,
        page: int = 1,
        page_size: int = 100
    ) -> List[Dict]:
        """
        Get time entries

        Args:
            start_date: Filter by start date
            end_date: Filter by end date
            page: Page number
            page_size: Items per page

        Returns:
            List of time entry dictionaries
        """
        endpoint = '/v4_6_release/apis/3.0/time/entries'
        params = {
            'page': page,
            'pageSize': page_size
        }

        conditions = []
        if start_date:
            conditions.append(f"timeStart>=[{start_date.isoformat()}]")
        if end_date:
            conditions.append(f"timeEnd<=[{end_date.isoformat()}]")

        if conditions:
            params['conditions'] = ' AND '.join(conditions)

        return self._make_request('GET', endpoint, params=params)

    # ===== PRODUCTS =====

    def get_products(
        self,
        page: int = 1,
        page_size: int = 100
    ) -> List[Dict]:
        """
        Get products from catalog

        Args:
            page: Page number
            page_size: Items per page

        Returns:
            List of product dictionaries
        """
        endpoint = '/v4_6_release/apis/3.0/procurement/products'
        params = {
            'page': page,
            'pageSize': page_size
        }
        return self._make_request('GET', endpoint, params=params)

    # ===== ACTIVITIES =====

    def get_activities(
        self,
        start_date: datetime = None,
        end_date: datetime = None,
        page: int = 1,
        page_size: int = 100
    ) -> List[Dict]:
        """
        Get sales activities

        Args:
            start_date: Filter by start date
            end_date: Filter by end date
            page: Page number
            page_size: Items per page

        Returns:
            List of activity dictionaries
        """
        endpoint = '/v4_6_release/apis/3.0/sales/activities'
        params = {
            'page': page,
            'pageSize': page_size
        }

        conditions = []
        if start_date:
            conditions.append(f"dateStart>=[{start_date.isoformat()}]")
        if end_date:
            conditions.append(f"dateEnd<=[{end_date.isoformat()}]")

        if conditions:
            params['conditions'] = ' AND '.join(conditions)

        return self._make_request('GET', endpoint, params=params)


class ConnectWiseReportingService:
    """Service for generating reports from ConnectWise data"""

    def __init__(self, client: ConnectWiseManageClient = None):
        self.client = client or ConnectWiseManageClient()

    def get_sales_summary(self) -> Dict:
        """Get sales summary from ConnectWise"""
        if not self.client.is_configured():
            return {"error": "ConnectWise not configured"}

        try:
            # Get opportunities
            open_opps = self.client.get_opportunities(status='Open', page_size=1000)
            won_opps = self.client.get_opportunities(status='Won', page_size=1000)
            lost_opps = self.client.get_opportunities(status='Lost', page_size=1000)

            # Calculate totals
            open_value = sum(opp.get('expectedRevenue', 0) for opp in open_opps)
            won_value = sum(opp.get('expectedRevenue', 0) for opp in won_opps)

            return {
                'opportunities': {
                    'open': {
                        'count': len(open_opps),
                        'value': open_value
                    },
                    'won': {
                        'count': len(won_opps),
                        'value': won_value
                    },
                    'lost': {
                        'count': len(lost_opps)
                    }
                },
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e)}

    def get_service_summary(self) -> Dict:
        """Get service ticket summary from ConnectWise"""
        if not self.client.is_configured():
            return {"error": "ConnectWise not configured"}

        try:
            # Get tickets
            open_tickets = self.client.get_tickets(status='Open', page_size=1000)
            closed_tickets = self.client.get_tickets(status='Closed', page_size=1000)

            return {
                'tickets': {
                    'open': len(open_tickets),
                    'closed': len(closed_tickets),
                    'total': len(open_tickets) + len(closed_tickets)
                },
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e)}

    def get_time_summary(self, start_date: datetime = None, end_date: datetime = None) -> Dict:
        """Get time entry summary from ConnectWise"""
        if not self.client.is_configured():
            return {"error": "ConnectWise not configured"}

        # Default to current month if no dates provided
        if not start_date:
            start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0)
        if not end_date:
            end_date = datetime.now()

        try:
            time_entries = self.client.get_time_entries(
                start_date=start_date,
                end_date=end_date,
                page_size=1000
            )

            # Calculate total hours
            total_hours = sum(
                entry.get('actualHours', 0) for entry in time_entries
            )

            # Group by type
            billable_hours = sum(
                entry.get('actualHours', 0)
                for entry in time_entries
                if entry.get('billableOption') == 'Billable'
            )

            return {
                'time_entries': {
                    'total_count': len(time_entries),
                    'total_hours': total_hours,
                    'billable_hours': billable_hours,
                    'non_billable_hours': total_hours - billable_hours
                },
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e)}


# Dependency injection for FastAPI
def get_connectwise_client() -> ConnectWiseManageClient:
    """Get ConnectWise client instance"""
    return ConnectWiseManageClient()


def get_connectwise_reporting_service() -> ConnectWiseReportingService:
    """Get ConnectWise reporting service instance"""
    return ConnectWiseReportingService()
