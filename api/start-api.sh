#!/bin/bash

# TotalCareIT Partner Portal API - Quick Start Script
# This script starts the backend API server for local development

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}TotalCareIT Partner Portal API${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Warning: .env file not found${NC}"
    echo ""
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo -e "${YELLOW}Please edit .env and add your API credentials:${NC}"
    echo "  - HUBSPOT_ACCESS_TOKEN"
    echo "  - AUTOTASK credentials (optional)"
    echo ""
    echo "To get HubSpot access token:"
    echo "  1. Go to HubSpot Settings → Integrations → Private Apps"
    echo "  2. Create a new private app"
    echo "  3. Add scopes: crm.objects.contacts.read, crm.objects.deals.read, sales-email-read"
    echo "  4. Copy the access token to .env"
    echo ""
    read -p "Press Enter after configuring .env..."
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo ""
echo "Installing/upgrading dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

# Check if installation was successful
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Display configuration
echo -e "${GREEN}Configuration:${NC}"
if grep -q "HUBSPOT_ACCESS_TOKEN=your_hubspot_access_token_here" .env 2>/dev/null; then
    echo -e "  HubSpot: ${YELLOW}⚠️  Not configured${NC}"
else
    echo -e "  HubSpot: ${GREEN}✅ Configured${NC}"
fi

if grep -q "AUTOTASK_API_INTEGRATION_CODE=your_integration_code" .env 2>/dev/null; then
    echo -e "  Autotask: ${YELLOW}⚠️  Not configured (optional)${NC}"
else
    echo -e "  Autotask: ${GREEN}✅ Configured${NC}"
fi

echo ""
echo -e "${GREEN}Starting API server...${NC}"
echo ""
echo -e "API will be available at: ${GREEN}http://localhost:8000${NC}"
echo ""
echo "Available endpoints:"
echo "  - GET  /                              - Welcome message"
echo "  - GET  /api/health                    - Health check"
echo "  - GET  /api/hubspot/crm/summary       - CRM summary"
echo "  - GET  /api/hubspot/contacts/recent   - Recent contacts"
echo "  - GET  /api/hubspot/deals/pipeline    - Sales pipeline"
echo "  - GET  /api/hubspot/sales-metrics     - Sales report metrics"
echo "  - GET  /api/hubspot/analytics         - Website analytics"
echo "  - GET  /api/hubspot/forms             - Form statistics"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""
echo "=========================================="
echo ""

# Start the API server
python3 main.py
