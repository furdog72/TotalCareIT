#!/bin/bash
# Simple wrapper script to download secrets from AWS Secrets Manager

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the secrets manager
python scripts/setup_secrets_manager.py download
