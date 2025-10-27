"""
AWS Lambda handler for QuickBooks AI Agent
Clean implementation using Claude Agent SDK
"""

import json
import os
from qbo_ai.mcp_server import QBOMCPServer
from qbo_ai.token_manager import TokenManager

# Initialize outside handler for warm starts
mcp_server = None
token_manager = None


def get_cors_headers():
    """Get CORS headers for Function URL responses"""
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }


def handler(event, context):
    """
    Lambda handler function

    Args:
        event: Lambda event (HTTP request from Function URL or direct invocation)
        context: Lambda context

    Returns:
        Response dictionary
    """
    global mcp_server, token_manager

    try:
        # Initialize on first invocation
        if mcp_server is None:
            print("Initializing MCP server...")
            token_manager = TokenManager()
            mcp_server = QBOMCPServer(token_manager=token_manager)
            print("MCP server initialized successfully")

        # Log request
        print(f"Received event: {json.dumps(event)}")

        # Parse request - support both direct invocation and HTTP requests
        if 'body' in event:
            # HTTP request from Function URL
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
            tool_name = body.get('tool')
            parameters = body.get('parameters', {})
        else:
            # Direct Lambda invocation
            tool_name = event.get('tool')
            parameters = event.get('parameters', {})

        if not tool_name:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'error': 'Missing required field: tool'
                })
            }

        # Get QB client and attach server reference for token refresh
        qb_client = mcp_server._get_qb_client()
        qb_client._server = mcp_server  # Enable automatic token refresh

        # Route to appropriate tool
        if tool_name == 'ai_analyze':
            # Use the Claude Agent SDK for AI analysis
            from qbo_ai.tools.ai_agent import analyze_quickbooks_sync

            question = parameters.get('question', '')
            model = parameters.get('model', 'claude-3-sonnet-20240229')
            anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY')

            if not anthropic_api_key:
                return {
                    'statusCode': 500,
                    'headers': get_cors_headers(),
                    'body': json.dumps({
                        'success': False,
                        'error': 'ANTHROPIC_API_KEY not configured'
                    })
                }

            result = analyze_quickbooks_sync(
                question=question,
                qb_client=qb_client,
                anthropic_api_key=anthropic_api_key,
                model=model
            )

            return {
                'statusCode': 200,
                'headers': get_cors_headers(),
                'body': json.dumps(result)
            }

        else:
            # Regular query tools
            from qbo_ai.tools.query_tools import (
                query_customers,
                query_invoices,
                query_accounts,
                query_vendors,
                query_bills,
                query_payments,
                query_items,
            )

            tool_map = {
                'query_customers': query_customers,
                'query_invoices': query_invoices,
                'query_accounts': query_accounts,
                'query_vendors': query_vendors,
                'query_bills': query_bills,
                'query_payments': query_payments,
                'query_items': query_items,
            }

            if tool_name not in tool_map:
                return {
                    'statusCode': 400,
                    'headers': get_cors_headers(),
                    'body': json.dumps({
                        'error': f'Unknown tool: {tool_name}',
                        'available_tools': list(tool_map.keys()) + ['ai_analyze']
                    })
                }

            # Execute tool
            print(f"Executing tool: {tool_name} with parameters: {parameters}")
            result = tool_map[tool_name](qb_client, **parameters)
            print(f"Tool executed successfully, returned {len(result)} results")

            return {
                'statusCode': 200,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'success': True,
                    'tool': tool_name,
                    'data': result,
                    'count': len(result)
                })
            }

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        import traceback
        traceback.print_exc()

        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            })
        }