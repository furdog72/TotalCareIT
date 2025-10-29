"""
Update all partner portal pages to use the new navigation structure
"""

import os
import re

# List of pages to update
PAGES = [
    'website/dashboard.html',
    'website/linkedin-performance.html',
    'website/scorecard.html',
    'website/contract-monitor.html',
    'website/quickbooks.html',
    'website/prospective-business.html',
    'website/finance.html',
    'website/trumethods-qbr.html'
]

def update_page_navigation(filepath):
    """Replace old sidebar with new navigation loader"""

    print(f"📄 Updating {filepath}...")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if already updated
        if 'partner-nav-placeholder' in content:
            print(f"   ✅ Already updated - skipping")
            return True

        # Pattern to match the entire sidebar section
        # Match from <aside class="sidebar"> to </aside>
        sidebar_pattern = r'<aside class="sidebar">.*?</aside>'

        # Replacement HTML
        replacement = '''<!-- Partner Portal Navigation (loaded from includes/partner-nav.html) -->
        <div id="partner-nav-placeholder"></div>
        <script src="js/load-nav.js"></script>'''

        # Replace sidebar with new navigation
        new_content = re.sub(
            sidebar_pattern,
            replacement,
            content,
            flags=re.DOTALL
        )

        if new_content == content:
            print(f"   ⚠️ No sidebar found to replace")
            return False

        # Write updated content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"   ✅ Updated successfully")
        return True

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    print("🔧 Updating Partner Portal Navigation\n")

    updated_count = 0
    skipped_count = 0
    error_count = 0

    for page in PAGES:
        if not os.path.exists(page):
            print(f"❌ File not found: {page}")
            error_count += 1
            continue

        result = update_page_navigation(page)

        if result is True:
            updated_count += 1
        elif result is False:
            error_count += 1
        else:
            skipped_count += 1

    print(f"\n📊 Summary:")
    print(f"   ✅ Updated: {updated_count}")
    print(f"   ⏭️  Skipped: {skipped_count}")
    print(f"   ❌ Errors: {error_count}")


if __name__ == '__main__':
    main()
