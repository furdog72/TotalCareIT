#!/usr/bin/env python3
"""
Generate complete scorecard HTML from Excel data sources.
Combines operations metrics from Scorecard 2024.xlsx and Pro Service PBR from TotalCareIT PBR 2024.xlsx
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path

# File paths
SCORECARD_EXCEL = "/Users/charles/Desktop/Jess2/Prevailing Networks Inc. dba TotalCareIT/TotalCareIT - IDS/Scorecard 2024.xlsx"
PBR_EXCEL = "/Users/charles/Desktop/Jess2/Prevailing Networks Inc. dba TotalCareIT/TotalCareIT - Sales - Sales/TotalCareIT PBR 2024.xlsx"
OUTPUT_HTML = "/Users/charles/Projects/qbo-ai/website/scorecard-2024-q4.html"

def extract_scorecard_data():
    """Extract operations scorecard data from Excel"""
    print("📊 Extracting Scorecard 2024 data...")

    df = pd.read_excel(SCORECARD_EXCEL, sheet_name='Scorecard 2024', header=None)

    # Q4 October columns: 46 (Oct 4), 47 (Oct 11), 48 (Oct 18), 49 (Oct 25)
    oct_cols = [46, 47, 48, 49]
    date_row = df.iloc[2]

    metrics = []

    for row_idx in range(3, df.shape[0]):
        kpi_name = df.iloc[row_idx, 0]
        if pd.isna(kpi_name):
            continue

        accountable = df.iloc[row_idx, 1]
        goal = df.iloc[row_idx, 2]

        # Extract October values
        oct_values = []
        for col_idx in oct_cols:
            value = df.iloc[row_idx, col_idx]
            date_val = date_row[col_idx]
            oct_values.append({
                'date': date_val.strftime('%m/%d') if isinstance(date_val, datetime) else str(col_idx),
                'value': value if pd.notna(value) else None
            })

        is_section = pd.isna(accountable)

        # Check if this section header has a goal or any values
        has_goal = pd.notna(goal) and goal != ''
        has_values = any(v['value'] is not None for v in oct_values)

        # If it's a section with goal/values, treat it as a metric row
        if is_section and (has_goal or has_values):
            is_section = False  # Treat as a metric row for display purposes
            accountable = 'Calculated'  # Mark as calculated field

        metrics.append({
            'kpi': str(kpi_name),
            'accountable': str(accountable) if pd.notna(accountable) else None,
            'goal': goal if pd.notna(goal) else None,
            'is_section': is_section,
            'october_weeks': oct_values,
            'metric_type': determine_metric_type(str(kpi_name))
        })

    print(f"  ✓ Extracted {len(metrics)} metrics")
    return metrics

def extract_pbr_data():
    """Extract Pro Service PBR data from all quarters"""
    print("💼 Extracting Pro Service PBR data...")

    quarters = {
        'Q1': 'PRO SVC Q1',
        'Q2': 'PRO SVC Q2',
        'Q3': 'PRO SVC Q3 (2)',
        'Q4': 'PRO SVC Q4'
    }

    pbr_data = {}

    for quarter, sheet_name in quarters.items():
        try:
            df = pd.read_excel(PBR_EXCEL, sheet_name=sheet_name, header=None)

            # Determine column position for this quarter
            quarter_positions = {'Q1': 3, 'Q2': 4, 'Q3': 5, 'Q4': 6}
            col = quarter_positions[quarter]

            goal = df.iloc[2, col] if pd.notna(df.iloc[2, col]) else None
            actual = df.iloc[3, col] if pd.notna(df.iloc[3, col]) else None

            # Handle variance (Q4 may have "." character)
            variance_val = df.iloc[4, col]
            if pd.notna(variance_val) and variance_val != '.':
                variance = float(variance_val)
            else:
                variance = None

            goal_pct = df.iloc[5, col] if pd.notna(df.iloc[5, col]) else None

            pbr_data[quarter] = {
                'goal': float(goal) if goal else None,
                'actual': float(actual) if actual else None,
                'variance': variance,
                'goal_percent': float(goal_pct) if goal_pct else None
            }

            print(f"  ✓ {quarter}: ${actual:,.2f} / ${goal:,.0f}" if actual and goal else f"  ✓ {quarter}: Data extracted")

        except Exception as e:
            print(f"  ✗ {quarter} error: {str(e)}")
            pbr_data[quarter] = None

    return pbr_data

def determine_metric_type(kpi_name):
    """Determine if metric is 'lower is better' or 'higher is better'"""
    lower_is_better = ['response time', 'resolution time', 'tickets >7', 'failed backup',
                       'missing', 'windows 7', 'eol', 'tickets over 30']

    kpi_lower = kpi_name.lower()

    for phrase in lower_is_better:
        if phrase in kpi_lower:
            return 'lower_is_better'

    return 'higher_is_better'

def get_cell_class(value, goal, metric_type):
    """Determine CSS class for cell based on value vs goal"""
    if value is None or goal is None:
        return 'empty'

    try:
        value_num = float(value)
        goal_num = float(goal)

        if metric_type == 'lower_is_better':
            # For metrics like response time, lower is better
            if value_num < goal_num:
                return 'good'  # Green
            elif value_num == goal_num:
                return 'warning'  # Yellow
            else:
                return 'bad'  # Red
        else:
            # For metrics like sales, higher is better
            if value_num > goal_num:
                return 'good'  # Green
            elif value_num == goal_num:
                return 'warning'  # Yellow
            else:
                return 'bad'  # Red
    except (ValueError, TypeError):
        return 'neutral'

def format_value(value):
    """Format value for display"""
    if value is None:
        return '-'

    if isinstance(value, (int, float)):
        # Format numbers appropriately
        if abs(value) < 1 and value != 0:
            return f"{value:.2f}"  # Decimals like 0.59
        elif abs(value) >= 1000:
            return f"{value:,.0f}"  # Thousands with commas
        else:
            return f"{value:.0f}"  # Whole numbers

    return str(value)

def generate_html(metrics, pbr_data):
    """Generate complete scorecard HTML"""
    print("🎨 Generating HTML...")

    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scorecard 2024 Q4 - TotalCareIT</title>
    <link rel="stylesheet" href="css/styles.css">
    <style>
        body {
            font-family: 'Inter', -apple-system, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }

        .scorecard-container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .scorecard-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }

        .scorecard-header h1 {
            margin: 0 0 0.5rem 0;
            font-size: 2rem;
        }

        .scorecard-header p {
            margin: 0;
            opacity: 0.9;
        }

        .table-wrapper {
            overflow-x: auto;
            padding: 1rem;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }

        th, td {
            padding: 10px 8px;
            text-align: left;
            border: 1px solid #e0e0e0;
        }

        th {
            background: #34495e;
            color: white;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 10;
        }

        th.metric-col {
            width: 250px;
            background: #2c3e50;
        }

        th.owner-col {
            width: 100px;
        }

        th.goal-col {
            width: 80px;
        }

        th.week-col {
            width: 90px;
            text-align: center;
            background: #667eea;
        }

        td.metric-name {
            font-weight: 600;
            background: #f8f9fa;
        }

        td.section-header {
            background: #e9ecef;
            font-weight: 700;
            font-size: 14px;
            color: #495057;
        }

        td.week-value {
            text-align: center;
            font-weight: 500;
        }

        /* Color coding */
        .good {
            background: #d4edda !important;
            color: #155724;
        }

        .warning {
            background: #fff3cd !important;
            color: #856404;
        }

        .bad {
            background: #f8d7da !important;
            color: #721c24;
        }

        .empty {
            background: #fafafa;
            color: #999;
        }

        .neutral {
            background: white;
        }

        /* PBR Section */
        .pbr-section {
            margin: 2rem 1rem;
            background: #f8f9fa;
            border-radius: 8px;
            padding: 1.5rem;
        }

        .pbr-section h2 {
            margin: 0 0 1rem 0;
            color: #2c3e50;
        }

        .pbr-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }

        .pbr-card {
            background: white;
            padding: 1rem;
            border-radius: 6px;
            border: 1px solid #dee2e6;
        }

        .pbr-card h3 {
            margin: 0 0 0.5rem 0;
            font-size: 0.9rem;
            color: #6c757d;
            font-weight: 600;
        }

        .pbr-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #2c3e50;
        }

        .pbr-positive {
            color: #28a745;
        }

        .pbr-negative {
            color: #dc3545;
        }

        .quarter-toggle {
            margin: 1rem;
            padding: 0.5rem 1rem;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }

        .quarter-toggle:hover {
            background: #5568d3;
        }

        .historical-quarters {
            display: none;
            margin: 1rem;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 6px;
        }

        .historical-quarters.visible {
            display: block;
        }
    </style>
</head>
<body>
    <div class="scorecard-container">
        <div class="scorecard-header">
            <h1>TotalCareIT Scorecard</h1>
            <p>2024 Q4 - October Metrics</p>
        </div>
"""

    # Add Pro Service PBR Section
    html += """
        <div class="pbr-section">
            <h2>💼 Pro Service PBR - 2024 Q4</h2>
            <div class="pbr-grid">
"""

    q4_data = pbr_data.get('Q4', {})
    if q4_data:
        goal = q4_data.get('goal')
        actual = q4_data.get('actual')
        variance = q4_data.get('variance')
        goal_pct = q4_data.get('goal_percent')

        html += f"""
                <div class="pbr-card">
                    <h3>PS Team Goal</h3>
                    <div class="pbr-value">${goal:,.0f}</div>
                </div>
                <div class="pbr-card">
                    <h3>PS Team Actual</h3>
                    <div class="pbr-value">${actual:,.2f}</div>
                </div>
                <div class="pbr-card">
                    <h3>(+/-) Variance</h3>
                    <div class="pbr-value {'pbr-positive' if variance and variance > 0 else 'pbr-negative' if variance and variance < 0 else ''}">
                        {f'${variance:,.2f}' if variance else 'TBD'}
                    </div>
                </div>
                <div class="pbr-card">
                    <h3>Goal Achievement</h3>
                    <div class="pbr-value {'pbr-positive' if goal_pct and goal_pct > 0.5 else 'pbr-negative' if goal_pct and goal_pct <= 0.5 else ''}">
                        {f'{goal_pct*100:.1f}%' if goal_pct is not None else 'N/A'}
                    </div>
                </div>
"""

    html += """
            </div>
        </div>

        <button class="quarter-toggle" onclick="toggleHistorical()">
            📊 Show Historical Quarters (Q1-Q3)
        </button>

        <div class="historical-quarters" id="historicalQuarters">
            <h3>Historical Pro Service PBR Performance</h3>
"""

    # Add historical quarters
    for quarter in ['Q1', 'Q2', 'Q3']:
        q_data = pbr_data.get(quarter, {})
        if q_data:
            actual = q_data.get('actual', 0)
            goal = q_data.get('goal', 0)
            pct = q_data.get('goal_percent')
            pct_text = f"{pct*100:.1f}% achievement" if pct is not None else "N/A"
            html += f"""
            <div style="margin-bottom: 1rem;">
                <strong>{quarter} 2024:</strong>
                ${actual:,.2f} / ${goal:,.0f}
                ({pct_text})
            </div>
"""

    html += """
        </div>

        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th class="metric-col">Metric / KPI</th>
                        <th class="owner-col">Owner</th>
                        <th class="goal-col">Goal</th>
                        <th class="week-col">10/04</th>
                        <th class="week-col">10/11</th>
                        <th class="week-col">10/18</th>
                        <th class="week-col">10/25</th>
                    </tr>
                </thead>
                <tbody>
"""

    # Add metrics rows
    for metric in metrics:
        if metric['is_section']:
            # Section header row - check if it has week values
            has_week_values = any(week['value'] is not None for week in metric['october_weeks'])

            if has_week_values:
                # Section header with values (like "Reactive Operations 2024 Q4")
                html += f"""
                    <tr>
                        <td class="section-header">{metric['kpi']}</td>
                        <td colspan="2" class="section-header"></td>
"""
                # Add weekly values
                for week in metric['october_weeks']:
                    value = week['value']
                    formatted_value = format_value(value) if value is not None else ''

                    html += f"""
                        <td class="section-header week-value">{formatted_value}</td>
"""
                html += """
                    </tr>
"""
            else:
                # Regular section header with no data
                html += f"""
                    <tr>
                        <td colspan="7" class="section-header">{metric['kpi']}</td>
                    </tr>
"""
        else:
            # Regular metric row
            kpi = metric['kpi']
            owner = metric['accountable'] or ''
            goal = format_value(metric['goal'])
            metric_type = metric['metric_type']

            html += f"""
                    <tr>
                        <td class="metric-name">{kpi}</td>
                        <td>{owner}</td>
                        <td>{goal}</td>
"""

            # Add weekly values
            for week in metric['october_weeks']:
                value = week['value']
                cell_class = get_cell_class(value, metric['goal'], metric_type)
                formatted_value = format_value(value)

                html += f"""
                        <td class="week-value {cell_class}">{formatted_value}</td>
"""

            html += """
                    </tr>
"""

    html += """
                </tbody>
            </table>
        </div>
    </div>

    <script>
        function toggleHistorical() {
            const historical = document.getElementById('historicalQuarters');
            historical.classList.toggle('visible');

            const btn = event.target;
            if (historical.classList.contains('visible')) {
                btn.textContent = '📊 Hide Historical Quarters';
            } else {
                btn.textContent = '📊 Show Historical Quarters (Q1-Q3)';
            }
        }
    </script>
</body>
</html>
"""

    return html

def main():
    """Main execution function"""
    print("="*100)
    print("SCORECARD GENERATOR - STARTING")
    print("="*100)

    # Extract data
    metrics = extract_scorecard_data()
    pbr_data = extract_pbr_data()

    # Generate HTML
    html = generate_html(metrics, pbr_data)

    # Write to file
    output_path = Path(OUTPUT_HTML)
    output_path.write_text(html, encoding='utf-8')

    print(f"\n✅ Scorecard generated successfully!")
    print(f"📁 Output: {OUTPUT_HTML}")
    print(f"📊 Metrics: {len(metrics)}")
    print(f"💼 PBR Quarters: {len([q for q in pbr_data.values() if q])}")
    print("="*100)

if __name__ == "__main__":
    main()
