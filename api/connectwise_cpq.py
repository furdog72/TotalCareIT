"""
ConnectWise CPQ API Integration
For pulling Pro Services opportunities and quotes data
"""

import os
import requests
import base64
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class ConnectWiseCPQ:
    """
    ConnectWise CPQ API Client
    Docs: https://developer.connectwise.com/
    """

    def __init__(self):
        # API Credentials from .env
        self.public_key = os.getenv('CONNECTWISE_CPQ_PUBLIC_KEY')
        self.private_key = os.getenv('CONNECTWISE_CPQ_PRIVATE_KEY')
        self.access_key = os.getenv('CONNECTWISE_CPQ_ACCESS_KEY')  # subdomain_azure

        # Base URL - Extract subdomain from access_key (remove _azure)
        subdomain = self.access_key.replace('_azure', '') if self.access_key else ''
        # Try the QuosalWeb API service endpoint
        self.base_url = f"https://{subdomain}.quosalsell.com/QuosalWeb/Service.asmx"

        # Headers
        self.headers = {
            'Content-Type': 'application/json',
            'PublicKey': self.public_key,
            'PrivateKey': self.private_key
        }

    def _make_request(self, method, endpoint, params=None, data=None):
        """
        Make API request with error handling
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

        except requests.exceptions.HTTPError as e:
            print(f"❌ CPQ API Error: {e}")
            print(f"Response: {response.text}")
            return None
        except Exception as e:
            print(f"❌ Request Error: {e}")
            return None

    def get_opportunities(self, status=None, start_date=None, end_date=None):
        """
        Get opportunities (quotes) from CPQ

        Args:
            status: Filter by status (Open, Won, Lost, etc.)
            start_date: Start date for filtering (YYYY-MM-DD)
            end_date: End date for filtering (YYYY-MM-DD)

        Returns:
            List of opportunities
        """
        params = {}

        if status:
            params['status'] = status
        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date

        return self._make_request('GET', '/opportunities', params=params)

    def get_opportunity_by_id(self, opportunity_id):
        """
        Get detailed information about a specific opportunity

        Args:
            opportunity_id: The CPQ opportunity ID

        Returns:
            Opportunity details
        """
        return self._make_request('GET', f'/opportunities/{opportunity_id}')

    def get_quotes(self, status=None, client_name=None):
        """
        Get quotes from CPQ

        Args:
            status: Filter by status
            client_name: Filter by client name

        Returns:
            List of quotes
        """
        params = {}

        if status:
            params['status'] = status
        if client_name:
            params['clientName'] = client_name

        return self._make_request('GET', '/quotes', params=params)

    def get_quote_by_id(self, quote_id):
        """
        Get detailed information about a specific quote

        Args:
            quote_id: The CPQ quote ID

        Returns:
            Quote details including line items, pricing, etc.
        """
        return self._make_request('GET', f'/quotes/{quote_id}')

    def get_products(self):
        """
        Get all products from CPQ catalog

        Returns:
            List of products
        """
        return self._make_request('GET', '/products')

    def get_clients(self):
        """
        Get all clients from CPQ

        Returns:
            List of clients
        """
        return self._make_request('GET', '/clients')

    def search_opportunities(self, search_term):
        """
        Search opportunities by term

        Args:
            search_term: Search string

        Returns:
            Matching opportunities
        """
        params = {'search': search_term}
        return self._make_request('GET', '/opportunities/search', params=params)

    # Pro Services PBR Specific Methods

    def get_pro_services_pipeline(self, days=30):
        """
        Get Pro Services opportunities for the last X days
        Useful for Pro Services PBR dashboard

        Args:
            days: Number of days to look back (default 30)

        Returns:
            Dictionary with pipeline metrics
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        opportunities = self.get_opportunities(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )

        if not opportunities:
            return {
                'total_opportunities': 0,
                'total_value': 0,
                'open_opportunities': 0,
                'open_value': 0,
                'won_opportunities': 0,
                'won_value': 0,
                'lost_opportunities': 0,
                'lost_value': 0
            }

        # Calculate metrics
        metrics = {
            'total_opportunities': len(opportunities),
            'total_value': 0,
            'open_opportunities': 0,
            'open_value': 0,
            'won_opportunities': 0,
            'won_value': 0,
            'lost_opportunities': 0,
            'lost_value': 0,
            'opportunities': []
        }

        for opp in opportunities:
            value = float(opp.get('totalValue', 0))
            status = opp.get('status', '').lower()

            metrics['total_value'] += value

            if 'open' in status or 'pending' in status:
                metrics['open_opportunities'] += 1
                metrics['open_value'] += value
            elif 'won' in status or 'closed won' in status:
                metrics['won_opportunities'] += 1
                metrics['won_value'] += value
            elif 'lost' in status or 'closed lost' in status:
                metrics['lost_opportunities'] += 1
                metrics['lost_value'] += value

            # Add to opportunities list for display
            metrics['opportunities'].append({
                'id': opp.get('id'),
                'name': opp.get('name'),
                'client': opp.get('clientName'),
                'value': value,
                'status': opp.get('status'),
                'created_date': opp.get('createdDate'),
                'close_date': opp.get('closeDate'),
                'owner': opp.get('owner')
            })

        return metrics

    def get_pro_services_backlog(self):
        """
        Get all open Pro Services opportunities (backlog)

        Returns:
            List of open opportunities
        """
        opportunities = self.get_opportunities(status='Open')

        if not opportunities:
            return []

        backlog = []
        for opp in opportunities:
            backlog.append({
                'id': opp.get('id'),
                'name': opp.get('name'),
                'client': opp.get('clientName'),
                'value': float(opp.get('totalValue', 0)),
                'created_date': opp.get('createdDate'),
                'age_days': self._calculate_age(opp.get('createdDate')),
                'owner': opp.get('owner'),
                'stage': opp.get('stage'),
                'probability': opp.get('probability', 0)
            })

        # Sort by age (oldest first)
        backlog.sort(key=lambda x: x['age_days'], reverse=True)

        return backlog

    def _calculate_age(self, created_date):
        """
        Calculate age of opportunity in days
        """
        if not created_date:
            return 0

        try:
            created = datetime.strptime(created_date, '%Y-%m-%dT%H:%M:%S')
            age = datetime.now() - created
            return age.days
        except:
            return 0


