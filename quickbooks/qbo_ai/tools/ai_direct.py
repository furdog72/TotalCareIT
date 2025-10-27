"""
Direct AI integration using Anthropic API for QuickBooks analysis
This replaces the Claude Agent SDK which requires Claude Code CLI
"""

import json
from typing import Dict, Any, List, Optional
from anthropic import Anthropic
from datetime import datetime

from qbo_ai.tools.query_tools import (
    query_customers,
    query_invoices,
    query_payments,
    query_items,
    query_accounts,
    query_vendors,
    query_bills
)


class QuickBooksAIAnalyzer:
    """
    AI analyzer using direct Anthropic API with tool calling
    """

    def __init__(self, api_key: str):
        """Initialize with Anthropic API key"""
        self.client = Anthropic(api_key=api_key)

    def _create_tools_schema(self) -> List[Dict]:
        """Create tool schemas for Claude"""
        return [
            {
                "name": "query_customers",
                "description": "Query customer data from QuickBooks",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Maximum number of results"},
                        "active_only": {"type": "boolean", "description": "Only return active customers"},
                        "name_filter": {"type": "string", "description": "Filter by customer name"}
                    }
                }
            },
            {
                "name": "query_invoices",
                "description": "Query invoice data from QuickBooks",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Maximum number of results"},
                        "customer_id": {"type": "string", "description": "Filter by customer ID"},
                        "status": {"type": "string", "description": "Filter by status (paid/unpaid)"},
                        "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                        "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"}
                    }
                }
            },
            {
                "name": "query_payments",
                "description": "Query payment data from QuickBooks",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Maximum number of results"},
                        "customer_id": {"type": "string", "description": "Filter by customer ID"},
                        "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                        "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"}
                    }
                }
            },
            {
                "name": "query_items",
                "description": "Query products and services from QuickBooks",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Maximum number of results"},
                        "active_only": {"type": "boolean", "description": "Only return active items"},
                        "type_filter": {"type": "string", "description": "Filter by type (Service/Inventory)"}
                    }
                }
            },
            {
                "name": "query_accounts",
                "description": "Query chart of accounts from QuickBooks",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Maximum number of results"},
                        "account_type": {"type": "string", "description": "Filter by account type"}
                    }
                }
            },
            {
                "name": "query_vendors",
                "description": "Query vendor data from QuickBooks",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Maximum number of results"},
                        "active_only": {"type": "boolean", "description": "Only return active vendors"}
                    }
                }
            },
            {
                "name": "query_bills",
                "description": "Query bills from QuickBooks",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Maximum number of results"},
                        "vendor_id": {"type": "string", "description": "Filter by vendor ID"},
                        "status": {"type": "string", "description": "Filter by status (paid/unpaid)"}
                    }
                }
            }
        ]

    def _execute_tool(self, tool_name: str, arguments: Dict, qb_client) -> Any:
        """Execute a tool with given arguments"""
        tool_map = {
            "query_customers": query_customers,
            "query_invoices": query_invoices,
            "query_payments": query_payments,
            "query_items": query_items,
            "query_accounts": query_accounts,
            "query_vendors": query_vendors,
            "query_bills": query_bills
        }

        if tool_name not in tool_map:
            raise ValueError(f"Unknown tool: {tool_name}")

        # Execute the tool with the QB client and arguments
        tool_func = tool_map[tool_name]
        return tool_func(qb_client, **arguments)

    def analyze(self, question: str, qb_client, model: str = "claude-3-haiku-20240307") -> Dict[str, Any]:
        """
        Analyze QuickBooks data using AI with tool calling

        Args:
            question: Natural language question
            qb_client: QuickBooks client instance
            model: Claude model to use

        Returns:
            Analysis results dictionary
        """
        try:
            # System prompt for QuickBooks analysis
            system_prompt = """You are an expert QuickBooks financial analyst with access to query tools.

When answering questions:
1. Break down complex questions into specific queries
2. Use tools to gather relevant data
3. Analyze patterns, discrepancies, and trends
4. Provide clear, actionable insights
5. Include specific examples and amounts when relevant

You have access to tools for querying customers, invoices, payments, items, accounts, vendors, and bills.
Use these tools to gather data before providing analysis."""

            # Initial message to Claude with tools
            message = self.client.messages.create(
                model=model,
                max_tokens=4000,
                temperature=0,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": question}
                ],
                tools=self._create_tools_schema()
            )

            # Process tool calls and gather results
            tool_results = []
            final_answer = ""

            for content in message.content:
                if content.type == "tool_use":
                    # Execute the tool
                    try:
                        result = self._execute_tool(
                            content.name,
                            content.input,
                            qb_client
                        )
                        tool_results.append({
                            "tool": content.name,
                            "input": content.input,
                            "output": result
                        })
                    except Exception as e:
                        tool_results.append({
                            "tool": content.name,
                            "input": content.input,
                            "error": str(e)
                        })
                elif content.type == "text":
                    final_answer += content.text

            # If tools were used, get final analysis with the results
            if tool_results:
                # Build context with tool results
                tool_context = "Here are the query results:\n\n"
                for result in tool_results:
                    if "error" in result:
                        tool_context += f"Tool {result['tool']} failed: {result['error']}\n\n"
                    else:
                        tool_context += f"Tool {result['tool']} returned:\n{json.dumps(result['output'], indent=2)}\n\n"

                # Get final analysis
                final_message = self.client.messages.create(
                    model=model,
                    max_tokens=4000,
                    temperature=0,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": question},
                        {"role": "assistant", "content": "I'll analyze your QuickBooks data to answer this question."},
                        {"role": "user", "content": tool_context + "Based on this data, please provide your analysis and answer the original question."}
                    ]
                )

                final_answer = final_message.content[0].text if final_message.content else "No response generated"

            return {
                "success": True,
                "question": question,
                "answer": final_answer,
                "tools_used": [r["tool"] for r in tool_results],
                "model": model,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "question": question,
                "error": str(e),
                "model": model,
                "timestamp": datetime.now().isoformat()
            }


# Async wrapper for FastAPI
async def analyze_quickbooks_async(question: str, qb_client, api_key: str, model: str = "claude-3-haiku-20240307") -> Dict[str, Any]:
    """Async wrapper for QuickBooks analysis"""
    analyzer = QuickBooksAIAnalyzer(api_key)
    # Run synchronously since Anthropic client is sync
    return analyzer.analyze(question, qb_client, model)