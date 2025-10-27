#!/usr/bin/env python3
"""
Test if current refresh token is still valid
"""
import os
from dotenv import load_dotenv
from intuitlib.client import AuthClient

# Load environment variables
load_dotenv()

def test_refresh():
    """Test if refresh token is still valid"""
    print("Testing Refresh Token Validity")
    print("-" * 50)

    # Read current tokens
    with open('.qbo_tokens', 'r') as f:
        lines = f.readlines()
        tokens = {}
        for line in lines:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                tokens[key.lower()] = value

    print(f"Realm ID: {tokens.get('realm_id')}")
    print(f"Refresh Token: {tokens.get('refresh_token')[:20]}...")

    # Try to refresh
    auth_client = AuthClient(
        client_id=os.getenv('QBO_CLIENT_ID'),
        client_secret=os.getenv('QBO_CLIENT_SECRET'),
        redirect_uri=os.getenv('QBO_REDIRECT_URI', 'http://localhost:8000/callback'),
        environment=os.getenv('QBO_ENVIRONMENT', 'sandbox')
    )

    # Set tokens
    auth_client.refresh_token = tokens.get('refresh_token')

    try:
        print("\nAttempting to refresh token...")
        auth_client.refresh()

        print("✅ SUCCESS! Token refreshed!")
        print(f"New Access Token: {auth_client.access_token[:20]}...")
        print(f"New Refresh Token: {auth_client.refresh_token[:20]}...")

        # Save new tokens
        with open('.qbo_tokens', 'w') as f:
            f.write(f"ACCESS_TOKEN={auth_client.access_token}\n")
            f.write(f"REFRESH_TOKEN={auth_client.refresh_token}\n")
            f.write(f"REALM_ID={tokens.get('realm_id')}\n")

        print("\n✓ New tokens saved to .qbo_tokens")
        print("The automatic refresh mechanism will now work!")

    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        print("\nRefresh token is expired or invalid.")
        print("You need to re-authenticate through the OAuth flow.")
        print("\nRun: python examples/oauth_server.py")
        print("Then visit the authorization URL to get new tokens.")


if __name__ == "__main__":
    test_refresh()