def test_cpq_connection():
    """
    Test ConnectWise CPQ API connection
    """
    print("🔧 Testing ConnectWise CPQ API connection...\n")

    cpq = ConnectWiseCPQ()

    if not cpq.public_key or not cpq.private_key or not cpq.access_key:
        print("❌ Missing CPQ credentials in .env file")
        print("\nPlease add:")
        print("CONNECTWISE_CPQ_PUBLIC_KEY=your_public_key")
        print("CONNECTWISE_CPQ_PRIVATE_KEY=your_private_key")
        print("CONNECTWISE_CPQ_ACCESS_KEY=your_subdomain_azure")
        return

    # Test getting opportunities
    print("📊 Fetching Pro Services pipeline (last 30 days)...")
    pipeline = cpq.get_pro_services_pipeline(days=30)

    if pipeline:
        print(f"\n✅ Pipeline Metrics:")
        print(f"   Total Opportunities: {pipeline['total_opportunities']}")
        print(f"   Total Value: ${pipeline['total_value']:,.2f}")
        print(f"   Open: {pipeline['open_opportunities']} (${pipeline['open_value']:,.2f})")
        print(f"   Won: {pipeline['won_opportunities']} (${pipeline['won_value']:,.2f})")
        print(f"   Lost: {pipeline['lost_opportunities']} (${pipeline['lost_value']:,.2f})")

        if pipeline.get('opportunities'):
            print(f"\n📋 Recent Opportunities:")
            for opp in pipeline['opportunities'][:5]:
                print(f"   - {opp['name']} ({opp['client']}): ${opp['value']:,.2f} - {opp['status']}")
    else:
        print("❌ Failed to fetch pipeline data")

    # Test getting backlog
    print("\n📋 Fetching Pro Services backlog...")
    backlog = cpq.get_pro_services_backlog()

    if backlog:
        print(f"\n✅ Found {len(backlog)} open opportunities")
        print(f"\n🔴 Oldest opportunities:")
        for opp in backlog[:5]:
            print(f"   - {opp['name']} ({opp['client']}): {opp['age_days']} days old - ${opp['value']:,.2f}")
    else:
        print("ℹ️ No open opportunities found")


if __name__ == '__main__':
    test_cpq_connection()
