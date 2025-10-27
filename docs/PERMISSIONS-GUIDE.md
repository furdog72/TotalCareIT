# TotalCare AI Dashboard - Permissions Guide

## Overview

The TotalCare AI Partner Portal now includes a comprehensive role-based permissions system to control access to different sections of the dashboard.

## User Roles and Access

### Admin (Charles Berry only)
**Users**: charles@totalcareit.com, cberry@totalcareit.com

**Access to**:
- ✅ Everything (full access to all sections)
- AWS Billing (Finance tab)
- QuickBooks
- TruMethods QBR
- Sales Report
- Prospective Business
- LinkedIn Performance
- Scorecard
- Dashboard Home

### Finance & Sales (Scott Clark)
**Users**: scott@totalcareit.com, sclark@totalcareit.com

**Access to**:
- ✅ AWS Billing (Finance tab)
- ✅ QuickBooks
- ✅ TruMethods QBR
- ✅ Sales Report
- ✅ Prospective Business
- ✅ LinkedIn Performance
- ✅ Scorecard
- ✅ Dashboard Home

### Sales Only (Jason Snow)
**Users**: jason@totalcareit.com, jsnow@totalcareit.com

**Access to**:
- ✅ Sales Report
- ✅ Prospective Business
- ✅ LinkedIn Performance
- ✅ Scorecard
- ✅ Dashboard Home
- ❌ AWS Billing (Finance tab) - Hidden
- ❌ QuickBooks - Hidden
- ❌ TruMethods QBR - Hidden

### All Other Users
**Default access**:
- ✅ LinkedIn Performance
- ✅ Scorecard
- ✅ Dashboard Home
- ❌ All other sections - Hidden

## Section Permissions Breakdown

| Section | Charles Berry | Scott Clark | Jason Snow | Others |
|---------|--------------|-------------|------------|--------|
| Dashboard Home | ✅ | ✅ | ✅ | ✅ |
| LinkedIn Performance | ✅ | ✅ | ✅ | ✅ |
| Scorecard | ✅ | ✅ | ✅ | ✅ |
| Sales Report | ✅ | ✅ | ✅ | ❌ |
| Prospective Business | ✅ | ✅ | ✅ | ❌ |
| **Finance Tab** | ✅ | ✅ | ❌ | ❌ |
| - AWS Billing | ✅ | ✅ | ❌ | ❌ |
| QuickBooks | ✅ | ✅ | ❌ | ❌ |
| TruMethods QBR | ✅ | ✅ | ❌ | ❌ |

## Implementation Details

### Files Created

1. **[website/js/permissions.js](website/js/permissions.js)** - Main permissions system
   - User role mapping
   - Section permission definitions
   - Permission checking functions
   - Auto-hides unauthorized sections

2. **[website/finance.html](website/finance.html)** - New Finance page
   - AWS Billing section (moved from dashboard)
   - Placeholder for QuickBooks metrics
   - Protected with `data-permission="aws-billing"` attribute

### Files Modified

1. **[website/dashboard.html](website/dashboard.html)**
   - Removed AWS Billing section
   - Added `permissions.js` script
   - Removed `billing.js` script (now only on finance.html)

2. **[website/js/billing.js](website/js/billing.js)**
   - Already updated to work with current month only
   - Loads on finance.html page only

### How Permissions Work

1. **User Authentication**: Microsoft SSO via MSAL
   - User email is extracted from Microsoft Graph API
   - Stored in sessionStorage as `userInfo`

2. **Role Assignment**: Based on email address
   ```javascript
   USER_ROLES = {
       'charles@totalcareit.com': ['admin', 'finance', 'sales', 'all'],
       'scott@totalcareit.com': ['finance', 'sales', 'all'],
       'jason@totalcareit.com': ['sales', 'all']
   }
   ```

3. **Section Protection**: Using `data-permission` attributes
   ```html
   <div class="content-card" data-permission="aws-billing">
       <!-- Protected content -->
   </div>
   ```

4. **Auto-hiding**: JavaScript automatically:
   - Checks user's email and assigned roles
   - Compares against required permissions for each section
   - Hides navigation items and content sections user can't access
   - Shows admin badge for Charles Berry

## Adding New Users

To add new users to the system, edit **[website/js/permissions.js](website/js/permissions.js)**:

```javascript
const USER_ROLES = {
    // Add new user
    'newuser@totalcareit.com': ['sales', 'all']  // Sales access only
    // or
    'newfinance@totalcareit.com': ['finance', 'sales', 'all']  // Finance + Sales
    // or
    'newadmin@totalcareit.com': ['admin', 'finance', 'sales', 'all']  // Full admin
};
```

Then deploy:
```bash
aws s3 cp website/js/permissions.js s3://totalcareit.ai/js/permissions.js
aws cloudfront create-invalidation --distribution-id EBUCQMMFVHWED --paths "/js/permissions.js"
```

## Adding New Sections

To protect a new section, add to **permissions.js**:

```javascript
const SECTION_PERMISSIONS = {
    'new-section-id': ['finance'],  // Only finance role can access
    // or
    'public-section': ['all']  // Everyone can access
};
```

Then add `data-permission` attribute to HTML:
```html
<div class="content-card" data-permission="new-section-id">
    <!-- Protected content -->
</div>
```

## Navigation Links

Navigation links are automatically hidden based on the linked page's primary section:

- `sales-report.html` → Requires 'sales-report' permission
- `prospective-business.html` → Requires 'prospective-business' permission
- `finance.html` → Requires 'aws-billing' permission
- `quickbooks.html` → Requires 'quickbooks' permission
- `trumethods-qbr.html` → Requires 'trumethods-qbr' permission
- `linkedin-performance.html` → Available to 'all'
- `scorecard-complete.html` → Available to 'all'

## Testing Permissions

To test permissions locally:

1. Open browser DevTools → Application → Session Storage
2. Find or create `userInfo` entry
3. Set value to test different users:
```json
{
    "mail": "jason@totalcareit.com",
    "userPrincipalName": "jason@totalcareit.com"
}
```
4. Refresh the page to see permissions applied

## Deployment

All changes have been deployed to:
- S3 bucket: `s3://totalcareit.ai/`
- CloudFront distribution: `EBUCQMMFVHWED`
- Live URL: https://totalcareit.ai

### Deployed Files:
- ✅ dashboard.html (AWS Billing removed)
- ✅ finance.html (New page with AWS Billing)
- ✅ js/permissions.js (New permissions system)
- ✅ js/billing.js (Works on finance.html)

### CloudFront Invalidation:
- Invalidation ID: I4VVSDKEVNNKFGPZZADTK73EWH
- Status: InProgress
- Files: /dashboard.html, /finance.html, /js/permissions.js, /js/billing.js

## Security Considerations

- ⚠️ **Client-side only**: Current implementation is client-side JavaScript. For production, consider:
  - Server-side permission checks
  - API endpoint protection
  - JWT token validation
  - Rate limiting

- ✅ **Current security**:
  - Microsoft SSO authentication required
  - Email-based role assignment
  - Auto-hiding of unauthorized content
  - No sensitive data exposed in JavaScript

## Future Enhancements

1. **Server-side enforcement**: Move permission logic to backend API
2. **Database-driven roles**: Store user roles in database instead of hardcoded
3. **Granular permissions**: Add feature-level permissions (read, write, delete)
4. **Audit logging**: Track who accessed what and when
5. **Permission groups**: Create reusable permission groups/templates
6. **Dynamic navigation**: Generate navigation based on user permissions
