"""
Data formatters for QuickBooks Online entities
Convert QBO objects to clean dictionaries suitable for MCP responses
"""

from typing import Dict, Any, List


def format_customer(customer: Any) -> Dict[str, Any]:
    """
    Format a QuickBooks Customer object for MCP response

    Args:
        customer: QuickBooks Customer object

    Returns:
        Dictionary with formatted customer data
    """
    formatted = {
        "id": customer.Id,
        "display_name": customer.DisplayName,
        "active": customer.Active,
    }

    # Optional fields
    if hasattr(customer, "CompanyName") and customer.CompanyName:
        formatted["company_name"] = customer.CompanyName

    if hasattr(customer, "GivenName") and customer.GivenName:
        formatted["first_name"] = customer.GivenName

    if hasattr(customer, "FamilyName") and customer.FamilyName:
        formatted["last_name"] = customer.FamilyName

    if hasattr(customer, "PrimaryEmailAddr") and customer.PrimaryEmailAddr:
        formatted["email"] = customer.PrimaryEmailAddr.Address

    if hasattr(customer, "PrimaryPhone") and customer.PrimaryPhone:
        formatted["phone"] = customer.PrimaryPhone.FreeFormNumber

    if hasattr(customer, "Balance") and customer.Balance:
        formatted["balance"] = float(customer.Balance)

    if hasattr(customer, "BillAddr") and customer.BillAddr:
        formatted["billing_address"] = _format_address(customer.BillAddr)

    return formatted


def format_invoice(invoice: Any) -> Dict[str, Any]:
    """
    Format a QuickBooks Invoice object for MCP response

    Args:
        invoice: QuickBooks Invoice object

    Returns:
        Dictionary with formatted invoice data
    """
    formatted = {
        "id": invoice.Id,
        "doc_number": invoice.DocNumber,
        "total_amount": float(invoice.TotalAmt) if invoice.TotalAmt else 0.0,
        "balance": float(invoice.Balance) if invoice.Balance else 0.0,
        "txn_date": str(invoice.TxnDate) if invoice.TxnDate else None,
    }

    # Customer reference
    if hasattr(invoice, "CustomerRef") and invoice.CustomerRef:
        formatted["customer"] = {
            "id": invoice.CustomerRef.value,
            "name": invoice.CustomerRef.name,
        }

    # Due date
    if hasattr(invoice, "DueDate") and invoice.DueDate:
        formatted["due_date"] = str(invoice.DueDate)

    # Email status
    if hasattr(invoice, "EmailStatus") and invoice.EmailStatus:
        formatted["email_status"] = invoice.EmailStatus

    # Line items
    if hasattr(invoice, "Line") and invoice.Line:
        formatted["line_items"] = [_format_line_item(line) for line in invoice.Line]

    return formatted


def format_account(account: Any) -> Dict[str, Any]:
    """
    Format a QuickBooks Account object for MCP response

    Args:
        account: QuickBooks Account object

    Returns:
        Dictionary with formatted account data
    """
    formatted = {
        "id": account.Id,
        "name": account.Name,
        "account_type": account.AccountType,
        "active": account.Active,
    }

    # Optional fields
    if hasattr(account, "AccountSubType") and account.AccountSubType:
        formatted["account_subtype"] = account.AccountSubType

    if hasattr(account, "CurrentBalance") and account.CurrentBalance is not None:
        formatted["current_balance"] = float(account.CurrentBalance)

    if hasattr(account, "Description") and account.Description:
        formatted["description"] = account.Description

    return formatted


def format_vendor(vendor: Any) -> Dict[str, Any]:
    """
    Format a QuickBooks Vendor object for MCP response

    Args:
        vendor: QuickBooks Vendor object

    Returns:
        Dictionary with formatted vendor data
    """
    formatted = {
        "id": vendor.Id,
        "display_name": vendor.DisplayName,
        "active": vendor.Active,
    }

    # Optional fields
    if hasattr(vendor, "CompanyName") and vendor.CompanyName:
        formatted["company_name"] = vendor.CompanyName

    if hasattr(vendor, "PrimaryEmailAddr") and vendor.PrimaryEmailAddr:
        formatted["email"] = vendor.PrimaryEmailAddr.Address

    if hasattr(vendor, "PrimaryPhone") and vendor.PrimaryPhone:
        formatted["phone"] = vendor.PrimaryPhone.FreeFormNumber

    if hasattr(vendor, "Balance") and vendor.Balance:
        formatted["balance"] = float(vendor.Balance)

    if hasattr(vendor, "BillAddr") and vendor.BillAddr:
        formatted["billing_address"] = _format_address(vendor.BillAddr)

    return formatted


