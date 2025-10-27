"""
LinkedIn API Integration
Connects to LinkedIn profile for data extraction and automation
"""

import os
import requests
from typing import Dict, Optional, List
from dotenv import load_dotenv

load_dotenv()

class LinkedInAPI:
    """LinkedIn API client for profile management and data extraction"""

    BASE_URL = "https://api.linkedin.com/v2"

    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize LinkedIn API client

        Args:
            access_token: LinkedIn OAuth access token (or use LINKEDIN_ACCESS_TOKEN env var)
        """
        self.access_token = access_token or os.getenv('LINKEDIN_ACCESS_TOKEN')

        if not self.access_token:
            raise ValueError("LinkedIn access token is required. Set LINKEDIN_ACCESS_TOKEN env variable or pass access_token parameter.")

        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }

    def get_profile(self) -> Dict:
        """
        Get authenticated user's LinkedIn profile

        Returns:
            Dict containing profile data (name, headline, location, etc.)
        """
        url = f"{self.BASE_URL}/me"

        # Request profile fields
        params = {
            'projection': '(id,firstName,lastName,profilePicture(displayImage~:playableStreams))'
        }

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        return response.json()

    def get_profile_details(self) -> Dict:
        """
        Get detailed profile information including headline, location, industry

        Returns:
            Dict with detailed profile data
        """
        url = f"{self.BASE_URL}/me"

        params = {
            'projection': '(id,firstName,lastName,headline,location,industryName,profilePicture(displayImage~:playableStreams))'
        }

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        return response.json()

    def get_connections_count(self) -> int:
        """
        Get total number of LinkedIn connections

        Returns:
            Integer count of connections
        """
        url = f"{self.BASE_URL}/networkSizes/urn:li:person:{self.get_profile()['id']}"

        params = {
            'edgeType': 'CompanyFollowedByMember'
        }

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        data = response.json()
        return data.get('firstDegreeSize', 0)

    def share_post(self, text: str, visibility: str = "PUBLIC") -> Dict:
        """
        Share a post on LinkedIn

        Args:
            text: Post content/text
            visibility: Post visibility (PUBLIC, CONNECTIONS, LOGGED_IN)

        Returns:
            Dict with post creation response
        """
        profile = self.get_profile()
        person_urn = f"urn:li:person:{profile['id']}"

        url = f"{self.BASE_URL}/ugcPosts"

        payload = {
            "author": person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()

        return response.json()

    def get_posts(self, count: int = 10) -> List[Dict]:
        """
        Get recent posts from user's profile

        Args:
            count: Number of posts to retrieve (default 10)

        Returns:
            List of post objects
        """
        profile = self.get_profile()
        person_urn = f"urn:li:person:{profile['id']}"

        url = f"{self.BASE_URL}/ugcPosts"

        params = {
            'q': 'authors',
            'authors': person_urn,
            'count': count
        }

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        return response.json().get('elements', [])

    def get_post_statistics(self, post_urn: str) -> Dict:
        """
        Get statistics for a specific post

        Args:
            post_urn: URN of the post

        Returns:
            Dict with likes, comments, shares counts
        """
        url = f"{self.BASE_URL}/socialMetadata/{post_urn}"

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        return response.json()


def setup_linkedin_oauth():
    """
    Instructions for setting up LinkedIn OAuth

    LinkedIn OAuth Flow:
    1. Create LinkedIn App at https://www.linkedin.com/developers/apps
    2. Get Client ID and Client Secret
    3. Set redirect URI (e.g., http://localhost:8000/callback/linkedin)
    4. Request authorization:
       https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=r_liteprofile%20r_emailaddress%20w_member_social
    5. Exchange authorization code for access token:
       POST https://www.linkedin.com/oauth/v2/accessToken
    6. Store access token in .env file
    """
    print("""
    LinkedIn OAuth Setup Instructions:
    ===================================

    1. Go to https://www.linkedin.com/developers/apps
    2. Create a new app or select existing
    3. Get your Client ID and Client Secret
    4. Add redirect URI: http://localhost:8000/callback/linkedin
    5. Request these permissions:
       - r_liteprofile (read profile)
       - r_emailaddress (read email)
       - w_member_social (post updates)
       - rw_organization_admin (if managing company page)

    6. Authorization URL:
       https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:8000/callback/linkedin&scope=r_liteprofile%20r_emailaddress%20w_member_social

    7. After authorization, exchange code for token:
       POST https://www.linkedin.com/oauth/v2/accessToken
       grant_type=authorization_code
       code=AUTHORIZATION_CODE
       redirect_uri=http://localhost:8000/callback/linkedin
       client_id=YOUR_CLIENT_ID
       client_secret=YOUR_CLIENT_SECRET

    8. Add to .env file:
       LINKEDIN_CLIENT_ID=your_client_id
       LINKEDIN_CLIENT_SECRET=your_client_secret
       LINKEDIN_ACCESS_TOKEN=your_access_token
       LINKEDIN_REDIRECT_URI=http://localhost:8000/callback/linkedin
    """)


# Example usage
if __name__ == "__main__":
    # Show setup instructions
    setup_linkedin_oauth()

    # Example of using the API (requires valid access token)
    # linkedin = LinkedInAPI()
    # profile = linkedin.get_profile()
    # print(f"Connected to: {profile['firstName']} {profile['lastName']}")
