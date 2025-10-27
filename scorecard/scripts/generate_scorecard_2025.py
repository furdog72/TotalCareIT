#!/usr/bin/env python3
"""
Generate Scorecard 2025 Q4 HTML from Excel data
Uses Scorecard 2025.xlsx as template and data source
"""

import pandas as pd
from datetime import datetime
from pathlib import Path

# File paths
SCORECARD_2025 = "/Users/charles/Projects/Reference/Scorecard 2025.xlsx"
PBR_2024 = "/Users/charles/Desktop/Jess2/Prevailing Networks Inc. dba TotalCareIT/TotalCareIT - Sales - Sales/TotalCareIT PBR 2024.xlsx"
OUTPUT_HTML = "/Users/charles/Projects/qbo-ai/website/scorecard-2025-q4.html"

# October 2025 columns (46-49 for 4 weeks: Oct 3, 10, 17, 24)
OCT_COLS = [46, 47, 48, 49]

def extract_scorecard_data():
    """Extract October 2025 Q4 data from Scorecard 2025"""
    print("📊 Extracting Scorecard 2025 Q4 data...")

    df = pd.read_excel(SCORECARD_2025, sheet_name='Scorecard 2025', header=None)

    metrics = []
    date_row = df.iloc[2]

    for row_idx in range(3, df.shape[0]):
        kpi_name = df.iloc[row_idx, 0]
        if pd.isna(kpi_name):
            continue

        accountable = df.iloc[row_idx, 1]
        goal = df.iloc[row_idx, 2]

        # Extract October values
        oct_values = []
        for col_idx in OCT_COLS:
            value = df.iloc[row_idx, col_idx]
            date_val = date_row[col_idx]
            oct_values.append({
                'date': date_val.strftime('%m/%d') if isinstance(date_val, datetime) else '',
                'value': value if pd.notna(value) else None
            })

        is_section = pd.isna(accountable)

        # Check if section has goal/values (calculated fields)
        has_goal = pd.notna(goal) and str(goal).strip() != ''
        has_values = any(v['value'] is not None for v in oct_values)

        if is_section and (has_goal or has_values):
            is_section = False
            accountable = 'Calculated'

        metrics.append({
            'kpi': str(kpi_name),
            'accountable': str(accountable) if pd.notna(accountable) else None,
            'goal': goal if pd.notna(goal) else None,
            'is_section': is_section,
            'values': oct_values,
            'metric_type': determine_metric_type(str(kpi_name))
        })

    print(f"  ✓ Extracted {len(metrics)} metrics")
    return metrics

def extract_pbr_data():
    """Extract Q4 PBR data"""
    print("💼 Extracting Pro Service PBR Q4 data...")

    try:
        df = pd.read_excel(PBR_2024, sheet_name='PRO SVC Q4', header=None)

        goal = df.iloc[2, 6] if pd.notna(df.iloc[2, 6]) else None
        actual = df.iloc[3, 6] if pd.notna(df.iloc[3, 6]) else None
        variance_val = df.iloc[4, 6]
        variance = float(variance_val) if pd.notna(variance_val) and variance_val != '.' else None
        goal_pct = df.iloc[5, 6] if pd.notna(df.iloc[5, 6]) else None

        print(f"  ✓ Q4: ${actual:,.2f} / ${goal:,.0f}" if actual and goal else "  ✓ Q4 data extracted")

        return {
            'goal': float(goal) if goal else None,
            'actual': float(actual) if actual else None,
            'variance': variance,
            'goal_percent': float(goal_pct) if goal_pct else None
        }
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None

def determine_metric_type(kpi_name):
    """Determine if lower or higher is better"""
    lower_is_better = ['response time', 'resolution time', 'tickets >7', 'failed backup',
                       'missing', 'windows 7', 'eol', 'tickets over 30', 'utilization']

    kpi_lower = kpi_name.lower()

    # Special case: Utilization is "higher is better"
    if 'utilization' in kpi_lower:
        return 'higher_is_better'

    for phrase in lower_is_better:
        if phrase in kpi_lower:
            return 'lower_is_better'

    return 'higher_is_better'

def get_cell_class(value, goal, metric_type):
    """Get CSS class based on value vs goal"""
    if value is None or goal is None:
        return 'empty'

    try:
        v = float(value)
        g = float(goal)

        if metric_type == 'lower_is_better':
            if v < g: return 'good'
            elif v == g: return 'warning'
            else: return 'bad'
        else:
            if v > g: return 'good'
            elif v == g: return 'warning'
            else: return 'bad'
    except:
        return 'neutral'

def format_value(value):
    """Format value for display"""
    if value is None:
        return '-'

    if isinstance(value, str):
        return value

    if isinstance(value, (int, float)):
        if abs(value) < 1 and value != 0:
            return f"{value:.2f}"
        elif abs(value) >= 1000:
            return f"{value:,.0f}"
        else:
            return f"{value:.0f}"

    return str(value)

