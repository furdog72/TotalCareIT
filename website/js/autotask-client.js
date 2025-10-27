console.log('🔌 Autotask Client.js loaded');

/**
 * Autotask API Client
 *
 * SECURITY WARNING:
 * This client is designed to run in the browser for demonstration purposes.
 * For production use, you MUST implement a backend proxy to:
 * 1. Protect API credentials from exposure
 * 2. Implement proper rate limiting
 * 3. Add caching to reduce API calls
 * 4. Handle errors and retries securely
 *
 * RECOMMENDED ARCHITECTURE:
 * Browser -> Backend API Proxy -> Autotask API
 */

class AutotaskClient {
    constructor(config) {
        this.config = config || AutotaskConfig;
        this.isInitialized = false;
        this.cache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
    }

    /**
     * Initialize the client by determining the correct zone URL
     */
    async initialize() {
        console.log('🚀 Initializing Autotask client...');

        if (!this.config.credentials.username || !this.config.credentials.secret) {
            throw new Error('Autotask credentials not configured. Please set username and secret.');
        }

        try {
            // Get zone information
            const zoneInfo = await this.getZoneInfo();
            this.config.baseURL = zoneInfo.url;
            this.isInitialized = true;

            console.log('✅ Autotask client initialized. Base URL:', this.config.baseURL);
            return zoneInfo;
        } catch (error) {
            console.error('❌ Failed to initialize Autotask client:', error);
            throw error;
        }
    }

    /**
     * Get zone information to determine the correct API endpoint
     */
    async getZoneInfo() {
        console.log('🌍 Getting zone information...');

        const response = await fetch(this.config.zoneInfoURL, {
            method: 'GET',
            headers: {
                'UserName': this.config.credentials.username,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`Zone info request failed: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        console.log('✅ Zone info retrieved:', data);
        return data;
    }

    /**
     * Make a query request to Autotask API
     */
    async query(endpoint, queryFilter = null) {
        if (!this.isInitialized) {
            await this.initialize();
        }

        const cacheKey = `${endpoint}_${JSON.stringify(queryFilter)}`;

        // Check cache
        if (this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (Date.now() - cached.timestamp < this.cacheTimeout) {
                console.log('📦 Returning cached data for:', endpoint);
                return cached.data;
            }
        }

        console.log('🔍 Querying Autotask:', endpoint);

        try {
            const url = this.config.getEndpointURL(endpoint);
            const response = await fetch(url, {
                method: 'POST',
                headers: this.config.getHeaders(),
                body: JSON.stringify(queryFilter || {})
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Autotask API error: ${response.status} ${response.statusText} - ${errorText}`);
            }

            const data = await response.json();

            // Cache the result
            this.cache.set(cacheKey, {
                data: data,
                timestamp: Date.now()
            });

            console.log('✅ Query successful. Records returned:', data.items?.length || 0);
            return data;
        } catch (error) {
            console.error('❌ Query failed:', error);
            throw error;
        }
    }

    /**
     * Get a single entity by ID
     */
    async getById(endpoint, id) {
        if (!this.isInitialized) {
            await this.initialize();
        }

        console.log(`🔍 Getting ${endpoint} by ID:`, id);

        try {
            const url = this.config.getEndpointURL(endpoint.replace('{id}', id));
            const response = await fetch(url, {
                method: 'GET',
                headers: this.config.getHeaders()
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Autotask API error: ${response.status} ${response.statusText} - ${errorText}`);
            }

            const data = await response.json();
            console.log('✅ Entity retrieved');
            return data;
        } catch (error) {
            console.error('❌ Get by ID failed:', error);
            throw error;
        }
    }

    /**
     * Get tickets for reporting
     */
    async getTickets(filters = null) {
        return this.query(this.config.endpoints.tickets, filters || this.config.queries.ticketsThisMonth);
    }

    /**
     * Get time entries for reporting
     */
    async getTimeEntries(filters = null) {
        return this.query(this.config.endpoints.timeEntries, filters || this.config.queries.timeEntriesThisMonth);
    }

    /**
     * Get opportunities (sales pipeline)
     */
    async getOpportunities(filters = null) {
        return this.query(this.config.endpoints.opportunities, filters || this.config.queries.activeOpportunities);
    }

    /**
     * Get activities (calls, meetings, tasks)
     */
    async getActivities(filters = null) {
        return this.query(this.config.endpoints.activities, filters);
    }

    /**
     * Get appointments
     */
    async getAppointments(filters = null) {
        return this.query(this.config.endpoints.appointments, filters);
    }

    /**
     * Get companies (clients)
     */
    async getCompanies(filters = null) {
        return this.query(this.config.endpoints.companies, filters);
    }

    /**
     * Get contacts
     */
    async getContacts(filters = null) {
        return this.query(this.config.endpoints.contacts, filters);
    }

    /**
     * Clear cache
     */
    clearCache() {
        this.cache.clear();
        console.log('🗑️ Cache cleared');
    }

    /**
     * Build date range filter for queries
     */
    buildDateRangeFilter(field, startDate, endDate) {
        const filters = [];

        if (startDate) {
            filters.push({
                field: field,
                op: 'gte',
                value: startDate.toISOString()
            });
        }

        if (endDate) {
            filters.push({
                field: field,
                op: 'lte',
                value: endDate.toISOString()
            });
        }

        return { filter: filters };
    }

    /**
     * Get sales metrics for reporting
     */
    async getSalesMetrics(startDate, endDate) {
        console.log('📊 Getting sales metrics...');

        try {
            // Get opportunities in date range
            const opportunitiesFilter = this.buildDateRangeFilter('createDate', startDate, endDate);
            const opportunities = await this.getOpportunities(opportunitiesFilter);

            // Get activities (calls, meetings) in date range
            const activitiesFilter = this.buildDateRangeFilter('createDateTime', startDate, endDate);
            const activities = await this.getActivities(activitiesFilter);

            // Get appointments in date range
            const appointmentsFilter = this.buildDateRangeFilter('startDateTime', startDate, endDate);
            const appointments = await this.getAppointments(appointmentsFilter);

            return {
                opportunities: opportunities.items || [],
                activities: activities.items || [],
                appointments: appointments.items || []
            };
        } catch (error) {
            console.error('❌ Failed to get sales metrics:', error);
            throw error;
        }
    }
}

console.log('✅ Autotask Client.js loaded');

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AutotaskClient;
}
