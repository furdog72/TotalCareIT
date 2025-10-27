// Microsoft 365 Authentication - Partner Portal
// Simplified version with fixed redirect URIs

console.log("🔐 Partner Auth.js loaded");

const msalConfig = {
    auth: {
        clientId: "60f36a5b-4fb3-4723-a5e3-cffb61fc4015",
        authority: "https://login.microsoftonline.com/ebdb5fce-7ff2-4680-9436-04ae800fd041",
        redirectUri: "https://totalcareit.ai/dashboard.html"
    },
    cache: {
        cacheLocation: "sessionStorage",
        storeAuthStateInCookie: false
    }
};

console.log("📋 Config:", msalConfig);

const loginRequest = {
    scopes: ["User.Read", "profile", "openid", "email"]
};

let myMSALObj;

// Initialize MSAL
try {
    console.log("🚀 Initializing MSAL...");
    myMSALObj = new msal.PublicClientApplication(msalConfig);
    console.log("✅ MSAL initialized");

    // Handle redirect
    myMSALObj.handleRedirectPromise()
        .then(response => {
            console.log("✅ Redirect handled:", response);
            if (response) {
                console.log("✅ Authenticated as:", response.account.username);
                if (window.location.pathname.includes('partner-login.html')) {
                    console.log("➡️ Redirecting to dashboard");
                    window.location.href = 'dashboard.html';
                }
            }
        })
        .catch(error => {
            console.error("❌ Redirect error:", error);
            alert("Authentication error: " + error.message);
        });

} catch (error) {
    console.error("❌ MSAL initialization failed:", error);
    alert("Failed to initialize authentication: " + error.message);
}

// Wait for DOM
document.addEventListener('DOMContentLoaded', function() {
    console.log("📄 DOM loaded");

    // Check MSAL library
    if (typeof msal === 'undefined') {
        console.error("❌ MSAL library not loaded!");
        alert("Authentication library not loaded. Please refresh the page.");
        return;
    }

    // Find button
    const loginBtn = document.getElementById('ms365LoginBtn');
    console.log("🔘 Login button:", loginBtn ? "Found" : "NOT FOUND");

    if (loginBtn) {
        console.log("✅ Attaching click handler to button");

        loginBtn.onclick = function(e) {
            e.preventDefault();
            console.log("🖱️ BUTTON CLICKED!");
            console.log("📋 Calling loginRedirect with:", loginRequest);

            try {
                myMSALObj.loginRedirect(loginRequest)
                    .then(() => {
                        console.log("✅ loginRedirect called");
                    })
                    .catch(error => {
                        console.error("❌ Login error:", error);
                        alert("Login failed: " + error.message);
                    });
            } catch (error) {
                console.error("❌ Exception:", error);
                alert("Error: " + error.message);
            }
        };

        console.log("✅ Click handler attached");
    } else {
        // Login button not found - this is okay for pages like dashboard, sales-report, scorecard
        console.log("ℹ️ Login button not found - skipping (this is normal for authenticated pages)");
    }

    console.log("✅ Setup complete");
});

console.log("✅ Partner auth.js fully loaded");
