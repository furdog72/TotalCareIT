// Dashboard functionality for TotalCare AI

document.addEventListener('DOMContentLoaded', function() {
    // Sidebar navigation
    const navItems = document.querySelectorAll('.nav-item');

    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            const href = this.getAttribute('href');

            // Only prevent default for disabled links or hash links
            // Allow normal navigation for .html page links
            if (!href || href === '#' || this.classList.contains('disabled')) {
                e.preventDefault();

                // Remove active class from all items
                navItems.forEach(navItem => navItem.classList.remove('active'));

                // Add active class to clicked item
                this.classList.add('active');

                // In a real application, this would load different content
                if (href && href !== '#') {
                    const section = href.substring(1);
                    console.log('Navigating to:', section);

                    // Show placeholder message
                    showPlaceholder(section);
                }
            }
            // For .html links, let the browser navigate normally (don't prevent default)
        });
    });

    // Quick action buttons
    const actionCards = document.querySelectorAll('.action-card');

    actionCards.forEach(card => {
        card.addEventListener('click', function() {
            const action = this.querySelector('span').textContent;
            console.log('Action clicked:', action);

            // Show placeholder for each action
            if (action.includes('Automation')) {
                alert('New Automation\n\nThis feature will allow you to create custom automation workflows. Coming soon!');
            } else if (action.includes('Document')) {
                alert('Upload Document\n\nThis feature will allow you to upload and process documents with AI. Coming soon!');
            } else if (action.includes('Analytics')) {
                alert('View Analytics\n\nDetailed analytics and insights will be available here. Coming soon!');
            } else if (action.includes('Support')) {
                window.location.href = 'mailto:support@totalcareit.com?subject=Dashboard Support Request';
            }
        });
    });

    // Simulate loading data
    setTimeout(() => {
        loadDashboardData();
    }, 1000);

    // Add search functionality
    const searchBtn = document.querySelector('.header-actions .btn');
    if (searchBtn) {
        searchBtn.addEventListener('click', function() {
            alert('Search functionality coming soon!\n\nYou will be able to search through automations, documents, and analytics.');
        });
    }
});

// Function to show placeholder messages
function showPlaceholder(section) {
    const messages = {
        'overview': 'Overview section - Your dashboard home',
        'analytics': 'Analytics section - View detailed metrics and insights',
        'automations': 'Automations section - Manage your automation workflows',
        'ai-models': 'AI Models section - View and manage deployed AI models',
        'documents': 'Documents section - Access and manage your documents',
        'settings': 'Settings section - Configure your preferences'
    };

    const message = messages[section] || 'Section coming soon';
    console.log(message);

    // You could update a content area here in a real implementation
    // For now, we'll just log to console
}

// Simulate loading dashboard data
function loadDashboardData() {
    // In a real application, this would fetch data from an API
    console.log('Loading dashboard data...');

    // Simulate some stats
    const stats = {
        activeAutomations: Math.floor(Math.random() * 20),
        aiModels: Math.floor(Math.random() * 10),
        tasksAutomated: Math.floor(Math.random() * 1000),
        timeSaved: Math.floor(Math.random() * 100)
    };

    console.log('Dashboard Stats:', stats);

    // Update activity list with sample data
    updateActivityList();
}

// Update activity list
function updateActivityList() {
    const activityList = document.querySelector('.activity-list');
    if (!activityList) return;

    // Sample activities
    const activities = [
        {
            icon: 'clock',
            title: 'Dashboard initialized',
            time: 'Just now'
        }
    ];

    // Keep the existing activity items
    // In a real app, you'd fetch these from an API
    console.log('Activity list updated');
}

// Function to refresh dashboard data
function refreshDashboard() {
    console.log('Refreshing dashboard...');
    loadDashboardData();
}

// Set up auto-refresh (optional)
// Refresh every 5 minutes
const AUTO_REFRESH_INTERVAL = 5 * 60 * 1000;
let refreshInterval = setInterval(refreshDashboard, AUTO_REFRESH_INTERVAL);

// Clean up interval when page is unloaded
window.addEventListener('beforeunload', function() {
    clearInterval(refreshInterval);
});

// Export functions for external use
window.dashboard = {
    refresh: refreshDashboard,
    loadData: loadDashboardData
};
