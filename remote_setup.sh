#!/bin/bash
# Remote Computer Setup Script
# Run this on any new machine to set up the TotalCareIT environment

set -e

echo "🚀 TotalCareIT Remote Setup"
echo "================================"
echo ""

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d ".git" ]; then
    echo "❌ Error: Please run this script from the TotalCareIT directory"
    echo "   cd ~/Projects/TotalCareIT && ./remote_setup.sh"
    exit 1
fi

echo "📍 Current directory: $(pwd)"
echo ""

# Step 1: Check Python version
echo "1️⃣  Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✅ Found: $PYTHON_VERSION"
else
    echo "   ❌ Python 3 not found. Please install Python 3.9 or higher"
    exit 1
fi
echo ""

# Step 2: Create virtual environment if it doesn't exist
echo "2️⃣  Setting up virtual environment..."
if [ ! -d ".venv" ]; then
    echo "   Creating .venv..."
    python3 -m venv .venv
    echo "   ✅ Virtual environment created"
else
    echo "   ✅ Virtual environment already exists"
fi
echo ""

# Step 3: Install dependencies
echo "3️⃣  Installing Python dependencies..."
source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "   ✅ Dependencies installed"
echo ""

# Step 4: Check for AWS CLI
echo "4️⃣  Checking AWS CLI..."
if command -v aws &> /dev/null; then
    AWS_VERSION=$(aws --version)
    echo "   ✅ Found: $AWS_VERSION"

    # Check if AWS is configured
    if aws sts get-caller-identity &> /dev/null; then
        echo "   ✅ AWS credentials are configured"
        AWS_IDENTITY=$(aws sts get-caller-identity --query 'Account' --output text)
        echo "   📋 AWS Account: $AWS_IDENTITY"
    else
        echo "   ⚠️  AWS CLI found but not configured"
        echo ""
        echo "   You need to configure AWS credentials. Choose one option:"
        echo ""
        echo "   Option 1 - Configure AWS CLI (if you have AWS keys):"
        echo "   $ aws configure"
        echo ""
        echo "   Option 2 - Copy credentials from another computer:"
        echo "   On your main computer: cat ~/.aws/credentials"
        echo "   Then create: mkdir -p ~/.aws && nano ~/.aws/credentials"
        echo ""
        AWS_CONFIGURED=false
    fi
else
    echo "   ❌ AWS CLI not installed"
    echo ""
    echo "   Install AWS CLI:"
    echo "   $ brew install awscli"
    echo ""
    echo "   Or download from: https://aws.amazon.com/cli/"
    echo ""
    AWS_CONFIGURED=false
fi
echo ""

# Step 5: Download secrets from AWS
echo "5️⃣  Downloading API secrets from AWS Secrets Manager..."
if [ "$AWS_CONFIGURED" != "false" ] && command -v aws &> /dev/null && aws sts get-caller-identity &> /dev/null; then
    if [ ! -f ".env" ]; then
        echo "   Downloading secrets..."
        python scripts/setup_secrets_manager.py download
        echo "   ✅ Secrets downloaded to .env"
    else
        echo "   ⚠️  .env file already exists"
        read -p "   Do you want to download fresh secrets? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            python scripts/setup_secrets_manager.py download
            echo "   ✅ Secrets updated"
        else
            echo "   ⏭️  Skipping secret download"
        fi
    fi
else
    echo "   ⚠️  Skipping - AWS not configured"
    echo "   After configuring AWS, run:"
    echo "   $ python scripts/setup_secrets_manager.py download"
fi
echo ""

# Step 6: Summary
echo "================================"
echo "✅ Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo ""

if [ "$AWS_CONFIGURED" == "false" ]; then
    echo "1. Configure AWS credentials:"
    echo "   $ aws configure"
    echo ""
    echo "2. Download API secrets:"
    echo "   $ python scripts/setup_secrets_manager.py download"
    echo ""
fi

echo "3. Test an integration:"
echo "   $ source .venv/bin/activate"
echo "   $ python integrations/hubspot/tests/test_hubspot_auth.py"
echo ""

echo "4. Update the scorecard:"
echo "   $ python scorecard/scripts/extract_and_deploy_scorecard.py"
echo ""

echo "📚 Documentation:"
echo "   - Quick Start: QUICK-START.md"
echo "   - Secure Credentials: docs/SECURE-CREDENTIALS-GUIDE.md"
echo "   - Main README: README.md"
echo ""

echo "🔗 Repository: https://github.com/furdog72/TotalCareIT"
echo ""
