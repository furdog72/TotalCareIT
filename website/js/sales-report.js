console.log('📊 Sales Report.js loaded');

// Initialize Backend API client
let backendAPIClient = null;
let salesReportAdapter = null;
let useBackendAPI = false;

// Initialize Autotask client and adapter (Legacy)
let autotaskClient = null;
let autotaskAdapter = null;
let useAutotaskData = false;

// Try to initialize Backend API integration (preferred)
let backendAPIReady = Promise.resolve(false);
try {
    backendAPIClient = new BackendAPIClient();
    salesReportAdapter = new SalesReportAdapter(backendAPIClient);
    console.log('🔧 Backend API client initialized');

    // Check if backend API is available
    backendAPIReady = backendAPIClient.healthCheck().then(health => {
        if (health && health.checks && health.checks.hubspot === 'configured') {
            useBackendAPI = true;
            console.log('✅ Backend API configured with HubSpot');
            return true;
        } else {
            console.log('⚠️ Backend API not configured');
            return false;
        }
    }).catch(err => {
        console.log('⚠️ Backend API health check failed:', err.message);
        return false;
    });
} catch (error) {
    console.log('⚠️ Backend API client not available:', error.message);
}

// Try to initialize Autotask integration (Legacy fallback)
try {
    autotaskClient = new AutotaskClient();
    autotaskAdapter = new AutotaskSalesAdapter(autotaskClient);
    useAutotaskData = autotaskAdapter.isConfigured();
    console.log('🔧 Autotask integration available:', useAutotaskData);
} catch (error) {
    console.log('⚠️ Autotask integration not available:', error.message);
}

// Sample data - Used as fallback when Autotask is not configured
const sampleData = {
    thisMonth: {
        callsMade: 127,
        conversationsHad: 89,
        appointmentsScheduled: 34,
        outboundCalls: 98,
        inboundCalls: 29,
        emailConversations: 45,
        meetingConversations: 44,
        prospects: 250,
        contacted: 195,
        qualified: 78,
        proposal: 42,
        closedWon: 18
    },
    lastMonth: {
        callsMade: 112,
        conversationsHad: 76,
        appointmentsScheduled: 28
    },
    upcomingAppointments: [
        {
            date: '2025-10-24',
            time: '10:00 AM',
            contact: 'ABC Manufacturing',
            type: 'Discovery Call',
            notes: 'Initial consultation about AI automation'
        },
        {
            date: '2025-10-24',
            time: '2:00 PM',
            contact: 'XYZ Solutions',
            type: 'Proposal Review',
            notes: 'Present custom AI solution proposal'
        },
        {
            date: '2025-10-25',
            time: '11:30 AM',
            contact: 'Tech Innovators Inc',
            type: 'Demo',
            notes: 'Live demo of workflow automation'
        },
        {
            date: '2025-10-25',
            time: '3:00 PM',
            contact: 'Global Services Ltd',
            type: 'Follow-up',
            notes: 'Follow up on previous meeting'
        }
    ],
    recentActivity: [
        {
            datetime: '2025-10-23 4:30 PM',
            type: 'Phone Call',
            contact: 'John Smith - ABC Manufacturing',
            duration: '23 min',
            outcome: 'Qualified',
            nextSteps: 'Send proposal by Friday'
        },
        {
            datetime: '2025-10-23 2:15 PM',
            type: 'Email',
            contact: 'Sarah Johnson - XYZ Solutions',
            duration: '-',
            outcome: 'Meeting Scheduled',
            nextSteps: 'Prepare demo for next week'
        },
        {
            datetime: '2025-10-23 11:00 AM',
            type: 'Meeting',
            contact: 'Michael Chen - Tech Innovators',
            duration: '45 min',
            outcome: 'Hot Lead',
            nextSteps: 'Contract review in progress'
        },
        {
            datetime: '2025-10-23 9:30 AM',
            type: 'Phone Call',
            contact: 'Emily Davis - Global Services',
            duration: '15 min',
            outcome: 'Follow-up Needed',
            nextSteps: 'Call back next Tuesday'
        },
        {
            datetime: '2025-10-22 3:45 PM',
            type: 'Email',
            contact: 'David Brown - Innovate Corp',
            duration: '-',
            outcome: 'Information Sent',
            nextSteps: 'Await response'
        },
        {
            datetime: '2025-10-22 1:00 PM',
            type: 'Meeting',
            contact: 'Lisa Martinez - Smart Solutions',
            duration: '30 min',
            outcome: 'Proposal Sent',
            nextSteps: 'Follow up in 3 days'
        },
        {
            datetime: '2025-10-22 10:15 AM',
            type: 'Phone Call',
            contact: 'Robert Wilson - Future Tech',
            duration: '18 min',
            outcome: 'Not Interested',
            nextSteps: 'Add to nurture campaign'
        },
        {
            datetime: '2025-10-21 4:00 PM',
            type: 'Email',
            contact: 'Jennifer Taylor - Prime Industries',
            duration: '-',
            outcome: 'Meeting Scheduled',
            nextSteps: 'Discovery call on Monday'
        }
    ]
};

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 DOM loaded, initializing sales report...');

    // Check authentication
    checkAuthentication();

    // Check Autotask configuration
    checkAutotaskConfiguration();

    // Load initial data
    loadSalesData();

    // Setup event listeners
    setupEventListeners();

    // Setup Autotask modal listeners
    setupAutotaskModal();
});

