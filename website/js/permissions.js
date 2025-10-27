/**
 * Permissions System for TotalCare AI Dashboard
 * Defines which users can access which sections
 */

// User email to role mapping
const USER_ROLES = {
    'charles@totalcareit.com': ['admin', 'finance', 'sales', 'all'],
    'cberry@totalcareit.com': ['admin', 'finance', 'sales', 'all'],
    'scott@totalcareit.com': ['finance', 'sales', 'all'],
    'sclark@totalcareit.com': ['finance', 'sales', 'all'],
    'jason@totalcareit.com': ['sales', 'all'],
    'jsnow@totalcareit.com': ['sales', 'all']
};

// Section permissions configuration
const SECTION_PERMISSIONS = {
    // Finance sections (Scott Clark, Charles Berry only)
    'aws-billing': ['finance'],
    'quickbooks': ['finance'],
    'trumethods-qbr': ['finance'],

    // Sales sections (Scott Clark, Charles Berry, Jason Snow)
    'sales-report': ['sales'],
    'prospective-business': ['sales'],

    // Everyone can see these
    'linkedin-performance': ['all'],
    'scorecard': ['all'],
    'dashboard-home': ['all']
};

/**
 * Get current user's email from Microsoft authentication
 */
function getCurrentUserEmail() {
    // Get from Microsoft Graph API response stored in session
    const userInfo = sessionStorage.getItem('userInfo');
    if (userInfo) {
        try {
            const user = JSON.parse(userInfo);
            return user.mail || user.userPrincipalName;
        } catch (e) {
            console.error('Error parsing user info:', e);
        }
    }
    return null;
}

/**
 * Get user's roles based on their email
 */
function getUserRoles(userEmail) {
    if (!userEmail) return [];

    // Normalize email to lowercase
    const email = userEmail.toLowerCase();

    // Check exact match
    if (USER_ROLES[email]) {
        return USER_ROLES[email];
    }

    // Check domain patterns
    for (const [pattern, roles] of Object.entries(USER_ROLES)) {
        if (email.includes(pattern)) {
            return roles;
        }
    }

    // Default: all users can see 'all' sections
    return ['all'];
}

/**
 * Check if user has permission to access a section
 */
function hasPermission(sectionId, userEmail = null) {
    const email = userEmail || getCurrentUserEmail();
    const userRoles = getUserRoles(email);
    const requiredRoles = SECTION_PERMISSIONS[sectionId] || ['all'];

    // Check if user has any of the required roles
    return requiredRoles.some(role => userRoles.includes(role));
}

/**
 * Check if user has admin access (Charles Berry only)
 */
function isAdmin(userEmail = null) {
    const email = userEmail || getCurrentUserEmail();
    const userRoles = getUserRoles(email);
    return userRoles.includes('admin');
}

/**
 * Hide sections based on user permissions
 */
function applySectionPermissions() {
    const userEmail = getCurrentUserEmail();

    if (!userEmail) {
        console.warn('No user email found - showing all sections');
        return;
    }

    // Hide sections user doesn't have access to
    document.querySelectorAll('[data-permission]').forEach(element => {
        const sectionId = element.getAttribute('data-permission');

        if (!hasPermission(sectionId, userEmail)) {
            element.style.display = 'none';
            element.classList.add('permission-denied');
        }
    });

    // Hide navigation items user doesn't have access to
    applyNavigationPermissions(userEmail);

    // Show admin indicator if user is admin
    if (isAdmin(userEmail)) {
        showAdminIndicator();
    }
}

/**
 * Apply permissions to navigation items
 */
function applyNavigationPermissions(userEmail) {
    const navPermissions = {
        'sales-report.html': 'sales-report',
        'prospective-business.html': 'prospective-business',
        'quickbooks.html': 'quickbooks',
        'finance.html': 'aws-billing',
        'trumethods-qbr.html': 'trumethods-qbr',
        'linkedin-performance.html': 'linkedin-performance',
        'scorecard-complete.html': 'scorecard'
    };

    document.querySelectorAll('.sidebar-nav .nav-item').forEach(link => {
        const href = link.getAttribute('href');

        if (href && navPermissions[href]) {
            const sectionId = navPermissions[href];

            if (!hasPermission(sectionId, userEmail)) {
                link.style.display = 'none';
                link.classList.add('permission-denied');
            }
        }
    });
}

/**
 * Show admin indicator in UI
 */
function showAdminIndicator() {
    const userNameElement = document.getElementById('userName');
    if (userNameElement && !userNameElement.querySelector('.admin-badge')) {
        const adminBadge = document.createElement('span');
        adminBadge.className = 'admin-badge';
        adminBadge.textContent = 'Admin';
        adminBadge.style.cssText = `
            display: inline-block;
            margin-left: 0.5rem;
            padding: 0.25rem 0.5rem;
            background: #0066cc;
            color: white;
            font-size: 0.7rem;
            border-radius: 4px;
            font-weight: 600;
        `;
        userNameElement.appendChild(adminBadge);
    }
}

/**
 * Get user's display name and role
 */
function getUserDisplayInfo() {
    const email = getCurrentUserEmail();
    const roles = getUserRoles(email);

    let roleName = 'User';
    if (roles.includes('admin')) {
        roleName = 'Administrator';
    } else if (roles.includes('finance')) {
        roleName = 'Finance & Sales';
    } else if (roles.includes('sales')) {
        roleName = 'Sales';
    }

    return {
        email: email,
        roles: roles,
        roleName: roleName
    };
}

// Apply permissions when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applySectionPermissions);
} else {
    applySectionPermissions();
}

// Export functions for use in other scripts
window.PermissionsManager = {
    hasPermission,
    isAdmin,
    getUserRoles,
    getCurrentUserEmail,
    getUserDisplayInfo,
    applySectionPermissions
};
