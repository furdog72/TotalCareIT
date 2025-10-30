#!/bin/bash

# TotalCareIT API - Deploy Code to Server Script
# This script is run ON THE SERVER to deploy the API code

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}TotalCareIT API - Code Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Configuration
APP_DIR="/var/www/totalcareit-api"
REPO_URL="https://github.com/furdog72/TotalCareIT.git"

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv

# Clone repository
echo ""
echo -e "${YELLOW}Cloning repository...${NC}"
cd /var/www
sudo rm -rf totalcareit-api
sudo git clone $REPO_URL totalcareit-api
cd $APP_DIR

# Set permissions
sudo chown -R ubuntu:ubuntu $APP_DIR

# Create virtual environment
echo ""
echo -e "${YELLOW}Creating Python virtual environment...${NC}"
cd $APP_DIR/api
python3 -m venv venv
source venv/bin/activate

# Install requirements
echo ""
echo -e "${YELLOW}Installing Python packages...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file from example
echo ""
echo -e "${YELLOW}Creating .env file...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠️  .env file created from example${NC}"
    echo -e "${YELLOW}⚠️  You MUST edit /var/www/totalcareit-api/api/.env and add your API credentials${NC}"
fi

# Create systemd service
echo ""
echo -e "${YELLOW}Creating systemd service...${NC}"
sudo tee /etc/systemd/system/totalcareit-api.service > /dev/null <<EOF
[Unit]
Description=TotalCareIT Partner Portal API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=$APP_DIR/api
Environment="PATH=$APP_DIR/api/venv/bin"
EnvironmentFile=$APP_DIR/api/.env
ExecStart=$APP_DIR/api/venv/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload
sudo systemctl enable totalcareit-api

# Configure Nginx
echo ""
echo -e "${YELLOW}Configuring Nginx...${NC}"
sudo tee /etc/nginx/sites-available/api.totalcareit.ai > /dev/null <<'EOF'
server {
    listen 80;
    server_name api.totalcareit.ai;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # CORS headers
        add_header 'Access-Control-Allow-Origin' 'https://totalcareit.ai' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Content-Type' always;
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/api.totalcareit.ai /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}API Code Deployed Successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo ""
echo "1. Edit API credentials:"
echo "   sudo nano /var/www/totalcareit-api/api/.env"
echo ""
echo "2. Start the API service:"
echo "   sudo systemctl start totalcareit-api"
echo ""
echo "3. Check service status:"
echo "   sudo systemctl status totalcareit-api"
echo ""
echo "4. View logs:"
echo "   sudo journalctl -u totalcareit-api -f"
echo ""
echo "5. Set up SSL certificate:"
echo "   sudo certbot --nginx -d api.totalcareit.ai"
echo ""
echo "6. Test the API:"
echo "   curl http://api.totalcareit.ai/api/health"
echo ""
