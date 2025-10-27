#!/usr/bin/env python3
"""
Collect Scorecard Data for Week Ending October 24, 2025

Uses existing API services:
- api/hubspot_service.py
- api/autotask_service.py
- api/datto_service.py
"""

#!/usr/bin/env python3
import sys
from pathlib import Path

# IMPORTANT: Load environment variables BEFORE importing api modules
# The api modules have module-level os.getenv() calls that run at import time
from dotenv import load_dotenv
load_dotenv()

from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from api.hubspot_service import HubSpotConfig, HubSpotClient, HubSpotReportingService
from api.autotask_service import AutotaskConfig, AutotaskClient, AutotaskReportingService
from api.datto_service import DattoConfig, DattoClient, DattoReportingService

# Week 4: Oct 18-24, 2025
WEEK_START = datetime(2025, 10, 18)
WEEK_END = datetime(2025, 10, 24, 23, 59, 59)

def collect_hubspot_metrics():
    """Collect HubSpot sales metrics for week 10/24"""
    print("\n📊 Collecting HubSpot metrics...")

    try:
        config = HubSpotConfig.from_env()
        client = HubSpotClient(config)
        service = HubSpotReportingService(client)

        # Get metrics for Jason (Inside Sales)
        jason_metrics = service.get_sales_activity_metrics(
            start_date=WEEK_START,
            end_date=WEEK_END,
            owner_email='jason@totalcareit.com'
        )

        # Get metrics for Charles (W250 Activity)
        charles_metrics = service.get_sales_activity_metrics(
            start_date=WEEK_START,
            end_date=WEEK_END,
            owner_email='charles@totalcareit.com'
        )

        # Get metrics for Josh (Hybrid Sales)
        josh_metrics = service.get_sales_activity_metrics(
            start_date=WEEK_START,
            end_date=WEEK_END,
            owner_email='josh@totalcareit.com'
        )

        # Get overall metrics (for Jason/Charles combined)
        overall_metrics = service.get_sales_activity_metrics(
            start_date=WEEK_START,
            end_date=WEEK_END
        )

        return {
            # Inside Sales Activity - Jason
            'dials_jason': jason_metrics.get('dials', 0),
            'conversations_jason': jason_metrics.get('conversations_with_dm', 0),
            'ftas_set_jason': jason_metrics.get('ftas_set', 0),

            # Outside Sales Activity - Jason/Charles combined
            'fta_attended': overall_metrics.get('ftas_set', 0),  # Meetings set = attended
            'coi_attended_outside': 0,  # TODO: Need COI metric
            'mrr_closed': overall_metrics.get('mrr_closed', 0),

            # Hybrid Sales Activity - Josh
            'coi_created_josh': 0,  # TODO: Need COI created metric
            'coi_attended_josh': 0,  # TODO: Need COI attended metric

            # W250 Activity - Charles
            'w250_dials': charles_metrics.get('dials', 0),
            'w250_conversations': charles_metrics.get('conversations_with_dm', 0),
            'w250_ftas_set': charles_metrics.get('ftas_set', 0),
        }
    except Exception as e:
        print(f"❌ Error collecting HubSpot metrics: {e}")
        import traceback
        traceback.print_exc()
        return {}

def collect_autotask_metrics():
    """Collect Autotask operations metrics for week 10/24"""
    print("\n📊 Collecting Autotask metrics...")

    try:
        config = AutotaskConfig.from_env()
        client = AutotaskClient(config)
        service = AutotaskReportingService(client)

        # Get ticket metrics for the week
        metrics = service.get_ticket_metrics(
            start_date=WEEK_START,
            end_date=WEEK_END
        )

        return {
            # Reactive Operations
            'reactive_tickets_opened': metrics.get('reactive_tickets_opened', 0),
            'reactive_tickets_closed': metrics.get('reactive_tickets_closed', 0),
            'same_day_close': metrics.get('same_day_close_pct', 0),
            'utilization': metrics.get('utilization_pct', 0),
            'tickets_over_7_days': metrics.get('tickets_over_7_days', 0),
            'tickets_per_endpoint': metrics.get('tickets_per_endpoint', 0),
            'rhem': metrics.get('service_noise', 0),
            'avg_response_time': metrics.get('avg_response_time_hours', 0),
            'avg_resolution_time': metrics.get('avg_resolution_time_hours', 0),

            # Professional Services
            'prof_services_opened': metrics.get('prof_services_opened', 0),
            'prof_services_closed': metrics.get('prof_services_closed', 0),
            'tickets_over_30_days': metrics.get('tickets_over_30_days', 0),

            # TAM
            'tam_questions': metrics.get('tam_questions', 0),
            'tam_tickets_opened': metrics.get('tam_tickets_opened', 0),
            'tam_tickets_closed': metrics.get('tam_tickets_closed', 0),
        }
    except Exception as e:
        print(f"❌ Error collecting Autotask metrics: {e}")
        import traceback
        traceback.print_exc()
        return {}

