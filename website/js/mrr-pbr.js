/**
 * MRR PBR Dashboard
 * Loads and displays MRR Professional Business Review data from TotalCareIT PBR 2025.xlsx
 */

const API_BASE_URL = window.location.hostname === 'localhost' ? 'data' : '/data';

let currentQuarter = 'Q3';
let currentYear = 2025;

/**
 * Initialize the dashboard
 */
document.addEventListener('DOMContentLoaded', () => {
    const quarterSelector = document.getElementById('quarterSelector');
    quarterSelector.addEventListener('change', (e) => {
        const [quarter, year] = e.target.value.split('-');
        currentQuarter = quarter;
        currentYear = parseInt(year);
        loadMRRPBRData();
    });

    const refreshBtn = document.getElementById('refreshBtn');
    refreshBtn.addEventListener('click', () => {
        loadMRRPBRData();
    });

    loadMRRPBRData();
});

/**
 * Load MRR PBR data
 */
async function loadMRRPBRData() {
    try {
        showLoading();

        const filename = `mrr-pbr-${currentQuarter.toLowerCase()}-${currentYear}.json`;
        const response = await fetch(`${API_BASE_URL}/${filename}`);

        if (!response.ok) {
            throw new Error(`Failed to load MRR PBR data: ${response.status}`);
        }

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        renderQuarterlyGoals(data);
        renderProspects(data);
        renderSuspects(data);
        renderClosedSales(data);
        renderNurture(data);

        hideLoading();
    } catch (error) {
        console.error('Error loading MRR PBR data:', error);
        showError(error.message || 'Failed to load MRR PBR data. Please try again.');
    }
}

/**
 * Render quarterly goals table (matching Excel layout)
 */
function renderQuarterlyGoals(data) {
    const tbody = document.getElementById('quarterlyGoalsBody');
    const summary = data.summary;

    // Extract quarterly data
    const q1_goal = summary.mrr_goal_q1 || 0;
    const q2_goal = summary.mrr_goal_q2 || 0;
    const q3_goal = summary.mrr_goal_q3 || 0;
    const q4_goal = summary.mrr_goal_q4 || 0;

    const q1_actual = summary.mrr_actual_q1 || 0;
    const q2_actual = summary.mrr_actual_q2 || 0;
    const q3_actual = summary.mrr_actual_q3 || 0;
    const q4_actual = summary.mrr_actual_q4 || 0;

    const q1_variance = summary.variance_q1 || 0;
    const q2_variance = summary.variance_q2 || 0;
    const q3_variance = summary.variance_q3 || 0;
    const q4_variance = summary.variance_q4 || 0;

    tbody.innerHTML = `
        <tr style="background: #f9fafb;">
            <td style="font-weight: 600;">MRR Goal</td>
            <td style="text-align: center;">${formatCurrency(q1_goal)}</td>
            <td style="text-align: center;">${formatCurrency(q2_goal)}</td>
            <td style="text-align: center;">${formatCurrency(q3_goal)}</td>
            <td style="text-align: center;">${formatCurrency(q4_goal)}</td>
            <td></td>
        </tr>
        <tr style="background: #ffffff;">
            <td style="font-weight: 600;">MRR Actual</td>
            <td style="text-align: center;">${formatCurrency(q1_actual)}</td>
            <td style="text-align: center;">${formatCurrency(q2_actual)}</td>
            <td style="text-align: center;">${formatCurrency(q3_actual)}</td>
            <td style="text-align: center;">${formatCurrency(q4_actual)}</td>
            <td></td>
        </tr>
        <tr style="background: #f9fafb;">
            <td style="font-weight: 600;">(+/-) MRR Goal</td>
            <td style="text-align: center; color: ${q1_variance >= 0 ? '#10b981' : '#ef4444'};">${formatCurrency(q1_variance)}</td>
            <td style="text-align: center; color: ${q2_variance >= 0 ? '#10b981' : '#ef4444'};">${formatCurrency(q2_variance)}</td>
            <td style="text-align: center; color: ${q3_variance >= 0 ? '#10b981' : '#ef4444'};">${formatCurrency(q3_variance)}</td>
            <td style="text-align: center; color: ${q4_variance >= 0 ? '#10b981' : '#ef4444'};">${formatCurrency(q4_variance)}</td>
            <td></td>
        </tr>
    `;

    // Update forecasted months
    document.getElementById('forecastedThisMonth').textContent = formatCurrency(summary.forecast_current_month || 0);
    document.getElementById('forecastedNextMonth').textContent = formatCurrency(summary.forecast_next_month || 0);
}

