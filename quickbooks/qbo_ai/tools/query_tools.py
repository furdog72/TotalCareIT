"""
Query tools for QuickBooks Online MCP Server
Implements read-only query operations for QBO entities
"""

from typing import Dict, Any, Optional, List
from quickbooks.objects.customer import Customer
from quickbooks.objects.invoice import Invoice
from quickbooks.objects.account import Account
from quickbooks.objects.vendor import Vendor
from quickbooks.objects.bill import Bill
from quickbooks.objects.payment import Payment
from quickbooks.objects.item import Item
from quickbooks.exceptions import AuthorizationException, QuickbooksException
from ..utils.formatters import (
    format_customer,
    format_invoice,
    format_account,
    format_vendor,
    format_bill,
    format_payment,
    format_item,
    format_list,
)


def _handle_qb_api_call(api_call_func, qb_client, *args, **kwargs):
    """
    Execute a QuickBooks API call with automatic token refresh on 401 errors.

    Args:
        api_call_func: The QuickBooks API function to call
        qb_client: QuickBooks client instance
        *args: Arguments for the API call
        **kwargs: Keyword arguments for the API call

    Returns:
        Result of the API call

    Raises:
        Original exception if not a 401 error or if token refresh fails
    """
    try:
        # First attempt
        return api_call_func(*args, qb=qb_client, **kwargs)
    except (AuthorizationException, QuickbooksException, Exception) as e:
        error_str = str(e)
        # Check for 401 authentication error
        if '401' in error_str or 'authentication' in error_str.lower() or 'token' in error_str.lower() or 'expired' in error_str.lower():
            print(f"Authentication error detected: {error_str}")

            # Try to refresh the client
            if hasattr(qb_client, '_server'):
                print("Refreshing QuickBooks client with new tokens...")
                try:
                    # Refresh the client (this will refresh tokens internally)
                    refreshed_client = qb_client._server.refresh_qb_client()

                    # Retry with refreshed client
                    print("Retrying operation with refreshed tokens...")
                    return api_call_func(*args, qb=refreshed_client, **kwargs)

                except Exception as refresh_error:
                    print(f"Failed to refresh tokens: {refresh_error}")
                    raise e  # Re-raise original error
            else:
                print("No server reference available for token refresh")
                raise
        else:
            # Not an authentication error, re-raise
            raise


