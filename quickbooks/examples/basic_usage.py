"""
Basic usage example for QBO AI
"""

from qbo_ai import QBOClient


def main():
    # Initialize client
    client = QBOClient()

    # Step 1: Get authorization URL
    print("Step 1: Get Authorization URL")
    auth_url = client.get_authorization_url()
    print(f"Visit this URL to authorize: {auth_url}")

    # Step 2: After authorization, exchange code for tokens
    # (You'll get auth_code and realm_id from the callback)
    # tokens = client.get_bearer_token(auth_code, realm_id)

    # Step 3: Connect with tokens
    # client.connect(tokens['access_token'], tokens['refresh_token'])

    # Step 4: Query data
    # customers = client.query('Customer', limit=10)
    # print(f"Found {len(customers)} customers")


if __name__ == "__main__":
    main()