function checkAuthentication() {
    // Temporarily bypass authentication for testing
    try {
        const accounts = myMSALObj.getAllAccounts();
        if (accounts.length === 0) {
            console.log('⚠️ Not authenticated - using test mode');
            // Don't redirect, just set a default username
            const userNameElement = document.getElementById('userName');
            if (userNameElement) {
                userNameElement.textContent = 'Test User';
            }
            return;
        }

        const account = accounts[0];
        console.log('✅ Authenticated as:', account.username);

        // Update user info in header
        document.getElementById('userName').textContent = account.name || account.username;
    } catch (error) {
        console.log('⚠️ MSAL not available - using test mode');
        const userNameElement = document.getElementById('userName');
        if (userNameElement) {
            userNameElement.textContent = 'Test User';
        }
    }
}

async function loadSalesData() {
    console.log('📊 Loading sales data...');

    let data, lastMonthData;
    let dataSource = 'sample';

    // Wait for backend API health check to complete
    await backendAPIReady;

    // Try to load data from Backend API first (preferred)
    if (useBackendAPI && salesReportAdapter) {
        try {
            console.log('🔄 Attempting to load data from Backend API (HubSpot)...');
            const backendData = await salesReportAdapter.getSalesData();

            if (backendData && backendData.thisMonth) {
                data = backendData.thisMonth;
                lastMonthData = backendData.lastMonth;
                dataSource = 'hubspot';
                console.log('✅ Using HubSpot data from Backend API');

                // Update appointments and activity if available
                if (backendData.upcomingAppointments) {
                    sampleData.upcomingAppointments = backendData.upcomingAppointments;
                }
                if (backendData.recentActivity) {
                    sampleData.recentActivity = backendData.recentActivity;
                }
            }
        } catch (error) {
            console.error('❌ Failed to load Backend API data:', error);
            showAPIError('Failed to load data from HubSpot API. Trying fallback options...');
        }
    }

    // Try to load data from Autotask if Backend API failed and Autotask is configured
    if (!data && useAutotaskData && autotaskAdapter) {
        try {
            console.log('🔄 Attempting to load data from Autotask...');
            const dateRange = autotaskAdapter.getDateRange('thisMonth');
            const autotaskData = await autotaskAdapter.getSalesData(dateRange.start, dateRange.end);

            if (autotaskData) {
                data = autotaskData.thisMonth;
                dataSource = 'autotask';
                console.log('✅ Using Autotask data');

                // Update appointments and activity from Autotask
                sampleData.upcomingAppointments = autotaskData.upcomingAppointments;
                sampleData.recentActivity = autotaskData.recentActivity;
            }
        } catch (error) {
            console.error('❌ Failed to load Autotask data:', error);
            showAutotaskError('Failed to load data from Autotask. Using sample data.');
        }
    }

    // Fallback to sample data
    if (!data) {
        data = sampleData.thisMonth;
        lastMonthData = sampleData.lastMonth;
        console.log('📦 Using sample data');
    }

    // Update key metrics
    console.log('📊 About to update metrics with data:', data);
    console.log('callsMade value:', data.callsMade);
    console.log('conversationsHad value:', data.conversationsHad);
    console.log('appointmentsScheduled value:', data.appointmentsScheduled);

    try {
        updateMetric('callsMade', data.callsMade, lastMonthData?.callsMade);
        console.log('✅ Updated callsMade');
    } catch (e) {
        console.error('❌ Error updating callsMade:', e);
    }

    try {
        updateMetric('conversationsHad', data.conversationsHad, lastMonthData?.callsMade);
        console.log('✅ Updated conversationsHad');
    } catch (e) {
        console.error('❌ Error updating conversationsHad:', e);
    }

    try {
        updateMetric('appointmentsScheduled', data.appointmentsScheduled, lastMonthData?.appointmentsScheduled);
        console.log('✅ Updated appointmentsScheduled');
    } catch (e) {
        console.error('❌ Error updating appointmentsScheduled:', e);
    }

    // Calculate and update conversion rate
    try {
        const conversionRate = data.prospects ? ((data.closedWon / data.prospects) * 100).toFixed(1) : '0.0';
        const conversionElement = document.getElementById('conversionRate');
        const conversionChangeElement = document.getElementById('conversionChange');

        if (conversionElement) {
            conversionElement.textContent = conversionRate + '%';
            console.log('✅ Updated conversion rate:', conversionRate);
        }
        if (conversionChangeElement) {
            const spanElement = conversionChangeElement.querySelector('span');
            if (spanElement) {
                spanElement.textContent = '+2.3% vs last period';
            }
        }
    } catch (e) {
        console.error('❌ Error updating conversion rate:', e);
    }

    // Update activity breakdown
    try {
        const totalActivities = data.outboundCalls + data.inboundCalls + data.emailConversations + data.meetingConversations;
        console.log('📊 Total activities:', totalActivities);
        updateBreakdown('outboundCalls', 'outboundPercent', data.outboundCalls, totalActivities);
        updateBreakdown('inboundCalls', 'inboundPercent', data.inboundCalls, totalActivities);
        updateBreakdown('emailConversations', 'emailPercent', data.emailConversations, totalActivities);
        updateBreakdown('meetingConversations', 'meetingPercent', data.meetingConversations, totalActivities);
        console.log('✅ Updated activity breakdown');
    } catch (e) {
        console.error('❌ Error updating activity breakdown:', e);
    }

    // Update sales funnel
    try {
        updateFunnel(data);
        console.log('✅ Updated sales funnel');
    } catch (e) {
        console.error('❌ Error updating sales funnel:', e);
    }

    // Load appointments
    try {
        loadAppointments();
        console.log('✅ Loaded appointments');
    } catch (e) {
        console.error('❌ Error loading appointments:', e);
    }

    // Load activity table
    try {
        loadActivityTable();
        console.log('✅ Loaded activity table');
    } catch (e) {
        console.error('❌ Error loading activity table:', e);
    }

    console.log(`✅ Sales data loaded from ${dataSource}`);
}

