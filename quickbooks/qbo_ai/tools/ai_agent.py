"""
QuickBooks AI Agent using Claude Agent SDK with MCP tools
Proper implementation using SDK MCP server pattern
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    tool,
    create_sdk_mcp_server,
    SdkMcpTool
)


class QuickBooksAIAgent:
    """
    AI Agent for sophisticated QuickBooks analysis using Claude Agent SDK
    """

    def __init__(self, anthropic_api_key: str):
        """
        Initialize the AI agent

        Args:
            anthropic_api_key: Anthropic API key
        """
        self.api_key = anthropic_api_key
        self.qb_client = None  # Will be set when analyze is called

    def create_tools(self) -> List[SdkMcpTool]:
        """
        Create MCP tools for QuickBooks queries
        """
        from qbo_ai.tools.query_tools import (
            query_customers as qb_query_customers,
            query_invoices as qb_query_invoices,
            query_payments as qb_query_payments,
            query_items as qb_query_items,
            query_accounts as qb_query_accounts,
            query_vendors as qb_query_vendors,
            query_bills as qb_query_bills
        )

        # Create wrapped tool functions
        @tool("query_customers", "Query customer data from QuickBooks", {
            "limit": int,
            "active_only": bool,
            "name_filter": str
        })
        async def query_customers(args: dict[str, Any]) -> dict[str, Any]:
            """Query customers with optional filters"""
            result = qb_query_customers(
                self.qb_client,
                limit=args.get("limit", 10),
                active_only=args.get("active_only", True),
                name_filter=args.get("name_filter")
            )
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }]
            }

        @tool("query_invoices", "Query invoice data from QuickBooks", {
            "limit": int,
            "customer_id": str,
            "start_date": str,
            "end_date": str,
            "unpaid_only": bool
        })
        async def query_invoices(args: dict[str, Any]) -> dict[str, Any]:
            """Query invoices with optional filters"""
            result = qb_query_invoices(
                self.qb_client,
                limit=args.get("limit", 10),
                customer_id=args.get("customer_id"),
                start_date=args.get("start_date"),
                end_date=args.get("end_date"),
                unpaid_only=args.get("unpaid_only", False)
            )
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }]
            }

        @tool("query_payments", "Query payment records from QuickBooks", {
            "limit": int,
            "customer_id": str,
            "start_date": str,
            "end_date": str
        })
        async def query_payments(args: dict[str, Any]) -> dict[str, Any]:
            """Query payments with optional filters"""
            result = qb_query_payments(
                self.qb_client,
                limit=args.get("limit", 10),
                customer_id=args.get("customer_id"),
                start_date=args.get("start_date"),
                end_date=args.get("end_date")
            )
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }]
            }

        @tool("query_items", "Query items/services from QuickBooks", {
            "limit": int,
            "active_only": bool,
            "item_type": str
        })
        async def query_items(args: dict[str, Any]) -> dict[str, Any]:
            """Query items/services with optional filters"""
            result = qb_query_items(
                self.qb_client,
                limit=args.get("limit", 100),
                active_only=args.get("active_only", True),
                item_type=args.get("item_type")
            )
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }]
            }

        @tool("query_accounts", "Query chart of accounts from QuickBooks", {
            "limit": int,
            "account_type": str,
            "active_only": bool
        })
        async def query_accounts(args: dict[str, Any]) -> dict[str, Any]:
            """Query accounts with optional filters"""
            result = qb_query_accounts(
                self.qb_client,
                limit=args.get("limit", 100),
                account_type=args.get("account_type"),
                active_only=args.get("active_only", True)
            )
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }]
            }

        @tool("query_vendors", "Query vendor data from QuickBooks", {
            "limit": int,
            "active_only": bool,
            "name_filter": str
        })
        async def query_vendors(args: dict[str, Any]) -> dict[str, Any]:
            """Query vendors with optional filters"""
            result = qb_query_vendors(
                self.qb_client,
                limit=args.get("limit", 10),
                active_only=args.get("active_only", True),
                name_filter=args.get("name_filter")
            )
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }]
            }

        @tool("query_bills", "Query bills from QuickBooks", {
            "limit": int,
            "vendor_id": str,
            "start_date": str,
            "end_date": str,
            "unpaid_only": bool
        })
        async def query_bills(args: dict[str, Any]) -> dict[str, Any]:
            """Query bills with optional filters"""
            result = qb_query_bills(
                self.qb_client,
                limit=args.get("limit", 10),
                vendor_id=args.get("vendor_id"),
                start_date=args.get("start_date"),
                end_date=args.get("end_date"),
                unpaid_only=args.get("unpaid_only", False)
            )
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }]
            }

        return [
            query_customers,
            query_invoices,
            query_payments,
            query_items,
            query_accounts,
            query_vendors,
            query_bills
        ]

    def analyze_sync(self, question: str, qb_client, model: str = "claude-3-sonnet-20240229") -> Dict[str, Any]:
        """
        Synchronous version for use with run_in_executor
        """
        import asyncio
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(self.analyze(question, qb_client, model))
        finally:
            loop.close()

    async def analyze(self,
                     question: str,
                     qb_client,
                     model: str = "claude-sonnet-4-5") -> Dict[str, Any]:
        """
        Analyze QuickBooks data using Claude Agent SDK

        Args:
            question: Natural language question to answer
            qb_client: QuickBooks client instance
            model: Claude model to use

        Returns:
            Dictionary with analysis results
        """
        # Store QB client for tool access
        self.qb_client = qb_client

        # Set API key in environment for Claude Agent SDK
        import os
        os.environ['ANTHROPIC_API_KEY'] = self.api_key

        # Create MCP tools
        tools = self.create_tools()

        # Create SDK MCP server with tools
        qb_server = create_sdk_mcp_server(
            name="quickbooks",
            version="1.0.0",
            tools=tools  # Pass the list of decorated functions
        )

        # System prompt for QuickBooks analysis
        system_prompt = """You are an expert QuickBooks financial analyst with access to query tools.

