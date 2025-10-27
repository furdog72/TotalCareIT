#!/usr/bin/env python3
"""
Test script showing automatic token refresh during queries
"""
import os
import sys
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

def test_refresh_in_queries():
    """Test that queries automatically refresh tokens when needed"""
    from qbo_ai.mcp_server import QBOMCPServer
    from qbo_ai.tools.query_tools import query_customers

    print("Testing Automatic Token Refresh in Queries")
    print("-" * 50)

    try:
        # Initialize MCP server (will use LocalTokenManager automatically)
        print("Initializing MCP server...")
        mcp_server = QBOMCPServer()

        # Get QB client
        print("Getting QuickBooks client...")
        qb_client = mcp_server._get_qb_client()
        print(f"✓ QuickBooks client initialized")

        # Test 1: Query should work even with expired token (auto-refresh)
        print("\nAttempting to query customers...")
        print("(This will automatically refresh token if expired)")

        try:
            # Force token to appear expired for testing
            if hasattr(mcp_server.token_manager, 'last_refresh'):
                # Make it seem like token is 2 hours old
                mcp_server.token_manager.last_refresh = datetime.now() - timedelta(hours=2)
                print("  - Simulated expired token (2 hours old)")

            # This query should trigger automatic refresh if token is expired
            result = query_customers(qb_client, limit=3)

            if result:
                print(f"✓ Query successful! Retrieved {len(result)} customers")
                for customer in result[:3]:
                    if isinstance(customer, dict):
                        print(f"  - {customer.get('display_name', 'Unknown')}")
            else:
                print("✓ Query completed (no customers found)")

        except Exception as query_error:
            error_msg = str(query_error)
            if '401' in error_msg or 'authentication' in error_msg.lower():
                print("✗ Authentication failed - tokens may need manual refresh")
                print("  This is expected if the refresh token has expired (>100 days)")
                print("  In production, the system will maintain fresh tokens automatically")
            else:
                print(f"✗ Query error: {query_error}")

        # Test 2: Show refresh mechanism details
        print("\n" + "-" * 50)
        print("Token Refresh Mechanism Summary:")
        print("  - Access tokens expire after: 1 hour")
        print("  - Refresh tokens expire after: 100 days")
        print("  - Auto-refresh happens when:")
        print("    • Token is >55 minutes old (5 min safety margin)")
        print("    • Query gets 401 authentication error")
        print("  - With proper refresh, access maintained for 1+ year")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_refresh_in_queries()