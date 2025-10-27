console.log('🔄 Autotask Sales Adapter.js loaded');

/**
 * Autotask Sales Adapter
 *
 * This adapter transforms Autotask API data into the format
 * expected by the sales report dashboard.
 */

class AutotaskSalesAdapter {
    constructor(autotaskClient) {
        this.client = autotaskClient;
    }

    /**
     * Check if Autotask credentials are configured
     */
    isConfigured() {
        const username = localStorage.getItem('autotask_username');
        const secret = localStorage.getItem('autotask_secret');
        const integrationCode = localStorage.getItem('autotask_integration_code');

        return !!(username && secret && integrationCode);
    }

    /**
     * Load credentials from localStorage
     */
    loadCredentials() {
        if (!this.isConfigured()) {
            return false;
        }

        this.client.config.credentials.username = localStorage.getItem('autotask_username');
        this.client.config.credentials.secret = localStorage.getItem('autotask_secret');
        this.client.config.credentials.integrationCode = localStorage.getItem('autotask_integration_code');

        return true;
    }

    /**
     * Save credentials to localStorage (encrypted storage recommended for production)
     */
    saveCredentials(username, secret, integrationCode) {
        localStorage.setItem('autotask_username', username);
        localStorage.setItem('autotask_secret', secret);
        localStorage.setItem('autotask_integration_code', integrationCode);

        this.client.config.credentials.username = username;
        this.client.config.credentials.secret = secret;
        this.client.config.credentials.integrationCode = integrationCode;
    }

    /**
     * Clear credentials
     */
    clearCredentials() {
        localStorage.removeItem('autotask_username');
        localStorage.removeItem('autotask_secret');
        localStorage.removeItem('autotask_integration_code');

        this.client.config.credentials.username = '';
        this.client.config.credentials.secret = '';
        this.client.config.credentials.integrationCode = '';
    }

    /**
     * Get sales data for the specified date range
     */
    async getSalesData(startDate, endDate) {
        console.log('📊 Getting sales data from Autotask...');

        if (!this.loadCredentials()) {
            console.log('⚠️ Autotask credentials not configured');
            return null;
        }

        try {
            const metrics = await this.client.getSalesMetrics(startDate, endDate);

            // Transform data to match sales report format
            return this.transformToSalesReport(metrics, startDate, endDate);
        } catch (error) {
            console.error('❌ Failed to get Autotask sales data:', error);
            throw error;
        }
    }

    /**
     * Transform Autotask data to sales report format
     */
    transformToSalesReport(autotaskData, startDate, endDate) {
        const { opportunities, activities, appointments } = autotaskData;

        // Count calls from activities
        const calls = activities.filter(a => a.actionType === 4); // 4 = Phone Call
        const outboundCalls = calls.filter(c => c.description?.toLowerCase().includes('outbound') || c.direction === 1);
        const inboundCalls = calls.filter(c => c.description?.toLowerCase().includes('inbound') || c.direction === 2);

        // Count conversations (calls + meetings)
        const meetings = activities.filter(a => a.actionType === 6); // 6 = Meeting
        const conversations = calls.length + meetings.length;

        // Count opportunities by stage
        const prospects = opportunities.length;
        const contacted = opportunities.filter(o => o.stage >= 1).length;
        const qualified = opportunities.filter(o => o.stage >= 2).length;
        const proposal = opportunities.filter(o => o.stage >= 3).length;
        const closedWon = opportunities.filter(o => o.stage === 5).length; // 5 = Closed Won

        return {
            thisMonth: {
                callsMade: calls.length,
                conversationsHad: conversations,
                appointmentsScheduled: appointments.length,
                outboundCalls: outboundCalls.length,
                inboundCalls: inboundCalls.length,
                emailConversations: activities.filter(a => a.actionType === 3).length, // 3 = Email
                meetingConversations: meetings.length,
                prospects: prospects,
                contacted: contacted,
                qualified: qualified,
                proposal: proposal,
                closedWon: closedWon
            },
            upcomingAppointments: this.transformAppointments(appointments),
            recentActivity: this.transformActivities(activities)
        };
    }

    /**
     * Transform appointments to sales report format
     */
    transformAppointments(appointments) {
        return appointments
            .filter(apt => new Date(apt.startDateTime) >= new Date())
            .sort((a, b) => new Date(a.startDateTime) - new Date(b.startDateTime))
            .slice(0, 4)
            .map(apt => ({
                date: new Date(apt.startDateTime).toISOString().split('T')[0],
                time: new Date(apt.startDateTime).toLocaleTimeString('en-US', {
                    hour: 'numeric',
                    minute: '2-digit',
                    hour12: true
                }),
                contact: apt.companyName || 'Unknown',
                type: apt.title || 'Meeting',
                notes: apt.description || ''
            }));
    }

    /**
     * Transform activities to sales report format
     */
    transformActivities(activities) {
        return activities
            .sort((a, b) => new Date(b.createDateTime) - new Date(a.createDateTime))
            .slice(0, 10)
            .map(activity => {
                const date = new Date(activity.createDateTime);
                const type = this.getActivityTypeName(activity.actionType);

                return {
                    datetime: date.toLocaleString('en-US', {
                        year: 'numeric',
                        month: '2-digit',
                        day: '2-digit',
                        hour: 'numeric',
                        minute: '2-digit',
                        hour12: true
                    }),
                    type: type,
                    contact: activity.companyName || 'Unknown',
                    duration: activity.hoursToComplete ? `${Math.round(activity.hoursToComplete * 60)} min` : '-',
                    outcome: activity.status ? this.getOutcomeText(activity.status) : 'In Progress',
                    nextSteps: activity.title || '-'
                };
            });
    }

    /**
     * Get activity type name
     */
    getActivityTypeName(actionType) {
        const types = {
            1: 'Note',
            2: 'To-Do',
            3: 'Email',
            4: 'Phone Call',
            5: 'Internal Meeting',
            6: 'Meeting',
            7: 'External Meeting'
        };
        return types[actionType] || 'Activity';
    }

    /**
     * Get outcome text from status
     */
    getOutcomeText(status) {
        const outcomes = {
            1: 'New',
            2: 'In Progress',
            3: 'Qualified',
            4: 'Meeting Scheduled',
            5: 'Closed Won'
        };
        return outcomes[status] || 'Unknown';
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

console.log('✅ Autotask Sales Adapter.js loaded');

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AutotaskSalesAdapter;
}
