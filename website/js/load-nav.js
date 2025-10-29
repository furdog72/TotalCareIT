/**
 * Load Partner Portal Navigation
 * This script loads the shared navigation from includes/partner-nav.html
 */

async function loadPartnerNav() {
    try {
        const response = await fetch('includes/partner-nav.html');
        if (!response.ok) throw new Error('Navigation file not found');

        const navHTML = await response.text();

        // Find sidebar placeholder or create one
        let sidebarPlaceholder = document.getElementById('partner-nav-placeholder');

        if (!sidebarPlaceholder) {
            // If no placeholder, insert at beginning of body
            sidebarPlaceholder = document.createElement('div');
            sidebarPlaceholder.id = 'partner-nav-placeholder';
            document.body.insertBefore(sidebarPlaceholder, document.body.firstChild);
        }

        sidebarPlaceholder.innerHTML = navHTML;

        console.log('✅ Partner navigation loaded');
    } catch (error) {
        console.error('❌ Failed to load navigation:', error);
    }
}

// Load navigation when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadPartnerNav);
} else {
    loadPartnerNav();
}
