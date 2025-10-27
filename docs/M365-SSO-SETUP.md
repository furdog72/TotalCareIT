# Microsoft 365 SSO Setup Guide for Partner Portal

This guide will help you configure Microsoft 365 Single Sign-On (SSO) for the TotalCare AI Partner Portal.

## Prerequisites

- Microsoft 365 admin access (Global Administrator or Application Administrator role)
- Access to Azure Portal (portal.azure.com)
- Your TotalCare IT Microsoft 365 tenant

---

## Part 1: Create Azure AD Application

### Step 1: Access Azure Portal

1. Go to https://portal.azure.com
2. Sign in with your Microsoft 365 admin account
3. In the search bar at the top, type **"Azure Active Directory"** and click on it

### Step 2: Register New Application

1. In the left sidebar, click **App registrations**
2. Click **+ New registration** at the top

### Step 3: Configure Application Details

Fill in the registration form:

**Name**: `TotalCare AI Partner Portal`

**Supported account types**: Select one of:
- **Single tenant** (Recommended): Only your organization's users can access
  - Choose: `Accounts in this organizational directory only (TotalCare IT only - Single tenant)`
- **Multi-tenant**: If you want partners from other organizations to access
  - Choose: `Accounts in any organizational directory (Any Azure AD directory - Multitenant)`

**Redirect URI**:
- Platform: Select **Single-page application (SPA)** from dropdown
- URL: Enter `https://totalcareit.ai/dashboard.html`

**Click "Register"**

### Step 4: Save Your Application Credentials

After registration, you'll see the application overview page. **SAVE THESE VALUES:**

```
Application (client) ID: [Example: 12345678-1234-1234-1234-123456789012]
Directory (tenant) ID: [Example: 87654321-4321-4321-4321-210987654321]
```

**⚠️ IMPORTANT:** Keep these values secure! You'll need them in Part 2.

---

## Part 2: Configure API Permissions

### Step 1: Add Microsoft Graph Permissions

