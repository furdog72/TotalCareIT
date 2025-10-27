# Autotask & HubSpot Integration Summary

## What Changed

### ❌ Previous (Insecure) Approach
- Frontend JavaScript tried to call Autotask API directly
- API credentials would be exposed in browser (visible to anyone)
- **THIS WOULD NOT WORK** - credentials would be stolen immediately

### ✅ New (Secure) Approach
- **Backend API** (FastAPI) handles all external API calls
- Credentials stored securely on server in `.env` file
- Frontend calls backend, backend calls Autotask/HubSpot
- Users never see API credentials

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Partner Portal                           │
│                  (totalcareit.ai)                            │
│                                                               │
│  ┌───────────────────────────────────────────┐              │
│  │   Sales Report Dashboard                   │              │
│  │   (sales-report.html)                      │              │
│  │                                             │              │
│  │   [View ROC Board Tickets]                 │              │
│  │   [View Activity Metrics]                  │              │
│  └───────────────────────────────────────────┘              │
│                        ↓                                      │
│         JavaScript calls backend API                         │
│         (backend-api-client.js)                              │
└───────────────────────┬─────────────────────────────────────┘
                        ↓ HTTPS
┌───────────────────────┴─────────────────────────────────────┐
│              Backend API Server                               │
│            (api.totalcareit.ai:8000)                         │
│                                                               │
│  ┌─────────────────────────────────────┐                    │
│  │   FastAPI Application                │                    │
│  │   (api/main.py)                      │                    │
│  │                                       │                    │
│  │   Endpoints:                          │                    │
│  │   • GET /api/autotask/tickets        │                    │
│  │   • GET /api/autotask/activity       │                    │
│  │   • GET /api/autotask/report/daily   │                    │
│  │   • GET /api/autotask/report/monthly │                    │
│  │   • GET /api/hubspot/stats           │                    │
│  └─────────────────────────────────────┘                    │
│                        ↓                                      │
│  ┌─────────────────────────────────────┐                    │
│  │   Autotask Service                   │                    │
│  │   (api/autotask_service.py)         │                    │
│  │                                       │                    │
│  │   • Authenticates with credentials   │                    │
│  │   • Queries ROC Board tickets ONLY   │                    │
│  │   • Calculates metrics               │                    │
│  │   • Returns sanitized data           │                    │
│  └─────────────────────────────────────┘                    │
└───────────────────────┬─────────────────────────────────────┘
                        ↓ Secure API calls
┌───────────────────────┴─────────────────────────────────────┐
│                  External Services                            │
│                                                               │
│  ┌────────────────────────┐  ┌──────────────────────┐       │
│  │   Autotask API          │  │   HubSpot API         │       │
│  │   (webservices.         │  │   (api.hubspot        │       │
│  │    autotask.net)        │  │    .com)              │       │
│  │                          │  │                        │       │
│  │   ROC Board Tickets     │  │   Website Stats       │       │
│  │   Time Entries          │  │   Form Submissions    │       │
│  │   Companies             │  │   Chat Conversations  │       │
│  └────────────────────────┘  └──────────────────────┘       │
└───────────────────────────────────────────────────────────────┘
```

## Key Points

### 1. Data Source: ROC Board ONLY
- **Not tracking sales/opportunities**
- **Tracking reactive service tickets** from ROC (Reactive Operations Center) board
- Shows ticket metrics:
  - Total tickets
  - Tickets by status
  - Tickets by priority
  - Average resolution time
  - Time logged per ticket

### 2. Security
- **Credentials never exposed to browser**
- Stored in `.env` file on server
- Only backend can access Autotask/HubSpot
- Frontend gets sanitized, filtered data only

### 3. HubSpot Chat
- **Only visible on authenticated pages:**
  - ✅ dashboard.html (after M365 login)
  - ✅ sales-report.html (after M365 login)
- **Not visible on public pages:**
  - ❌ index.html
  - ❌ partner-login.html
  - ❌ client-portal.html

## Files Created

### Backend API (NEW - Required for Security)
```
api/
├── __init__.py                    # Package marker
├── main.py                        # FastAPI application with endpoints
└── autotask_service.py           # Autotask API client and reporting
```

### Frontend Updates
```
website/js/
└── backend-api-client.js         # NEW: Calls backend instead of direct API

website/
├── dashboard.html                # UPDATED: Added HubSpot chat
└── sales-report.html             # UPDATED: Added HubSpot chat
```

### Configuration
```
.env.example                      # UPDATED: Added Autotask/HubSpot config
```

### Documentation
```
BACKEND-API-SETUP.md              # NEW: Complete setup guide
AUTOTASK-SETUP.md                 # UPDATED: Now references backend
INTEGRATION-SUMMARY.md            # NEW: This file
```

## What You Need to Do

### Step 1: Get Autotask ROC Board ID

1. Log in to Autotask as admin
2. Go to: **Admin > Service Desk > Queues**
3. Find your "ROC" or "Reactive Services" board
4. Note the **Queue ID** number
5. You'll need this for `.env` configuration

### Step 2: Configure Backend

1. Create `.env` file:
```bash
cd /Users/charles/Projects/qbo-ai
cp .env.example .env
```

2. Edit `.env` and add:
```bash
# Autotask API (READ-ONLY user)
AUTOTASK_USERNAME=api-readonly@totalcareit.com
AUTOTASK_SECRET=your_password_here
AUTOTASK_INTEGRATION_CODE=your_code_here
AUTOTASK_ROC_BOARD_ID=123456  # <-- YOUR ROC BOARD QUEUE ID