Your capabilities:
- Query customers, invoices, payments, items, accounts, vendors, and bills
- Perform multi-step investigations to find patterns and issues
- Cross-reference different data sources to verify accuracy
- Identify suspicious transactions, duplicates, and discrepancies
- Provide detailed explanations of your findings

Available tools:
- query_customers: Get customer data
- query_invoices: Get invoice data
- query_payments: Get payment data
- query_items: Get item/service data
- query_accounts: Get chart of accounts
- query_vendors: Get vendor data
- query_bills: Get bill data

When investigating:
1. Start with broad queries to understand the data
2. Drill down into specific areas based on findings
3. Cross-reference related data (e.g., invoices vs payments)
4. Provide clear explanations of any issues found
5. Include specific examples and amounts when relevant

Remember: You can call multiple tools iteratively to build understanding."""

        # Configure agent options with MCP server
        import os

        # Ensure API key is in environment for Claude Code
        if self.api_key:
            os.environ['ANTHROPIC_API_KEY'] = self.api_key

        # Detect if we're on EC2 or local development
        import platform
        if platform.system() == "Linux":
            cli_path = "/usr/bin/claude"  # EC2 path
        else:
            cli_path = "/Users/bob/.claude/local/claude"  # Local Mac path

        options = ClaudeAgentOptions(
            model=model,
            system_prompt=system_prompt,
            mcp_servers={"quickbooks": qb_server},
            max_turns=10,  # Allow multiple tool calls
            permission_mode="bypassPermissions",  # Skip permission prompts for server environment
            cli_path=cli_path  # Explicitly specify Claude Code path
        )

        try:
            # Create async generator for the message (following test.py pattern)
            async def message_generator():
                yield {
                    "type": "user",
                    "message": {
                        "role": "user",
                        "content": question
                    }
                }

            # Use ClaudeSDKClient for proper interaction
            final_answer = ""
            tool_calls = 0

            async with ClaudeSDKClient(options) as client:
                # Send the question using async generator pattern
                await client.query(message_generator())

                # Process responses
                async for message in client.receive_response():
                    if isinstance(message, AssistantMessage):
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                final_answer += block.text + "\n"
                            elif hasattr(block, 'name'):
                                # This is a tool call
                                tool_calls += 1

            return {
                "success": True,
                "question": question,
                "answer": final_answer.strip(),
                "tool_calls": tool_calls,
                "model": model
            }

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in analyze: {error_details}")

            return {
                "success": False,
                "question": question,
                "error": str(e),
                "error_details": error_details if len(error_details) < 1000 else error_details[:1000],
                "model": model
            }


def analyze_quickbooks_sync(question: str,
                           qb_client,
                           anthropic_api_key: str,
                           model: str = "claude-3-sonnet-20240229") -> Dict[str, Any]:
    """
    Synchronous wrapper for QuickBooks analysis (for Lambda/non-async environments)

    Args:
        question: Natural language question
        qb_client: QuickBooks client instance
        anthropic_api_key: Anthropic API key
        model: Claude model to use

    Returns:
        Analysis results dictionary
    """
    agent = QuickBooksAIAgent(anthropic_api_key)

    # Run async code in sync context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(
            agent.analyze(question, qb_client, model)
        )
    finally:
        loop.close()