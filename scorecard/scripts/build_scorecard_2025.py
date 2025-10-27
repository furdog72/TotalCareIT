#!/usr/bin/env python3
"""
Build scorecard HTML for October 2025 with weeks 1-4
"""
import json
from pathlib import Path

# Load October 2025 scorecard data
json_path = Path('/Users/charles/Projects/qbo-ai/website/data/scorecard-october-2025.json')
with open(json_path, 'r') as f:
    data = json.load(f)

def format_value(val):
    """Format cell value for display"""
    if val is None or val == '':
        return '-'

    # Handle string values
    val_str = str(val)

    # Section headers (like "Inside Sales 2025 Q4")
    if 'Q4' in val_str or 'Activity' in val_str or 'Operations' in val_str or 'Services' in val_str:
        return val_str

    try:
        # Try to convert to float
        num_val = float(val_str.replace(',', ''))

        # Percentages (values between 0 and 1 that aren't counts)
        if 0 < num_val < 1 and num_val != int(num_val):
            return f'{num_val * 100:.1f}%'

        # Large integers (format with commas)
        if num_val >= 100 and num_val == int(num_val):
            return f'{int(num_val):,}'

        # Decimals
        if num_val != int(num_val):
            return f'{num_val:.2f}'

        # Regular integers
        return str(int(num_val))
    except:
        return val_str

def get_status_class(value, goal, kpi_name):
    """Determine CSS class based on whether value meets goal"""
    if value is None or value == '' or value == '-' or goal is None or goal == '':
        return ''

    # Skip section headers
    if 'Q4' in str(value) or 'Activity' in str(value):
        return ''

    try:
        val_str = str(value).replace('%', '').replace('$', '').replace(',', '')
        val = float(val_str)
        goal_str = str(goal).replace('%', '').replace('$', '').replace(',', '')

        # Handle percentage goals (multiply by 100 if goal is < 1)
        if 0 < float(goal_str) < 1:
            goal_num = float(goal_str)
            val_normalized = val if val > 1 else val
            goal_normalized = goal_num * 100 if goal_num < 1 else goal_num

            # For metrics where lower is better
            if any(x in kpi_name.lower() for x in ['failed', 'missing', 'old', 'tickets >7', 'rhem', 'response time', 'resolution time']):
                return 'status-good' if val <= goal_normalized else 'status-warning'
            else:
                return 'status-good' if val >= goal_normalized else 'status-warning'
        else:
            goal_num = float(goal_str)

            # For metrics where lower is better
            if any(x in kpi_name.lower() for x in ['failed', 'missing', 'old', 'tickets >7', 'rhem', 'response time', 'resolution time']):
                return 'status-good' if val <= goal_num else 'status-warning'
            else:
                return 'status-good' if val >= goal_num else 'status-warning'
    except:
        return ''

# Build HTML
html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scorecard October 2025 - TotalCareIT</title>
    <link rel="stylesheet" href="css/styles.css">
    <style>
        .scorecard-container {
            max-width: 100%;
            margin: 0 auto;
            padding: 20px;
            overflow-x: auto;
        }

        .scorecard-header {
            text-align: center;
            margin-bottom: 20px;
        }

        .scorecard-header h1 {
            margin-bottom: 5px;
        }

        .scorecard-table {
            width: 100%;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
        }

        .date-header {
            background: #0078D4;
            color: white;
            position: sticky;
            top: 0;
            z-index: 10;
        }

        th {
            background: #0078D4;
            color: white;
            padding: 8px 6px;
            text-align: left;
            font-weight: 600;
            border: 1px solid #005a9e;
        }

        th.week-header {
            text-align: center;
            min-width: 80px;
        }

        td {
            padding: 6px 6px;
            border: 1px solid #e1e4e8;
            text-align: left;
        }

        td.week-cell {
            text-align: center;
            font-weight: 500;
        }

        td.goal-cell {
            text-align: center;
            font-weight: 600;
            background: #f6f8fa;
        }

        .section-row {
            background: #f0f0f0;
            font-weight: bold;
        }

        .section-row td {
            padding: 10px 6px;
            font-size: 13px;
            background: #e8f4f8;
            border-top: 2px solid #0078D4;
        }

        .status-good {
            background-color: #d4edda !important;
            color: #155724;
        }

        .status-warning {
            background-color: #fff3cd !important;
            color: #856404;
        }

        .accountable-cell {
            font-weight: 500;
            color: #0078D4;
        }

        tr:hover td {
            background-color: #f8f9fa;
        }

        .section-row:hover td {
            background-color: #e8f4f8 !important;
        }

        @media (max-width: 768px) {
            table {
                font-size: 10px;
            }
            th, td {
                padding: 4px 3px;
            }
        }
    </style>
