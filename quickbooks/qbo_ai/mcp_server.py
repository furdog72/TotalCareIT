"""
MCP Server for QuickBooks Online
Implements Model Context Protocol server for QBO integration
"""

import os
from typing import Dict, Any, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent
from quickbooks import QuickBooks
from .token_manager import TokenManager
from .local_token_manager import LocalTokenManager
from .tools.query_tools import (
    query_customers,
    query_invoices,
    query_accounts,
    query_vendors,
    query_bills,
    query_payments,
    query_items,
)


class QBOMCPServer:
    """
    MCP Server for QuickBooks Online integration
    """

    def __init__(self, token_manager=None):
        """
        Initialize QBO MCP Server

        Args:
            token_manager: Optional TokenManager instance (creates new one if not provided)
        """
        self.server = Server("qbo-mcp-server")

        # Use provided token manager or create appropriate one based on environment
        if token_manager:
            self.token_manager = token_manager
        else:
            # Check if running on AWS (has IAM role or AWS credentials)
            if os.getenv('AWS_EXECUTION_ENV') or os.getenv('AWS_CONTAINER_CREDENTIALS_RELATIVE_URI'):
                # Running on AWS, use AWS Secrets Manager
                self.token_manager = TokenManager()
            else:
                # Local development, use local token manager
                self.token_manager = LocalTokenManager()

        self.qb_client: Optional[QuickBooks] = None

        # Register MCP handlers
        self._register_handlers()

    def _initialize_qb_client(self) -> QuickBooks:
        """
        Initialize or refresh QuickBooks client with valid tokens

        Returns:
            Configured QuickBooks client
        """
        # Get valid tokens (will refresh if needed)
        tokens = self.token_manager.get_valid_tokens()

        # Create QuickBooks client
        from intuitlib.client import AuthClient

        auth_client = AuthClient(
            client_id=tokens["client_id"],
            client_secret=tokens["client_secret"],
            redirect_uri=tokens.get("redirect_uri", "http://localhost:8000/callback"),
            environment=tokens.get("environment", "production"),
        )

        # Set tokens
        auth_client.access_token = tokens["access_token"]
        auth_client.refresh_token = tokens["refresh_token"]

        # Create QB client
        qb_client = QuickBooks(
            auth_client=auth_client,
            refresh_token=tokens["refresh_token"],
            company_id=tokens["realm_id"],
        )

        # Add reference to server for token refresh capability
        qb_client._server = self

        return qb_client

    def _get_qb_client(self, force_refresh: bool = False) -> QuickBooks:
        """
        Get QuickBooks client, initializing if necessary

        Args:
            force_refresh: Force re-initialization of the client

        Returns:
            QuickBooks client instance
        """
        if self.qb_client is None or force_refresh:
            self.qb_client = self._initialize_qb_client()
        return self.qb_client

    def refresh_qb_client(self) -> QuickBooks:
        """
        Refresh the QuickBooks client with new tokens

        Returns:
            New QuickBooks client instance with refreshed tokens
        """
        # Force token refresh
        self.token_manager.refresh_tokens()
        # Reinitialize client with fresh tokens
        return self._get_qb_client(force_refresh=True)

    def _register_handlers(self):
        """
        Register MCP tool handlers
        """

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """
            List available MCP tools
            """
            return [
                Tool(
                    name="query_customers",
                    description="Query customer data from QuickBooks Online. Supports filtering by name and active status.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default 10, max 1000)",
                                "default": 10,
                            },
                            "active_only": {
                                "type": "boolean",
                                "description": "Only return active customers",
                                "default": True,
                            },
                            "name_filter": {
                                "type": "string",
                                "description": "Optional filter for customer name (partial match)",
                            },
                        },
                    },
                ),
                Tool(
                    name="query_invoices",
                    description="Query invoice data from QuickBooks Online. Supports filtering by customer, date range, and payment status.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default 10, max 1000)",
                                "default": 10,
                            },
                            "customer_id": {
                                "type": "string",
                                "description": "Optional filter for specific customer ID",
                            },
                            "start_date": {
                                "type": "string",
                                "description": "Optional start date in YYYY-MM-DD format",
                            },
                            "end_date": {
                                "type": "string",
                                "description": "Optional end date in YYYY-MM-DD format",
                            },
                            "unpaid_only": {
                                "type": "boolean",
                                "description": "Only return invoices with outstanding balance",
                                "default": False,
                            },
                        },
                    },
                ),
                Tool(
                    name="query_accounts",
                    description="Query chart of accounts from QuickBooks Online. Supports filtering by account type and active status.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default 100, max 1000)",
                                "default": 100,
                            },
                            "account_type": {
                                "type": "string",
                                "description": "Optional filter for account type (Bank, Income, Expense, etc.)",
                            },
                            "active_only": {
                                "type": "boolean",
                                "description": "Only return active accounts",
                                "default": True,
                            },
                        },
                    },
                ),
                Tool(
                    name="query_vendors",
                    description="Query vendor data from QuickBooks Online. Supports filtering by name and active status.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default 10, max 1000)",
                                "default": 10,
                            },
                            "active_only": {
                                "type": "boolean",
                                "description": "Only return active vendors",
                                "default": True,
                            },
                            "name_filter": {
                                "type": "string",
                                "description": "Optional filter for vendor name (partial match)",
                            },
                        },
                    },
                ),
                Tool(
                    name="query_bills",
                    description="Query bill data from QuickBooks Online. Supports filtering by vendor, date range, and payment status.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default 10, max 1000)",
                                "default": 10,
                            },
                            "vendor_id": {
                                "type": "string",
                                "description": "Optional filter for specific vendor ID",
                            },
                            "start_date": {
                                "type": "string",
                                "description": "Optional start date in YYYY-MM-DD format",
                            },
                            "end_date": {
                                "type": "string",
                                "description": "Optional end date in YYYY-MM-DD format",
                            },
                            "unpaid_only": {
                                "type": "boolean",
                                "description": "Only return bills with outstanding balance",
                                "default": False,
                            },
                        },
                    },
                ),
                Tool(
                    name="query_payments",
                    description="Query payment data from QuickBooks Online. Supports filtering by customer and date range.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default 10, max 1000)",
                                "default": 10,
                            },
                            "customer_id": {
                                "type": "string",
                                "description": "Optional filter for specific customer ID",
                            },
                            "start_date": {
                                "type": "string",
                                "description": "Optional start date in YYYY-MM-DD format",
                            },
                            "end_date": {
                                "type": "string",
                                "description": "Optional end date in YYYY-MM-DD format",
                            },
                        },
                    },
                ),
                Tool(
                    name="query_items",
                    description="Query product/service items from QuickBooks Online. Supports filtering by item type and active status.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default 100, max 1000)",
                                "default": 100,
                            },
                            "active_only": {
                                "type": "boolean",
                                "description": "Only return active items",
                                "default": True,
                            },
                            "item_type": {
                                "type": "string",
                                "description": "Optional filter for item type (Service, Inventory, etc.)",
                            },
                        },
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
            """
            Handle tool execution requests
            """
            try:
                # Get QB client
                qb = self._get_qb_client()

                # Route to appropriate handler
                if name == "query_customers":
                    results = query_customers(qb, **arguments)
                elif name == "query_invoices":
                    results = query_invoices(qb, **arguments)
                elif name == "query_accounts":
                    results = query_accounts(qb, **arguments)
                elif name == "query_vendors":
                    results = query_vendors(qb, **arguments)
                elif name == "query_bills":
                    results = query_bills(qb, **arguments)
                elif name == "query_payments":
                    results = query_payments(qb, **arguments)
                elif name == "query_items":
                    results = query_items(qb, **arguments)
                else:
                    return [
                        TextContent(
                            type="text", text=f"Error: Unknown tool '{name}'"
                        )
                    ]

                # Format response
                import json

                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {"success": True, "data": results, "count": len(results)},
                            indent=2,
                        ),
                    )
                ]

            except Exception as e:
                import json

                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "success": False,
                                "error": str(e),
                                "tool": name,
                                "arguments": arguments,
                            },
                            indent=2,
                        ),
                    )
                ]

    async def run(self):
        """
        Run the MCP server
        """
        from mcp.server.stdio import stdio_server

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, write_stream, self.server.create_initialization_options()
            )


def main():
    """
    Main entry point for running the MCP server
    """
    import asyncio

    server = QBOMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
