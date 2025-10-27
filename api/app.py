"""
FastAPI application for QuickBooks AI Agent
"""
import os
import json
import traceback
from typing import Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import secrets

from qbo_ai.mcp_server import QBOMCPServer
from qbo_ai.token_manager import TokenManager
from qbo_ai.tools.query_tools import (
    query_customers,
    query_invoices,
    query_payments,
    query_items,
    query_accounts,
    query_vendors,
    query_bills
)

# Initialize FastAPI app
app = FastAPI(
    title="QuickBooks AI Agent",
    description="AI-powered QuickBooks Online data analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize token manager and MCP server
token_manager = TokenManager()
mcp_server = QBOMCPServer(token_manager=token_manager)

# Security
security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify basic auth credentials"""
    # Get credentials from environment or use defaults
    correct_username = os.environ.get("ADMIN_USERNAME", "admin")
    correct_password = os.environ.get("ADMIN_PASSWORD", "qbo-ai-2025")

    # Use constant-time comparison to prevent timing attacks
    username_ok = secrets.compare_digest(credentials.username.encode("utf8"), correct_username.encode("utf8"))
    password_ok = secrets.compare_digest(credentials.password.encode("utf8"), correct_password.encode("utf8"))

    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# Request models
class AnalyzeRequest(BaseModel):
    question: str
    model: str = "claude-sonnet-4-5"


class QueryRequest(BaseModel):
    parameters: Dict[str, Any] = {}


# API Routes
@app.get("/", response_class=HTMLResponse)
async def serve_frontend(username: str = Depends(verify_credentials)):
    """Serve the debug frontend (protected)"""
    frontend_path = Path("frontend.html")
    if frontend_path.exists():
        with open(frontend_path, "r") as f:
            content = f.read()
            # Update the API endpoint in the frontend
            content = content.replace(
                'https://lozmsexzpslmiwzslnmutd6ini0ljcyu.lambda-url.us-west-2.on.aws/',
                '/api'
            )
            return HTMLResponse(content=content)
    else:
        raise HTTPException(status_code=404, detail="Frontend not found")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if we can get QB client
        qb_client = mcp_server._get_qb_client()
        return {
            "status": "healthy",
            "qb_connected": qb_client is not None,
            "tokens_available": token_manager.tokens_exist()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.post("/api/analyze")
async def analyze(request: AnalyzeRequest):
    """AI analysis endpoint"""
    try:
        # Get QB client
        qb_client = mcp_server._get_qb_client()
        if not qb_client:
            raise HTTPException(status_code=503, detail="QuickBooks client not available")

        # Get Anthropic API key
        anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not anthropic_api_key:
            raise HTTPException(status_code=500, detail="Anthropic API key not configured")

        # Use Claude Agent SDK with proper async handling
        from qbo_ai.tools.ai_agent import QuickBooksAIAgent
        import asyncio

        agent = QuickBooksAIAgent(anthropic_api_key)

        # Run in executor to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            agent.analyze_sync,
            request.question,
            qb_client,
            request.model
        )

        return JSONResponse(content=result)

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
        )


@app.post("/api/query/{entity}")
async def query_entity(entity: str, request: QueryRequest):
    """Direct query endpoint for QuickBooks entities"""
    try:
        # Get QB client
        qb_client = mcp_server._get_qb_client()
        if not qb_client:
            raise HTTPException(status_code=503, detail="QuickBooks client not available")

        # Map entity to query function
        query_functions = {
            "customers": query_customers,
            "invoices": query_invoices,
            "payments": query_payments,
            "items": query_items,
            "accounts": query_accounts,
            "vendors": query_vendors,
            "bills": query_bills
        }

        if entity not in query_functions:
            raise HTTPException(status_code=400, detail=f"Unknown entity: {entity}")

        # Execute query
        query_func = query_functions[entity]
        result = query_func(qb_client, **request.parameters)

        return JSONResponse(content={
            "success": True,
            "data": result
        })

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
        )


# Legacy Lambda compatibility endpoint
@app.post("/api")
async def lambda_compatibility(request: Request):
    """Legacy endpoint for Lambda compatibility"""
    try:
        body = await request.json()
        tool = body.get("tool")
        parameters = body.get("parameters", {})

        if tool == "ai_analyze":
            # AI analysis - use the same async logic
            qb_client = mcp_server._get_qb_client()
            if not qb_client:
                raise HTTPException(status_code=503, detail="QuickBooks client not available")

            anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not anthropic_api_key:
                raise HTTPException(status_code=500, detail="Anthropic API key not configured")

            from qbo_ai.tools.ai_agent import QuickBooksAIAgent
            import asyncio

            agent = QuickBooksAIAgent(anthropic_api_key)

            # Run in executor to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                agent.analyze_sync,
                parameters.get("question", ""),
                qb_client,
                parameters.get("model", "claude-sonnet-4-5")
            )
            return JSONResponse(content=result)

        elif tool in ["query_customers", "query_invoices", "query_payments",
                     "query_items", "query_accounts", "query_vendors", "query_bills"]:
            # Direct query
            entity = tool.replace("query_", "")
            query_req = QueryRequest(parameters=parameters)
            return await query_entity(entity, query_req)

        else:
            raise HTTPException(status_code=400, detail=f"Unknown tool: {tool}")

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)