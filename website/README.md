# TotalCare AI Website

A professional website showcasing TotalCare IT's AI and automation services, featuring Microsoft 365 authentication for client portal access.

## Features

- **Landing Page**: Showcases AI services and automation solutions
- **Microsoft 365 Authentication**: Secure login using Azure AD
- **Client Dashboard**: Protected portal for accessing company information
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Modern UI**: Clean, professional design with smooth animations

## Project Structure

```
website/
├── index.html              # Main landing page
├── login.html              # Microsoft 365 login page
├── dashboard.html          # Protected client dashboard
├── css/
│   └── styles.css          # All styles for the website
├── js/
│   ├── main.js             # Main website functionality
│   ├── auth.js             # Microsoft 365 authentication logic
│   └── dashboard.js        # Dashboard functionality
└── README.md               # This file
```

## Setup Instructions

### 1. Configure Microsoft 365 Authentication

To enable Microsoft 365 login, you need to set up an Azure AD application:

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to "Azure Active Directory" > "App registrations"
3. Click "New registration"
4. Configure:
   - Name: "TotalCare AI Portal"
   - Supported account types: "Accounts in this organizational directory only"
   - Redirect URI: `https://totalcareit.ai/dashboard.html`
5. After creation, note the:
   - Application (client) ID
   - Directory (tenant) ID

6. Update `js/auth.js`:
   ```javascript
   const msalConfig = {
       auth: {
           clientId: "YOUR_CLIENT_ID_HERE",  // Replace with your client ID
           authority: "https://login.microsoftonline.com/YOUR_TENANT_ID_HERE",  // Replace with your tenant ID
           redirectUri: "https://totalcareit.ai/dashboard.html"
       },
       // ...
   };
   ```

7. In Azure AD, configure API permissions:
   - Add "Microsoft Graph" > "Delegated permissions"
   - Add: `User.Read`, `profile`, `openid`, `email`
   - Grant admin consent

### 2. Deploy to AWS S3

#### Option A: Using AWS CLI

```bash
# Create S3 bucket
aws s3 mb s3://totalcareit.ai --region us-east-1

# Configure bucket for static website hosting
aws s3 website s3://totalcareit.ai --index-document index.html --error-document index.html

# Set bucket policy for public read access
aws s3api put-bucket-policy --bucket totalcareit.ai --policy file://bucket-policy.json

# Upload website files
aws s3 sync . s3://totalcareit.ai --exclude "*.md" --exclude "*.json" --exclude ".git/*"

# Enable versioning (optional but recommended)
aws s3api put-bucket-versioning --bucket totalcareit.ai --versioning-configuration Status=Enabled
```

#### Option B: Using AWS Console

1. Go to AWS S3 Console
2. Create new bucket named `totalcareit.ai`
3. Enable "Static website hosting"
4. Set index document to `index.html`
5. Update bucket policy for public access
6. Upload all website files

### 3. Configure Route53

Update the existing Route53 configuration to add the website A record:

```bash
# Get the hosted zone ID
aws route53 list-hosted-zones --query "HostedZones[?Name=='totalcareit.ai.'].Id" --output text

# Apply the Route53 changes (using the updated configuration)
aws route53 change-resource-record-sets --hosted-zone-id YOUR_ZONE_ID --change-batch file://route53-website-config.json
```

### 4. Set up CloudFront (Optional but Recommended)

For HTTPS and better performance:

1. Create CloudFront distribution
2. Origin: S3 bucket
3. Set up SSL certificate using AWS Certificate Manager
4. Update Route53 A record to point to CloudFront distribution

## Configuration Files Needed

### bucket-policy.json
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::totalcareit.ai/*"
    }
  ]
}
```

### route53-website-config.json
See the generated configuration file for adding website A records.

## Development

To test locally:

```bash
# Option 1: Using Python
python -m http.server 8000

# Option 2: Using Node.js
npx http-server -p 8000

# Then open http://localhost:8000
```

**Note**: Microsoft 365 authentication will only work when:
- Properly configured in Azure AD
- Running on the configured redirect URI (production domain)
- For local testing, add `http://localhost:8000/dashboard.html` to Azure AD redirect URIs

## Security Notes

1. **HTTPS Required**: Microsoft 365 authentication requires HTTPS in production
2. **CORS Configuration**: May need to configure CORS for API calls
3. **Content Security Policy**: Consider adding CSP headers
4. **Environment Variables**: Keep Azure AD credentials secure
5. **Token Storage**: Uses sessionStorage (cleared on browser close)

## Customization

### Updating Content

- **Services**: Edit the `.services-grid` section in `index.html`
- **Automation Features**: Modify `.automation-grid` section
- **Colors**: Update CSS variables in `styles.css`:
  ```css
  :root {
      --primary-color: #4F46E5;
      --secondary-color: #7C3AED;
      /* ... */
  }
  ```

### Adding Features to Dashboard

1. Add new navigation item in `dashboard.html`
2. Create corresponding section in main content area
3. Add handler in `dashboard.js`

## Support

For issues or questions:
- Email: ai@totalcareit.com
- Website: https://totalcareit.com

## License

© 2025 TotalCare IT. All rights reserved.