def format_bill(bill: Any) -> Dict[str, Any]:
    """
    Format a QuickBooks Bill object for MCP response

    Args:
        bill: QuickBooks Bill object

    Returns:
        Dictionary with formatted bill data
    """
    formatted = {
        "id": bill.Id,
        "doc_number": bill.DocNumber if hasattr(bill, "DocNumber") else None,
        "total_amount": float(bill.TotalAmt) if bill.TotalAmt else 0.0,
        "balance": float(bill.Balance) if bill.Balance else 0.0,
        "txn_date": str(bill.TxnDate) if bill.TxnDate else None,
    }

    # Vendor reference
    if hasattr(bill, "VendorRef") and bill.VendorRef:
        formatted["vendor"] = {
            "id": bill.VendorRef.value,
            "name": bill.VendorRef.name,
        }

    # Due date
    if hasattr(bill, "DueDate") and bill.DueDate:
        formatted["due_date"] = str(bill.DueDate)

    return formatted


def format_payment(payment: Any) -> Dict[str, Any]:
    """
    Format a QuickBooks Payment object for MCP response

    Args:
        payment: QuickBooks Payment object

    Returns:
        Dictionary with formatted payment data
    """
    formatted = {
        "id": payment.Id,
        "total_amount": float(payment.TotalAmt) if payment.TotalAmt else 0.0,
        "txn_date": str(payment.TxnDate) if payment.TxnDate else None,
    }

    # Customer reference
    if hasattr(payment, "CustomerRef") and payment.CustomerRef:
        formatted["customer"] = {
            "id": payment.CustomerRef.value,
            "name": payment.CustomerRef.name,
        }

    # Payment reference number
    if hasattr(payment, "PaymentRefNum") and payment.PaymentRefNum:
        formatted["reference_number"] = payment.PaymentRefNum

    return formatted


def format_item(item: Any) -> Dict[str, Any]:
    """
    Format a QuickBooks Item object for MCP response

    Args:
        item: QuickBooks Item object

    Returns:
        Dictionary with formatted item data
    """
    formatted = {
        "id": item.Id,
        "name": item.Name,
        "type": item.Type,
        "active": item.Active,
    }

    # Optional fields
    if hasattr(item, "Description") and item.Description:
        formatted["description"] = item.Description

    if hasattr(item, "UnitPrice") and item.UnitPrice is not None:
        formatted["unit_price"] = float(item.UnitPrice)

    if hasattr(item, "QtyOnHand") and item.QtyOnHand is not None:
        formatted["quantity_on_hand"] = float(item.QtyOnHand)

    return formatted


def _format_address(addr: Any) -> Dict[str, Any]:
    """
    Format an address object

    Args:
        addr: QuickBooks address object

    Returns:
        Dictionary with formatted address
    """
    address = {}

    if hasattr(addr, "Line1") and addr.Line1:
        address["line1"] = addr.Line1
    if hasattr(addr, "Line2") and addr.Line2:
        address["line2"] = addr.Line2
    if hasattr(addr, "City") and addr.City:
        address["city"] = addr.City
    if hasattr(addr, "CountrySubDivisionCode") and addr.CountrySubDivisionCode:
        address["state"] = addr.CountrySubDivisionCode
    if hasattr(addr, "PostalCode") and addr.PostalCode:
        address["postal_code"] = addr.PostalCode

    return address


def _format_line_item(line: Any) -> Dict[str, Any]:
    """
    Format a line item

    Args:
        line: QuickBooks line item object

    Returns:
        Dictionary with formatted line item
    """
    item = {"amount": float(line.Amount) if hasattr(line, "Amount") else 0.0}

    if hasattr(line, "Description") and line.Description:
        item["description"] = line.Description

    if hasattr(line, "DetailType") and line.DetailType:
        item["detail_type"] = line.DetailType

    # Sales item line detail
    if hasattr(line, "SalesItemLineDetail") and line.SalesItemLineDetail:
        detail = line.SalesItemLineDetail
        if hasattr(detail, "Qty") and detail.Qty:
            item["quantity"] = float(detail.Qty)
        if hasattr(detail, "UnitPrice") and detail.UnitPrice is not None:
            item["unit_price"] = float(detail.UnitPrice)
        if hasattr(detail, "ItemRef") and detail.ItemRef:
            item["item"] = {"id": detail.ItemRef.value, "name": detail.ItemRef.name}

    return item


def format_list(items: List[Any], formatter_func) -> List[Dict[str, Any]]:
    """
    Format a list of QuickBooks objects

    Args:
        items: List of QuickBooks objects
        formatter_func: Function to format each item

    Returns:
        List of formatted dictionaries
    """
    return [formatter_func(item) for item in items]
