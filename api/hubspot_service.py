"""
HubSpot API Service
Provides access to HubSpot CRM data for sales reporting
"""
import os
import logging
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import requests
from functools import lru_cache

logger = logging.getLogger(__name__)


class HubSpotClient:
    """Client for HubSpot API integration"""

    def __init__(self, access_token: str = None):
        """
        Initialize HubSpot client

        Args:
            access_token: HubSpot private app access token or OAuth token
        """
        self.access_token = access_token or os.getenv('HUBSPOT_ACCESS_TOKEN')
        self.base_url = 'https://api.hubapi.com'
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        if not self.access_token:
            logger.warning("HubSpot access token not configured")

    def is_configured(self) -> bool:
        """Check if HubSpot client is properly configured"""
        return bool(self.access_token)

    def _make_request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None) -> Dict:
        """
        Make HTTP request to HubSpot API

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            data: Request body data

        Returns:
            Response data as dictionary
        """
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
            logger.error(f"HubSpot API request failed: {e}")
            raise

    # ===== CONTACTS API =====

    def get_contacts(self, limit: int = 100, properties: List[str] = None) -> Dict:
        """
        Get contacts from HubSpot CRM

        Args:
            limit: Maximum number of contacts to return
            properties: List of contact properties to include

        Returns:
            Dictionary with contacts data
        """
        endpoint = '/crm/v3/objects/contacts'
        params = {
            'limit': limit,
            'properties': ','.join(properties) if properties else 'firstname,lastname,email,phone,createdate'
        }

        return self._make_request('GET', endpoint, params=params)

    def get_recent_contacts(self, days: int = 30) -> Dict:
        """
        Get recently created contacts

        Args:
            days: Number of days to look back

        Returns:
            Dictionary with recent contacts
        """
        since_date = (datetime.now() - timedelta(days=days)).timestamp() * 1000
        endpoint = '/crm/v3/objects/contacts'
        params = {
            'limit': 100,
            'properties': 'firstname,lastname,email,createdate',
            'createdSince': int(since_date)
        }

        return self._make_request('GET', endpoint, params=params)

    # ===== DEALS API =====

    def get_deals(self, limit: int = 100) -> Dict:
        """
        Get deals from HubSpot CRM

        Args:
            limit: Maximum number of deals to return

        Returns:
            Dictionary with deals data
        """
        endpoint = '/crm/v3/objects/deals'
        params = {
            'limit': limit,
            'properties': 'dealname,amount,closedate,dealstage,pipeline,createdate'
        }

        return self._make_request('GET', endpoint, params=params)

    def get_deals_by_pipeline(self, pipeline_id: str = None) -> Dict:
        """
        Get deals filtered by pipeline

        Args:
            pipeline_id: HubSpot pipeline ID

        Returns:
            Dictionary with filtered deals
        """
        deals = self.get_deals(limit=500)

        if pipeline_id:
            filtered_results = [
                d for d in deals.get('results', [])
                if d.get('properties', {}).get('pipeline') == pipeline_id
            ]
            deals['results'] = filtered_results

        return deals

    # ===== CALLS & MEETINGS API =====

    def get_calls(self, limit: int = 100, start_date: datetime = None) -> Dict:
        """
        Get call activities from HubSpot

        Args:
            limit: Maximum number of calls to return
            start_date: Filter calls from this date onwards

        Returns:
            Dictionary with calls data
        """
        endpoint = '/crm/v3/objects/calls'
        params = {
            'limit': limit,
            'properties': 'hs_call_title,hs_call_body,hs_call_duration,hs_call_from_number,hs_call_to_number,hs_call_status,hs_timestamp'
        }

        return self._make_request('GET', endpoint, params=params)

    def get_meetings(self, limit: int = 100) -> Dict:
        """
        Get meeting activities from HubSpot

        Args:
            limit: Maximum number of meetings to return

        Returns:
            Dictionary with meetings data
        """
        endpoint = '/crm/v3/objects/meetings'
        params = {
            'limit': limit,
            'properties': 'hs_meeting_title,hs_meeting_body,hs_meeting_start_time,hs_meeting_end_time,hs_meeting_outcome'
        }

        return self._make_request('GET', endpoint, params=params)

    # ===== ANALYTICS API =====

    def get_crm_summary(self) -> Dict:
        """
        Get CRM summary statistics

        Returns:
            Dictionary with summary stats
        """
        try:
            # Get counts for different object types
            contacts = self.get_contacts(limit=1)
            deals = self.get_deals(limit=1)

            # Count recent activities
            recent_contacts = self.get_recent_contacts(days=30)

            return {
                'total_contacts': contacts.get('total', 0),
                'total_deals': deals.get('total', 0),
                'new_contacts_30_days': len(recent_contacts.get('results', [])),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get CRM summary: {e}")
            return {
                'error': str(e),
                'total_contacts': 0,
                'total_deals': 0,
                'new_contacts_30_days': 0
            }


class HubSpotReportingService:
    """Service for generating reports from HubSpot data"""

    def __init__(self, client: HubSpotClient):
        self.client = client

    def get_crm_summary(self) -> Dict:
        """
        Get CRM summary statistics

        Returns:
            Dictionary with CRM summary
        """
        return self.client.get_crm_summary()

    def get_recent_contacts(self, limit: int = 10) -> Dict:
        """
        Get recently created contacts

        Args:
            limit: Number of contacts to return

        Returns:
            Dictionary with recent contacts
        """
        return self.client.get_recent_contacts(days=30)

    def get_deal_pipeline(self) -> Dict:
        """
        Get sales pipeline report

        Returns:
            Dictionary with pipeline data
        """
        return self.get_pipeline_report()

    def get_website_analytics(self) -> Dict:
        """
        Get website analytics (placeholder)

        Returns:
            Dictionary with analytics data
        """
        # Note: HubSpot Marketing Hub API required for full analytics
        return {
            'page_views': 0,
            'sessions': 0,
            'note': 'Website analytics require HubSpot Marketing Hub API access'
        }

    def get_form_stats(self) -> Dict:
        """
        Get form submission statistics (placeholder)

        Returns:
            Dictionary with form stats
        """
        # Note: Forms API requires additional scope
        return {
            'forms': [],
            'note': 'Form statistics require additional API scope configuration'
        }

    def get_sales_metrics(self, start_date: datetime = None, end_date: datetime = None) -> Dict:
        """
        Get sales metrics for reporting

        Args:
            start_date: Start date for metrics
            end_date: End date for metrics

        Returns:
            Dictionary with sales metrics
        """
        try:
            # Get calls and meetings data
            calls = self.client.get_calls(limit=500)
            meetings = self.client.get_meetings(limit=500)
            deals = self.client.get_deals(limit=500)
            contacts = self.client.get_recent_contacts(days=30)

            # Calculate metrics
            total_calls = len(calls.get('results', []))
            total_meetings = len(meetings.get('results', []))

            # Count deals by stage
            deal_results = deals.get('results', [])
            prospects = sum(1 for d in deal_results if 'appointmentscheduled' in d.get('properties', {}).get('dealstage', '').lower())
            qualified = sum(1 for d in deal_results if 'qualifiedtobuy' in d.get('properties', {}).get('dealstage', '').lower())
            proposal = sum(1 for d in deal_results if 'presentationscheduled' in d.get('properties', {}).get('dealstage', '').lower())
            closed_won = sum(1 for d in deal_results if 'closedwon' in d.get('properties', {}).get('dealstage', '').lower())

            return {
                'callsMade': total_calls,
                'conversationsHad': total_calls + total_meetings,
                'appointmentsScheduled': total_meetings,
                'outboundCalls': int(total_calls * 0.7),  # Estimate
                'inboundCalls': int(total_calls * 0.3),   # Estimate
                'emailConversations': len(contacts.get('results', [])),
                'meetingConversations': total_meetings,
                'prospects': len(deal_results),
                'contacted': prospects,
                'qualified': qualified,
                'proposal': proposal,
                'closedWon': closed_won,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get sales metrics: {e}")
            return {
                'error': str(e),
                'callsMade': 0,
                'conversationsHad': 0,
                'appointmentsScheduled': 0
            }

    def get_pipeline_report(self) -> Dict:
        """
        Get sales pipeline report

        Returns:
            Dictionary with pipeline metrics
        """
        try:
            deals = self.client.get_deals(limit=500)
            deal_results = deals.get('results', [])

            # Group deals by stage
            pipeline = {}
            for deal in deal_results:
                stage = deal.get('properties', {}).get('dealstage', 'unknown')
                if stage not in pipeline:
                    pipeline[stage] = {
                        'count': 0,
                        'total_value': 0
                    }
                pipeline[stage]['count'] += 1
                amount = float(deal.get('properties', {}).get('amount', 0) or 0)
                pipeline[stage]['total_value'] += amount

            return {
                'pipeline': pipeline,
                'total_deals': len(deal_results),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get pipeline report: {e}")
            return {
                'error': str(e),
                'pipeline': {},
                'total_deals': 0
            }


# Dependency injection functions for FastAPI

@lru_cache()
def get_hubspot_client() -> HubSpotClient:
    """Get or create HubSpot client instance"""
    return HubSpotClient()


def get_hubspot_reporting_service(
    client: HubSpotClient = None
) -> HubSpotReportingService:
    """Get HubSpot reporting service instance"""
    if client is None:
        client = get_hubspot_client()
    return HubSpotReportingService(client)
