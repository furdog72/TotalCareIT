/**
 * Pro Services PBR Dashboard
 * Loads and displays Professional Services Business Review data from TotalCareIT PBR 2025.xlsx
 */

const API_BASE_URL = window.location.hostname === 'localhost' ? 'data' : '/data';

let currentQuarter = 'Q3';
let currentYear = 2025;

/**
 * Initialize the dashboard
 */
document.addEventListener('DOMContentLoaded', () => {
    // Set up quarter selector
    const quarterSelector = document.getElementById('quarterSelector');
    quarterSelector.addEventListener('change', (e) => {
        const [quarter, year] = e.target.value.split('-');
        currentQuarter = quarter;
        currentYear = parseInt(year);
        loadPBRData();
    });

    // Set up refresh button
    const refreshBtn = document.getElementById('refreshBtn');
    refreshBtn.addEventListener('click', () => {
        loadPBRData();
    });

    // Initial load
    loadPBRData();
});

/**
 * Load PBR data from JSON file
 */
async function loadPBRData() {
    try {
        showLoading();

        const filename = `pro-svc-pbr-${currentQuarter.toLowerCase()}-${currentYear}.json`;
        const response = await fetch(`${API_BASE_URL}/${filename}`);

        if (!response.ok) {
            throw new Error(`Failed to load Pro Services PBR data: ${response.status}`);
        }

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        // Render all sections
        renderGoalsTable(data);
        renderPendingQuotes(data);
        renderActiveQuotes(data);
        renderWonQuotes(data);
        renderAllQuotes(data);

        hideLoading();
    } catch (error) {
        console.error('Error loading PBR data:', error);
        showError(error.message || 'Failed to load Pro Services PBR data. Please try again.');
    }
}

/**
 * Render goals table (matching Excel layout)
 */
function renderGoalsTable(data) {
    const tbody = document.getElementById('goalsTableBody');
    const summary = data.summary;

    // Extract data for 2024 and quarterly goals
    const year2024Goal = summary.ps_team_goal_2024 || 0;
    const year2024Actual = summary.ps_team_actual_2024 || 0;
    const year2024Variance = summary.variance_2024 || 0;

    const q1_goal = summary.ps_team_goal_q1 || 0;
    const q2_goal = summary.ps_team_goal_q2 || 0;
    const q3_goal = summary.ps_team_goal_q3 || 0;
    const q4_goal = summary.ps_team_goal_q4 || 0;

    const q1_actual = summary.ps_team_actual_q1 || 0;
    const q2_actual = summary.ps_team_actual_q2 || 0;
    const q3_actual = summary.ps_team_actual_q3 || 0;
    const q4_actual = summary.ps_team_actual_q4 || 0;

    const q1_variance = summary.variance_q1 || 0;
    const q2_variance = summary.variance_q2 || 0;
    const q3_variance = summary.variance_q3 || 0;
    const q4_variance = summary.variance_q4 || 0;

    tbody.innerHTML = `
        <tr style="background: #f9fafb;">
            <td style="font-weight: 600;">PS Team Goal</td>
            <td style="text-align: center;">${formatCurrency(year2024Goal)}</td>
            <td style="text-align: center;">${formatCurrency(q1_goal)}</td>
            <td style="text-align: center;">${formatCurrency(q2_goal)}</td>
            <td style="text-align: center;">${formatCurrency(q3_goal)}</td>
            <td style="text-align: center;">${formatCurrency(q4_goal)}</td>
        </tr>
        <tr style="background: #ffffff;">
            <td style="font-weight: 600;">PS Team Actual</td>
            <td style="text-align: center;">${formatCurrency(year2024Actual)}</td>
            <td style="text-align: center;">${formatCurrency(q1_actual)}</td>
            <td style="text-align: center;">${formatCurrency(q2_actual)}</td>
            <td style="text-align: center;">${formatCurrency(q3_actual)}</td>
            <td style="text-align: center;">${formatCurrency(q4_actual)}</td>
        </tr>
        <tr style="background: #f9fafb;">
            <td style="font-weight: 600;">(+/-) Goal</td>
            <td style="text-align: center; color: ${year2024Variance >= 0 ? '#10b981' : '#ef4444'};">${formatCurrency(year2024Variance)}</td>
            <td style="text-align: center; color: ${q1_variance >= 0 ? '#10b981' : '#ef4444'};">${formatCurrency(q1_variance)}</td>
            <td style="text-align: center; color: ${q2_variance >= 0 ? '#10b981' : '#ef4444'};">${formatCurrency(q2_variance)}</td>
            <td style="text-align: center; color: ${q3_variance >= 0 ? '#10b981' : '#ef4444'};">${formatCurrency(q3_variance)}</td>
            <td style="text-align: center; color: ${q4_variance >= 0 ? '#10b981' : '#ef4444'};">${formatCurrency(q4_variance)}</td>
        </tr>
    `;

    // Update pipeline coverage
    const coverageRatio = summary.pipeline_coverage_ratio ? (summary.pipeline_coverage_ratio * 100).toFixed(0) + '%' : '-';
    document.getElementById('pipelineCoverage').textContent = coverageRatio;
}

/**
 * Render pending quotes table
 */
