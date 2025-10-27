# Scorecard Management System

Automated scorecard generation and deployment system.

## Quick Start
```bash
cd scorecard/scripts
python extract_and_deploy_scorecard.py
```

## What It Does
1. Extracts historical data from Excel
2. Collects live data from APIs (HubSpot, Autotask, Datto)
3. Generates HTML with retractable quarters
4. Deploys to S3 + CloudFront

## Files
- `extract_and_deploy_scorecard.py` - Main deployment script
- `collect_scorecard_week_oct24.py` - Weekly data collection
- `calculate_autotask_metrics.py` - Autotask metrics calculator
