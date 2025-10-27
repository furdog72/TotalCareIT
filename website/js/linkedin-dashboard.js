/**
 * LinkedIn Performance Dashboard
 * Handles data fetching and display for LinkedIn metrics with historical comparison
 */

// Historical data from Marketing Scorecard
const sampleHistoricalData = {
    "charles": [
        { month: "Oct 2025", impressions: 1861, profile_views: 335, followers: 2163, search: 68, connections: 1864, real_time: true },
        { month: "Sep 2025", impressions: 576, profile_views: 326, followers: 2115, search: 41, connections: 1842 },
        { month: "Aug 2025", impressions: 2265, profile_views: 284, followers: 2070, search: 31, connections: 1824 },
        { month: "Jul 2025", impressions: 432, profile_views: 246, followers: 2046, search: 58, connections: 1813 },
        { month: "Jun 2025", impressions: 2980, profile_views: 226, followers: 2032, search: 36, connections: 1803 },
        { month: "May 2025", impressions: 512, profile_views: 239, followers: 2008, search: 71, connections: 1790 },
        { month: "Feb 2025", impressions: 126, profile_views: 246, followers: 1930, search: 83, connections: 1930 },
        { month: "Jan 2025", impressions: 2746, profile_views: 311, followers: 2185, search: 64, connections: 1883 },
        { month: "Dec 2024", impressions: 70, profile_views: 254, followers: 1892, search: 52, connections: 1729 },
        { month: "Nov 2024", impressions: 207, profile_views: 167, followers: 1841, search: 65, connections: 1701 }
    ],
    "jason": [
        { month: "Oct 2025", impressions: "N/A", profile_views: "N/A", followers: "N/A", search: "N/A", connections: "N/A", real_time: true, note: "Historical tracking not available - LinkedIn metrics collection starting soon" },
        { month: "Sep 2025", impressions: "N/A", profile_views: "N/A", followers: "N/A", search: "N/A", connections: "N/A", note: "Historical tracking not available" },
        { month: "Aug 2025", impressions: "N/A", profile_views: "N/A", followers: "N/A", search: "N/A", connections: "N/A", note: "Historical tracking not available" },
        { month: "Jul 2025", impressions: "N/A", profile_views: "N/A", followers: "N/A", search: "N/A", connections: "N/A", note: "Historical tracking not available" },
        { month: "Jun 2025", impressions: "N/A", profile_views: "N/A", followers: "N/A", search: "N/A", connections: "N/A", note: "Historical tracking not available" },
        { month: "May 2025", impressions: "N/A", profile_views: "N/A", followers: "N/A", search: "N/A", connections: "N/A", note: "Historical tracking not available" }
    ],
    "company": [
        { month: "Oct 2025", followers: 879, engagement: "6.60%", posts: 27, rank: 3, vs_competitor: "1057.10%", real_time: true },
        { month: "Sep 2025", followers: 845, engagement: "1.30%", posts: 24, rank: 2, vs_competitor: "116.70%" },
        { month: "Aug 2025", followers: 818, engagement: "2.80%", posts: 21, rank: 3, vs_competitor: "1011.80%" },
        { month: "Jul 2025", followers: 813, engagement: "2.90%", posts: 21, rank: 2, vs_competitor: "845%" },
        { month: "Jun 2025", followers: 791, engagement: "2.40%", posts: 21, rank: 3, vs_competitor: "721.70%" },
        { month: "May 2025", followers: 780, engagement: "1.10%", posts: 21, rank: 3, vs_competitor: "894.70%" },
        { month: "Feb 2025", followers: 740, engagement: "4.00%", posts: 20, rank: 4, vs_competitor: "1536.4%" },
        { month: "Jan 2025", followers: 891, engagement: "2.70%", posts: 31, rank: 3, vs_competitor: "597.5%" },
        { month: "Dec 2024", followers: 728, engagement: "490.00%", posts: 20, rank: 2, vs_competitor: "1284.6%" },
        { month: "Nov 2024", followers: 0, engagement: "5.50%", posts: 22, rank: 7, vs_competitor: "518.8%" }
    ]
};

/**
 * Calculate percentage change between two values
 */
function calculatePercentChange(current, previous) {
    if (!previous || previous === 0) return 0;
    return ((current - previous) / previous * 100).toFixed(1);
}

/**
 * Format number with commas
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Generate historical comparison table for individual metrics
 */
