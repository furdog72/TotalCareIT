#!/usr/bin/env python3
"""
Build complete scorecard HTML from extracted JSON data with collapsible sections
"""
import json

# Load scorecard data
with open('/Users/charles/Projects/qbo-ai/scorecard_data.json', 'r') as f:
    data = json.load(f)

# Quarter boundaries
quarters = [
    {'name': 'Q1 2025', 'start': 0, 'end': 13},
    {'name': 'Q2 2025', 'start': 14, 'end': 27},
    {'name': 'Q3 2025', 'start': 28, 'end': 42},
    {'name': 'Q4 2025', 'start': 43, 'end': 57},
]

def format_value(val):
    """Format cell value for display"""
    if val is None or val == '':
        return '-'
    if isinstance(val, (int, float)):
        if val == 0 and isinstance(val, int):
            return '0'
        if abs(val) >= 1000 and isinstance(val, int):
            return f'{int(val):,}'
        if isinstance(val, float) and val != int(val):
            return f'{val:.2f}'
        return str(int(val) if val == int(val) else val)
    return str(val)

def get_status_class(value, goal):
    """Determine CSS class based on whether value meets goal"""
    if value is None or value == '' or goal is None or goal == '' or goal == '-':
        return ''

    try:
        val = float(str(value).replace('%', '').replace('$', '').replace(',', ''))
        goal_str = str(goal)

        if '<=' in goal_str:
            goal_num = float(goal_str.replace('<=', '').strip())
            return 'status-good' if val <= goal_num else 'status-warning'
        elif '>=' in goal_str:
            goal_num = float(goal_str.replace('>=', '').strip())
            return 'status-good' if val >= goal_num else 'status-warning'
        else:
            goal_num = float(str(goal).replace('%', '').replace('$', '').replace(',', ''))
            return 'status-good' if val >= goal_num else 'status-warning'
    except:
        return ''

def build_section_table(section_name, metrics, section_id):
    """Build HTML table for a section"""
    html = f'''
                <!-- {section_name} -->
                <div class="section-table">
                    <div class="section-header">
                        <strong>{section_name}</strong>
                    </div>
                    <div class="section-content">
                        <table>
                            <thead>
                                <tr>
                                    <th class="metric-name"></th>
                                    <th class="accountable">Accountable</th>
                                    <th class="goal">Goal</th>
'''

    # Add single row of dates/headers across the top
    week_dates = data['week_dates']
    for i, date in enumerate(week_dates):
        # Determine which quarter this column belongs to
        if i <= 13:
            week_class = "q1-week"
        elif i <= 27:
            week_class = "q2-week"
        elif i <= 42:
            week_class = "q3-week"
        elif i <= 57:
            week_class = "q4-week"
        else:
            week_class = "year-summary"

        if date == 'AVG':
            quarter_num = [13, 27, 42, 57].index(i) + 1
            # Quarterly AVG always visible - clickable to toggle that quarter
            html += f'''                                    <th class="q-avg quarter-separator quarter-toggle-header" onclick="toggleQuarter('q{quarter_num}')" style="cursor: pointer;" title="Click to toggle Q{quarter_num} weeks">
                                        <span id="toggle-q{quarter_num}" class="toggle-icon">▼</span> Q{quarter_num}
                                    </th>\n'''
        elif i == 58:
            # Year AVG always visible
            html += f'                                    <th class="year-avg">Year</th>\n'
        else:
            # Weekly columns can be hidden - show date
            html += f'                                    <th class="week {week_class}">{date}</th>\n'

    html += '''                                </tr>
                            </thead>
                            <tbody>
'''

    # Add metric rows
    for metric in metrics:
        kpi_name = metric['kpi']
        accountable = metric['accountable'] if metric['accountable'] else '-'
        goal = format_value(metric['goal'])

        html += f'''                                <tr>
                                    <td class="metric-name">{kpi_name}</td>
                                    <td class="accountable">{accountable}</td>
                                    <td class="goal">{goal}</td>
'''

        # Add data cells with color coding
        values = metric['values']
        for i, val in enumerate(values):
            formatted_val = format_value(val)

            # Determine which quarter this column belongs to
            if i <= 13:
                week_class = "q1-week"
            elif i <= 27:
                week_class = "q2-week"
            elif i <= 42:
                week_class = "q3-week"
            elif i <= 57:
                week_class = "q4-week"
            else:
                week_class = "year-summary"

            cell_class = ''
            if i in [13, 27, 42, 57]:
                # Quarterly AVG - always visible
                cell_class = 'q-avg quarter-separator'
                if val is not None and val != '':
                    status = get_status_class(val, metric['goal'])
                    if status:
                        cell_class += f' {status}'
            elif i == 58:
                # Year AVG - always visible
                cell_class = 'year-avg'
            else:
                # Weekly column - can be hidden
                cell_class = week_class
                if val is None or val == '':
                    cell_class += ' tbd'
                else:
                    status = get_status_class(val, metric['goal'])
                    if status:
                        cell_class += f' {status}'

            html += f'                                    <td class="{cell_class}">{formatted_val}</td>\n'

        html += '                                </tr>\n'

    html += '''                            </tbody>
                        </table>
                    </div>
                </div>

'''

    return html