</head>
<body class="dashboard-page">
    <div class="dashboard-container">
        <aside class="sidebar">
            <div class="sidebar-header">
                <img src="https://totalcareit.com/wp-content/uploads/2024/11/TotalCareIT-Registered-Logo-White-1024x189.png" alt="TotalCare IT Logo" class="sidebar-logo">
            </div>
            <nav class="sidebar-nav">
                <a href="dashboard.html" class="nav-item">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="3" width="7" height="7"/>
                        <rect x="14" y="3" width="7" height="7"/>
                        <rect x="14" y="14" width="7" height="7"/>
                        <rect x="3" y="14" width="7" height="7"/>
                    </svg>
                    <span>Dashboard</span>
                </a>
                <a href="sales-report.html" class="nav-item">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="12" y1="20" x2="12" y2="10"/>
                        <line x1="18" y1="20" x2="18" y2="4"/>
                        <line x1="6" y1="20" x2="6" y2="16"/>
                    </svg>
                    <span>Sales Report</span>
                </a>
                <a href="linkedin-performance.html" class="nav-item">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/>
                        <rect x="2" y="9" width="4" height="12"/>
                        <circle cx="4" cy="4" r="2"/>
                    </svg>
                    <span>LinkedIn Performance</span>
                </a>
                <a href="scorecard-complete.html" class="nav-item active">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="20" x2="18" y2="10"/>
                        <line x1="12" y1="20" x2="12" y2="4"/>
                        <line x1="6" y1="20" x2="6" y2="14"/>
                    </svg>
                    <span>Scorecard</span>
                </a>
                <a href="quickbooks.html" class="nav-item">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
                        <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
                    </svg>
                    <span>QuickBooks</span>
                </a>
                <a href="prospective-business.html" class="nav-item">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
                        <circle cx="9" cy="7" r="4"/>
                        <path d="M22 21v-2a4 4 0 0 0-3-3.87"/>
                        <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                    </svg>
                    <span>Prospective Business</span>
                </a>
                <a href="finance.html" class="nav-item">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="12" y1="1" x2="12" y2="23"/>
                        <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                    </svg>
                    <span>Finance</span>
                </a>
                <a href="trumethods-qbr.html" class="nav-item">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                        <polyline points="14 2 14 8 20 8"/>
                        <line x1="16" y1="13" x2="8" y2="13"/>
                        <line x1="16" y1="17" x2="8" y2="17"/>
                        <polyline points="10 9 9 9 8 9"/>
                    </svg>
                    <span>TruMethods QBR</span>
                </a>
            </nav>
        </aside>

        <main class="dashboard-main">
            <div class="scorecard-container">
                <div class="scorecard-header">
                    <h1>Scorecard October 2025</h1>
                    <p style="color: #666; font-size: 14px;">Week ending dates: 10/03, 10/10, 10/17, 10/24</p>
                </div>

                <div class="scorecard-table">
                    <table>
                        <thead>
                            <tr class="date-header">
                                <th style="min-width: 200px;">KPI</th>
                                <th style="min-width: 100px;">Accountable</th>
                                <th style="min-width: 80px;">Goal</th>
                                <th class="week-header">10/03</th>
                                <th class="week-header">10/10</th>
                                <th class="week-header">10/17</th>
                                <th class="week-header">10/24</th>
                            </tr>
                        </thead>
                        <tbody>
"""

# Add data rows
for item in data:
    kpi = item['kpi']
    accountable = item['accountable'] if item['accountable'] else ''
    goal = item['goal'] if item['goal'] else ''
    weeks = item['october_weeks']

    # Determine if this is a section header
    is_section = item.get('is_section', False)

    if is_section:
        # Section header row
        html += f"""                            <tr class="section-row">
                                <td colspan="7">{kpi}</td>
                            </tr>
"""
    else:
        # Regular KPI row
        html += f"""                            <tr>
                                <td>{kpi}</td>
                                <td class="accountable-cell">{accountable}</td>
                                <td class="goal-cell">{format_value(goal)}</td>
"""
        # Add week cells with status coloring
        for week in weeks:
            value = week['value']
            formatted_value = format_value(value)
            status_class = get_status_class(value, goal, kpi)
            html += f"""                                <td class="week-cell {status_class}">{formatted_value}</td>
"""
        html += """                            </tr>
"""

# Close HTML
html += """                        </tbody>
                    </table>
                </div>
            </div>
        </main>
    </div>

    <script src="https://alcdn.msauth.net/browser/2.30.0/js/msal-browser.min.js"></script>
    <script src="js/auth.js"></script>
    <script src="js/permissions.js"></script>
</body>
</html>
"""

# Write to file
output_path = Path('/Users/charles/Projects/qbo-ai/website/scorecard-complete.html')
with open(output_path, 'w') as f:
    f.write(html)

print(f"✅ Built scorecard HTML with {len(data)} KPIs")
print(f"✅ Saved to: {output_path}")
print(f"\nWeeks included:")
print(f"  - 10/03 (Week 1)")
print(f"  - 10/10 (Week 2)")
print(f"  - 10/17 (Week 3)")
print(f"  - 10/24 (Week 4) - Needs automated data collection")