function generateIndividualHistoricalTable(person) {
    const data = sampleHistoricalData[person];
    if (!data || data.length === 0) return '';

    let html = `
        <div class="historical-section">
            <h3>Historical Performance</h3>
            <div class="historical-table-container">
                <table class="historical-table">
                    <thead>
                        <tr>
                            <th>Month</th>
                            <th>Post Impressions</th>
                            <th>Profile Views</th>
                            <th>Followers</th>
                            <th>Search Appearances</th>
                            <th>Connections</th>
                        </tr>
                    </thead>
                    <tbody>
    `;

    data.forEach((row, index) => {
        const isRealTime = row.real_time;
        const rowClass = isRealTime ? 'real-time-row' : '';

        html += `<tr class="${rowClass}">`;
        html += `<td><strong>${row.month}</strong>${isRealTime ? ' <span class="real-time-badge">Real-Time</span>' : ''}</td>`;

        // Add cells with change indicators
        const prev = data[index + 1];

        // Post Impressions
        html += generateHistoricalCell(row.impressions, prev?.impressions);

        // Profile Views
        html += generateHistoricalCell(row.profile_views, prev?.profile_views);

        // Followers
        html += generateHistoricalCell(row.followers, prev?.followers);

        // Search Appearances
        html += generateHistoricalCell(row.search, prev?.search);

        // Connections
        html += generateHistoricalCell(row.connections, prev?.connections);

        html += `</tr>`;
    });

    html += `
                    </tbody>
                </table>
            </div>
            <div class="update-note">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <polyline points="12 6 12 12 16 14"/>
                </svg>
                Real-time data updated weekly on Saturdays. Historical snapshots captured on 1st of each month.
            </div>
        </div>
    `;

    return html;
}

/**
 * Generate historical comparison table for company metrics
 */
function generateCompanyHistoricalTable() {
    const data = sampleHistoricalData.company;
    if (!data || data.length === 0) return '';

    let html = `
        <div class="historical-section">
            <h3>Historical Performance</h3>
            <div class="historical-table-container">
                <table class="historical-table">
                    <thead>
                        <tr>
                            <th>Month</th>
                            <th>Competitor Rank</th>
                            <th>Posts vs Competitor</th>
                            <th>vs Competitor</th>
                            <th>Engagement</th>
                            <th>Followers</th>
                        </tr>
                    </thead>
                    <tbody>
    `;

    data.forEach((row, index) => {
        const isRealTime = row.real_time;
        const rowClass = isRealTime ? 'real-time-row' : '';

        html += `<tr class="${rowClass}">`;
        html += `<td><strong>${row.month}</strong>${isRealTime ? ' <span class="real-time-badge">Real-Time</span>' : ''}</td>`;

        const prev = data[index + 1];

        // Competitor Rank
        if (row.rank) {
            html += `<td><div class="cell-value">${row.rank}</div></td>`;
        } else {
            html += `<td>-</td>`;
        }

        // Posts vs Competitor
        html += generateHistoricalCell(row.posts, prev?.posts);

        // vs Competitor percentage
        html += `<td>${row.vs_competitor || '-'}</td>`;

        // Engagement Rate
        html += `<td>${row.engagement}</td>`;

        // Followers
        html += generateHistoricalCell(row.followers, prev?.followers);

        html += `</tr>`;
    });

    html += `
                    </tbody>
                </table>
            </div>
            <div class="update-note">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <polyline points="12 6 12 12 16 14"/>
                </svg>
                Real-time data updated weekly on Saturdays. Historical snapshots captured on 1st of each month.
            </div>
        </div>
    `;

    return html;
}

/**
 * Generate a historical table cell with value and change indicator
 */
function generateHistoricalCell(current, previous) {
    if (!current) return '<td>-</td>';

    let html = `<td>`;
    html += `<div class="cell-value">${formatNumber(current)}</div>`;

    if (previous) {
        const change = calculatePercentChange(current, previous);
        const changeClass = change > 0 ? 'change-positive' : (change < 0 ? 'change-negative' : 'change-neutral');
        const arrow = change > 0 ? '↑' : (change < 0 ? '↓' : '→');
        html += `<div class="cell-change ${changeClass}">${arrow} ${Math.abs(change)}%</div>`;
    }

    html += `</td>`;
    return html;
}

/**
 * Load historical data into each tab
 */
function loadHistoricalData() {
    // Charles tab
    const charlesTab = document.getElementById('charles-tab');
    if (charlesTab) {
        const charlesTable = generateIndividualHistoricalTable('charles');
        charlesTab.innerHTML += charlesTable;
    }

    // Jason tab
    const jasonTab = document.getElementById('jason-tab');
    if (jasonTab) {
        const jasonTable = generateIndividualHistoricalTable('jason');
        jasonTab.innerHTML += jasonTable;
    }

    // Company tab
    const companyTab = document.getElementById('company-tab');
    if (companyTab) {
        const companyTable = generateCompanyHistoricalTable();
        // Insert before competitor section
        const competitorSection = companyTab.querySelector('.comparison-section');
        if (competitorSection) {
            competitorSection.insertAdjacentHTML('beforebegin', companyTable);
        } else {
            companyTab.innerHTML += companyTable;
        }
    }
}

/**
 * Initialize dashboard when page loads
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('LinkedIn Performance Dashboard initializing...');
    loadHistoricalData();
    console.log('Historical data loaded');
});

/**
 * Fetch real data from API (to be implemented)
 */
async function fetchLinkedInData() {
    try {
        const response = await fetch('/api/linkedin/dashboard-data');
        const data = await response.json();
        // Update dashboard with real data
        updateDashboard(data);
    } catch (error) {
        console.error('Error fetching LinkedIn data:', error);
        // Fall back to sample data
        loadHistoricalData();
    }
}

/**
 * Update dashboard with real API data
 */
function updateDashboard(data) {
    // TODO: Implement real data update logic
    console.log('Updating dashboard with:', data);
}