1. In your app, click **API permissions** in the left sidebar
2. Click **+ Add a permission**
3. Select **Microsoft Graph**
4. Select **Delegated permissions**
5. Search for and check these permissions:
   - `User.Read` (Read user profile)
   - `profile` (View users' basic profile)
   - `openid` (Sign users in)
   - `email` (View users' email address)

6. Click **Add permissions** at the bottom

### Step 2: Grant Admin Consent

1. Click the **Grant admin consent for [Your Organization]** button
2. Click **Yes** to confirm
3. You should see green checkmarks next to all permissions under "Status"

---

## Part 3: Configure Authentication Settings

### Step 1: Set Up Redirect URIs

1. In your app, click **Authentication** in the left sidebar
2. Under **Single-page application**, verify you see:
   - `https://totalcareit.ai/dashboard.html`

3. **For testing purposes**, you can also add (optional):
   - `http://localhost:8000/dashboard.html`

### Step 2: Configure Token Settings

Under **Implicit grant and hybrid flows**, ensure these are checked:
- ✅ **Access tokens** (used for implicit flows)
- ✅ **ID tokens** (used for implicit and hybrid flows)

### Step 3: Save Changes

Click **Save** at the bottom

---

## Part 4: Update Website Configuration

Now you need to update the website code with your Azure AD credentials.

### Step 1: Update auth.js File

You have two options:

#### Option A: Update Locally and Redeploy

1. Open the file: `/Users/charles/Projects/qbo-ai/website/js/auth.js`

2. Find this section (lines 3-13):
```javascript
const msalConfig = {
    auth: {
        clientId: "YOUR_CLIENT_ID_HERE",
        authority: "https://login.microsoftonline.com/YOUR_TENANT_ID_HERE",
        redirectUri: "https://totalcareit.ai/dashboard.html"
    },
    cache: {
        cacheLocation: "sessionStorage",
        storeAuthStateInCookie: false
    }
};
```

3. Replace with your actual values:
```javascript
const msalConfig = {
    auth: {
        clientId: "12345678-1234-1234-1234-123456789012", // Your Application (client) ID from Step 4
        authority: "https://login.microsoftonline.com/87654321-4321-4321-4321-210987654321", // Your Directory (tenant) ID
        redirectUri: "https://totalcareit.ai/dashboard.html"
    },
    cache: {
        cacheLocation: "sessionStorage",
        storeAuthStateInCookie: false
    }
};
```

4. Save the file

5. Upload to S3:
```bash
cd /Users/charles/Projects/qbo-ai/website
aws s3 cp js/auth.js s3://totalcareit.ai/js/auth.js --cache-control "public, max-age=3600"
```

6. Invalidate CloudFront cache:
```bash
aws cloudfront create-invalidation --distribution-id EBUCQMMFVHWED --paths "/js/auth.js"
```

#### Option B: Use the Helper Script (I can create this for you)

Let me know your:
- Application (client) ID
- Directory (tenant) ID

And I'll update the file and deploy it for you.

---

## Part 5: Test the SSO Connection

### Step 1: Clear Browser Cache

1. Open your browser
2. Press `Ctrl+Shift+Delete` (Windows) or `Cmd+Shift+Delete` (Mac)
3. Clear cached images and files
4. Close and reopen browser

### Step 2: Test Login Flow

1. Go to https://totalcareit.ai
2. Click **Partner Portal** button in the navigation
3. You should see the Partner Portal login page
4. Click **Sign in with Microsoft 365**
5. You should be redirected to Microsoft login page
6. Enter your Microsoft 365 credentials
7. You may see a consent screen - click **Accept**
8. You should be redirected to the Partner Dashboard

### Step 3: Verify Dashboard Access

You should see:
- Your name in the sidebar
- Your email address
- Navigation items working
- Logout button functional

---

## Troubleshooting

### Error: "AADSTS50011: The reply URL specified in the request does not match"

**Solution**:
- Check that redirect URI in Azure AD matches exactly: `https://totalcareit.ai/dashboard.html`
- No trailing slashes
- Must be HTTPS in production

### Error: "AADSTS65001: The user or administrator has not consented"

**Solution**:
- Go back to Azure Portal → Your App → API Permissions
- Click "Grant admin consent for [Your Organization]"

### Error: "AADSTS7000215: Invalid client secret is provided"

**Solution**:
- For Single-Page Applications (SPA), you don't need a client secret
- Make sure you selected "Single-page application (SPA)" as the platform, not "Web"

### Login Button Does Nothing

**Solution**:
1. Open browser console (F12 → Console tab)
2. Look for errors
3. Verify auth.js was updated with correct credentials
4. Check that CloudFront cache was invalidated
5. Try in incognito/private mode

### "The security token included in the request is invalid"

**Solution**:
- Your Client ID or Tenant ID is incorrect
- Double-check values in Azure Portal
- Make sure you didn't include extra spaces or characters

---

## Security Best Practices

1. **Restrict Access**:
   - In Azure AD, you can assign only specific users/groups to this app
   - Go to: Your App → Enterprise applications → Users and groups

2. **Monitor Sign-ins**:
   - Azure AD → Sign-in logs
   - Review who's accessing the portal

3. **Enable MFA**:
   - Require Multi-Factor Authentication for partner accounts
   - Azure AD → Conditional Access

4. **Regular Review**:
   - Review API permissions quarterly
   - Remove unused permissions
   - Audit access logs

---

## Quick Command Reference

```bash
# Update auth.js file
cd /Users/charles/Projects/qbo-ai/website

# Upload to S3
aws s3 cp js/auth.js s3://totalcareit.ai/js/auth.js

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id EBUCQMMFVHWED --paths "/js/*"

# View CloudFront invalidation status
aws cloudfront get-invalidation --distribution-id EBUCQMMFVHWED --id [INVALIDATION_ID]
```

---

## Need Help?

If you encounter issues:

1. **Check Azure AD Sign-in Logs**:
   - Azure Portal → Azure Active Directory → Sign-in logs
   - Look for failed sign-ins with error codes

2. **Browser Console**:
   - Press F12 → Console tab
   - Look for MSAL or authentication errors

3. **Contact Information**:
   - Email: support@totalcareit.com
   - Documentation: https://docs.microsoft.com/en-us/azure/active-directory/develop/

---

## What's Next?

After SSO is working:

1. **Customize Dashboard**: Add partner-specific data and features
2. **User Management**: Add/remove partner users in Azure AD
3. **Monitoring**: Set up alerts for failed logins
4. **Backup**: Document your configuration for disaster recovery

---

**Last Updated**: 2025-10-23
**Version**: 1.0
