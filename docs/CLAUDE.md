# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

QBO AI is a Python-based tool for performing advanced queries and AI-powered analysis on QuickBooks Online (QBO) data. The project uses the Intuit OAuth library and python-quickbooks SDK to interact with the QuickBooks Online API.

## Architecture

### Core Components

- **qbo_ai/client.py**: Main `QBOClient` class handling OAuth flow and API queries
  - OAuth authorization URL generation
  - Token exchange (authorization code for bearer token)
  - Connection management with access/refresh tokens
  - Query execution against QBO entities (Customer, Invoice, Account, etc.)

- **qbo_ai/config.py**: Pydantic-based configuration model (`QBOConfig`) for environment-based settings

- **qbo_ai/__init__.py**: Package entry point, exports `QBOClient`

### Authentication Flow

The OAuth flow is a three-step process:
1. Generate authorization URL via `get_authorization_url()`
2. Exchange auth code and realm_id for tokens via `get_bearer_token()`
3. Connect to API with tokens via `connect(access_token, refresh_token)`

The `company_id` (realm_id) is obtained during OAuth callback and required for API operations.

## Development Commands

### Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your QBO credentials
```

### Running Examples

```bash
# Run basic usage example
python examples/basic_usage.py
```

### Testing

```bash
# Run tests (when test suite is implemented)
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_client.py

# Run with verbose output
python -m pytest -v
```

## Configuration

Environment variables are loaded from `.env` file:
- `QBO_CLIENT_ID`: QuickBooks app client ID (required)
- `QBO_CLIENT_SECRET`: QuickBooks app client secret (required)
- `QBO_REDIRECT_URI`: OAuth redirect URI (default: http://localhost:8000/callback)
- `QBO_ENVIRONMENT`: 'sandbox' or 'production' (default: sandbox)
- `QBO_COMPANY_ID`: Company/realm ID (obtained after OAuth)
- `OPENAI_API_KEY`: Optional, for AI features
- `ANTHROPIC_API_KEY`: Optional, for AI features

## Key Dependencies

- **intuit-oauth**: Intuit OAuth library for authentication
- **python-quickbooks**: QuickBooks API SDK
- **python-dotenv**: Environment variable management
- **pydantic**: Configuration validation
- **pandas**: Data processing (for future analysis features)

## Important Notes

- OAuth tokens must be refreshed periodically (QuickBooks tokens expire)
- The `company_id` is required before calling `connect()` - it's obtained during OAuth flow
- Query strings follow QuickBooks Online Query Language format: `SELECT * FROM {entity} WHERE {condition} MAXRESULTS {limit}`
- AI capabilities (OpenAI/Anthropic) are optional and not yet implemented in core functionality
