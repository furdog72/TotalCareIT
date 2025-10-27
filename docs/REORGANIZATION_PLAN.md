# TotalCareIT Project Reorganization Plan

## Current Structure Issues
- Everything mixed in qbo-ai folder
- All APIs in single `api/` folder
- Scorecard scripts scattered in root
- Test files everywhere
- No clear separation of concerns

## Proposed New Structure

```
/Users/charles/Projects/TotalCareIT/
├── README.md                          # Main project documentation
├── .env                               # Environment variables (shared)
├── .gitignore                         # Git ignore file
├── requirements.txt                   # Python dependencies (combined)
├── .venv/                            # Virtual environment
│
├── quickbooks/                        # QuickBooks Online Integration
│   ├── README.md                      # QBO-specific docs
│   ├── qbo_ai/                       # QBO Python package
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── config.py
│   │   ├── token_manager.py
│   │   └── local_token_manager.py
│   ├── scripts/                      # QBO scripts
│   │   ├── auth_qbo.py
│   │   └── query_qbo.py
│   ├── examples/                     # QBO examples
│   │   ├── basic_usage.py
│   │   ├── oauth_server.py
│   │   └── test_query.py
│   ├── tests/                        # QBO tests
│   │   ├── test_client.py
│   │   ├── test_refresh_token.py
│   │   └── test_token_refresh.py
│   └── lambda_handler.py             # AWS Lambda for QBO
│
├── integrations/                      # Third-party API integrations
│   ├── __init__.py
│   │
│   ├── hubspot/                      # HubSpot CRM integration
│   │   ├── __init__.py
│   │   ├── service.py                # Main HubSpot service
│   │   ├── config.py                 # HubSpot config
│   │   ├── models.py                 # Data models
│   │   ├── tests/
│   │   │   └── test_hubspot_auth.py
│   │   └── README.md
│   │
│   ├── autotask/                     # Autotask PSA integration
│   │   ├── __init__.py
│   │   ├── service.py                # Main Autotask service
│   │   ├── config.py                 # Autotask config
│   │   ├── models.py                 # Data models
│   │   ├── tests/
│   │   │   └── test_autotask_auth.py
│   │   └── README.md
│   │
│   ├── datto/                        # Datto integration
│   │   ├── __init__.py
│   │   ├── service.py                # Main Datto service
│   │   ├── config.py                 # Datto config
│   │   ├── models.py                 # Data models
│   │   ├── tests/
│   │   │   └── test_datto.py
│   │   └── README.md
│   │
│   ├── linkedin/                     # LinkedIn integration
│   │   ├── __init__.py
│   │   ├── service.py
│   │   ├── data_tracker.py
│   │   ├── performance.py
│   │   └── README.md
│   │
│   └── aws/                          # AWS integrations
│       ├── __init__.py
│       ├── billing.py                # Cost Explorer
│       └── README.md
│
├── scorecard/                        # Scorecard management system
│   ├── __init__.py
│   ├── extractor.py                  # Extract from Excel
│   ├── generator.py                  # Generate HTML
│   ├── collector.py                  # Collect API data
│   ├── deployer.py                   # Deploy to S3
│   ├── scripts/
│   │   ├── extract_and_deploy_scorecard.py
│   │   ├── collect_scorecard_week_oct24.py
│   │   ├── calculate_autotask_metrics.py
│   │   └── build_scorecard_2025.py
│   ├── data/                         # Generated JSON data
│   └── README.md
│
├── website/                          # Frontend website
│   ├── index.html
│   ├── dashboard.html
│   ├── scorecard.html
│   ├── linkedin-performance.html
│   ├── sales-report.html
│   ├── quickbooks.html
│   ├── prospective-business.html
│   ├── finance.html
│   ├── trumethods-qbr.html
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   ├── auth.js
│   │   ├── linkedin-dashboard.js
│   │   ├── billing.js
│   │   └── permissions.js
│   ├── data/                         # Static data files
│   │   └── scorecard-2025.json
│   └── README.md
│
├── api/                              # Backend API (FastAPI)
│   ├── __init__.py
│   ├── main.py                       # FastAPI app entry point
│   ├── routes/                       # API routes
│   │   ├── __init__.py
│   │   ├── hubspot.py
│   │   ├── autotask.py
│   │   ├── linkedin.py
│   │   └── scorecard.py
│   ├── models/                       # Pydantic models
│   │   ├── __init__.py
│   │   └── scorecard.py
│   ├── services/                     # Business logic
│   │   ├── __init__.py
│   │   └── scorecard_service.py
│   └── README.md
│
├── tests/                            # Integration tests
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_integrations.py
│   └── test_scorecard.py
│
├── scripts/                          # Utility scripts
│   ├── deploy_website.sh
│   ├── update_scorecard.sh
│   └── setup_environment.sh
│
├── docs/                             # Documentation
│   ├── API_SETUP.md
│   ├── DEPLOYMENT.md
│   ├── SCORECARD_GUIDE.md
│   └── ARCHITECTURE.md
│
└── deployment/                       # Deployment configs
    ├── aws/
    │   ├── cloudfront_config.json
    │   └── s3_policy.json
    └── README.md
```

