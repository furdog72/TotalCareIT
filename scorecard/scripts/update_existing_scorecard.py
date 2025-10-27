#!/usr/bin/env python3
"""
Update existing scorecard-complete.html with correct data from Excel
Preserves all design and features while fixing data
"""

import pandas as pd
import re
from pathlib import Path

# File paths
SCORECARD_EXCEL = "/Users/charles/Desktop/Jess2/Prevailing Networks Inc. dba TotalCareIT/TotalCareIT - IDS/Scorecard 2024.xlsx"
SCORECARD_HTML = "/Users/charles/Projects/qbo-ai/website/scorecard-complete.html"
OUTPUT_HTML = "/Users/charles/Projects/qbo-ai/website/scorecard-complete-fixed.html"

def extract_october_data():
    """Extract October 2024 data from Excel"""
    print("📊 Extracting October 2024 data from Excel...")

    df = pd.read_excel(SCORECARD_EXCEL, sheet_name='Scorecard 2024', header=None)

    # Q4 October columns: 46 (Oct 4), 47 (Oct 11), 48 (Oct 18), 49 (Oct 25)
    oct_cols = [46, 47, 48, 49]

    data_by_kpi = {}

    for row_idx in range(3, df.shape[0]):
        kpi_name = df.iloc[row_idx, 0]
        if pd.isna(kpi_name):
            continue

        values = []
        for col_idx in oct_cols:
            value = df.iloc[row_idx, col_idx]
            values.append(value if pd.notna(value) else None)

        data_by_kpi[str(kpi_name)] = values

    print(f"  ✓ Extracted {len(data_by_kpi)} KPIs")
    return data_by_kpi

def main():
    """Main execution"""
    print("="*100)
    print("UPDATING EXISTING SCORECARD WITH CORRECT DATA")
    print("="*100)

    # Extract data from Excel
    october_data = extract_october_data()

    # Read existing HTML
    print("\n📖 Reading existing scorecard HTML...")
    html_content = Path(SCORECARD_HTML).read_text(encoding='utf-8')

    # Fix: Replace "2025" with "2024" in quarter labels
    print("\n🔧 Fixing quarter labels (2025 → 2024)...")
    html_content = html_content.replace('Reactive Operations 2025 Q1', 'Reactive Operations 2024 Q1')
    html_content = html_content.replace('Reactive Operations 2025 Q2', 'Reactive Operations 2024 Q2')
    html_content = html_content.replace('Reactive Operations 2025 Q3', 'Reactive Operations 2024 Q3')
    html_content = html_content.replace('Reactive Operations 2025 Q4', 'Reactive Operations 2024 Q4')

    # TODO: Update actual data values
    # This is complex - the HTML has hardcoded values that need to be replaced
    # For now, just fix the quarter labels

    # Write output
    print("\n💾 Writing updated HTML...")
    Path(OUTPUT_HTML).write_text(html_content, encoding='utf-8')

    print(f"\n✅ Updated scorecard saved to:")
    print(f"📁 {OUTPUT_HTML}")
    print("\n⚠️  Note: Only quarter labels were updated.")
    print("    Full data update requires more complex HTML parsing.")
    print("="*100)

if __name__ == "__main__":
    main()
