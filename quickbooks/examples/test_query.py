"""
Test script to query QuickBooks Online data
"""

import os
from qbo_ai import QBOClient


def load_tokens():
    """Load tokens from .qbo_tokens file"""
    tokens_file = os.path.join(os.path.dirname(__file__), '..', '.qbo_tokens')

    if not os.path.exists(tokens_file):
        print(f"Token file not found: {tokens_file}")
        print("Please run oauth_server.py first to authenticate")
        return None

    tokens = {}
    with open(tokens_file, 'r') as f:
        for line in f:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                tokens[key] = value

    return tokens


def main():
    print("="*60)
    print("Testing QuickBooks Online Connection")
    print("="*60)

    # Load tokens
    tokens = load_tokens()
    if not tokens:
        return

    # Initialize and connect client
    client = QBOClient()

    print("\nConnecting to QuickBooks...")
    try:
        client.connect(tokens['ACCESS_TOKEN'], tokens['REFRESH_TOKEN'])
        print("Connected successfully!")
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    # Test 1: Query Customers
    print("\n1. Querying Customers (limit 5)...")
    try:
        customers = client.query('Customer', limit=5)
        print(f"   Found {len(customers)} customers")

        if customers:
            print("\n   Sample Customer Data:")
            for i, customer in enumerate(customers, 1):
                print(f"   {i}. {customer.DisplayName}")
                if hasattr(customer, 'CompanyName') and customer.CompanyName:
                    print(f"      Company: {customer.CompanyName}")
                if hasattr(customer, 'PrimaryEmailAddr') and customer.PrimaryEmailAddr:
                    print(f"      Email: {customer.PrimaryEmailAddr.Address}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test 2: Query Invoices
    print("\n2. Querying Invoices (limit 5)...")
    try:
        invoices = client.query('Invoice', limit=5)
        print(f"   Found {len(invoices)} invoices")

        if invoices:
            print("\n   Sample Invoice Data:")
            for i, invoice in enumerate(invoices, 1):
                print(f"   {i}. Invoice #{invoice.DocNumber}")
                print(f"      Total: ${invoice.TotalAmt}")
                if hasattr(invoice, 'CustomerRef'):
                    print(f"      Customer: {invoice.CustomerRef.name}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test 3: Query Accounts
    print("\n3. Querying Chart of Accounts (limit 5)...")
    try:
        accounts = client.query('Account', limit=5)
        print(f"   Found {len(accounts)} accounts")

        if accounts:
            print("\n   Sample Account Data:")
            for i, account in enumerate(accounts, 1):
                print(f"   {i}. {account.Name}")
                print(f"      Type: {account.AccountType}")
                if hasattr(account, 'CurrentBalance'):
                    print(f"      Balance: ${account.CurrentBalance}")
    except Exception as e:
        print(f"   Error: {e}")

    print("\n" + "="*60)
    print("Test Complete!")
    print("="*60)


if __name__ == "__main__":
    main()