# HubSpot (optional for now)
HUBSPOT_API_KEY=your_key_here
HUBSPOT_HUB_ID=8752461
```

### Step 3: Test Backend Locally

```bash
# Install dependencies (if not already done)
pip install -r requirements.txt

# Start backend API
python -m uvicorn api.main:app --reload --port 8000
```

Visit in browser: http://localhost:8000/
Should see: `{"status": "healthy", ...}`

Test ticket endpoint:
```bash
curl http://localhost:8000/api/autotask/tickets
```

### Step 4: Deploy Backend to Production

You need to deploy the backend API to a server. Options:

**Option A: AWS EC2** (Recommended for now)
- Launch t3.small instance
- Install Python and dependencies
- Run backend with systemd
- Setup nginx reverse proxy
- Configure SSL with Let's Encrypt
- Point `api.totalcareit.ai` to EC2 IP

**Option B: AWS Lambda**
- Package code for Lambda
- Setup API Gateway
- Configure custom domain

**Option C: Docker**
- Build Docker image
- Deploy to ECS or EC2
- Configure load balancer

See `BACKEND-API-SETUP.md` for detailed instructions.

### Step 5: Update Frontend (After Backend is Live)

The frontend is already configured! It will automatically:
- Use `https://api.totalcareit.ai` in production
- Use `http://localhost:8000` in development

No code changes needed once backend is deployed.

## Testing Checklist

### Backend API
- [ ] Backend starts without errors
- [ ] Health check returns "configured" for autotask
- [ ] `/api/autotask/tickets` returns ticket data
- [ ] `/api/autotask/activity` returns activity summary
- [ ] ROC board filter works (only shows ROC tickets)

### Frontend
- [ ] Login to partner portal works (M365 SSO)
- [ ] Sales report page loads
- [ ] HubSpot chat widget appears on dashboard
- [ ] HubSpot chat does NOT appear on public pages
- [ ] Report shows ticket metrics from backend API

### Integration
- [ ] Frontend can reach backend API
- [ ] CORS configured correctly (no browser errors)
- [ ] Data flows: Autotask → Backend → Frontend
- [ ] Tickets from ROC board appear in report

## Current Status

### ✅ Completed
- Backend API created with FastAPI
- Autotask service for ROC board tickets
- Frontend API client for secure calls
- HubSpot chat added to authenticated pages only
- Comprehensive setup documentation

### ⏳ Pending (Your Action Required)
- Get ROC Board Queue ID from Autotask
- Configure `.env` with real credentials
- Test backend locally
- Deploy backend to production server
- Setup `api.totalcareit.ai` DNS record
- Test end-to-end integration

### 🚫 Removed (Security Issues)
- Direct Autotask calls from browser (DELETED)
- Autotask credentials in frontend JavaScript (DELETED)
- Sales/opportunities tracking (CHANGED to tickets only)

## Important Notes

### Why Backend is REQUIRED

**You cannot skip the backend API.** Here's why:

1. **Security:** API credentials in browser = instant theft
2. **CORS:** Autotask API blocks browser requests
3. **Rate Limiting:** Backend can cache and limit requests
4. **Filtering:** Backend only sends ROC board data, not all tickets
5. **Audit Logging:** Backend tracks who accesses what

### ROC Board vs Sales

You correctly identified that we should track:
- **Tickets** from ROC (Reactive Services) board
- **NOT** sales opportunities or pipelines

The backend is configured to filter by `AUTOTASK_ROC_BOARD_ID` to ensure only reactive service tickets are shown.

### HubSpot Chat

Chat widget is configured to load ONLY on:
- dashboard.html (authenticated)
- sales-report.html (authenticated)

It will NOT appear on:
- index.html (public homepage)
- partner-login.html (login page)
- client-portal.html (public placeholder)

## Next Steps

1. **Review this document** - Make sure you understand the architecture
2. **Get ROC Board ID** - Find it in Autotask admin panel
3. **Configure .env** - Add real credentials
4. **Test locally** - Make sure backend starts and returns data
5. **Deploy backend** - Follow BACKEND-API-SETUP.md
6. **Test production** - Verify end-to-end data flow

## Questions?

If anything is unclear, check:
- `BACKEND-API-SETUP.md` - Detailed deployment guide
- `AUTOTASK-SETUP.md` - Autotask-specific configuration
- `api/main.py` - API endpoint definitions
- `api/autotask_service.py` - Autotask integration logic

The backend API is the foundation - once it's running, everything else will work automatically.
