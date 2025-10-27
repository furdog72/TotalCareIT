"""
HubSpot Service API
Backend integration for HubSpot CRM and Analytics
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from functools import lru_cache
import requests
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class HubSpotConfig(BaseModel):
    """HubSpot API Configuration"""
    api_key: str = Field(..., description="Private App Access Token")
    hub_id: str = Field(..., description="HubSpot Hub ID")

    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        return cls(
            api_key=os.getenv('HUBSPOT_API_KEY', ''),
            hub_id=os.getenv('HUBSPOT_HUB_ID', '8752461')
        )


class HubSpotClient:
    """HubSpot REST API Client"""

    BASE_URL = "https://api.hubapi.com"

    def __init__(self, config: HubSpotConfig):
        self.config = config
        self._session = requests.Session()
        self._cache = {}
        self._cache_timeout = 300  # 5 minutes

    def _get_headers(self) -> Dict[str, str]:
        """Get API request headers"""
        return {
            'Authorization': f'Bearer {self.config.api_key}',
            'Content-Type': 'application/json'
        }

    def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached response if still valid"""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if datetime.now().timestamp() - timestamp < self._cache_timeout:
                logger.debug(f"Cache hit: {key}")
                return data
        return None

    def _set_cache(self, key: str, data: Any):
        """Set cached response"""
        self._cache[key] = (data, datetime.now().timestamp())

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Make API request with caching"""
        cache_key = f"{method}:{endpoint}:{str(params)}"

        # Check cache for GET requests
        if method == 'GET' and use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                return cached

        url = f"{self.BASE_URL}{endpoint}"

        logger.debug(f"HubSpot API {method} {endpoint}")

        try:
            response = self._session.request(
                method=method,
                url=url,
                headers=self._get_headers(),
                params=params,
                json=json_data,
                timeout=30
            )

            if not response.ok:
                logger.error(f"HubSpot API Error: {response.status_code} - {response.text}")
                response.raise_for_status()

            data = response.json()

            # Cache successful GET requests
            if method == 'GET' and use_cache:
                self._set_cache(cache_key, data)

            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"HubSpot API request failed: {e}")
            raise

    # ===== CONTACTS API =====

    def get_contacts(
        self,
        limit: int = 100,
        properties: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get contacts from HubSpot CRM"""
        params = {
            'limit': limit
        }

        if properties:
            params['properties'] = ','.join(properties)

        return self._make_request('GET', '/crm/v3/objects/contacts', params=params)

    def search_contacts(
        self,
        filters: List[Dict],
        limit: int = 100
    ) -> Dict[str, Any]:
        """Search contacts with filters"""
        json_data = {
            'filterGroups': [{'filters': filters}],
            'limit': limit
        }

        return self._make_request(
            'POST',
            '/crm/v3/objects/contacts/search',
            json_data=json_data,
            use_cache=False
        )

    # ===== DEALS API =====

    def get_deals(
        self,
        limit: int = 100,
        properties: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get deals from HubSpot CRM"""
        params = {
            'limit': limit
        }

        if properties:
            params['properties'] = ','.join(properties)

        return self._make_request('GET', '/crm/v3/objects/deals', params=params)

    def search_deals(
        self,
        filters: List[Dict],
        limit: int = 100
    ) -> Dict[str, Any]:
        """Search deals with filters"""
        json_data = {
            'filterGroups': [{'filters': filters}],
            'limit': limit
        }

        return self._make_request(
            'POST',
            '/crm/v3/objects/deals/search',
            json_data=json_data,
            use_cache=False
        )

    # ===== COMPANIES API =====

    def get_companies(
        self,
        limit: int = 100,
        properties: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get companies from HubSpot CRM"""
        params = {
            'limit': limit
        }

        if properties:
            params['properties'] = ','.join(properties)

        return self._make_request('GET', '/crm/v3/objects/companies', params=params)

    # ===== ANALYTICS API =====

    def get_analytics_views(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get website analytics page views"""
        # Note: Analytics API requires specific scopes and may have different endpoint
        # This is a placeholder - actual endpoint may vary based on HubSpot plan
        params = {
            'start': int(start_date.timestamp() * 1000),
            'end': int(end_date.timestamp() * 1000)
        }

        try:
            return self._make_request('GET', '/analytics/v2/reports', params=params)
        except Exception as e:
            logger.warning(f"Analytics API not available: {e}")
            return {'results': []}

    # ===== FORMS API =====

    def get_forms(self) -> Dict[str, Any]:
        """Get all forms"""
        return self._make_request('GET', '/marketing/v3/forms')

    def get_form_submissions(
        self,
        form_guid: str,
        after: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Get form submissions"""
        params = {'limit': limit}
        if after:
            params['after'] = after

        return self._make_request(
            'GET',
            f'/form-integrations/v1/submissions/forms/{form_guid}',
            params=params
        )

    # ===== CONVERSATIONS API =====

    def get_conversations(
        self,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get conversations (chat, email, etc)"""
        params = {'limit': limit}

        try:
            return self._make_request('GET', '/conversations/v3/conversations', params=params)
        except Exception as e:
            logger.warning(f"Conversations API not available: {e}")
            return {'results': []}

    # ===== ENGAGEMENTS API (Calls, Meetings, Notes, Tasks) =====

    def search_engagements(
        self,
        engagement_type: str,
        filters: List[Dict],
        limit: int = 100
    ) -> Dict[str, Any]:
        """Search for engagements (calls, meetings, notes, tasks) with filters

        Args:
            engagement_type: Type of engagement ('calls', 'meetings', 'notes', 'tasks', 'emails')
            filters: List of filter dictionaries for search
            limit: Maximum number of results
        """
        json_data = {
            'filterGroups': [{'filters': filters}],
            'limit': limit,
            'sorts': [{'propertyName': 'hs_timestamp', 'direction': 'DESCENDING'}]
        }

        try:
            return self._make_request(
                'POST',
                f'/crm/v3/objects/{engagement_type}/search',
                json_data=json_data,
                use_cache=False
            )
        except Exception as e:
            logger.error(f"Failed to search {engagement_type}: {e}")
            return {'results': [], 'total': 0}

    def get_calls(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        owner_id: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get calls (dials) from HubSpot

        Args:
            start_date: Filter calls after this date
            end_date: Filter calls before this date
            owner_id: Filter by call owner (sales rep ID)
            limit: Maximum results
        """
        filters = []

        if start_date:
            filters.append({
                'propertyName': 'hs_timestamp',
                'operator': 'GTE',
                'value': int(start_date.timestamp() * 1000)
            })

        if end_date:
            filters.append({
                'propertyName': 'hs_timestamp',
                'operator': 'LTE',
                'value': int(end_date.timestamp() * 1000)
            })

        if owner_id:
            filters.append({
                'propertyName': 'hubspot_owner_id',
                'operator': 'EQ',
                'value': owner_id
            })

        return self.search_engagements('calls', filters, limit)

    def get_meetings(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        owner_id: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get meetings (FTAs, appointments) from HubSpot"""
        filters = []

        if start_date:
            filters.append({
                'propertyName': 'hs_timestamp',
                'operator': 'GTE',
                'value': int(start_date.timestamp() * 1000)
            })

        if end_date:
            filters.append({
                'propertyName': 'hs_timestamp',
                'operator': 'LTE',
                'value': int(end_date.timestamp() * 1000)
            })

        if owner_id:
            filters.append({
                'propertyName': 'hubspot_owner_id',
                'operator': 'EQ',
                'value': owner_id
            })

        return self.search_engagements('meetings', filters, limit)

    def get_notes(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        owner_id: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get notes from HubSpot (can track conversations with decision makers)"""
        filters = []

        if start_date:
            filters.append({
                'propertyName': 'hs_timestamp',
                'operator': 'GTE',
                'value': int(start_date.timestamp() * 1000)
            })

        if end_date:
            filters.append({
                'propertyName': 'hs_timestamp',
                'operator': 'LTE',
                'value': int(end_date.timestamp() * 1000)
            })

        if owner_id:
            filters.append({
                'propertyName': 'hubspot_owner_id',
                'operator': 'EQ',
                'value': owner_id
            })

        return self.search_engagements('notes', filters, limit)

    def get_owners(self) -> Dict[str, Any]:
        """Get list of HubSpot owners (users/sales reps)"""
        try:
            return self._make_request('GET', '/crm/v3/owners')
        except Exception as e:
            logger.error(f"Failed to get owners: {e}")
            return {'results': []}


class HubSpotReportingService:
    """Service for generating reports from HubSpot data"""

    def __init__(self, client: HubSpotClient):
        self.client = client

    def get_crm_summary(self) -> Dict[str, Any]:
        """Get CRM summary statistics"""
        logger.info("📊 Getting HubSpot CRM summary...")

        try:
            # Get contacts
            contacts_response = self.client.get_contacts(limit=1)
            total_contacts = contacts_response.get('total', 0)

            # Get deals
            deals_response = self.client.get_deals(
                limit=100,
                properties=['dealname', 'amount', 'dealstage', 'closedate']
            )
            deals = deals_response.get('results', [])

            # Calculate deal metrics
            total_deals = len(deals)
            total_deal_value = sum(
                float(deal.get('properties', {}).get('amount', 0) or 0)
                for deal in deals
            )

            # Count by stage
            deals_by_stage = {}
            for deal in deals:
                stage = deal.get('properties', {}).get('dealstage', 'unknown')
                deals_by_stage[stage] = deals_by_stage.get(stage, 0) + 1

            # Get companies
            companies_response = self.client.get_companies(limit=1)
            total_companies = companies_response.get('total', 0)

            return {
                'contacts': {
                    'total': total_contacts
                },
                'deals': {
                    'total': total_deals,
                    'total_value': round(total_deal_value, 2),
                    'by_stage': deals_by_stage
                },
                'companies': {
                    'total': total_companies
                }
            }

        except Exception as e:
            logger.error(f"Failed to get CRM summary: {e}")
            return {
                'contacts': {'total': 0},
                'deals': {'total': 0, 'total_value': 0, 'by_stage': {}},
                'companies': {'total': 0},
                'error': str(e)
            }

    def get_recent_contacts(self, limit: int = 10) -> List[Dict]:
        """Get recently created contacts"""
        try:
            # Search for contacts created in last 30 days
            thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

            filters = [{
                'propertyName': 'createdate',
                'operator': 'GTE',
                'value': thirty_days_ago
            }]

            response = self.client.search_contacts(filters, limit=limit)
            contacts = response.get('results', [])

            return [
                {
                    'id': contact.get('id'),
                    'email': contact.get('properties', {}).get('email'),
                    'firstname': contact.get('properties', {}).get('firstname'),
                    'lastname': contact.get('properties', {}).get('lastname'),
                    'createdate': contact.get('properties', {}).get('createdate'),
                    'company': contact.get('properties', {}).get('company')
                }
                for contact in contacts
            ]

        except Exception as e:
            logger.error(f"Failed to get recent contacts: {e}")
            return []

    def get_deal_pipeline(self) -> Dict[str, Any]:
        """Get sales pipeline overview"""
        try:
            deals_response = self.client.get_deals(
                limit=500,
                properties=['dealname', 'amount', 'dealstage', 'closedate', 'pipeline']
            )
            deals = deals_response.get('results', [])

            # Calculate pipeline metrics
            pipeline_value = 0
            closed_won_value = 0
            deals_by_stage = {}

            for deal in deals:
                props = deal.get('properties', {})
                amount = float(props.get('amount', 0) or 0)
                stage = props.get('dealstage', 'unknown')

                deals_by_stage[stage] = {
                    'count': deals_by_stage.get(stage, {}).get('count', 0) + 1,
                    'value': deals_by_stage.get(stage, {}).get('value', 0) + amount
                }

                if 'closedwon' in stage.lower():
                    closed_won_value += amount
                else:
                    pipeline_value += amount

            return {
                'total_deals': len(deals),
                'pipeline_value': round(pipeline_value, 2),
                'closed_won_value': round(closed_won_value, 2),
                'by_stage': deals_by_stage
            }

        except Exception as e:
            logger.error(f"Failed to get deal pipeline: {e}")
            return {
                'total_deals': 0,
                'pipeline_value': 0,
                'closed_won_value': 0,
                'by_stage': {},
                'error': str(e)
            }

    def get_website_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get website analytics summary"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()

        try:
            analytics = self.client.get_analytics_views(start_date, end_date)

            return {
                'page_views': analytics.get('total_page_views', 0),
                'sessions': analytics.get('total_sessions', 0),
                'new_contacts': analytics.get('total_new_contacts', 0),
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }

        except Exception as e:
            logger.warning(f"Analytics not available: {e}")
            return {
                'page_views': 0,
                'sessions': 0,
                'new_contacts': 0,
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'note': 'Analytics data requires HubSpot Marketing Hub'
            }

    def get_form_stats(self) -> Dict[str, Any]:
        """Get form submission statistics"""
        try:
            forms_response = self.client.get_forms()
            forms = forms_response.get('results', [])

            total_forms = len(forms)
            form_submissions = 0

            # Get submission count for each form
            for form in forms[:10]:  # Limit to first 10 forms
                form_guid = form.get('guid')
                if form_guid:
                    try:
                        submissions = self.client.get_form_submissions(form_guid, limit=1)
                        form_submissions += submissions.get('total', 0)
                    except:
                        pass

            return {
                'total_forms': total_forms,
                'total_submissions': form_submissions
            }

        except Exception as e:
            logger.warning(f"Forms API not available: {e}")
            return {
                'total_forms': 0,
                'total_submissions': 0
            }

    def get_sales_activity_metrics(
        self,
        start_date: datetime,
        end_date: datetime,
        owner_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get sales activity metrics for scorecard

        Tracks:
        - Dials (phone calls made)
        - Conversations with DM (contacts with lifecycle stage = 'Connected')
        - FTAs set (meetings scheduled)
        - MRR Closed (deals closed with monthly value)

        NOTE: Excludes Joe Vinsky (TAM, manages HubSpot access)

        Args:
            start_date: Start of date range
            end_date: End of date range
            owner_email: Filter by sales rep email (e.g., 'jason@totalcareit.com')
        """
        try:
            # Get owner ID from email if provided (exclude Joe Vinsky)
            owner_id = None
            excluded_emails = ['jvinsky@totalcareit.com', 'joseph@totalcareit.com']

            if owner_email:
                # Exclude if it's Joe Vinsky
                if owner_email.lower() in excluded_emails:
                    return {
                        'dials': 0,
                        'conversations_with_dm': 0,
                        'ftas_set': 0,
                        'mrr_closed': 0,
                        'note': 'Joe Vinsky excluded from sales metrics (TAM role)'
                    }

                owners_response = self.client.get_owners()
                for owner in owners_response.get('results', []):
                    if owner.get('email', '').lower() == owner_email.lower():
                        owner_id = owner.get('id')
                        break

            # 1. Dials (phone calls) - exclude Joe Vinsky
            calls_response = self.client.get_calls(
                start_date=start_date,
                end_date=end_date,
                owner_id=owner_id,
                limit=200  # HubSpot max limit
            )

            # Filter out Joe Vinsky's calls if getting all owners
            calls = calls_response.get('results', [])
            if not owner_id:
                # Get Joe's owner ID to filter him out
                joe_owner_id = None
                owners_response = self.client.get_owners()
                for owner in owners_response.get('results', []):
                    if owner.get('email', '').lower() in excluded_emails:
                        joe_owner_id = owner.get('id')
                        break

                if joe_owner_id:
                    calls = [c for c in calls if c.get('properties', {}).get('hubspot_owner_id') != joe_owner_id]

            total_dials = len(calls)

            # 2. Conversations with DM = Contacts with lifecycle stage "Connected"
            # Search for contacts created/modified in date range with lifecycle stage = "connected"
            contact_filters = [
                {
                    'propertyName': 'lifecyclestage',
                    'operator': 'EQ',
                    'value': 'connected'
                },
                {
                    'propertyName': 'createdate',
                    'operator': 'GTE',
                    'value': int(start_date.timestamp() * 1000)
                },
                {
                    'propertyName': 'createdate',
                    'operator': 'LTE',
                    'value': int(end_date.timestamp() * 1000)
                }
            ]

            if owner_id:
                contact_filters.append({
                    'propertyName': 'hubspot_owner_id',
                    'operator': 'EQ',
                    'value': owner_id
                })

            connected_contacts_response = self.client.search_contacts(
                filters=contact_filters,
                limit=200
            )
            conversations_with_dm = connected_contacts_response.get('total', len(connected_contacts_response.get('results', [])))

            # 3. FTAs set (meetings scheduled)
            meetings_response = self.client.get_meetings(
                start_date=start_date,
                end_date=end_date,
                owner_id=owner_id,
                limit=200  # HubSpot max limit
            )
            ftas_set = meetings_response.get('total', len(meetings_response.get('results', [])))

            # 4. MRR Closed (deals closed in date range)
            closed_deals_filters = [
                {
                    'propertyName': 'closedate',
                    'operator': 'GTE',
                    'value': start_date.strftime('%Y-%m-%d')
                },
                {
                    'propertyName': 'closedate',
                    'operator': 'LTE',
                    'value': end_date.strftime('%Y-%m-%d')
                },
                {
                    'propertyName': 'dealstage',
                    'operator': 'EQ',
                    'value': 'closedwon'
                }
            ]

            if owner_id:
                closed_deals_filters.append({
                    'propertyName': 'hubspot_owner_id',
                    'operator': 'EQ',
                    'value': owner_id
                })

            closed_deals_response = self.client.search_deals(
                filters=closed_deals_filters,
                limit=200  # HubSpot max limit
            )
            closed_deals = closed_deals_response.get('results', [])

            # Calculate MRR (assuming deals have an 'mrr' or 'amount' property)
            mrr_closed = 0
            for deal in closed_deals:
                props = deal.get('properties', {})
                # Try to get MRR first, fallback to amount
                mrr = props.get('mrr') or props.get('amount') or 0
                if mrr:
                    mrr_closed += float(mrr)

            return {
                'dials': total_dials,
                'conversations_with_dm': conversations_with_dm,
                'ftas_set': ftas_set,
                'mrr_closed': round(mrr_closed, 2),
                'period': {
                    'start': start_date.strftime('%Y-%m-%d'),
                    'end': end_date.strftime('%Y-%m-%d')
                },
                'owner': owner_email or 'All'
            }

        except Exception as e:
            logger.error(f"Failed to get sales activity metrics: {e}")
            return {
                'dials': 0,
                'conversations_with_dm': 0,
                'ftas_set': 0,
                'mrr_closed': 0,
                'error': str(e)
            }


@lru_cache()
def get_hubspot_client() -> HubSpotClient:
    """Get cached HubSpot client instance"""
    config = HubSpotConfig.from_env()

    if not config.api_key:
        raise ValueError("HubSpot API key not configured in environment variables")

    return HubSpotClient(config)


def get_hubspot_reporting_service() -> HubSpotReportingService:
    """Get HubSpot reporting service instance"""
    client = get_hubspot_client()
    return HubSpotReportingService(client)
