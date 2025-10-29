console.log('🔌 Backend API Client.js loaded');

/**
 * Backend API Client
 *
 * Connects to the secure backend API instead of calling Autotask/HubSpot directly
 * This keeps API credentials secure on the server
 */

class BackendAPIClient {
    constructor() {
        // Backend API URL - configure based on environment
        this.baseURL = this.getAPIBaseURL();
        console.log('📡 Backend API URL:', this.baseURL);
    }

    /**
     * Get the backend API base URL based on environment
     */
    getAPIBaseURL() {
        const hostname = window.location.hostname;

        // Production
        if (hostname === 'totalcareit.ai' || hostname === 'www.totalcareit.ai') {
            return 'https://api.totalcareit.ai';  // TODO: Set up API subdomain
        }

        // Local development
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return 'http://localhost:8000';
        }

        // Fallback
        return 'https://api.totalcareit.ai';
    }

    /**
     * Make a GET request to the backend API
     */
    async get(endpoint, params = {}) {
        const url = new URL(`${this.baseURL}${endpoint}`);

        // Add query parameters
        Object.keys(params).forEach(key => {
            if (params[key] !== null && params[key] !== undefined) {
                url.searchParams.append(key, params[key]);
            }
        });

        console.log('📡 API GET:', url.toString());

        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    // Add authentication header if needed
                    // 'Authorization': `Bearer ${token}`
                },
                credentials: 'include'  // Include cookies if using session auth
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({ error: 'Unknown error' }));
                throw new Error(error.error || `HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('✅ API Response:', data);
            return data;

        } catch (error) {
            console.error('❌ API Error:', error);
            throw error;
        }
    }

    /**
     * Health check - verify backend is accessible
     */
    async healthCheck() {
        try {
            const response = await this.get('/api/health');
            return response;
        } catch (error) {
            console.error('❌ Backend health check failed:', error);
            return null;
        }
    }

    // ===== AUTOTASK ENDPOINTS =====

    /**
     * Get ROC board tickets
     */
    async getROCTickets(startDate = null, endDate = null) {
        const params = {};
        if (startDate) params.start_date = startDate.toISOString();
        if (endDate) params.end_date = endDate.toISOString();

        return this.get('/api/autotask/tickets', params);
    }

    /**
     * Get ticket activity summary
     */
    async getTicketActivity(startDate = null, endDate = null) {
        const params = {};
        if (startDate) params.start_date = startDate.toISOString();
        if (endDate) params.end_date = endDate.toISOString();

        return this.get('/api/autotask/activity', params);
    }

    /**
     * Get daily report
     */
    async getDailyReport(date = null) {
        const params = {};
        if (date) params.date = date.toISOString().split('T')[0];

        return this.get('/api/autotask/report/daily', params);
    }

    /**
     * Get monthly report
     */
    async getMonthlyReport(year = null, month = null) {
        const params = {};
        if (year) params.year = year;
        if (month) params.month = month;

        return this.get('/api/autotask/report/monthly', params);
    }

    // ===== HUBSPOT ENDPOINTS =====

    /**
     * Get HubSpot CRM summary
     */
    async getHubSpotCRMSummary() {
        return this.get('/api/hubspot/crm/summary');
    }

    /**
     * Get recent HubSpot contacts
     */
    async getHubSpotRecentContacts(limit = 10) {
        return this.get('/api/hubspot/contacts/recent', { limit });
    }

    /**
     * Get HubSpot deals pipeline
     */
    async getHubSpotDealsPipeline() {
        return this.get('/api/hubspot/deals/pipeline');
    }

    /**
     * Get HubSpot website analytics
     */
    async getHubSpotAnalytics() {
        return this.get('/api/hubspot/analytics');
    }

    /**
     * Get HubSpot form statistics
     */
    async getHubSpotFormStats() {
        return this.get('/api/hubspot/forms');
    }

    /**
     * Get HubSpot sales metrics (for sales report dashboard)
     */
    async getHubSpotSalesMetrics() {
        return this.get('/api/hubspot/sales-metrics');
    }
}

/**
 * Adapter for Sales Report
 * Transforms backend API data into the format expected by the sales report dashboard
 */
class SalesReportAdapter {
    constructor(apiClient) {
        this.api = apiClient;
    }

    /**
     * Check if backend API is available
     */
    async isAvailable() {
        const health = await this.api.healthCheck();
        return health && health.checks && (health.checks.hubspot === 'configured' || health.checks.autotask === 'configured');
    }

    /**
     * Get sales report data from HubSpot via backend API
     */
    async getSalesData(startDate = null, endDate = null) {
        console.log('📊 Getting sales data from HubSpot backend API...');

        try {
            // Get sales metrics from HubSpot
            const response = await this.api.getHubSpotSalesMetrics();

            if (!response.success) {
                throw new Error(response.error || 'Failed to fetch sales metrics');
            }

            const metrics = response.data;

            // Return data in sales report format
            return {
                thisMonth: {
                    callsMade: metrics.callsMade || 0,
                    conversationsHad: metrics.conversationsHad || 0,
                    appointmentsScheduled: metrics.appointmentsScheduled || 0,
                    outboundCalls: metrics.outboundCalls || 0,
                    inboundCalls: metrics.inboundCalls || 0,
                    emailConversations: metrics.emailConversations || 0,
                    meetingConversations: metrics.meetingConversations || 0,
                    prospects: metrics.prospects || 0,
                    contacted: metrics.contacted || 0,
                    qualified: metrics.qualified || 0,
                    proposal: metrics.proposal || 0,
                    closedWon: metrics.closedWon || 0
                },
                lastMonth: {
                    callsMade: 0,
                    conversationsHad: 0,
                    appointmentsScheduled: 0
                },
                upcomingAppointments: [],
                recentActivity: []
            };

        } catch (error) {
            console.error('❌ Failed to get sales data from HubSpot:', error);
            throw error;
        }
    }

    /**
     * DEPRECATED - Old method for ticket-based data
     * Get sales report data for date range
     * Transforms ticket data into sales metrics format
     */
    async getSalesDataFromTickets(startDate, endDate) {
        console.log('📊 Getting sales data from Autotask backend API...');

        try {
            // Get ticket metrics and activity from backend
            const [ticketsResponse, activityResponse] = await Promise.all([
                this.api.getROCTickets(startDate, endDate),
                this.api.getTicketActivity(startDate, endDate)
            ]);

            const tickets = ticketsResponse.data || {};
            const activity = activityResponse.data || {};

            // Transform to sales report format
            return this.transformToSalesReport(tickets, activity);

        } catch (error) {
            console.error('❌ Failed to get sales data:', error);
            throw error;
        }
    }

    /**
     * DEPRECATED - Transform ticket data to sales report format
     */
    transformToSalesReport(tickets, activity) {
        // Map ticket metrics to sales report metrics
        // ROC Board tickets ≠ sales, but we're showing ticket activity

        return {
            thisMonth: {
                // Use ticket counts as "activity" metrics
                callsMade: 0,  // Not tracking calls in tickets
                conversationsHad: tickets.total || 0,  // Total tickets = conversations
                appointmentsScheduled: 0,  // Not tracking appointments here

                // Ticket breakdown
                outboundCalls: 0,
                inboundCalls: tickets.total || 0,  // ROC tickets are reactive (inbound)
                emailConversations: 0,
                meetingConversations: 0,

                // Activity summary
                totalTickets: tickets.total || 0,
                totalHoursLogged: activity.total_hours_logged || 0,
                avgHoursPerTicket: activity.avg_hours_per_ticket || 0,

                // Sales funnel (not applicable for tickets, use ticket statuses instead)
                prospects: 0,
                contacted: 0,
                qualified: 0,
                proposal: 0,
                closedWon: Object.values(tickets.by_status || {}).reduce((a, b) => a + b, 0)
            },
            tickets: tickets,  // Include full ticket data
            activity: activity,
            recentActivity: this.transformTicketsToActivity(tickets.tickets || []),
            upcomingAppointments: []
        };
    }

    /**
     * DEPRECATED - Transform tickets to activity format for display
     */
    transformTicketsToActivity(tickets) {
        return tickets.slice(0, 10).map(ticket => ({
            datetime: new Date(ticket.createDate).toLocaleString('en-US', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: 'numeric',
                minute: '2-digit',
                hour12: true
            }),
            type: 'Ticket',
            contact: `Ticket #${ticket.ticketNumber}: ${ticket.title}`,
            duration: '-',
            outcome: ticket.status,
            nextSteps: ticket.completedDate ? 'Completed' : 'In Progress'
        }));
    }

    /**
     * Get date range for common periods
     */
    getDateRange(period) {
        const now = new Date();
        const ranges = {
            today: {
                start: new Date(now.getFullYear(), now.getMonth(), now.getDate()),
                end: new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59)
            },
            yesterday: {
                start: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1),
                end: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1, 23, 59, 59)
            },
            thisWeek: {
                start: new Date(now.getFullYear(), now.getMonth(), now.getDate() - now.getDay()),
                end: now
            },
            lastWeek: {
                start: new Date(now.getFullYear(), now.getMonth(), now.getDate() - now.getDay() - 7),
                end: new Date(now.getFullYear(), now.getMonth(), now.getDate() - now.getDay() - 1)
            },
            thisMonth: {
                start: new Date(now.getFullYear(), now.getMonth(), 1),
                end: now
            },
            lastMonth: {
                start: new Date(now.getFullYear(), now.getMonth() - 1, 1),
                end: new Date(now.getFullYear(), now.getMonth(), 0, 23, 59, 59)
            },
            thisQuarter: {
                start: new Date(now.getFullYear(), Math.floor(now.getMonth() / 3) * 3, 1),
                end: now
            },
            thisYear: {
                start: new Date(now.getFullYear(), 0, 1),
                end: now
            }
        };

        return ranges[period] || ranges.thisMonth;
    }
}

console.log('✅ Backend API Client.js loaded');

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { BackendAPIClient, SalesReportAdapter };
}
