# QBO AI Setup Guide

Complete setup instructions for getting the QuickBooks Online AI environment running on a new Mac.

## Prerequisites

- macOS with Python 3.9 or later
- Git
- QuickBooks Online account (sandbox or production)
- QuickBooks App credentials (Client ID and Secret)

## Step 1: Check Python Installation

```bash
# Check Python version (should be 3.9+)
python3 --version

# If Python is not installed or version is too old:
# Download from https://www.python.org/downloads/
# Or install via Homebrew:
brew install python@3.9
```

## Step 2: Clone the Repository

```bash
# Clone the repo
git clone https://github.com/furdog72/qbo-ai.git

# Navigate to the project
cd qbo-ai
```

## Step 3: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# You should see (.venv) prefix in your terminal prompt
```

## Step 4: Install Dependencies

```bash
# Make sure venv is activated (you should see .venv in prompt)
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

## Step 5: Configure Environment Variables

```bash
# Copy the example env file
cp .env.example .env

# Edit .env file with your credentials
nano .env  # or use any text editor
```

Update the following in `.env`:

```bash
# QuickBooks Online API Configuration
QBO_CLIENT_ID=your_client_id_here
QBO_CLIENT_SECRET=your_client_secret_here
QBO_REDIRECT_URI=http://localhost:8000/callback
QBO_ENVIRONMENT=sandbox  # or 'production'

# Company/Realm ID (obtained after OAuth - leave blank for now)
QBO_COMPANY_ID=

# AI API Keys (optional)
# OPENAI_API_KEY=
# ANTHROPIC_API_KEY=
```

### Where to Get QuickBooks Credentials

1. Go to [Intuit Developer Portal](https://developer.intuit.com/)
2. Sign in and create an app
3. Get your **Client ID** and **Client Secret** from the app settings
4. Set redirect URI to `http://localhost:8000/callback`

## Step 6: Authenticate with QuickBooks

```bash
# Make sure you're in the project directory with venv activated
source .venv/bin/activate

# Navigate to qbo_scripts folder
cd qbo_scripts

# Run the OAuth authentication script
python auth_qbo.py
```

This will:
1. Start a local server on port 8000
2. Display an authorization URL
3. Open that URL in your browser
4. After you authorize, it will save tokens to `.qbo_tokens`
5. Display the Company ID (Realm ID)

**Important**: Copy the Company ID and add it to your `.env` file:

```bash
QBO_COMPANY_ID=1234567890123456  # Replace with your actual Company ID
```

## Step 7: Test the Setup

```bash
# Still in qbo_scripts folder with venv activated
python query_qbo.py
```

You should see output showing:
- Customers from your QuickBooks account
- Invoices
- Chart of Accounts

## Directory Structure

```
qbo-ai/
├── .venv/                  # Virtual environment (created by you)
├── .env                    # Your environment variables (created by you)
├── .env.example            # Example env file
├── requirements.txt        # Python dependencies
├── qbo_ai/                 # Main package (not currently used)
│   ├── __init__.py
│   ├── client.py
│   └── config.py
├── qbo_scripts/            # Standalone scripts
│   ├── .env               # Copy of .env (or symlink)
│   ├── .qbo_tokens        # OAuth tokens (created by auth_qbo.py)
│   ├── auth_qbo.py        # OAuth authentication script
│   └── query_qbo.py       # Example query script
└── examples/               # Additional examples
    ├── basic_usage.py
    ├── oauth_server.py
    └── test_query.py
```

## Common Issues and Troubleshooting

### Issue: `ModuleNotFoundError`

**Solution**: Make sure virtual environment is activated:
```bash
source .venv/bin/activate
```

### Issue: Port 8000 already in use

**Solution**: Kill the process using port 8000:
```bash
lsof -ti:8000 | xargs kill -9
```

### Issue: SSL/OpenSSL warnings

You may see warnings like:
```
NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+
```

This is a warning and won't prevent the scripts from working. To fix it properly, you'd need to upgrade OpenSSL on your system.

### Issue: Environment variables not loading

**Solution**: Make sure:
1. `.env` file is in the project root
2. No extra spaces around the `=` in .env file
3. Virtual environment is activated

### Issue: "Not connected" error

**Solution**:
1. Run `auth_qbo.py` first to get tokens
2. Make sure `QBO_COMPANY_ID` is set in `.env`
3. Make sure `.qbo_tokens` file exists in `qbo_scripts/`

## Quick Reference Commands

```bash
# Activate virtual environment (do this every time you open a new terminal)
source .venv/bin/activate

# Run authentication (only needed once, or when tokens expire)
cd qbo_scripts && python auth_qbo.py

# Run queries
cd qbo_scripts && python query_qbo.py

# Deactivate virtual environment (when done)
deactivate
```

## Working with Multiple Environments

If you need to work with both sandbox and production:

1. Create separate `.env` files:
   - `.env.sandbox`
   - `.env.production`

2. Before running scripts, copy the appropriate one:
   ```bash
   cp .env.sandbox .env
   # or
   cp .env.production .env
   ```

3. Re-run authentication for each environment

## Security Notes

- **Never commit** `.env` or `.qbo_tokens` files to git
- These are already in `.gitignore`
- Access tokens expire periodically - you may need to re-authenticate
- Keep your Client ID and Secret secure

## Next Steps

Once setup is complete, you can:
1. Create custom query scripts in `qbo_scripts/`
2. Modify `query_qbo.py` to query different entities
3. Build AI-powered analysis tools using the QBO data

## Available QuickBooks Entities

You can query these entities:
- Account
- Bill
- BillPayment
- Class
- CreditMemo
- Customer
- Department
- Deposit
- Employee
- Estimate
- Invoice
- Item
- JournalEntry
- Payment
- PaymentMethod
- Purchase
- PurchaseOrder
- RefundReceipt
- SalesReceipt
- TaxCode
- TaxRate
- TimeActivity
- Transfer
- Vendor
- VendorCredit

See [python-quickbooks documentation](https://github.com/sidecars/python-quickbooks) for more details.

## Support

For issues:
- Check the [QuickBooks API documentation](https://developer.intuit.com/app/developer/qbo/docs/get-started)
- Review [python-quickbooks GitHub](https://github.com/sidecars/python-quickbooks)
- Check this project's issues on GitHub
