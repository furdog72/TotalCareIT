"""
LinkedIn Performance Tracking API
Tracks individual and company page performance metrics
"""

import os
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


class LinkedInPerformanceAPI:
    """Track LinkedIn performance metrics for individuals and company pages"""

    BASE_URL = "https://api.linkedin.com/v2"

    def __init__(self, access_token: Optional[str] = None):
        """Initialize with access token"""
        self.access_token = access_token or os.getenv('LINKEDIN_ACCESS_TOKEN')

        if not self.access_token:
            raise ValueError("LinkedIn access token required")

        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0',
            'LinkedIn-Version': '202310'
        }

    # ==================== INDIVIDUAL METRICS ====================

    def get_profile_analytics(self, start_date: datetime, end_date: datetime) -> Dict:
        """
        Get profile analytics for individual member

        Metrics:
        - Profile Views
        - Search Appearances
        - Post Impressions

        Args:
            start_date: Start date for analytics
            end_date: End date for analytics

        Returns:
            Dict with profile analytics
        """
        url = f"{self.BASE_URL}/analyticsV2"

        params = {
            'q': 'analytics',
            'pivot': 'MEMBER',
            'timeRange.start': int(start_date.timestamp() * 1000),
            'timeRange.end': int(end_date.timestamp() * 1000)
        }

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        return response.json()

    def get_profile_views(self, days: int = 7) -> int:
        """
        Get profile view count for last N days

        Args:
            days: Number of days to look back

        Returns:
            Total profile views
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        try:
            analytics = self.get_profile_analytics(start_date, end_date)

            # Extract profile views from analytics
            views = 0
            if 'elements' in analytics:
                for element in analytics['elements']:
                    if 'totalProfileViews' in element:
                        views += element['totalProfileViews']

            return views
        except Exception as e:
            print(f"Error getting profile views: {e}")
            return 0

    def get_search_appearances(self, days: int = 7) -> int:
        """
        Get search appearance count

        Args:
            days: Number of days to look back

        Returns:
            Total search appearances
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        try:
            analytics = self.get_profile_analytics(start_date, end_date)

            appearances = 0
            if 'elements' in analytics:
                for element in analytics['elements']:
                    if 'totalSearchAppearances' in element:
                        appearances += element['totalSearchAppearances']

            return appearances
        except Exception as e:
            print(f"Error getting search appearances: {e}")
            return 0

    def get_follower_count(self) -> int:
        """
        Get current follower count for member

        Returns:
            Number of followers
        """
        url = f"{self.BASE_URL}/networkSizes/urn:li:person:MEMBER"

        params = {
            'edgeType': 'FOLLOWED_BY'
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            data = response.json()
            return data.get('firstDegreeSize', 0)
        except Exception as e:
            print(f"Error getting follower count: {e}")
            return 0

    def get_connection_count(self) -> int:
        """
        Get current connection count

        Returns:
            Number of connections
        """
        url = f"{self.BASE_URL}/connections"

        params = {
            'q': 'viewer',
            'count': 0  # Only get count, not actual connections
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            data = response.json()
            return data.get('paging', {}).get('total', 0)
        except Exception as e:
            print(f"Error getting connection count: {e}")
            return 0

    def get_post_impressions(self, days: int = 7) -> int:
        """
        Get total post impressions for last N days

        Args:
            days: Number of days to look back

        Returns:
            Total post impressions
        """
        # Get recent posts
        posts = self.get_recent_posts(count=50)

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        total_impressions = 0

        for post in posts:
            # Check if post is within date range
            post_date = datetime.fromtimestamp(post.get('created', {}).get('time', 0) / 1000)

            if start_date <= post_date <= end_date:
                # Get post statistics
                post_id = post.get('id')
                if post_id:
                    stats = self.get_post_statistics(post_id)
                    total_impressions += stats.get('impressions', 0)

        return total_impressions

    def get_recent_posts(self, count: int = 10) -> List[Dict]:
        """Get recent posts"""
        url = f"{self.BASE_URL}/ugcPosts"

        params = {
            'q': 'authors',
            'count': count
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            return response.json().get('elements', [])
        except Exception as e:
            print(f"Error getting posts: {e}")
            return []

    def get_post_statistics(self, post_id: str) -> Dict:
        """Get statistics for a specific post"""
        url = f"{self.BASE_URL}/socialActions/{post_id}/statistics"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            return response.json()
        except Exception as e:
            print(f"Error getting post stats: {e}")
            return {}

    def get_individual_metrics(self, person_name: str, days: int = 7) -> Dict:
        """
        Get all individual metrics for a person

        Args:
            person_name: Name of the person (Charles, Jason, etc.)
            days: Days to look back

        Returns:
            Dict with all metrics
        """
        return {
            'name': person_name,
            'profile_views': self.get_profile_views(days),
            'search_appearances': self.get_search_appearances(days),
            'post_impressions': self.get_post_impressions(days),
            'followers': self.get_follower_count(),
            'connections': self.get_connection_count(),
            'period_days': days,
            'last_updated': datetime.now().isoformat()
        }

    # ==================== COMPANY PAGE METRICS ====================

    def get_company_page_stats(self, company_id: str, days: int = 7) -> Dict:
        """
        Get company page statistics

        Args:
            company_id: LinkedIn company ID (organization URN)
            days: Days to look back

        Returns:
            Dict with company metrics
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        url = f"{self.BASE_URL}/organizationalEntityShareStatistics"

        params = {
            'q': 'organizationalEntity',
            'organizationalEntity': f'urn:li:organization:{company_id}',
            'timeIntervals.timeGranularityType': 'DAY',
            'timeIntervals.timeRange.start': int(start_date.timestamp() * 1000),
            'timeIntervals.timeRange.end': int(end_date.timestamp() * 1000)
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            return response.json()
        except Exception as e:
            print(f"Error getting company stats: {e}")
            return {}

    def get_company_followers(self, company_id: str) -> int:
        """
        Get company page follower count

        Args:
            company_id: LinkedIn company ID

        Returns:
            Number of followers
        """
        url = f"{self.BASE_URL}/networkSizes/urn:li:organization:{company_id}"

        params = {
            'edgeType': 'CompanyFollowedByMember'
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            data = response.json()
            return data.get('firstDegreeSize', 0)
        except Exception as e:
            print(f"Error getting company followers: {e}")
            return 0

    def get_company_engagement(self, company_id: str, days: int = 7) -> Dict:
        """
        Get company page engagement metrics

        Args:
            company_id: LinkedIn company ID
            days: Days to look back

        Returns:
            Dict with engagement metrics (likes, comments, shares, clicks)
        """
        stats = self.get_company_page_stats(company_id, days)

        engagement = {
            'likes': 0,
            'comments': 0,
            'shares': 0,
            'clicks': 0,
            'impressions': 0,
            'engagement_rate': 0.0
        }

        if 'elements' in stats:
            for element in stats['elements']:
                engagement['likes'] += element.get('likeCount', 0)
                engagement['comments'] += element.get('commentCount', 0)
                engagement['shares'] += element.get('shareCount', 0)
                engagement['clicks'] += element.get('clickCount', 0)
                engagement['impressions'] += element.get('impressionCount', 0)

        # Calculate engagement rate
        if engagement['impressions'] > 0:
            total_engagement = engagement['likes'] + engagement['comments'] + engagement['shares']
            engagement['engagement_rate'] = (total_engagement / engagement['impressions']) * 100

        return engagement

    def get_company_post_count(self, company_id: str, days: int = 7) -> int:
        """
        Get number of posts published by company in last N days

        Args:
            company_id: LinkedIn company ID
            days: Days to look back

        Returns:
            Number of posts
        """
        url = f"{self.BASE_URL}/ugcPosts"

        params = {
            'q': 'authors',
            'authors': f'urn:li:organization:{company_id}',
            'count': 100
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            posts = response.json().get('elements', [])

            # Filter by date
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            recent_posts = 0
            for post in posts:
                post_date = datetime.fromtimestamp(post.get('created', {}).get('time', 0) / 1000)
                if start_date <= post_date <= end_date:
                    recent_posts += 1

            return recent_posts
        except Exception as e:
            print(f"Error getting company post count: {e}")
            return 0

    def get_competitor_metrics(self, competitor_id: str, days: int = 7) -> Dict:
        """
        Get competitor company metrics

        Args:
            competitor_id: Competitor's LinkedIn company ID
            days: Days to look back

        Returns:
            Dict with competitor metrics
        """
        return {
            'followers': self.get_company_followers(competitor_id),
            'posts': self.get_company_post_count(competitor_id, days),
            'engagement': self.get_company_engagement(competitor_id, days)
        }

    def compare_with_competitors(self, company_id: str, competitor_ids: List[str], days: int = 7) -> Dict:
        """
        Compare company performance with competitors

        Args:
            company_id: Your company ID
            competitor_ids: List of competitor company IDs
            days: Days to look back

        Returns:
            Dict with comparison data
        """
        # Get your company metrics
        your_metrics = {
            'followers': self.get_company_followers(company_id),
            'posts': self.get_company_post_count(company_id, days),
            'engagement': self.get_company_engagement(company_id, days)
        }

        # Get competitor metrics
        competitors = []
        for comp_id in competitor_ids:
            comp_metrics = self.get_competitor_metrics(comp_id, days)
            comp_metrics['id'] = comp_id
            competitors.append(comp_metrics)

        # Calculate rankings
        all_companies = [your_metrics] + competitors

        # Rank by followers
        sorted_by_followers = sorted(all_companies, key=lambda x: x['followers'], reverse=True)
        your_follower_rank = sorted_by_followers.index(your_metrics) + 1

        # Rank by engagement rate
        sorted_by_engagement = sorted(all_companies, key=lambda x: x['engagement']['engagement_rate'], reverse=True)
        your_engagement_rank = sorted_by_engagement.index(your_metrics) + 1

        # Rank by posts
        sorted_by_posts = sorted(all_companies, key=lambda x: x['posts'], reverse=True)
        your_post_rank = sorted_by_posts.index(your_metrics) + 1

        return {
            'your_company': your_metrics,
            'competitors': competitors,
            'rankings': {
                'followers': your_follower_rank,
                'engagement': your_engagement_rank,
                'posts': your_post_rank,
                'total_companies': len(all_companies)
            },
            'period_days': days,
            'last_updated': datetime.now().isoformat()
        }


# Example usage
if __name__ == "__main__":
    api = LinkedInPerformanceAPI()

    # Individual metrics
    print("Charles metrics:")
    charles_metrics = api.get_individual_metrics("Charles", days=7)
    print(charles_metrics)

    print("\nJason metrics:")
    jason_metrics = api.get_individual_metrics("Jason", days=7)
    print(jason_metrics)

    # Company metrics with competitor comparison
    print("\nTotalCareIT vs Competitors:")
    totalcareit_company_id = "YOUR_COMPANY_ID"
    competitor_ids = ["COMPETITOR_1_ID", "COMPETITOR_2_ID"]

    comparison = api.compare_with_competitors(
        totalcareit_company_id,
        competitor_ids,
        days=7
    )
    print(comparison)
