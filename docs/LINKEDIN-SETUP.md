# LinkedIn API Integration Setup

## Overview
This guide will help you connect your LinkedIn profile to the TotalCareIT platform for automated data extraction, profile management, and social media posting.

## Step 1: Create LinkedIn Developer App

1. Go to https://www.linkedin.com/developers/apps
2. Click **"Create app"**
3. Fill in the application details:
   - **App name**: TotalCareIT Platform
   - **LinkedIn Page**: Select your company page (Prevailing Networks Inc. dba TotalCareIT)
   - **App logo**: Upload TotalCareIT logo
   - **Legal agreement**: Accept LinkedIn API Terms of Use

4. Click **"Create app"**

## Step 2: Configure OAuth Settings

1. In your app dashboard, go to the **"Auth"** tab
2. Under **"OAuth 2.0 settings"**, add redirect URLs:
   ```
   http://localhost:8000/callback/linkedin
   https://totalcareit.ai/callback/linkedin
   ```

3. Under **"OAuth 2.0 scopes"**, request these permissions:
   - ✅ `r_liteprofile` - Read basic profile info
   - ✅ `r_emailaddress` - Read email address
   - ✅ `w_member_social` - Post updates on your behalf
   - ✅ `rw_organization_admin` - Manage company page (optional)

4. Click **"Update"**

## Step 3: Get API Credentials

1. In the **"Auth"** tab, locate:
   - **Client ID** (e.g., `77abcdef123456`)
   - **Client Secret** (click "Show" to reveal)

2. Copy these values

## Step 4: Update .env File

Add the following to your `.env` file:

```bash
# LinkedIn API Configuration
LINKEDIN_CLIENT_ID=your_client_id_here
LINKEDIN_CLIENT_SECRET=your_client_secret_here
LINKEDIN_ACCESS_TOKEN=  # Will be obtained in Step 5
LINKEDIN_REDIRECT_URI=http://localhost:8000/callback/linkedin
```

## Step 5: Authorize the Application

### Option A: Manual OAuth Flow

1. Open your browser and go to:
   ```
   https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:8000/callback/linkedin&scope=r_liteprofile%20r_emailaddress%20w_member_social
   ```

2. Replace `YOUR_CLIENT_ID` with your actual Client ID

3. Click **"Allow"** to authorize the app

4. You'll be redirected to:
   ```
   http://localhost:8000/callback/linkedin?code=AUTHORIZATION_CODE&state=...
   ```

5. Copy the `AUTHORIZATION_CODE` from the URL

### Option B: Use the Built-in OAuth Endpoint

1. Start the API server:
   ```bash
   source .venv/bin/activate
   python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
   ```

2. Open your browser to:
   ```
   http://localhost:8000/linkedin/authorize
   ```

3. Follow the OAuth flow - the access token will be automatically saved

## Step 6: Exchange Code for Access Token (Manual Method)

If using Manual OAuth (Option A), exchange the authorization code for an access token:

```bash
curl -X POST https://www.linkedin.com/oauth/v2/accessToken \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=authorization_code' \
  -d 'code=AUTHORIZATION_CODE' \
  -d 'redirect_uri=http://localhost:8000/callback/linkedin' \
  -d 'client_id=YOUR_CLIENT_ID' \
  -d 'client_secret=YOUR_CLIENT_SECRET'
```

Response:
```json
{
  "access_token": "AQV...",
  "expires_in": 5184000,
  "refresh_token": "AQX...",
  "refresh_token_expires_in": 31536000
}
```

Copy the `access_token` value and add it to your `.env` file:
```bash
LINKEDIN_ACCESS_TOKEN=AQV...your_access_token_here
```

## Step 7: Test the Connection

```bash
source .venv/bin/activate
python -c "from api.linkedin_integration import LinkedInAPI; api = LinkedInAPI(); print(api.get_profile())"
```

You should see your LinkedIn profile data printed.

## Available Features

### 1. Get Profile Information
```python
from api.linkedin_integration import LinkedInAPI

linkedin = LinkedInAPI()

# Get basic profile
profile = linkedin.get_profile()
print(f"Name: {profile['firstName']} {profile['lastName']}")

# Get detailed profile
details = linkedin.get_profile_details()
print(f"Headline: {details['headline']}")
```

### 2. Post to LinkedIn
```python
# Share a post
response = linkedin.share_post(
    text="Excited to announce our new AI-powered platform!",
    visibility="PUBLIC"  # or "CONNECTIONS"
)
```

### 3. Get Connection Count
```python
connections = linkedin.get_connections_count()
print(f"Total connections: {connections}")
```

### 4. Get Recent Posts
```python
posts = linkedin.get_posts(count=5)
for post in posts:
    print(post['specificContent']['com.linkedin.ugc.ShareContent']['shareCommentary']['text'])
```

## Integration with Scorecard

The LinkedIn API can be integrated with the scorecard to track:
- **COI Attended**: LinkedIn networking events attended
- **Networking Events**: LinkedIn live events participated in
- **Connections Growth**: Track new connections week over week
- **Post Engagement**: Likes, comments, shares on your posts

## Security Best Practices

1. ✅ **Never commit `.env` file to Git**
2. ✅ **Rotate access tokens every 60 days**
3. ✅ **Use refresh tokens** to get new access tokens automatically
4. ✅ **Limit scope** to only required permissions
5. ✅ **Monitor API usage** in LinkedIn Developer Console

## Token Expiration

- **Access Token**: Expires in 60 days (5,184,000 seconds)
- **Refresh Token**: Expires in 1 year (31,536,000 seconds)

Set up automatic token refresh in your application to avoid manual renewal.

## Troubleshooting

### Error: "Invalid access token"
- Token may have expired - re-authorize the application
- Check that `LINKEDIN_ACCESS_TOKEN` is correctly set in `.env`

### Error: "Insufficient permissions"
- Ensure all required scopes are approved in the LinkedIn app
- Re-authorize with updated scopes

### Error: "Redirect URI mismatch"
- Verify redirect URI in LinkedIn app matches exactly (including http vs https)
- Check that redirect URI in authorization URL matches `.env` configuration

## Support

For issues or questions:
- LinkedIn Developer Documentation: https://docs.microsoft.com/en-us/linkedin/
- API Support: https://www.linkedin.com/help/linkedin/answer/a1339724

---

**Created**: 2025-10-27
**Last Updated**: 2025-10-27
**Status**: ✅ Ready for Implementation