function updateMetric(elementId, currentValue, previousValue) {
    console.log(`📊 updateMetric called: elementId="${elementId}", currentValue=${currentValue}, previousValue=${previousValue}`);

    const element = document.getElementById(elementId);
    console.log(`  Element found:`, element ? 'YES' : 'NO');

    if (element) {
        element.textContent = currentValue;
        console.log(`  ✅ Set ${elementId} to ${currentValue}`);
    } else {
        console.warn(`  ⚠️ Element #${elementId} not found in DOM!`);
    }

    const changeElement = document.getElementById(elementId.replace('Made', 'Change').replace('Had', 'Change').replace('Scheduled', 'Change'));

    if (changeElement && previousValue) {
        const change = currentValue - previousValue;
        const percentChange = ((change / previousValue) * 100).toFixed(1);
        const isPositive = change >= 0;

        changeElement.className = 'stat-change ' + (isPositive ? 'positive' : 'negative');
        const polyline = changeElement.querySelector('svg polyline');
        const span = changeElement.querySelector('span');

        if (polyline) {
            polyline.setAttribute('points', isPositive ? '18 15 12 9 6 15' : '6 9 12 15 18 9');
        }
        if (span) {
            span.textContent = `${isPositive ? '+' : ''}${change} (${isPositive ? '+' : ''}${percentChange}%) vs last period`;
        }
    }
}

