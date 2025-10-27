"""
Autotask Service API
Secure backend for Autotask integration - ROC Board Ticket Reporting
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from functools import lru_cache
import requests
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AutotaskConfig(BaseModel):
    """Autotask API Configuration"""
    username: str = Field(..., description="API username (email)")
    secret: str = Field(..., description="API secret/password")
    integration_code: str = Field(..., description="API integration tracking code")
    base_url: Optional[str] = Field(None, description="Zone-specific API URL")

    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        return cls(
            username=os.getenv('AUTOTASK_USERNAME', ''),
            secret=os.getenv('AUTOTASK_SECRET', ''),
            integration_code=os.getenv('AUTOTASK_INTEGRATION_CODE', ''),
            base_url=os.getenv('AUTOTASK_ZONE_URL', '')
        )


class AutotaskClient:
    """Autotask REST API Client"""

    ZONE_INFO_URL = "https://webservices.autotask.net/ATServicesRest/V1.0/zoneInformation"
    API_VERSION = "V1.0"

    # Queue IDs for different boards
    ROC_BOARD_QUEUE_ID = os.getenv('AUTOTASK_ROC_BOARD_ID', None)
    PRO_SERVICES_QUEUE_ID = os.getenv('AUTOTASK_PRO_SERVICES_ID', None)
    TAM_QUEUE_ID = os.getenv('AUTOTASK_TAM_ID', None)
    SALES_QUEUE_ID = os.getenv('AUTOTASK_SALES_ID', None)

    def __init__(self, config: AutotaskConfig):
        self.config = config
        self._session = requests.Session()
        self._base_url = config.base_url

    def _get_headers(self) -> Dict[str, str]:
        """Get API request headers"""
        return {
            'Content-Type': 'application/json',
            'UserName': self.config.username,
            'Secret': self.config.secret,
            'ApiIntegrationcode': self.config.integration_code
        }

    def _get_zone_info(self) -> str:
        """Get zone-specific API URL"""
        if self._base_url:
            return self._base_url

        logger.info("Fetching zone information...")
        response = self._session.get(
            self.ZONE_INFO_URL,
            headers={'UserName': self.config.username, 'Content-Type': 'application/json'},
            timeout=10
        )
        response.raise_for_status()

        data = response.json()
        self._base_url = data.get('url')
        logger.info(f"Zone URL: {self._base_url}")
        return self._base_url

    def _build_url(self, endpoint: str) -> str:
        """Build full API URL"""
        base_url = self._get_zone_info()
        return f"{base_url}/ATServicesRest/{self.API_VERSION}{endpoint}"

    def query(self, endpoint: str, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute a query against Autotask API"""
        url = self._build_url(endpoint)

        logger.debug(f"Querying: {endpoint}")
        logger.debug(f"Filters: {filters}")

        # Ensure body has "filter" field (Autotask API requirement)
        body = filters or {}
        if 'filter' not in body:
            body = {'filter': [], 'MaxRecords': body.get('MaxRecords', 500)}

        response = self._session.post(
            url,
            json=body,
            headers=self._get_headers(),
            timeout=30
        )

        if not response.ok:
            logger.error(f"API Error: {response.status_code} - {response.text}")
            response.raise_for_status()

        data = response.json()
        logger.debug(f"Returned {len(data.get('items', []))} items")
        return data

    def get_roc_board_tickets(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get tickets from ROC (Reactive Services) board only

        Args:
            start_date: Start date for ticket filter (default: 30 days ago)
            end_date: End date for ticket filter (default: now)

        Returns:
            List of ticket dictionaries
        """
        if not self.ROC_BOARD_QUEUE_ID:
            logger.warning("ROC_BOARD_QUEUE_ID not configured, returning all tickets")
            # Fallback: get all tickets if board ID not specified
            return self._get_tickets(start_date, end_date)

        # Default date range: last 30 days
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()

        # Build query filter for ROC board tickets
        filters = {
            "filter": [
                {
                    "field": "queueID",
                    "op": "eq",
                    "value": self.ROC_BOARD_QUEUE_ID
                },
                {
                    "field": "createDate",
                    "op": "gte",
                    "value": start_date.isoformat()
                },
                {
                    "field": "createDate",
                    "op": "lte",
                    "value": end_date.isoformat()
                }
            ]
        }

        result = self.query('/Tickets/query', filters)
        tickets = result.get('items', [])

        logger.info(f"Retrieved {len(tickets)} tickets from ROC board")
        return tickets

    def _get_tickets(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """Get all tickets (fallback when board ID not specified)"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()

        filters = {
            "filter": [
                {
                    "field": "createDate",
                    "op": "gte",
                    "value": start_date.isoformat()
                },
                {
                    "field": "createDate",
                    "op": "lte",
                    "value": end_date.isoformat()
                }
            ]
        }

        result = self.query('/Tickets/query', filters)
        return result.get('items', [])

    def get_ticket_time_entries(self, ticket_ids: List[int]) -> List[Dict]:
        """Get time entries for specific tickets"""
        if not ticket_ids:
            return []

        # Autotask API may have limits on filter array size
        # Batch if needed (typical limit is 500 items)
        filters = {
            "filter": [
                {
                    "field": "ticketID",
                    "op": "in",
                    "value": ticket_ids[:500]  # Limit batch size
                }
            ]
        }

        result = self.query('/TimeEntries/query', filters)
        return result.get('items', [])

    def get_tickets_by_queue(
        self,
        queue_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        only_open: bool = False
    ) -> List[Dict]:
        """
        Get tickets from a specific queue

        Args:
            queue_id: The queue ID to filter by
            start_date: Start date for ticket filter (optional)
            end_date: End date for ticket filter (optional)
            only_open: If True, only return open tickets (status != 5/Complete)

        Returns:
            List of ticket dictionaries
        """
        filters = {
            "filter": [
                {"field": "queueID", "op": "eq", "value": queue_id}
            ]
        }

        # Add date filters if provided
        if start_date:
            filters["filter"].append({
                "field": "createDate",
                "op": "gte",
                "value": start_date.isoformat()
            })

        if end_date:
            filters["filter"].append({
                "field": "createDate",
                "op": "lte",
                "value": end_date.isoformat()
            })

        # Filter for only open tickets (status != 5 which is Complete)
        if only_open:
            filters["filter"].append({
                "field": "status",
                "op": "ne",
                "value": 5
            })

        result = self.query('/Tickets/query', filters)
        return result.get('items', [])

    def get_board_info(self, queue_id: int) -> Optional[Dict]:
        """Get information about a specific board/queue"""
        try:
            result = self.query(f'/TicketCategories/{queue_id}')
            return result.get('item')
        except Exception as e:
            logger.error(f"Failed to get board info: {e}")
            return None


class AutotaskReportingService:
    """Service for generating reports from Autotask data"""

    def __init__(self, client: AutotaskClient):
        self.client = client

    def get_ticket_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get ticket metrics for ROC board

        Returns metrics like:
        - Total tickets
        - Tickets by status
        - Tickets by priority
        - Average resolution time
        - etc.
        """
        tickets = self.client.get_roc_board_tickets(start_date, end_date)

        if not tickets:
            return {
                'total': 0,
                'by_status': {},
                'by_priority': {},
                'avg_resolution_hours': 0,
                'tickets': []
            }

        # Calculate metrics
        by_status = {}
        by_priority = {}
        resolution_times = []

        for ticket in tickets:
            # Count by status
            status = ticket.get('status', 'Unknown')
            by_status[status] = by_status.get(status, 0) + 1

            # Count by priority
            priority = ticket.get('priority', 'Unknown')
            by_priority[priority] = by_priority.get(priority, 0) + 1

            # Calculate resolution time if completed
            if ticket.get('completedDate'):
                create_date = datetime.fromisoformat(ticket['createDate'].replace('Z', '+00:00'))
                completed_date = datetime.fromisoformat(ticket['completedDate'].replace('Z', '+00:00'))
                resolution_hours = (completed_date - create_date).total_seconds() / 3600
                resolution_times.append(resolution_hours)

        avg_resolution = sum(resolution_times) / len(resolution_times) if resolution_times else 0

        return {
            'total': len(tickets),
            'by_status': by_status,
            'by_priority': by_priority,
            'avg_resolution_hours': round(avg_resolution, 2),
            'tickets': [
                {
                    'id': t.get('id'),
                    'ticketNumber': t.get('ticketNumber'),
                    'title': t.get('title'),
                    'status': t.get('status'),
                    'priority': t.get('priority'),
                    'createDate': t.get('createDate'),
                    'completedDate': t.get('completedDate'),
                    'companyID': t.get('companyID'),
                }
                for t in tickets
            ]
        }

    def get_activity_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get summary of ticket activity"""
        tickets = self.client.get_roc_board_tickets(start_date, end_date)

        # Get time entries for these tickets
        ticket_ids = [t['id'] for t in tickets if 'id' in t]
        time_entries = self.client.get_ticket_time_entries(ticket_ids)

        total_hours = sum(te.get('hoursWorked', 0) for te in time_entries)

        return {
            'total_tickets': len(tickets),
            'total_time_entries': len(time_entries),
            'total_hours_logged': round(total_hours, 2),
            'avg_hours_per_ticket': round(total_hours / len(tickets), 2) if tickets else 0
        }

    def get_roc_tickets_for_period(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """
        Get ROC board tickets for a specific time period

        Args:
            start_date: Start of period
            end_date: End of period

        Returns:
            List of ticket dictionaries
        """
        return self.client.get_roc_board_tickets(start_date, end_date)


@lru_cache()
def get_autotask_client() -> AutotaskClient:
    """Get cached Autotask client instance"""
    config = AutotaskConfig.from_env()

    if not config.username or not config.secret or not config.integration_code:
        raise ValueError("Autotask credentials not configured in environment variables")

    return AutotaskClient(config)


def get_reporting_service() -> AutotaskReportingService:
    """Get reporting service instance"""
    client = get_autotask_client()
    return AutotaskReportingService(client)
