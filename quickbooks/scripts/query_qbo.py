"""
Simple QuickBooks Online query script
Run this after authenticating with auth_qbo.py
"""

import os
from dotenv import load_dotenv
from intuitlib.client import AuthClient
from quickbooks import QuickBooks

# Load environment variables
load_dotenv()

# Load tokens from file
def load_tokens():
    if not os.path.exists('.qbo_tokens'):
        print("Error: .qbo_tokens file not found")
        print("Run auth_qbo.py first to authenticate")
        return None

    tokens = {}
    with open('.qbo_tokens', 'r') as f:
        for line in f:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                tokens[key] = value
    return tokens


def main():
    print("="*60)
    print("QuickBooks Online Query Script")
    print("="*60)

    # Load tokens
    tokens = load_tokens()
    if not tokens:
        return

    # Get config from environment
    client_id = os.getenv('QBO_CLIENT_ID')
    client_secret = os.getenv('QBO_CLIENT_SECRET')
    redirect_uri = os.getenv('QBO_REDIRECT_URI')
    environment = os.getenv('QBO_ENVIRONMENT', 'sandbox')
    company_id = os.getenv('QBO_COMPANY_ID') or '9341455537530838'  # Fallback to hardcoded value

    if not client_id or not client_secret:
        print("Error: QBO_CLIENT_ID and QBO_CLIENT_SECRET not set in .env file")
        return

    print(f"\nCompany ID: {company_id}")
    print(f"Environment: {environment}")

    # Initialize auth client
    auth_client = AuthClient(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        environment=environment,
    )

    # Set tokens
    auth_client.access_token = tokens['ACCESS_TOKEN']
    auth_client.refresh_token = tokens['REFRESH_TOKEN']

    # Create QuickBooks client
    qb_client = QuickBooks(
        auth_client=auth_client,
        refresh_token=tokens['REFRESH_TOKEN'],
        company_id=company_id,
    )

    print("\nConnected to QuickBooks!")
    print("="*60)

    # Query Customers
    print("\n1. Querying Customers (limit 5)...")
    try:
        from quickbooks.objects.customer import Customer
        customers = Customer.query("SELECT * FROM Customer MAXRESULTS 5", qb=qb_client)
        print(f"   Found {len(customers)} customers:")
        for customer in customers:
            print(f"   - {customer.DisplayName}")
            if hasattr(customer, 'PrimaryEmailAddr') and customer.PrimaryEmailAddr:
                print(f"     Email: {customer.PrimaryEmailAddr.Address}")
    except Exception as e:
        print(f"   Error: {e}")

    # Query Invoices
    print("\n2. Querying Invoices (limit 5)...")
    try:
        from quickbooks.objects.invoice import Invoice
        invoices = Invoice.query("SELECT * FROM Invoice MAXRESULTS 5", qb=qb_client)
        print(f"   Found {len(invoices)} invoices:")
        for invoice in invoices:
            print(f"   - Invoice #{invoice.DocNumber}: ${invoice.TotalAmt}")
            if hasattr(invoice, 'CustomerRef'):
                print(f"     Customer: {invoice.CustomerRef.name}")
    except Exception as e:
        print(f"   Error: {e}")

    # Query Accounts
    print("\n3. Querying Chart of Accounts (limit 5)...")
    try:
        from quickbooks.objects.account import Account
        accounts = Account.query("SELECT * FROM Account MAXRESULTS 5", qb=qb_client)
        print(f"   Found {len(accounts)} accounts:")
        for account in accounts:
            print(f"   - {account.Name} ({account.AccountType})")
    except Exception as e:
        print(f"   Error: {e}")

    print("\n" + "="*60)
    print("Query Complete!")
    print("="*60)


if __name__ == "__main__":
    main()
