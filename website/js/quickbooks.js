console.log('💼 QuickBooks.js loaded');

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 DOM loaded, initializing QuickBooks page...');

    // Check authentication
    checkAuthentication();

    // Load QuickBooks connection info
    loadQuickBooksInfo();

    // Setup event listeners
    setupEventListeners();
});

function checkAuthentication() {
    // Check if MSAL is loaded
    if (typeof myMSALObj === 'undefined') {
        console.log('⚠️ MSAL not loaded yet, redirecting to login...');
        window.location.href = 'partner-login.html';
        return;
    }

    const accounts = myMSALObj.getAllAccounts();
    if (accounts.length === 0) {
        console.log('❌ Not authenticated, redirecting to login...');
        window.location.href = 'partner-login.html';
        return;
    }

    const account = accounts[0];
    console.log('✅ Authenticated as:', account.username);

    // Update user info in header safely
    const userNameEl = document.getElementById('userName');
    if (userNameEl) {
        userNameEl.textContent = account.name || account.username;
    }
}

function loadQuickBooksInfo() {
    console.log('📊 Loading QuickBooks connection info...');

    // Check if we have QuickBooks connection data in URL params
    const urlParams = new URLSearchParams(window.location.search);
    const realmId = urlParams.get('realmId');
    const state = urlParams.get('state');

    if (realmId) {
        // User just completed OAuth flow
        console.log('✅ QuickBooks connected, Realm ID:', realmId);

        // Store connection info
        localStorage.setItem('qbo_realm_id', realmId);
        localStorage.setItem('qbo_connected_date', new Date().toISOString());

        // Get company info from backend
        fetchCompanyInfo(realmId);
    } else {
        // Check if previously connected
        const storedRealmId = localStorage.getItem('qbo_realm_id');
        if (storedRealmId) {
            fetchCompanyInfo(storedRealmId);
        } else {
            // No connection found
            showNotConnected();
        }
    }
}

async function fetchCompanyInfo(realmId) {
    try {
        // TODO: Call backend API to get company info
        // For now, display stored info
        const connectedDate = localStorage.getItem('qbo_connected_date');

        // Update UI safely
        const companyNameEl = document.getElementById('companyName');
        const connectionDateEl = document.getElementById('connectionDate');

        if (companyNameEl) {
            companyNameEl.textContent = 'QuickBooks Company';
        }

        if (connectionDateEl && connectedDate) {
            connectionDateEl.textContent = new Date(connectedDate).toLocaleDateString();
        }

        console.log('✅ Company info loaded');
    } catch (error) {
        console.error('❌ Failed to fetch company info:', error);
        const companyNameEl = document.getElementById('companyName');
        const connectionDateEl = document.getElementById('connectionDate');

        if (companyNameEl) {
            companyNameEl.textContent = 'Unable to load';
        }
        if (connectionDateEl) {
            connectionDateEl.textContent = '-';
        }
    }
}

function showNotConnected() {
    // Update status card to show "not connected" state
    const statusCard = document.getElementById('connectionStatus');
    statusCard.innerHTML = `
        <div class="qb-status-icon qb-status-warning">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
        </div>
        <h2>QuickBooks Not Connected</h2>
        <p class="qb-status-message">Connect your QuickBooks Online account to enable AI-powered financial insights.</p>
        <div class="qb-actions">
            <button id="connectQBBtn" class="btn-primary">
                Connect QuickBooks Online
            </button>
        </div>
    `;

    // Setup connect button
    document.getElementById('connectQBBtn').addEventListener('click', connectQuickBooks);
}

function connectQuickBooks() {
    // TODO: Redirect to QuickBooks OAuth flow
    // This should go through your backend to initiate OAuth
    console.log('🔗 Initiating QuickBooks connection...');

    // For now, redirect to Intuit OAuth (replace with your actual OAuth endpoint)
    const clientId = 'YOUR_CLIENT_ID';  // TODO: Get from backend config
    const redirectUri = encodeURIComponent(window.location.origin + '/quickbooks.html');
    const state = generateState();

    const authUrl = `https://appcenter.intuit.com/connect/oauth2?client_id=${clientId}&response_type=code&scope=com.intuit.quickbooks.accounting&redirect_uri=${redirectUri}&state=${state}`;

    window.location.href = authUrl;
}

function generateState() {
    // Generate random state for OAuth security
    return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

function setupEventListeners() {
    // Logout button
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            console.log('🚪 Logging out...');

            try {
                await myMSALObj.logoutRedirect({
                    postLogoutRedirectUri: window.location.origin + '/partner-login.html'
                });
            } catch (error) {
                console.error('❌ Logout error:', error);
            }
        });
    }
}

console.log('✅ QuickBooks.js fully loaded');
