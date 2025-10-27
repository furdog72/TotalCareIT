// Microsoft 365 Authentication using MSAL.js
// TotalCare AI Partner Portal

// Determine redirect URI based on current page
const currentPage = window.location.pathname.split('/').pop() || 'dashboard.html';
const redirectPage = currentPage === 'partner-login.html' ? 'dashboard.html' : currentPage;

const msalConfig = {
    auth: {
        clientId: "60f36a5b-4fb3-4723-a5e3-cffb61fc4015", // TotalCare AI Partner Portal Application ID
        authority: "https://login.microsoftonline.com/ebdb5fce-7ff2-4680-9436-04ae800fd041", // TotalCare IT Tenant ID
        redirectUri: `https://totalcareit.ai/${redirectPage}` // Dynamic redirect based on current page
    },
    cache: {
        cacheLocation: "sessionStorage",
        storeAuthStateInCookie: false
    }
};

const loginRequest = {
    scopes: ["User.Read", "profile", "openid", "email"]
};

let myMSALObj;
let username = "";

console.log("🔐 Auth.js loaded");
console.log("📋 MSAL Config:", {
    clientId: msalConfig.auth.clientId,
    authority: msalConfig.auth.authority,
    redirectUri: msalConfig.auth.redirectUri
});

// Initialize MSAL
function initializeMsal() {
    try {
        console.log("🚀 Initializing MSAL...");
        myMSALObj = new msal.PublicClientApplication(msalConfig);

        // Handle redirect promise
        myMSALObj.handleRedirectPromise()
            .then(response => {
                console.log("✅ Redirect promise resolved:", response);
                handleResponse(response);
            })
            .catch(err => {
                console.error("❌ Redirect Error:", err);
                alert("Authentication error: " + err.message);
            });

        console.log("✅ MSAL initialized successfully");
    } catch (error) {
        console.error("❌ Failed to initialize MSAL:", error);
        alert("Failed to initialize authentication: " + error.message);
    }
}

// Handle the response from redirect
function handleResponse(response) {
    console.log("🔄 Handling response...", response);

    if (response !== null) {
        console.log("✅ User authenticated:", response.account.username);
        username = response.account.username;
        showWelcomeMessage(response.account);

        // If on partner login page, redirect to dashboard
        if (window.location.pathname.includes('partner-login.html')) {
            console.log("➡️ Redirecting to dashboard");
            window.location.href = 'dashboard.html';
        }

        // If on test page, show success
        if (window.location.pathname.includes('test.html')) {
            console.log("✅ Test authentication successful");
            document.getElementById('status').textContent = 'Authenticated!';
            document.getElementById('userInfo').innerHTML = `
                <p><strong>Name:</strong> ${response.account.name}</p>
                <p><strong>Email:</strong> ${response.account.username}</p>
                <p><strong>Account ID:</strong> ${response.account.homeAccountId}</p>
            `;
        }
    } else {
        console.log("ℹ️ No authentication response");

        // Check if user is already signed in
        const currentAccounts = myMSALObj.getAllAccounts();
        console.log("👥 Current accounts:", currentAccounts.length);

        if (currentAccounts.length === 0) {
            console.log("⚠️ No user signed in");

            // List of protected pages that require authentication
            const protectedPages = ['dashboard.html', 'sales-report.html', 'linkedin-performance.html', 'scorecard.html', 'scorecard-complete.html',
                                   'quickbooks.html', 'prospective-business.html', 'finance.html', 'trumethods-qbr.html'];
            const currentPage = window.location.pathname.split('/').pop();

            // If on protected page, redirect to login
            if (protectedPages.includes(currentPage)) {
                console.log("🔒 Protected page - redirecting to login");
                window.location.href = 'partner-login.html';
            }
        } else if (currentAccounts.length === 1) {
            console.log("✅ User already signed in:", currentAccounts[0].username);
            username = currentAccounts[0].username;
            showWelcomeMessage(currentAccounts[0]);
        }
    }
}

// Sign in function
function signIn() {
    console.log("🔑 Sign in initiated...");
    console.log("📋 Login request:", loginRequest);

    try {
        myMSALObj.loginRedirect(loginRequest)
            .then(() => {
                console.log("✅ Login redirect successful");
            })
            .catch(error => {
                console.error("❌ Login Error:", error);
                alert("Login failed: " + error.message + "\n\nPlease contact support if this persists.");
            });
    } catch (error) {
        console.error("❌ Sign in exception:", error);
        alert("Sign in error: " + error.message);
    }
}

// Sign out function
function signOut() {
    console.log("🚪 Sign out initiated...");

    const logoutRequest = {
        account: myMSALObj.getAccountByUsername(username)
    };

    myMSALObj.logoutRedirect(logoutRequest);
}

// Show welcome message in dashboard and other authenticated pages
function showWelcomeMessage(account) {
    console.log("👋 Showing welcome message for:", account.name);

    const userNameElement = document.getElementById('userName');
    const userEmailElement = document.getElementById('userEmail');
    const userAvatarElement = document.getElementById('userAvatar');

    if (userNameElement && account.name) {
        userNameElement.textContent = account.name;
        console.log("✅ Set user name:", account.name);
    }

    if (userEmailElement && account.username) {
        userEmailElement.textContent = account.username;
        console.log("✅ Set user email:", account.username);
    }

    if (userAvatarElement && account.name) {
        const initials = account.name
            .split(' ')
            .map(n => n[0])
            .join('')
            .toUpperCase()
            .substring(0, 2);
        userAvatarElement.textContent = initials;
        console.log("✅ Set user avatar:", initials);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log("📄 DOM Content Loaded");
    console.log("🌍 Current page:", window.location.pathname);

    // Check if MSAL library is loaded
    if (typeof msal === 'undefined') {
        console.error("❌ MSAL library not loaded!");
        alert("Authentication library failed to load. Please check your internet connection and refresh the page.");
        return;
    }

    console.log("✅ MSAL library loaded");

    // Initialize MSAL
    initializeMsal();

    // Set up login button
    const loginBtn = document.getElementById('ms365LoginBtn');
    if (loginBtn) {
        console.log("🔘 Login button found, attaching click handler");

        loginBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log("🖱️ Login button clicked!");
            signIn();
        });

        console.log("✅ Login button click handler attached");
    } else {
        console.log("ℹ️ No login button found on this page");
    }

    // Set up logout button
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        console.log("🔘 Logout button found, attaching click handler");

        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log("🖱️ Logout button clicked!");
            signOut();
        });

        console.log("✅ Logout button click handler attached");
    } else {
        console.log("ℹ️ No logout button found on this page");
    }

    console.log("✅ Authentication setup complete");
});

// Export functions for use in other scripts
window.msalAuth = {
    signIn: signIn,
    signOut: signOut
};

console.log("✅ Auth.js fully loaded and ready");
