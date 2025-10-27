/**
 * AWS Billing Dashboard JavaScript
 * Fetches and displays AWS billing data
 */

// Load AWS billing data on page load
document.addEventListener('DOMContentLoaded', function() {
    loadBillingData();
});

async function loadBillingData() {
    try {
        // For now, use mock data - will be replaced with actual API call
        const billingData = await fetchBillingData();

        if (billingData) {
            updateBillingDisplay(billingData);
        }
    } catch (error) {
        console.error('Error loading billing data:', error);
        showBillingError();
    }
}

async function fetchBillingData() {
    // TODO: Replace with actual API endpoint once Cost Explorer access is enabled
    // const response = await fetch('/api/aws-billing/dashboard');
    // return await response.json();

    // Current data based on actual AWS usage
    const currentDate = new Date();
    const currentMonth = currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
    const daysElapsed = currentDate.getDate();
    const daysInMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate();

    // ACTUAL AWS costs from October 2025 billing (as of Oct 27, 2025)
    // Updated from AWS Bills page: Total = $5.80 for 27 days
    const actualOctoberTotal = 5.80; // Actual total from AWS Bills
    const octoberDaysElapsed = 27; // Days elapsed when this data was captured

    // Calculate current day's estimated cost based on actual billing
    const actualDailyCost = actualOctoberTotal / octoberDaysElapsed; // $5.80 / 27 = ~$0.215/day
    const currentCost = (daysElapsed * actualDailyCost).toFixed(2);
    const projectedTotal = (daysInMonth * actualDailyCost).toFixed(2);

    // Actual service breakdown from AWS Bills (October 2025)
    const actualServiceCosts = {
        'EC2 (Elastic Compute)': 4.29,
        'VPC (Virtual Private Cloud)': 0.90,
        'Route 53': 0.50,
        'Secrets Manager': 0.10,
        'S3 (Simple Storage)': 0.01
    };

    // Calculate proportional costs for current day
    const serviceBreakdown = Object.entries(actualServiceCosts).map(([name, cost]) => {
        const proportion = cost / actualOctoberTotal;
        const currentServiceCost = (parseFloat(currentCost) * proportion).toFixed(2);
        return { name, cost: currentServiceCost };
    });

    return {
        current_month: {
            month: currentMonth,
            total_cost: currentCost,
            days_elapsed: daysElapsed,
            days_in_month: daysInMonth,
            projected_total: projectedTotal,
            services: serviceBreakdown
        },
        past_months: [] // No historical data - account created October 2025
    };
}

function updateBillingDisplay(data) {
    const currentMonth = data.current_month;
    const pastMonths = data.past_months;

    // Update current month card
    updateCurrentMonthCard(currentMonth);

    // Update past months cards
    updatePastMonthsCards(pastMonths, currentMonth);

    // Update last updated time
    updateLastUpdatedTime();
}

function updateCurrentMonthCard(monthData) {
    // Update month name
    const currentMonthHeader = document.querySelector('.billing-card.current-month .billing-header h3');
    if (currentMonthHeader) {
        currentMonthHeader.textContent = monthData.month;
    }

    // Update amount
    const amountElement = document.querySelector('#currentMonthBilling .amount');
    if (amountElement) {
        amountElement.textContent = parseFloat(monthData.total_cost).toFixed(2);
    }

    // Update days elapsed
    const daysElapsedElement = document.getElementById('daysElapsed');
    if (daysElapsedElement) {
        daysElapsedElement.textContent = `${monthData.days_elapsed} of ${monthData.days_in_month} days`;
    }

    // Calculate and update daily average
    const dailyAvg = (parseFloat(monthData.total_cost) / monthData.days_elapsed).toFixed(2);
    const dailyAvgElement = document.getElementById('dailyAvg');
    if (dailyAvgElement) {
        dailyAvgElement.textContent = `$${dailyAvg}`;
    }

    // Update projected total
    const projectedTotalElement = document.getElementById('projectedTotal');
    if (projectedTotalElement && monthData.projected_total) {
        projectedTotalElement.textContent = `$${parseFloat(monthData.projected_total).toFixed(2)}`;
    }

    // Update service breakdown
    const servicesContainer = document.getElementById('currentServices');
    if (servicesContainer && monthData.services) {
        servicesContainer.innerHTML = monthData.services.map(service => `
            <div class="service-item">
                <span class="service-name">${service.name}</span>
                <span class="service-cost">$${parseFloat(service.cost).toFixed(2)}</span>
            </div>
        `).join('');
    }
}