## Benefits of This Structure

### 1. **Clear Separation of Concerns**
- Each API integration has its own folder
- QBO integration isolated in `quickbooks/`
- Website separate from backend
- Tests colocated with their modules

### 2. **Scalability**
- Easy to add new integrations (just add new folder in `integrations/`)
- Can deploy each integration independently if needed
- Clear module boundaries

### 3. **Maintainability**
- Easy to find files
- Logical grouping
- Each module has its own README
- Consistent structure across integrations

### 4. **Best Practices**
- Python package structure with `__init__.py`
- Tests near the code they test
- Separate scripts from library code
- Configuration centralized but overridable

### 5. **Development Workflow**
- Each integration can be developed independently
- Easy to run specific tests
- Clear documentation hierarchy
- Simple deployment scripts

## Migration Steps

1. Create new `TotalCareIT` directory structure
2. Move QuickBooks files to `quickbooks/`
3. Separate API integrations into `integrations/`
4. Move scorecard files to `scorecard/`
5. Keep website in `website/`
6. Update all import paths
7. Create documentation
8. Test everything
9. Update deployment scripts

## Additional Recommendations

### 1. Add Configuration Management
```python
# config/settings.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    # HubSpot
    hubspot_api_key: str
    hubspot_hub_id: str

    # Autotask
    autotask_username: str
    autotask_secret: str

    # AWS
    aws_region: str = "us-east-1"
    s3_bucket: str = "totalcareit.ai"

    class Config:
        env_file = ".env"
```

### 2. Add Dependency Injection
```python
# Use dependency injection for services
from fastapi import Depends

def get_hubspot_service():
    return HubSpotService(config=HubSpotConfig.from_env())
```

### 3. Add Logging
```python
# shared/logging.py
import logging
import structlog

def setup_logging():
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )
```

### 4. Add Docker Support
```dockerfile
# Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 5. Add CI/CD
```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to S3
        run: aws s3 sync website/ s3://totalcareit.ai/
```

### 6. Add Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
```

## Migration Commands

```bash
# 1. Create new structure
mkdir -p /Users/charles/Projects/TotalCareIT/{quickbooks,integrations,scorecard,api,tests,scripts,docs,deployment}

# 2. Move qbo-ai content
cd /Users/charles/Projects
cp -r qbo-ai TotalCareIT/

# 3. Reorganize (detailed in next script)
cd TotalCareIT
# ... reorganization commands ...

# 4. Update imports
# ... automated with script ...

# 5. Test
cd /Users/charles/Projects/TotalCareIT
source .venv/bin/activate
pytest tests/

# 6. Deploy
./scripts/deploy_website.sh
```