function renderPendingQuotes(data) {
    const tbody = document.getElementById('pendingQuotesBody');

    if (data.pending_quotes.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; padding: 2rem; color: #6b7280;">
                    No pending quotes at this time
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = data.pending_quotes.map(quote => `
        <tr>
            <td class="metric-name">${quote.company_name || '-'}</td>
            <td>${quote.project_type || '-'}</td>
            <td>${quote.notes || '-'}</td>
            <td>${quote.margin_dollars ? formatCurrency(quote.margin_dollars) : '-'}</td>
            <td>${quote.quote_number || '-'}</td>
        </tr>
    `).join('');
}

/**
 * Render active quotes table
 */
function renderActiveQuotes(data) {
    const tbody = document.getElementById('activeQuotesBody');

    if (data.active_quotes.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; padding: 2rem; color: #6b7280;">
                    No active quotes at this time
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = data.active_quotes.map(quote => `
        <tr>
            <td class="metric-name">${quote.account_name || '-'}</td>
            <td>${quote.quote_name || '-'}</td>
            <td>${quote.create_date ? formatDate(quote.create_date) : '-'}</td>
            <td><strong>${quote.gross_margin_amount ? formatCurrency(quote.gross_margin_amount) : '-'}</strong></td>
            <td>${quote.quote_number || '-'}</td>
        </tr>
    `).join('');
}

/**
 * Render won quotes table
 */
function renderWonQuotes(data) {
    const wonCard = document.getElementById('wonQuotesCard');
    const tbody = document.getElementById('wonQuotesBody');

    if (data.won_quotes.length === 0) {
        wonCard.style.display = 'none';
        return;
    }

    wonCard.style.display = 'block';

    tbody.innerHTML = data.won_quotes.map(quote => `
        <tr style="background: rgba(16, 185, 129, 0.05);">
            <td class="metric-name">${quote.account_name || '-'}</td>
            <td>${quote.quote_name || '-'}</td>
            <td>${quote.create_date ? formatDate(quote.create_date) : '-'}</td>
            <td><strong style="color: #10b981;">${quote.gross_margin_amount ? formatCurrency(quote.gross_margin_amount) : '-'}</strong></td>
            <td>${quote.invoice_number || '-'}</td>
            <td>${quote.invoice_date ? formatDate(quote.invoice_date) : '-'}</td>
        </tr>
    `).join('');
}

/**
 * Render all quotes table
 */
function renderAllQuotes(data) {
    const tbody = document.getElementById('allQuotesBody');

    if (data.all_quotes.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; padding: 2rem; color: #6b7280;">
                    No quotes available
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = data.all_quotes.map(quote => {
        const statusClass = quote.quote_status === 'Active' ? 'status-active' : 'status-inactive';

        return `
            <tr>
                <td class="metric-name">${quote.quote_name || '-'}</td>
                <td>${quote.account_name || '-'}</td>
                <td><span class="${statusClass}">${quote.quote_status || '-'}</span></td>
                <td>${quote.quote_total ? formatCurrency(quote.quote_total) : '-'}</td>
                <td><strong>${quote.gross_margin_amount ? formatCurrency(quote.gross_margin_amount) : '-'}</strong></td>
                <td>${quote.inside_rep || '-'}</td>
                <td>${quote.create_date ? formatDate(quote.create_date) : '-'}</td>
            </tr>
        `;
    }).join('');
}

/**
 * Format currency
 */
function formatCurrency(value) {
    if (value === null || value === undefined || isNaN(value)) {
        return '$0.00';
    }

    return '$' + parseFloat(value).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

/**
 * Format date
 */
function formatDate(dateValue) {
    if (!dateValue) return '-';

    try {
        // Handle various date formats
        let date;
        if (typeof dateValue === 'string') {
            date = new Date(dateValue);
        } else if (dateValue instanceof Date) {
            date = dateValue;
        } else {
            return dateValue.toString();
        }

        if (isNaN(date.getTime())) {
            return dateValue.toString();
        }

        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    } catch (e) {
        return dateValue.toString();
    }
}

/**
 * Show loading state
 */
function showLoading() {
    const main = document.querySelector('.dashboard-main');
    if (main) {
        main.style.opacity = '0.5';
        main.style.pointerEvents = 'none';
    }
}

/**
 * Hide loading state
 */
function hideLoading() {
    const main = document.querySelector('.dashboard-main');
    if (main) {
        main.style.opacity = '1';
        main.style.pointerEvents = 'auto';
    }
}

/**
 * Show error message
 */
function showError(message) {
    const dashboardHeader = document.querySelector('.dashboard-header');
    if (dashboardHeader) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert-banner';
        errorDiv.style.background = '#fef2f2';
        errorDiv.style.borderLeft = '4px solid #ef4444';
        errorDiv.style.padding = '1rem';
        errorDiv.style.marginBottom = '1.5rem';
        errorDiv.style.borderRadius = '0.5rem';
        errorDiv.innerHTML = `
            <div class="alert-content" style="display: flex; align-items: center; gap: 0.75rem;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="12" y1="8" x2="12" y2="12"/>
                    <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                <span style="color: #991b1b;">${message}</span>
            </div>
        `;
        dashboardHeader.parentNode.insertBefore(errorDiv, dashboardHeader.nextSibling);
    }
    hideLoading();
}