function updatePastMonthsCards(pastMonths, currentMonth) {
    if (!pastMonths || pastMonths.length === 0) return;

    // Update month 1 (most recent)
    const month1Header = document.querySelector('.billing-card:nth-child(2) .billing-header h3');
    const month1Amount = document.querySelector('#month1Billing .amount');
    const month1Change = document.getElementById('month1Change');

    if (month1Header && pastMonths[0]) {
        month1Header.textContent = pastMonths[0].name;
    }
    if (month1Amount && pastMonths[0]) {
        month1Amount.textContent = parseFloat(pastMonths[0].cost).toFixed(2);
    }
    if (month1Change) {
        const change = calculateMonthToDateComparison(currentMonth, pastMonths[0]);
        month1Change.innerHTML = change;
    }

    // Update month 2
    const month2Header = document.querySelector('.billing-card:nth-child(3) .billing-header h3');
    const month2Amount = document.querySelector('#month2Billing .amount');
    const month2Change = document.getElementById('month2Change');

    if (month2Header && pastMonths[1]) {
        month2Header.textContent = pastMonths[1].name;
    }
    if (month2Amount && pastMonths[1]) {
        month2Amount.textContent = parseFloat(pastMonths[1].cost).toFixed(2);
    }
    if (month2Change && pastMonths[0] && pastMonths[1]) {
        const change = calculateMonthOverMonthChange(pastMonths[0], pastMonths[1]);
        month2Change.innerHTML = change;
    }

    // Update month 3
    const month3Header = document.querySelector('.billing-card:nth-child(4) .billing-header h3');
    const month3Amount = document.querySelector('#month3Billing .amount');
    const month3Change = document.getElementById('month3Change');

    if (month3Header && pastMonths[2]) {
        month3Header.textContent = pastMonths[2].name;
    }
    if (month3Amount && pastMonths[2]) {
        month3Amount.textContent = parseFloat(pastMonths[2].cost).toFixed(2);
    }
    if (month3Change && pastMonths[1] && pastMonths[2]) {
        const change = calculateMonthOverMonthChange(pastMonths[1], pastMonths[2]);
        month3Change.innerHTML = change;
    }
}

function calculateMonthToDateComparison(currentMonth, lastMonth) {
    const currentCost = parseFloat(currentMonth.total_cost);
    const lastMonthCost = parseFloat(lastMonth.cost);
    const daysElapsed = currentMonth.days_elapsed;
    const daysInMonth = currentMonth.days_in_month;

    // Project current month's total
    const projectedTotal = (currentCost / daysElapsed) * daysInMonth;
    const difference = projectedTotal - lastMonthCost;
    const percentChange = ((difference / lastMonthCost) * 100).toFixed(1);

    if (difference > 0) {
        return `<span class="billing-change negative">Projected +${Math.abs(percentChange)}% vs ${lastMonth.name}</span>`;
    } else {
        return `<span class="billing-change positive">Projected ${percentChange}% vs ${lastMonth.name}</span>`;
    }
}

function calculateMonthOverMonthChange(currentMonth, previousMonth) {
    const current = parseFloat(currentMonth.cost);
    const previous = parseFloat(previousMonth.cost);
    const difference = current - previous;
    const percentChange = ((difference / previous) * 100).toFixed(1);

    if (difference > 0) {
        return `<span class="billing-change negative">+${percentChange}% vs ${previousMonth.name}</span>`;
    } else {
        return `<span class="billing-change positive">${percentChange}% vs ${previousMonth.name}</span>`;
    }
}

function updateLastUpdatedTime() {
    const updateTimeElement = document.getElementById('awsUpdateTime');
    if (updateTimeElement) {
        const now = new Date();
        const timeStr = now.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit'
        });
        updateTimeElement.textContent = `Updated ${timeStr}`;
    }
}

function showBillingError() {
    const billingGrid = document.querySelector('.billing-grid');
    if (billingGrid) {
        billingGrid.innerHTML = `
            <div class="error-message" style="grid-column: 1 / -1; padding: 2rem; text-align: center; color: #d73a49;">
                <p>Unable to load billing data. Please try again later.</p>
            </div>
        `;
    }
}