function updateBreakdown(valueId, percentId, value, total) {
    const percent = ((value / total) * 100).toFixed(1);
    document.getElementById(valueId).textContent = value;
    document.getElementById(percentId).textContent = percent + '%';
}

function updateFunnel(data) {
    // Update counts
    document.getElementById('prospectsCount').textContent = data.prospects;
    document.getElementById('contactedCount').textContent = data.contacted;
    document.getElementById('qualifiedCount').textContent = data.qualified;
    document.getElementById('proposalCount').textContent = data.proposal;
    document.getElementById('closedWonCount').textContent = data.closedWon;

    // Update bar widths and percentages
    const contactedPercent = (data.contacted / data.prospects * 100).toFixed(1);
    const qualifiedPercent = (data.qualified / data.prospects * 100).toFixed(1);
    const proposalPercent = (data.proposal / data.prospects * 100).toFixed(1);
    const closedWonPercent = (data.closedWon / data.prospects * 100).toFixed(1);

    updateFunnelBar('contactedBar', 'contactedPercent', contactedPercent, '#06b6d4');
    updateFunnelBar('qualifiedBar', 'qualifiedPercent', qualifiedPercent, '#8b5cf6');
    updateFunnelBar('proposalBar', 'proposalPercent', proposalPercent, '#f59e0b');
    updateFunnelBar('closedWonBar', 'closedWonPercent', closedWonPercent, '#10b981');
}

function updateFunnelBar(barId, percentId, percent, color) {
    const bar = document.getElementById(barId);
    const percentLabel = document.getElementById(percentId);

    if (bar) {
        bar.style.width = percent + '%';
        bar.style.background = color;
    }

    if (percentLabel) {
        percentLabel.textContent = percent + '%';
    }
}

function loadAppointments() {
    const appointmentsList = document.getElementById('appointmentsList');

    if (!appointmentsList) return;

    const appointments = sampleData.upcomingAppointments.slice(0, 4);

    if (appointments.length === 0) {
        appointmentsList.innerHTML = '<div class="empty-state">No upcoming appointments</div>';
        return;
    }

    appointmentsList.innerHTML = appointments.map(apt => `
        <div class="appointment-item">
            <div class="appointment-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                    <line x1="16" y1="2" x2="16" y2="6"/>
                    <line x1="8" y1="2" x2="8" y2="6"/>
                    <line x1="3" y1="10" x2="21" y2="10"/>
                </svg>
            </div>
            <div class="appointment-details">
                <div class="appointment-header">
                    <strong>${apt.contact}</strong>
                    <span class="appointment-badge">${apt.type}</span>
                </div>
                <div class="appointment-time">${formatDate(apt.date)} at ${apt.time}</div>
                <div class="appointment-notes">${apt.notes}</div>
            </div>
        </div>
    `).join('');
}