# Build complete HTML
html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scorecard 2025 - TotalCareIT</title>
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

        .section-table {
            width: 100%;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }

        .section-header {
            background: #2c3e50;
            color: white;
            font-weight: 700;
            font-size: 14px;
            padding: 12px 15px;
            border-radius: 8px 8px 0 0;
        }

        .section-content {
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 11px;
        }

        .quarter-header {
            background: #34495e;
            color: white;
            text-align: center;
            font-weight: 600;
            font-size: 10px;
        }

        .quarter-header td {
            padding: 8px 5px;
            border-right: 1px solid #2c3e50;
        }

        .quarter-header td:first-child {
            text-align: left;
            padding-left: 12px;
        }

        th {
            background: #0078D4;
            color: white;
            padding: 6px 4px;
            text-align: center;
            font-weight: 600;
            font-size: 9px;
            border-right: 1px solid #005a9e;
        }

        th.metric-name {
            text-align: left;
            width: 180px;
            background: transparent;
            border-right: 1px solid #ddd;
        }

        th.accountable {
            width: 80px;
            background: transparent;
            border-right: 1px solid #ddd;
        }

        th.goal {
            width: 60px;
            background: transparent;
            border-right: 2px solid #333;
        }

        th.week {
            width: 50px;
            min-width: 45px;
        }

        th.q-avg {
            width: 60px;
            background: #FFE4B5;
            color: #333;
        }

        th.year-avg {
            width: 60px;
            background: #E6E6FA;
            color: #333;
        }

        td {
            padding: 5px 3px;
            border-bottom: 1px solid #e5e7eb;
            border-right: 1px solid #f0f0f0;
            text-align: center;
            font-size: 10px;
        }

        td.metric-name {
            text-align: left;
            font-weight: 500;
            padding-left: 10px;
            border-right: 1px solid #ddd;
        }

        td.accountable {
            text-align: left;
            font-style: italic;
            color: #666;
            border-right: 1px solid #ddd;
        }

        td.goal {
            border-right: 2px solid #333;
        }

        tr:hover {
            background: #f9fafb;
        }

        .status-good {
            background-color: #90EE90 !important;
            font-weight: 600;
        }

        .status-warning {
            background-color: #FFB6C1 !important;
            font-weight: 600;
        }

        .status-bad {
            background-color: #FF6B6B !important;
            color: white;
            font-weight: 600;
        }

        .q-avg {
            background-color: #FFE4B5;
            font-weight: 700;
        }

        .year-avg {
            background-color: #E6E6FA;
            font-weight: 700;
        }

        .tbd {
            color: #999;
            font-style: italic;
        }

        .quarter-separator {
            border-right: 2px solid #666 !important;
        }

        /* Quarter column hiding - only hide weekly columns, keep AVGs visible */
        .q1-week.hidden,
        .q2-week.hidden,
        .q3-week.hidden,
        .q4-week.hidden {
            display: none;
        }

        .quarter-toggle:hover {
            background: #475569 !important;
        }

        .quarter-toggle-header {
            cursor: pointer;
            user-select: none;
        }

        .quarter-toggle-header:hover {
            background: #FFD699 !important;
        }

        .quarter-toggle-header .toggle-icon {
            display: inline-block;
            margin-right: 5px;
            transition: transform 0.2s;
            font-size: 10px;
        }

        .quarter-toggle-header .toggle-icon.collapsed {
            transform: rotate(-90deg);
        }
    </style>
    <script>
        // Track which quarters are visible (Q1, Q2, Q3 collapsed by default, Q4 visible)
        const quarterState = {
            q1: false,
            q2: false,
            q3: false,
            q4: true
        };

        function toggleQuarter(quarter) {
            // Toggle state
            quarterState[quarter] = !quarterState[quarter];

            // Get only weekly columns for this quarter (not the AVG)
            const elements = document.querySelectorAll('.' + quarter + '-week');
            const icon = document.getElementById('toggle-' + quarter);

            if (quarterState[quarter]) {
                // Show quarter weeks
                elements.forEach(el => el.classList.remove('hidden'));
                if (icon) icon.classList.remove('collapsed');
            } else {
                // Hide quarter weeks (AVG stays visible)
                elements.forEach(el => el.classList.add('hidden'));
                if (icon) icon.classList.add('collapsed');
            }
        }

        // Page load initialization - collapse Q1, Q2, Q3 by default
        window.addEventListener('DOMContentLoaded', function() {
            console.log('Scorecard loaded - Q1, Q2, Q3 collapsed by default, Q4 visible');

            // Collapse Q1, Q2, Q3
            ['q1', 'q2', 'q3'].forEach(quarter => {
                const elements = document.querySelectorAll('.' + quarter + '-week');
                const icon = document.getElementById('toggle-' + quarter);

                elements.forEach(el => el.classList.add('hidden'));
                if (icon) icon.classList.add('collapsed');
            });
        });
    </script>