def generate_html(metrics, pbr_data):
    """Generate complete HTML scorecard"""
    print("🎨 Generating HTML...")

    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scorecard 2025 Q4 - TotalCareIT</title>
    <link rel="stylesheet" href="css/styles.css">
    <style>
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f7fa;
        }

        .scorecard-container {
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            overflow: hidden;
        }

        .scorecard-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2.5rem;
            text-align: center;
        }

        .scorecard-header h1 {
            margin: 0 0 0.5rem 0;
            font-size: 2.5rem;
            font-weight: 700;
        }

        .scorecard-header p {
            margin: 0;
            font-size: 1.1rem;
            opacity: 0.95;
        }

        .pbr-section {
            margin: 2rem;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 12px;
            padding: 2rem;
            border: 2px solid #e1e8ed;
        }

        .pbr-section h2 {
            margin: 0 0 1.5rem 0;
            color: #2c3e50;
            font-size: 1.5rem;
        }

        .pbr-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.5rem;
        }

        .pbr-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            border: 1px solid #e1e8ed;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .pbr-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }

        .pbr-card h3 {
            margin: 0 0 0.75rem 0;
            font-size: 0.9rem;
            color: #6c757d;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .pbr-value {
            font-size: 2rem;
            font-weight: 700;
            color: #2c3e50;
        }

        .pbr-positive { color: #28a745; }
        .pbr-negative { color: #dc3545; }

        .table-wrapper {
            overflow-x: auto;
            padding: 2rem;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }

        th, td {
            padding: 12px 10px;
            text-align: left;
            border: 1px solid #e1e8ed;
        }

        th {
            background: #34495e;
            color: white;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 10;
        }

        th.metric-col { width: 280px; background: #2c3e50; }
        th.owner-col { width: 120px; }
        th.goal-col { width: 90px; }
        th.week-col {
            width: 100px;
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
            font-size: 15px;
            color: #495057;
            padding: 15px 10px;
        }

        td.week-value {
            text-align: center;
            font-weight: 500;
        }

        .good {
            background: #d4edda !important;
            color: #155724;
            font-weight: 600;
        }

        .warning {
            background: #fff3cd !important;
            color: #856404;
            font-weight: 600;
        }

        .bad {
            background: #f8d7da !important;
            color: #721c24;
            font-weight: 600;
        }

        .empty {
            background: #fafafa;
            color: #999;
        }

        .neutral {
            background: white;
        }
    </style>
</head>
<body>
    <div class="scorecard-container">
        <div class="scorecard-header">
            <h1>🎯 TotalCareIT Scorecard 2025</h1>
            <p>Q4 October Performance Dashboard</p>
        </div>
"""

    # Add PBR section
    if pbr_data:
        html += """
        <div class="pbr-section">
            <h2>💼 Pro Service PBR - Q4 2025</h2>
            <div class="pbr-grid">
"""
        goal = pbr_data.get('goal')
        actual = pbr_data.get('actual')
        variance = pbr_data.get('variance')
        goal_pct = pbr_data.get('goal_percent')

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
"""

    html += """
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th class="metric-col">Metric / KPI</th>
                        <th class="owner-col">Owner</th>
                        <th class="goal-col">Goal</th>
                        <th class="week-col">10/03</th>
                        <th class="week-col">10/10</th>
                        <th class="week-col">10/17</th>
                        <th class="week-col">10/24</th>
                    </tr>
                </thead>
                <tbody>
"""

    # Add metric rows
    for metric in metrics:
        if metric['is_section']:
            # Check if section has week values
            has_values = any(w['value'] is not None for w in metric['values'])

            if has_values:
                html += f"""
                    <tr>
                        <td class="section-header">{metric['kpi']}</td>
                        <td colspan="2" class="section-header"></td>
"""
                for week in metric['values']:
                    val = format_value(week['value']) if week['value'] else ''
                    html += f"""
                        <td class="section-header week-value">{val}</td>
"""
                html += """
                    </tr>
"""
            else:
                html += f"""
                    <tr>
                        <td colspan="7" class="section-header">{metric['kpi']}</td>
                    </tr>
"""
        else:
            # Regular metric row
            html += f"""
                    <tr>
                        <td class="metric-name">{metric['kpi']}</td>
                        <td>{metric['accountable'] or ''}</td>
                        <td>{format_value(metric['goal'])}</td>
"""
            for week in metric['values']:
                value = week['value']
                cell_class = get_cell_class(value, metric['goal'], metric['metric_type'])
                formatted = format_value(value)

                html += f"""
                        <td class="week-value {cell_class}">{formatted}</td>
"""
            html += """
                    </tr>
"""

    html += """
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

    return html

def main():
    """Main execution"""
    print("="*100)
    print("SCORECARD 2025 Q4 GENERATOR")
    print("="*100)

    metrics = extract_scorecard_data()
    pbr_data = extract_pbr_data()
    html = generate_html(metrics, pbr_data)

    Path(OUTPUT_HTML).write_text(html, encoding='utf-8')

    print(f"\n✅ Scorecard generated!")
    print(f"📁 {OUTPUT_HTML}")
    print(f"📊 Metrics: {len(metrics)}")
    print("="*100)

if __name__ == "__main__":
    main()
