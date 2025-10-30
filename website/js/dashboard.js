// Dashboard functionality for TotalCare AI

// Backend API client
const backendAPIClient = {
    baseURL: 'https://api.totalcareit.ai/api',

    async healthCheck() {
        try {
            const response = await fetch(`${this.baseURL}/health`);
            return await response.json();
        } catch (error) {
            console.error('Health check failed:', error);
            return null;
        }
    },

    async getHubSpotMetrics() {
        try {
            const response = await fetch(`${this.baseURL}/hubspot/sales-metrics`);
            const data = await response.json();
            if (data.success) {
                return data.data;
            }
            return null;
        } catch (error) {
            console.error('Failed to fetch HubSpot metrics:', error);
            return null;
        }
    }
};

document.addEventListener('DOMContentLoaded', function() {
    console.log('📊 Dashboard initializing...');

    // Check backend API health
    checkAPIHealth();

    // Load real dashboard data
    loadDashboardData();

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

// Check API health and update integration status
async function checkAPIHealth() {
    console.log('🔍 Checking API health...');

    try {
        const health = await backendAPIClient.healthCheck();

        if (health && health.status === 'healthy') {
            console.log('✅ Backend API is healthy');

            // Update HubSpot integration status based on health check
            if (health.checks && health.checks.hubspot === 'configured') {
                console.log('✅ HubSpot is configured');
                updateIntegrationStatus('hubspot', 'working', 'Active');
            } else {
                console.log('⚠️ HubSpot not configured');
                updateIntegrationStatus('hubspot', 'error', 'Not Configured');
            }
        } else {
            console.error('❌ Backend API is unhealthy');
            updateIntegrationStatus('hubspot', 'error', 'API Offline');
        }
    } catch (error) {
        console.error('❌ Health check failed:', error);
        updateIntegrationStatus('hubspot', 'error', 'Connection Failed');
    }
}

// Update integration status in UI
function updateIntegrationStatus(integration, status, text) {
    // Find the integration card (case-insensitive)
    const integrationCards = document.querySelectorAll('.integration-item');

    integrationCards.forEach(card => {
        const titleElement = card.querySelector('.integration-info h4');
        if (titleElement && titleElement.textContent.toLowerCase().includes(integration.toLowerCase())) {
            const statusDot = card.querySelector('.status-dot');
            const statusText = card.querySelector('.integration-status span:last-child');

            if (statusDot && statusText) {
                // Remove existing status classes
                statusDot.classList.remove('success', 'warning', 'error');

                // Add new status class
                if (status === 'working') {
                    statusDot.classList.add('success');
                } else if (status === 'warning') {
                    statusDot.classList.add('warning');
                } else {
                    statusDot.classList.add('error');
                }

                statusText.textContent = text;
            }
        }
    });
}

// Load dashboard data from HubSpot API
async function loadDashboardData() {
    console.log('📊 Loading dashboard data from HubSpot API...');

    try {
        const hubspotData = await backendAPIClient.getHubSpotMetrics();

        if (hubspotData) {
            console.log('✅ HubSpot data loaded:', hubspotData);

            // Update dashboard with real data
            updateDashboardStats(hubspotData);

            // Mark HubSpot as working
            updateIntegrationStatus('hubspot', 'working', 'Active');
        } else {
            console.error('❌ Failed to load HubSpot data');

            // Show default values
            showDefaultStats();

            // Mark HubSpot as error
            updateIntegrationStatus('hubspot', 'error', 'Data Load Failed');
        }
    } catch (error) {
        console.error('❌ Error loading dashboard data:', error);

        // Show default values
        showDefaultStats();

        // Mark HubSpot as error
        updateIntegrationStatus('hubspot', 'error', 'Error');
    }

    // Update activity list
    updateActivityList();
}

// Update dashboard stats with real HubSpot data
function updateDashboardStats(data) {
    // Map HubSpot data to dashboard elements
    // For now, use the data we have
    const activeAutomations = data.callsMade || 0;
    const aiModels = Math.ceil(data.conversationsHad / 10) || 0;
    const tasksAutomated = data.prospects || 0;
    const timeSaved = data.closedWon || 0;

    // Update stat cards if they exist
    updateStatValue('activeAutomations', activeAutomations);
    updateStatValue('aiModelsDeployed', aiModels);

    console.log('✅ Dashboard stats updated with HubSpot data');
}

// Helper function to update stat values
function updateStatValue(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = value;
        console.log(`Updated ${elementId} to ${value}`);
    }
}

// Show default stats if API fails
function showDefaultStats() {
    updateStatValue('activeAutomations', '--');
    updateStatValue('aiModelsDeployed', '--');
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