function loadActivityTable() {
    const tableBody = document.getElementById('activityTableBody');

    if (!tableBody) return;

    const activities = sampleData.recentActivity;

    if (activities.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7" class="empty-state">No recent activity</td></tr>';
        return;
    }

    tableBody.innerHTML = activities.map(activity => `
        <tr>
            <td>${activity.datetime}</td>
            <td>
                <span class="activity-badge activity-${activity.type.toLowerCase().replace(' ', '-')}">${activity.type}</span>
            </td>
            <td>${activity.contact}</td>
            <td>${activity.duration}</td>
            <td>
                <span class="outcome-badge outcome-${getOutcomeClass(activity.outcome)}">${activity.outcome}</span>
            </td>
            <td>${activity.nextSteps}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn-icon" title="View Details">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                            <circle cx="12" cy="12" r="3"/>
                        </svg>
                    </button>
                    <button class="btn-icon" title="Edit">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                        </svg>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

function getOutcomeClass(outcome) {
    const outcomeMap = {
        'Qualified': 'qualified',
        'Meeting Scheduled': 'scheduled',
        'Hot Lead': 'hot',
        'Follow-up Needed': 'followup',
        'Information Sent': 'info',
        'Proposal Sent': 'proposal',
        'Not Interested': 'rejected',
        'Closed Won': 'won'
    };

    return outcomeMap[outcome] || 'default';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    if (date.toDateString() === today.toDateString()) {
        return 'Today';
    } else if (date.toDateString() === tomorrow.toDateString()) {
        return 'Tomorrow';
    } else {
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
}

function setupEventListeners() {
    // Date range filter
    const dateRangeSelect = document.getElementById('dateRange');
    const customDateGroup = document.getElementById('customDateGroup');

    if (dateRangeSelect) {
        dateRangeSelect.addEventListener('change', function() {
            if (this.value === 'custom') {
                customDateGroup.style.display = 'flex';
            } else {
                customDateGroup.style.display = 'none';
                // Reload data for selected period
                loadSalesData();
            }
        });
    }

    // Refresh button
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            console.log('🔄 Refreshing data...');
            loadSalesData();
        });
    }

    // Search functionality
    const activitySearch = document.getElementById('activitySearch');
    if (activitySearch) {
        activitySearch.addEventListener('input', function() {
            filterActivityTable(this.value);
        });
    }

    // Logout button
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            console.log('🚪 Logging out...');

            try {
                await myMSALObj.logoutRedirect({
                    postLogoutRedirectUri: window.location.origin + '/partner-login.html'
                });
            } catch (error) {
                console.error('❌ Logout error:', error);
            }
        });
    }
}

function filterActivityTable(searchTerm) {
    const tableBody = document.getElementById('activityTableBody');
    const rows = tableBody.querySelectorAll('tr');

    searchTerm = searchTerm.toLowerCase();

    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? '' : 'none';
    });
}

// Autotask Integration Functions

function checkAutotaskConfiguration() {
    const banner = document.getElementById('autotaskBanner');

    if (!useAutotaskData) {
        banner.style.display = 'flex';
        banner.querySelector('#autotaskMessage').textContent = 'Connect to Autotask to view real-time sales data';
    } else {
        banner.style.display = 'none';
    }
}

function setupAutotaskModal() {
    const modal = document.getElementById('autotaskModal');
    const configureBtn = document.getElementById('configureAutotaskBtn');
    const closeBtn = document.getElementById('closeModal');
    const testBtn = document.getElementById('testConnectionBtn');
    const saveBtn = document.getElementById('saveAutotaskBtn');

    // Open modal
    if (configureBtn) {
        configureBtn.addEventListener('click', function() {
            modal.style.display = 'flex';
            loadSavedCredentials();
        });
    }

    // Close modal
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            modal.style.display = 'none';
        });
    }

    // Click outside to close
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Test connection
    if (testBtn) {
        testBtn.addEventListener('click', async function() {
            await testAutotaskConnection();
        });
    }

    // Save credentials
    if (saveBtn) {
        saveBtn.addEventListener('click', async function() {
            await saveAutotaskCredentials();
        });
    }
}

function loadSavedCredentials() {
    const username = localStorage.getItem('autotask_username');
    const secret = localStorage.getItem('autotask_secret');
    const integrationCode = localStorage.getItem('autotask_integration_code');

    if (username) document.getElementById('autotaskUsername').value = username;
    if (secret) document.getElementById('autotaskSecret').value = secret;
    if (integrationCode) document.getElementById('autotaskIntegrationCode').value = integrationCode;
}

async function testAutotaskConnection() {
    const errorDiv = document.getElementById('autotaskError');
    const successDiv = document.getElementById('autotaskSuccess');
    const testBtn = document.getElementById('testConnectionBtn');

    errorDiv.style.display = 'none';
    successDiv.style.display = 'none';

    const username = document.getElementById('autotaskUsername').value;
    const secret = document.getElementById('autotaskSecret').value;
    const integrationCode = document.getElementById('autotaskIntegrationCode').value;

    if (!username || !secret || !integrationCode) {
        errorDiv.textContent = 'Please fill in all fields';
        errorDiv.style.display = 'block';
        return;
    }

    testBtn.disabled = true;
    testBtn.textContent = 'Testing...';

    try {
        // Temporarily set credentials
        autotaskAdapter.saveCredentials(username, secret, integrationCode);

        // Try to initialize
        await autotaskClient.initialize();

        successDiv.textContent = '✅ Connection successful! Click "Save & Connect" to start using Autotask data.';
        successDiv.style.display = 'block';

        testBtn.textContent = 'Test Connection';
        testBtn.disabled = false;
    } catch (error) {
        errorDiv.textContent = `Connection failed: ${error.message}`;
        errorDiv.style.display = 'block';

        testBtn.textContent = 'Test Connection';
        testBtn.disabled = false;

        // Clear invalid credentials
        autotaskAdapter.clearCredentials();
    }
}

async function saveAutotaskCredentials() {
    const errorDiv = document.getElementById('autotaskError');
    const successDiv = document.getElementById('autotaskSuccess');
    const saveBtn = document.getElementById('saveAutotaskBtn');

    errorDiv.style.display = 'none';
    successDiv.style.display = 'none';

    const username = document.getElementById('autotaskUsername').value;
    const secret = document.getElementById('autotaskSecret').value;
    const integrationCode = document.getElementById('autotaskIntegrationCode').value;

    if (!username || !secret || !integrationCode) {
        errorDiv.textContent = 'Please fill in all fields';
        errorDiv.style.display = 'block';
        return;
    }

    saveBtn.disabled = true;
    saveBtn.textContent = 'Saving...';

    try {
        // Save credentials
        autotaskAdapter.saveCredentials(username, secret, integrationCode);

        // Initialize connection
        await autotaskClient.initialize();

        // Update global flag
        useAutotaskData = true;

        successDiv.textContent = '✅ Autotask connected successfully! Refreshing data...';
        successDiv.style.display = 'block';

        // Close modal after 1 second
        setTimeout(() => {
            document.getElementById('autotaskModal').style.display = 'none';
            saveBtn.textContent = 'Save & Connect';
            saveBtn.disabled = false;

            // Hide banner and reload data
            document.getElementById('autotaskBanner').style.display = 'none';
            loadSalesData();
        }, 1000);
    } catch (error) {
        errorDiv.textContent = `Failed to save: ${error.message}`;
        errorDiv.style.display = 'block';

        saveBtn.textContent = 'Save & Connect';
        saveBtn.disabled = false;
    }
}

function showAutotaskError(message) {
    const banner = document.getElementById('autotaskBanner');
    const messageEl = banner.querySelector('#autotaskMessage');

    banner.style.display = 'flex';
    banner.style.background = 'linear-gradient(135deg, #fee2e2, #fecaca)';
    banner.style.borderColor = '#ef4444';
    messageEl.textContent = message;
}

function showAPIError(message) {
    // Show error in the HubSpot or Autotask banner
    const banner = document.getElementById('hubspotBanner') || document.getElementById('autotaskBanner');
    if (banner) {
        const messageEl = banner.querySelector('#hubspotMessage') || banner.querySelector('#autotaskMessage');
        if (messageEl) {
            banner.style.display = 'flex';
            banner.style.background = 'linear-gradient(135deg, #fee2e2, #fecaca)';
            banner.style.borderColor = '#ef4444';
            messageEl.textContent = message;
        }
    }
}

console.log('✅ Sales Report.js fully loaded');