/**
 * Render prospects table
 */
function renderProspects(data) {
    const tbody = document.getElementById('prospectsBody');
    const prospects = data.prospects_30_days.prospects;

    if (prospects.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 2rem; color: #6b7280;">
                    No prospects at this time
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = prospects.map(item => `
        <tr>
            <td class="metric-name">${item.company_name || '-'}</td>
            <td>${item.sales_rep || '-'}</td>
            <td>${item.product || '-'}</td>
            <td>${item.seats || '-'}</td>
            <td><strong>${formatCurrency(item.mrr)}</strong></td>
            <td>${formatCurrency(item.arr)}</td>
        </tr>
    `).join('') + (data.prospects_30_days.totals ? `
        <tr style="font-weight: 600; background: rgba(59, 130, 246, 0.05); border-top: 2px solid #e5e7eb;">
            <td colspan="3">TOTALS</td>
            <td>${data.prospects_30_days.totals.total_seats || 0}</td>
            <td><strong>${formatCurrency(data.prospects_30_days.totals.total_mrr)}</strong></td>
            <td>${formatCurrency(data.prospects_30_days.totals.total_arr)}</td>
        </tr>
    ` : '');
}

/**
 * Render suspects table
 */
function renderSuspects(data) {
    const tbody = document.getElementById('suspectsBody');
    const suspects = data.suspects_60_90_days.suspects;

    if (suspects.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 2rem; color: #6b7280;">
                    No suspects at this time
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = suspects.map(item => `
        <tr>
            <td class="metric-name">${item.company_name || '-'}</td>
            <td>${item.sales_rep || '-'}</td>
            <td>${item.product || '-'}</td>
            <td>${item.seats || '-'}</td>
            <td><strong>${formatCurrency(item.mrr)}</strong></td>
            <td>${formatCurrency(item.arr)}</td>
        </tr>
    `).join('') + (data.suspects_60_90_days.totals ? `
        <tr style="font-weight: 600; background: rgba(59, 130, 246, 0.05); border-top: 2px solid #e5e7eb;">
            <td colspan="3">TOTALS</td>
            <td>${data.suspects_60_90_days.totals.total_seats || 0}</td>
            <td><strong>${formatCurrency(data.suspects_60_90_days.totals.total_mrr)}</strong></td>
            <td>${formatCurrency(data.suspects_60_90_days.totals.total_arr)}</td>
        </tr>
    ` : '');
}

/**
 * Render closed sales table
 */
function renderClosedSales(data) {
    const tbody = document.getElementById('closedSalesBody');
    const sales = data.closed_sales.sales;

    if (sales.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 2rem; color: #6b7280;">
                    No closed sales yet
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = sales.map(item => `
        <tr style="background: rgba(16, 185, 129, 0.05);">
            <td class="metric-name">${item.company_name || '-'}</td>
            <td>${item.sales_rep || '-'}</td>
            <td>${item.product || '-'}</td>
            <td>${item.seats || '-'}</td>
            <td><strong style="color: #10b981;">${formatCurrency(item.mrr)}</strong></td>
            <td style="color: #10b981;">${formatCurrency(item.arr)}</td>
            <td>${item.source || '-'}</td>
        </tr>
    `).join('') + (data.closed_sales.totals ? `
        <tr style="font-weight: 600; background: rgba(16, 185, 129, 0.1); border-top: 2px solid #10b981;">
            <td colspan="3">SALES TOTALS</td>
            <td>${data.closed_sales.totals.total_seats || 0}</td>
            <td><strong style="color: #10b981;">${formatCurrency(data.closed_sales.totals.total_mrr)}</strong></td>
            <td style="color: #10b981;">${formatCurrency(data.closed_sales.totals.total_arr)}</td>
            <td></td>
        </tr>
    ` : '');
}

/**
 * Render nurture table
 */
function renderNurture(data) {
    const tbody = document.getElementById('nurtureBody');
    const nurture = data.nurture;

    if (nurture.length === 0) {
        document.getElementById('nurtureCard').style.display = 'none';
        return;
    }

    document.getElementById('nurtureCard').style.display = 'block';

    tbody.innerHTML = nurture.map(item => `
        <tr>
            <td class="metric-name">${item.company_name || '-'}</td>
            <td>${item.sales_rep || '-'}</td>
            <td>${item.product || '-'}</td>
            <td>${item.seats || '-'}</td>
            <td>${formatCurrency(item.mrr)}</td>
            <td>${formatCurrency(item.arr)}</td>
        </tr>
    `).join('');
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
