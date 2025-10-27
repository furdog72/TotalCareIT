"""
AWS Billing Integration
Fetches AWS cost and usage data using AWS Cost Explorer API
"""

import os
import json
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import boto3
from botocore.exceptions import ClientError


class AWSBillingAPI:
    """AWS Cost Explorer API client for billing data"""

    def __init__(self):
        """Initialize AWS Cost Explorer client"""
        self.client = boto3.client('ce', region_name='us-east-1')
        self.data_dir = Path("data/aws_billing")
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def get_current_month_cost(self) -> Dict:
        """
        Get current month's cost so far (month-to-date)

        Returns:
            Dictionary with current month billing data
        """
        today = date.today()
        start_of_month = today.replace(day=1).isoformat()
        end_date = (today + timedelta(days=1)).isoformat()

        try:
            response = self.client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_of_month,
                    'End': end_date
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost', 'UsageQuantity'],
                GroupBy=[
                    {
                        'Type': 'DIMENSION',
                        'Key': 'SERVICE'
                    }
                ]
            )

            # Calculate total cost
            total_cost = 0.0
            services = {}

            if 'ResultsByTime' in response and len(response['ResultsByTime']) > 0:
                result = response['ResultsByTime'][0]

                # Get total from summary
                if 'Total' in result and 'UnblendedCost' in result['Total']:
                    total_cost = float(result['Total']['UnblendedCost']['Amount'])

                # Get service breakdown
                if 'Groups' in result:
                    for group in result['Groups']:
                        service_name = group['Keys'][0]
                        service_cost = float(group['Metrics']['UnblendedCost']['Amount'])
                        if service_cost > 0.01:  # Only include services with meaningful cost
                            services[service_name] = round(service_cost, 2)

            return {
                'month': today.strftime('%b %Y'),
                'month_key': today.strftime('%Y-%m'),
                'start_date': start_of_month,
                'end_date': today.isoformat(),
                'total_cost': round(total_cost, 2),
                'services': services,
                'is_current': True,
                'days_in_month': today.day,
                'fetched_at': datetime.now().isoformat()
            }

        except ClientError as e:
            print(f"Error fetching current month cost: {e}")
            return {
                'month': today.strftime('%b %Y'),
                'month_key': today.strftime('%Y-%m'),
                'total_cost': 0.0,
                'error': str(e),
                'fetched_at': datetime.now().isoformat()
            }

    def get_monthly_costs(self, months: int = 3) -> List[Dict]:
        """
        Get monthly costs for the last N completed months

        Args:
            months: Number of past months to retrieve

        Returns:
            List of dictionaries with monthly billing data
        """
        results = []
        today = date.today()

        for i in range(1, months + 1):
            # Calculate the month
            first_of_current_month = today.replace(day=1)
            first_of_target_month = first_of_current_month - timedelta(days=i * 30)
            # Adjust to actual first of month
            first_of_target_month = first_of_target_month.replace(day=1)

            # Calculate last day of the month
            if first_of_target_month.month == 12:
                first_of_next_month = first_of_target_month.replace(year=first_of_target_month.year + 1, month=1)
            else:
                first_of_next_month = first_of_target_month.replace(month=first_of_target_month.month + 1)

            last_of_month = first_of_next_month - timedelta(days=1)

            try:
                response = self.client.get_cost_and_usage(
                    TimePeriod={
                        'Start': first_of_target_month.isoformat(),
                        'End': first_of_next_month.isoformat()
                    },
                    Granularity='MONTHLY',
                    Metrics=['UnblendedCost'],
                    GroupBy=[
                        {
                            'Type': 'DIMENSION',
                            'Key': 'SERVICE'
                        }
                    ]
                )

                # Calculate total cost
                total_cost = 0.0
                services = {}

                if 'ResultsByTime' in response and len(response['ResultsByTime']) > 0:
                    result = response['ResultsByTime'][0]

                    # Get total from summary
                    if 'Total' in result and 'UnblendedCost' in result['Total']:
                        total_cost = float(result['Total']['UnblendedCost']['Amount'])

                    # Get service breakdown
                    if 'Groups' in result:
                        for group in result['Groups']:
                            service_name = group['Keys'][0]
                            service_cost = float(group['Metrics']['UnblendedCost']['Amount'])
                            if service_cost > 0.01:
                                services[service_name] = round(service_cost, 2)

                results.append({
                    'month': first_of_target_month.strftime('%b %Y'),
                    'month_key': first_of_target_month.strftime('%Y-%m'),
                    'start_date': first_of_target_month.isoformat(),
                    'end_date': last_of_month.isoformat(),
                    'total_cost': round(total_cost, 2),
                    'services': services,
                    'is_current': False,
                    'fetched_at': datetime.now().isoformat()
                })

            except ClientError as e:
                print(f"Error fetching cost for {first_of_target_month.strftime('%b %Y')}: {e}")
                results.append({
                    'month': first_of_target_month.strftime('%b %Y'),
                    'month_key': first_of_target_month.strftime('%Y-%m'),
                    'total_cost': 0.0,
                    'error': str(e),
                    'fetched_at': datetime.now().isoformat()
                })

        return results

    def get_billing_dashboard_data(self) -> Dict:
        """
        Get all billing data for dashboard display

        Returns:
            Dictionary with current and historical billing data
        """
        current_month = self.get_current_month_cost()
        past_months = self.get_monthly_costs(months=3)

        return {
            'current_month': current_month,
            'past_months': past_months,
            'last_updated': datetime.now().isoformat()
        }

    def save_billing_snapshot(self):
        """Save current billing data to file for historical tracking"""
        data = self.get_billing_dashboard_data()

        snapshot_file = self.data_dir / f"billing_snapshot_{date.today().isoformat()}.json"

        with open(snapshot_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Billing snapshot saved to {snapshot_file}")
        return snapshot_file

    def get_top_services(self, limit: int = 5) -> List[Dict]:
        """
        Get top N services by cost for current month

        Args:
            limit: Number of top services to return

        Returns:
            List of top services with costs
        """
        current_data = self.get_current_month_cost()

        if 'services' not in current_data:
            return []

        # Sort services by cost
        sorted_services = sorted(
            current_data['services'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

        return [
            {'service': service, 'cost': cost}
            for service, cost in sorted_services
        ]


def fetch_weekly_billing_update():
    """Run weekly billing update (for cron job)"""
    api = AWSBillingAPI()
    data = api.get_billing_dashboard_data()

    # Save to current month file
    current_file = api.data_dir / "current_month.json"
    with open(current_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Weekly billing update complete: ${data['current_month']['total_cost']:.2f}")
    return data


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "current":
            api = AWSBillingAPI()
            data = api.get_current_month_cost()
            print(json.dumps(data, indent=2))
        elif sys.argv[1] == "history":
            api = AWSBillingAPI()
            data = api.get_monthly_costs(months=3)
            print(json.dumps(data, indent=2))
        elif sys.argv[1] == "dashboard":
            api = AWSBillingAPI()
            data = api.get_billing_dashboard_data()
            print(json.dumps(data, indent=2))
        elif sys.argv[1] == "weekly":
            fetch_weekly_billing_update()
        elif sys.argv[1] == "snapshot":
            api = AWSBillingAPI()
            api.save_billing_snapshot()
        else:
            print("Usage: python aws_billing.py [current|history|dashboard|weekly|snapshot]")
    else:
        print("Usage: python aws_billing.py [current|history|dashboard|weekly|snapshot]")
