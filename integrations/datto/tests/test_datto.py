#!/usr/bin/env python3
"""
Test Datto RMM and Backup Portal API integration
"""
import sys
import os
from dotenv import load_dotenv

sys.path.insert(0, '/Users/charles/Projects/qbo-ai')

from api.datto_service import get_datto_reporting_service

# Load environment
load_dotenv()

print("Testing Datto API Integration")
print("=" * 80)
print()

# Get Datto service
try:
    service = get_datto_reporting_service()

    print("Datto API Configuration:")
    print(f"  Public Key: {service.client.config.api_public_key}")
    print(f"  RMM URL: {service.client.config.rmm_url}")
    print(f"  Portal URL: {service.client.config.portal_url}")
    print(f"  Configured: {service.client.is_configured()}")
    print()

    # Test 1: Get Centralized Services Metrics
    print("1. Testing Centralized Services Metrics")
    print("-" * 40)
    metrics = service.get_centralized_services_metrics()

    print(f"\nFailed Backups (>48 hours):")
    print(f"  Count: {metrics.get('failed_backups_48h', {}).get('count', 0)}")
    print(f"  Percentage: {metrics.get('failed_backups_48h', {}).get('percentage', 0)}%")
    print(f"  Total Devices: {metrics.get('failed_backups_48h', {}).get('total_devices', 0)}")

    print(f"\nFailed Backups on Continuity (>7 days):")
    print(f"  Count: {metrics.get('failed_backups_7days', {}).get('count', 0)}")
    print(f"  Percentage: {metrics.get('failed_backups_7days', {}).get('percentage', 0)}%")

    print(f"\nFailed SaaS Backups:")
    print(f"  Count: {metrics.get('failed_saas_backups', {}).get('count', 0)}")
    print(f"  Percentage: {metrics.get('failed_saas_backups', {}).get('percentage', 0)}%")

    print(f"\nMissing Patches (>5):")
    print(f"  Count: {metrics.get('missing_patches', {}).get('count', 0)}")
    print(f"  Percentage: {metrics.get('missing_patches', {}).get('percentage', 0)}%")
    print(f"  Total Devices: {metrics.get('missing_patches', {}).get('total_devices', 0)}")

    print(f"\nWindows Devices:")
    print(f"  Windows 7: {metrics.get('windows_devices', {}).get('windows_7', 0)}")
    print(f"  Windows 10: {metrics.get('windows_devices', {}).get('windows_10', 0)}")
    print(f"  Windows 11: {metrics.get('windows_devices', {}).get('windows_11', 0)}")
    print(f"  Windows 11 EOL: {metrics.get('windows_devices', {}).get('windows_11_eol', 0)}")

    print(f"\nMissing Hosted AV:")
    print(f"  Count: {metrics.get('missing_av', {}).get('count', 0)}")
    print(f"  Percentage: {metrics.get('missing_av', {}).get('percentage', 0)}%")
    print(f"  Total Devices: {metrics.get('missing_av', {}).get('total_devices', 0)}")

    if 'note' in metrics:
        print(f"\nNote: {metrics['note']}")

    if 'error' in metrics:
        print(f"\n❌ Error: {metrics['error']}")

    print()
    print("=" * 80)

    if service.client.is_configured():
        print("✓ Datto API integration configured and ready!")
        print("  Note: Actual API calls will be made when credentials are valid.")
    else:
        print("⚠ Datto API integration using placeholder data")
        print("  Configure DATTO_API_PUBLIC_KEY and DATTO_API_PRIVATE_KEY to use real data")

except Exception as e:
    print(f"❌ Error testing Datto integration: {e}")
    import traceback
    traceback.print_exc()