</head>
<body class="dashboard-page">
    <div class="dashboard-container">
        <!-- Sidebar -->
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
                <a href="#" class="nav-item disabled" title="Coming soon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="16 18 22 12 16 6"/>
                        <polyline points="8 6 2 12 8 18"/>
                    </svg>
                    <span>Automations</span>
                </a>
            </nav>
        </aside>

        <!-- Main Content -->
        <main class="dashboard-main">
            <div class="scorecard-container">
                <div class="scorecard-header">
                    <h1>Scorecard 2025</h1>
                    <p style="color: #666; margin: 5px 0;">Full Year Performance Metrics - Click section headers to expand/collapse</p>
                </div>

'''

# Add all sections with unique IDs
section_order = [
    ('Inside Sales Activity', 'inside-sales'),
    ('Outside Sales Activity', 'outside-sales'),
    ('Warm 250 Activity', 'warm-250'),
    ('Reactive Operations', 'reactive-ops'),
    ('Centralized Services', 'centralized'),
    ('Professional Services', 'pro-services'),
    ('TAM', 'tam'),
    ('vCIO', 'vcio')
]

for section_name, section_id in section_order:
    if section_name in data['sections']:
        html_content += build_section_table(section_name, data['sections'][section_name], section_id)

# Add footer
html_content += '''
                <div style="background: #f0f9ff; border-left: 4px solid #0078D4; padding: 20px; border-radius: 4px; margin-top: 30px;">
                    <h3 style="margin-top: 0;">Scorecard Details</h3>
                    <ul style="margin: 10px 0; padding-left: 20px; font-size: 13px;">
                        <li><strong>Color Coding:</strong> Green = Met/Exceeded Goal, Pink = Below Goal</li>
                        <li><strong>Data Sources:</strong> HubSpot (Sales metrics), Autotask (Operations, Pro Services, TAM), Manual (Centralized Services, vCIO)</li>
                        <li><strong>Collapsible Sections:</strong> Click any section header to expand or collapse that section</li>
                    </ul>
                </div>
            </div>
        </main>
    </div>
</body>
</html>
'''

# Write to file
with open('/Users/charles/Projects/qbo-ai/website/scorecard-complete.html', 'w') as f:
    f.write(html_content)

print('Scorecard HTML with collapsible sections generated successfully!')
