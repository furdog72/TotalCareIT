console.log('🔧 Autotask Config.js loaded');

/**
 * Autotask API Configuration
 *
 * IMPORTANT: This file contains configuration for Autotask API integration.
 * Credentials should be stored securely and never committed to version control.
 *
 * For production use:
 * 1. Store credentials in environment variables or secure vault
 * 2. Use a backend proxy to make API calls (avoid exposing credentials in browser)
 * 3. Implement proper error handling and rate limiting
 */

const AutotaskConfig = {
    // API Base URL - Will be determined after authentication
    // Autotask uses zone-specific URLs (e.g., webservices1.autotask.net)
    baseURL: null,

    // Zone information endpoint
    zoneInfoURL: 'https://webservices.autotask.net/ATServicesRest/V1.0/zoneInformation',

    // API Credentials - MUST BE CONFIGURED
    // These should come from secure storage, NOT hardcoded
    credentials: {
        username: '',  // API user email (e.g., apiuser@totalcareit.com)
        secret: '',    // API user secret/password
        integrationCode: ''  // API integration code from Autotask
    },

    // API version
    apiVersion: 'V1.0',

    // Read-only endpoints for reporting
    endpoints: {
        // Tickets/Service Desk
        tickets: '/Tickets/query',
        ticketById: '/Tickets/{id}',

        // Time entries
        timeEntries: '/TimeEntries/query',

        // Companies (clients)
        companies: '/Companies/query',
        companyById: '/Companies/{id}',

        // Contacts
        contacts: '/Contacts/query',
        contactById: '/Contacts/{id}',

        // Activities (calls, meetings, emails)
        activities: '/Tasks/query',

        // Opportunities (sales pipeline)
        opportunities: '/Opportunities/query',

        // Appointments
        appointments: '/Appointments/query',

        // Contracts
        contracts: '/Contracts/query',

        // Resources (users/employees)
        resources: '/Resources/query'
    },

    // Common query filters for reporting
    queries: {
        // Tickets created this month
        ticketsThisMonth: {
            filter: [
                {
                    field: 'createDate',
                    op: 'gte',
                    value: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString()
                }
            ]
        },

        // Active opportunities
        activeOpportunities: {
            filter: [
                {
                    field: 'status',
                    op: 'eq',
                    value: 1  // 1 = Active
                }
            ]
        },

        // Time entries this month
        timeEntriesThisMonth: {
            filter: [
                {
                    field: 'dateWorked',
                    op: 'gte',
                    value: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString()
                }
            ]
        }
    },

    // Request headers builder
    getHeaders: function() {
        return {
            'Content-Type': 'application/json',
            'UserName': this.credentials.username,
            'Secret': this.credentials.secret,
            'ApiIntegrationcode': this.credentials.integrationCode
        };
    },

    // Build full API URL
    getEndpointURL: function(endpoint) {
        if (!this.baseURL) {
            throw new Error('Base URL not set. Call getZoneInfo() first.');
        }
        return `${this.baseURL}/ATServicesRest/${this.apiVersion}${endpoint}`;
    }
};

console.log('✅ Autotask Config.js loaded');

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AutotaskConfig;
}