def query_customers(
    qb_client,
    limit: int = 10,
    active_only: bool = True,
    name_filter: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Query customer data from QuickBooks

    Args:
        qb_client: QuickBooks client instance
        limit: Maximum number of results (default 10, max 1000)
        active_only: Only return active customers
        name_filter: Optional filter for customer name (case-insensitive contains)

    Returns:
        List of formatted customer dictionaries
    """
    # Build query
    where_clauses = []

    if active_only:
        where_clauses.append("Active = true")

    if name_filter:
        # QBO uses LIKE for partial matching
        where_clauses.append(f"DisplayName LIKE '%{name_filter}%'")

    # Execute query using SDK's all method with retry on auth errors
    from quickbooks.objects.customer import Customer

    # Get all customers (SDK handles pagination) with automatic token refresh on 401
    all_customers = _handle_qb_api_call(Customer.all, qb_client, max_results=1000)

    # Apply filters
    filtered_customers = []
    for customer in all_customers:
        # Check active filter
        if active_only and not customer.Active:
            continue

        # Check name filter
        if name_filter and name_filter.lower() not in customer.DisplayName.lower():
            continue

        filtered_customers.append(customer)

        # Stop if we've reached the limit
        if len(filtered_customers) >= limit:
            break

    # Format results
    return format_list(filtered_customers, format_customer)


def query_invoices(
    qb_client,
    limit: int = 10,
    customer_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    unpaid_only: bool = False,
) -> List[Dict[str, Any]]:
    """
    Query invoice data from QuickBooks

    Args:
        qb_client: QuickBooks client instance
        limit: Maximum number of results (default 10, max 1000)
        customer_id: Optional filter for specific customer
        start_date: Optional start date (YYYY-MM-DD format)
        end_date: Optional end date (YYYY-MM-DD format)
        unpaid_only: Only return invoices with outstanding balance

    Returns:
        List of formatted invoice dictionaries
    """
    # Build query
    where_clauses = []

    if customer_id:
        where_clauses.append(f"CustomerRef = '{customer_id}'")

    if start_date:
        where_clauses.append(f"TxnDate >= '{start_date}'")

    if end_date:
        where_clauses.append(f"TxnDate <= '{end_date}'")

    if unpaid_only:
        where_clauses.append("Balance > '0'")

    where_clause = " AND ".join(where_clauses) if where_clauses else None

    # Execute query using SDK's query method with automatic token refresh on 401
    # The SDK expects just the WHERE clause, not a full SELECT statement
    # If no where clause, we'll use the all() method instead
    if where_clause:
        invoices = _handle_qb_api_call(Invoice.query, qb_client, where_clause)
    else:
        # Use the all() method when no filters are specified
        invoices = _handle_qb_api_call(Invoice.all, qb_client, max_results=limit)

    # Limit results
    invoices = invoices[:limit]

    # Format results
    return format_list(invoices, format_invoice)


def query_accounts(
    qb_client,
    limit: int = 100,
    account_type: Optional[str] = None,
    active_only: bool = True,
) -> List[Dict[str, Any]]:
    """
    Query chart of accounts from QuickBooks

    Args:
        qb_client: QuickBooks client instance
        limit: Maximum number of results (default 100, max 1000)
        account_type: Optional filter for account type (e.g., 'Bank', 'Income', 'Expense')
        active_only: Only return active accounts

    Returns:
        List of formatted account dictionaries
    """
    # Build query
    where_clauses = []

    if active_only:
        where_clauses.append("Active = true")

    if account_type:
        where_clauses.append(f"AccountType = '{account_type}'")

    where_clause = " AND ".join(where_clauses) if where_clauses else None

    # Execute query using SDK's query method with automatic token refresh on 401
    if where_clause:
        accounts = _handle_qb_api_call(Account.query, qb_client, where_clause)
    else:
        accounts = _handle_qb_api_call(Account.all, qb_client, max_results=limit)

    # Limit results
    accounts = accounts[:limit]

    # Format results
    return format_list(accounts, format_account)


def query_vendors(
    qb_client,
    limit: int = 10,
    active_only: bool = True,
    name_filter: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Query vendor data from QuickBooks

    Args:
        qb_client: QuickBooks client instance
        limit: Maximum number of results (default 10, max 1000)
        active_only: Only return active vendors
        name_filter: Optional filter for vendor name (case-insensitive contains)

    Returns:
        List of formatted vendor dictionaries
    """
    # Build query
    where_clauses = []

    if active_only:
        where_clauses.append("Active = true")

    if name_filter:
        where_clauses.append(f"DisplayName LIKE '%{name_filter}%'")

    where_clause = " AND ".join(where_clauses) if where_clauses else None

    # Execute query using SDK's query method with automatic token refresh on 401
    if where_clause:
        vendors = _handle_qb_api_call(Vendor.query, qb_client, where_clause)
    else:
        vendors = _handle_qb_api_call(Vendor.all, qb_client, max_results=limit)

    # Limit results
    vendors = vendors[:limit]

    # Format results
    return format_list(vendors, format_vendor)


def query_bills(
    qb_client,
    limit: int = 10,
    vendor_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    unpaid_only: bool = False,
) -> List[Dict[str, Any]]:
    """
    Query bill data from QuickBooks

    Args:
        qb_client: QuickBooks client instance
        limit: Maximum number of results (default 10, max 1000)
        vendor_id: Optional filter for specific vendor
        start_date: Optional start date (YYYY-MM-DD format)
        end_date: Optional end date (YYYY-MM-DD format)
        unpaid_only: Only return bills with outstanding balance

    Returns:
        List of formatted bill dictionaries
    """
    # Build query
    where_clauses = []

    if vendor_id:
        where_clauses.append(f"VendorRef = '{vendor_id}'")

    if start_date:
        where_clauses.append(f"TxnDate >= '{start_date}'")

    if end_date:
        where_clauses.append(f"TxnDate <= '{end_date}'")

    if unpaid_only:
        where_clauses.append("Balance > '0'")

    where_clause = " AND ".join(where_clauses) if where_clauses else None

    # Execute query using SDK's query method with automatic token refresh on 401
    if where_clause:
        bills = _handle_qb_api_call(Bill.query, qb_client, where_clause)
    else:
        bills = _handle_qb_api_call(Bill.all, qb_client, max_results=limit)

    # Limit results
    bills = bills[:limit]

    # Format results
    return format_list(bills, format_bill)


def query_payments(
    qb_client,
    limit: int = 10,
    customer_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Query payment data from QuickBooks

    Args:
        qb_client: QuickBooks client instance
        limit: Maximum number of results (default 10, max 1000)
        customer_id: Optional filter for specific customer
        start_date: Optional start date (YYYY-MM-DD format)
        end_date: Optional end date (YYYY-MM-DD format)

    Returns:
        List of formatted payment dictionaries
    """
    # Build query
    where_clauses = []

    if customer_id:
        where_clauses.append(f"CustomerRef = '{customer_id}'")

    if start_date:
        where_clauses.append(f"TxnDate >= '{start_date}'")

    if end_date:
        where_clauses.append(f"TxnDate <= '{end_date}'")

    where_clause = " AND ".join(where_clauses) if where_clauses else None

    # Execute query using SDK's query method with automatic token refresh on 401
    if where_clause:
        payments = _handle_qb_api_call(Payment.query, qb_client, where_clause)
    else:
        payments = _handle_qb_api_call(Payment.all, qb_client, max_results=limit)

    # Limit results
    payments = payments[:limit]

    # Format results
    return format_list(payments, format_payment)


def query_items(
    qb_client,
    limit: int = 100,
    active_only: bool = True,
    item_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Query item/product/service data from QuickBooks

    Args:
        qb_client: QuickBooks client instance
        limit: Maximum number of results (default 100, max 1000)
        active_only: Only return active items
        item_type: Optional filter for item type (e.g., 'Service', 'Inventory')

    Returns:
        List of formatted item dictionaries
    """
    # Build query
    where_clauses = []

    if active_only:
        where_clauses.append("Active = true")

    if item_type:
        where_clauses.append(f"Type = '{item_type}'")

    where_clause = " AND ".join(where_clauses) if where_clauses else None

    # Execute query using SDK's query method with automatic token refresh on 401
    if where_clause:
        items = _handle_qb_api_call(Item.query, qb_client, where_clause)
    else:
        items = _handle_qb_api_call(Item.all, qb_client, max_results=limit)

    # Limit results
    items = items[:limit]

    # Format results
    return format_list(items, format_item)
