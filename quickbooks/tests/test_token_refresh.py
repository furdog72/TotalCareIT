#!/usr/bin/env python3
"""
Test script for token refresh mechanism
"""
import os
from dotenv import load_dotenv
from qbo_ai.local_token_manager import LocalTokenManager

# Load environment variables
load_dotenv()

def test_token_refresh():
    """Test the token refresh functionality"""
    print("Testing QuickBooks Token Refresh Mechanism")
    print("-" * 50)

    try:
        # Initialize local token manager
        token_manager = LocalTokenManager()

        # Check if tokens exist
        if not token_manager.tokens_exist():
            print("Error: No tokens found. Please authenticate first.")
            return

        print("✓ Token file found")

        # Load and display token info (without showing actual tokens)
        tokens = token_manager._load_tokens()
        print(f"✓ Tokens loaded successfully")
        print(f"  - Realm ID: {tokens.get('realm_id')}")
        print(f"  - Environment: {tokens.get('environment')}")

        # Check if token is expired
        if token_manager._is_token_expired():
            print("⚠ Token appears to be expired (>55 minutes old)")
        else:
            print("✓ Token is still fresh")

        # Test refresh
        print("\nAttempting to refresh tokens...")
        try:
            refreshed_tokens = token_manager.refresh_tokens()
            print("✓ Tokens refreshed successfully!")
            print(f"  - New access token: {refreshed_tokens['access_token'][:20]}...")
            print(f"  - Refresh token: {refreshed_tokens['refresh_token'][:20]}...")
        except Exception as e:
            print(f"✗ Failed to refresh tokens: {e}")

        # Test getting valid tokens (should use cached if just refreshed)
        print("\nTesting get_valid_tokens (automatic refresh if needed)...")
        valid_tokens = token_manager.get_valid_tokens()
        print("✓ Valid tokens retrieved")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_token_refresh()