def collect_datto_metrics():
    """Collect Datto backup/device metrics for week 10/24"""
    print("\n📊 Collecting Datto metrics...")

    try:
        config = DattoConfig.from_env()
        client = DattoClient(config)
        service = DattoReportingService(client)

        # Get centralized services metrics (current snapshot)
        metrics = service.get_centralized_services_metrics()

        return {
            # Centralized Services - Backups
            'failed_backups_48h': metrics.get('failed_backups_48h_pct', 0),
            'failed_backups_continuity': metrics.get('failed_backups_continuity_7d_pct', 0),
            'failed_backups_saas': metrics.get('failed_backups_saas_48h_pct', 0),

            # Patches
            'missing_patches': metrics.get('missing_patches_pct', 0),

            # Windows Devices
            'windows_7_devices': metrics.get('windows_7_count', 0),
            'windows_10_devices': metrics.get('windows_10_eol_pct', 0),
            'windows_11_eol_devices': metrics.get('windows_11_eol_pct', 0),

            # Antivirus
            'missing_hosted_av': metrics.get('missing_av_pct', 0),
        }
    except Exception as e:
        print(f"❌ Error collecting Datto metrics: {e}")
        import traceback
        traceback.print_exc()
        return {}

def collect_microsoft_metrics():
    """Collect Microsoft 365 security score"""
    print("\n📊 Collecting Microsoft 365 metrics...")

    try:
        # TODO: Implement Microsoft Graph API call for security score
        # For now, return placeholder
        return {
            'security_score': None  # To be implemented
        }
    except Exception as e:
        print(f"❌ Error collecting Microsoft metrics: {e}")
        return {}

def main():
    """Main collection workflow"""
    print("=" * 80)
    print(f"🔄 Collecting Scorecard Data for Week Ending October 24, 2025")
    print(f"   Date Range: {WEEK_START.strftime('%Y-%m-%d')} to {WEEK_END.strftime('%Y-%m-%d')}")
    print("=" * 80)

    # Collect from all sources
    hubspot_data = collect_hubspot_metrics()
    autotask_data = collect_autotask_metrics()
    datto_data = collect_datto_metrics()
    microsoft_data = collect_microsoft_metrics()

    # Combine all metrics
    all_metrics = {
        **hubspot_data,
        **autotask_data,
        **datto_data,
        **microsoft_data
    }

    # Print collected metrics
    print("\n" + "=" * 80)
    print("✅ DATA COLLECTION COMPLETE")
    print("=" * 80)

    print("\n📈 HubSpot Metrics:")
    for key, value in hubspot_data.items():
        print(f"   {key}: {value}")

    print("\n📈 Autotask Metrics:")
    for key, value in autotask_data.items():
        print(f"   {key}: {value}")

    print("\n📈 Datto Metrics:")
    for key, value in datto_data.items():
        print(f"   {key}: {value}")

    print("\n📈 Microsoft Metrics:")
    for key, value in microsoft_data.items():
        print(f"   {key}: {value}")

    print("\n" + "=" * 80)
    print("📝 Next Steps:")
    print("   1. Review the collected metrics above")
    print("   2. Update scorecard Excel file with these values")
    print("   3. Rebuild scorecard HTML using build_scorecard_2025.py")
    print("   4. Deploy to S3")
    print("=" * 80)

    return all_metrics

if __name__ == '__main__':
    main()
