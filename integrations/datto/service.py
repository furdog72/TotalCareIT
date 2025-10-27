"""
Datto Service API
Backend integration for Datto RMM and Backup Portal

Datto RMM API: OAuth 2.0 authentication, v2 API
Datto Backup Portal API: Basic auth with API key/secret, REST API
"""
import os
import logging
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field
import base64

logger = logging.getLogger(__name__)


class DattoConfig(BaseModel):
    """Datto API Configuration"""
    api_public_key: Optional[str] = Field(None, description="Datto API Public Key")
    api_private_key: Optional[str] = Field(None, description="Datto API Private Key")
    portal_url: Optional[str] = Field(None, description="Datto Portal URL")
    rmm_url: Optional[str] = Field(None, description="Datto RMM URL")

    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        return cls(
            api_public_key=os.getenv('DATTO_API_PUBLIC_KEY', ''),
            api_private_key=os.getenv('DATTO_API_PRIVATE_KEY', ''),
            portal_url=os.getenv('DATTO_PORTAL_URL', 'https://portal.dattobackup.com'),
            rmm_url=os.getenv('DATTO_RMM_URL', 'https://vidal-rmm.centrastage.net')
        )


class DattoClient:
    """Datto API Client for RMM and Backup Portal"""

    def __init__(self, config: DattoConfig):
        self.config = config
        self._access_token = None
        self._token_expires_at = None
        self._session = requests.Session()

        if not config.api_public_key or not config.api_private_key:
            logger.warning("Datto API credentials not configured. Using placeholder data.")
        else:
            logger.info(f"Datto API configured with Public Key: {config.api_public_key[:6]}...")

    def is_configured(self) -> bool:
        """Check if Datto API is properly configured"""
        return bool(self.config.api_public_key and self.config.api_private_key)

    def _get_basic_auth_header(self) -> str:
        """Generate Basic Auth header for Backup Portal API"""
        credentials = f"{self.config.api_public_key}:{self.config.api_private_key}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    def _make_backup_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make authenticated request to Datto Backup Portal API

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., '/bcdr/device')
            **kwargs: Additional arguments to pass to requests

        Returns:
            Response JSON data
        """
        if not self.is_configured():
            raise ValueError("Datto API credentials not configured")

        url = f"https://api.datto.com{endpoint}"
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = self._get_basic_auth_header()
        headers['Content-Type'] = 'application/json'

        try:
            response = self._session.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"Datto Backup API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Datto Backup API request failed: {e}")
            raise

    def _get_rmm_access_token(self) -> str:
        """Get OAuth access token for Datto RMM API"""
        if self._access_token and self._token_expires_at:
            if datetime.now() < self._token_expires_at:
                return self._access_token

        # OAuth token endpoint for Datto RMM
        token_url = f"{self.config.rmm_url}/auth/oauth/token"

        try:
            response = requests.post(
                token_url,
                data={
                    'grant_type': 'password',
                    'username': self.config.api_public_key,
                    'password': self.config.api_private_key
                }
            )
            response.raise_for_status()
            token_data = response.json()

            self._access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 3600)
            self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)

            return self._access_token
        except Exception as e:
            logger.error(f"Failed to get Datto RMM access token: {e}")
            raise

    def _make_rmm_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make authenticated request to Datto RMM API

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., '/api/v2/account/devices')
            **kwargs: Additional arguments to pass to requests

        Returns:
            Response JSON data
        """
        if not self.is_configured():
            raise ValueError("Datto RMM credentials not configured")

        token = self._get_rmm_access_token()
        url = f"{self.config.rmm_url}{endpoint}"
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f"Bearer {token}"
        headers['Content-Type'] = 'application/json'

        try:
            response = self._session.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"Datto RMM API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Datto RMM API request failed: {e}")
            raise

    # ===== BACKUP PORTAL API =====

    def get_failed_backups(
        self,
        hours_threshold: int = 48
    ) -> Dict[str, Any]:
        """Get failed backups older than threshold

        Args:
            hours_threshold: Number of hours to check (48, 168 for 7 days, etc.)

        Returns:
            Dict with backup status information
        """
        if not self.is_configured():
            logger.warning("Datto API not configured - returning placeholder data")
            return {
                'total_devices': 50,
                'failed_backups': 5,
                'failed_percentage': 10.0,
                'threshold_hours': hours_threshold,
                'note': 'Placeholder data - Datto API credentials required'
            }

        try:
            # Get all BCDR devices
            devices_response = self._make_backup_request('GET', '/bcdr/device')
            devices = devices_response.get('devices', [])

            total_devices = len(devices)
            failed_count = 0
            threshold_time = datetime.now() - timedelta(hours=hours_threshold)

            for device in devices:
                device_id = device.get('serialNumber')
                if not device_id:
                    continue

                # Get assets for this device
                try:
                    assets_response = self._make_backup_request('GET', f'/bcdr/device/{device_id}/asset')
                    assets = assets_response.get('assets', [])

                    for asset in assets:
                        asset_id = asset.get('name')
                        if not asset_id:
                            continue

                        # Get latest snapshot
                        snapshots_response = self._make_backup_request(
                            'GET',
                            f'/bcdr/device/{device_id}/asset/{asset_id}/snapshots',
                            params={'limit': 1}
                        )
                        snapshots = snapshots_response.get('snapshots', [])

                        if snapshots:
                            latest_snapshot = snapshots[0]
                            snapshot_time = datetime.fromisoformat(
                                latest_snapshot.get('snapshotTimestamp', '').replace('Z', '+00:00')
                            )

                            if snapshot_time < threshold_time:
                                failed_count += 1
                                break  # Count device once even if multiple assets failed

                except Exception as e:
                    logger.warning(f"Failed to check device {device_id}: {e}")
                    continue

            failed_percentage = (failed_count / total_devices * 100) if total_devices > 0 else 0

            return {
                'total_devices': total_devices,
                'failed_backups': failed_count,
                'failed_percentage': round(failed_percentage, 2),
                'threshold_hours': hours_threshold
            }

        except Exception as e:
            logger.error(f"Failed to get backup status: {e}")
            return {
                'total_devices': 0,
                'failed_backups': 0,
                'failed_percentage': 0.0,
                'threshold_hours': hours_threshold,
                'error': str(e)
            }

    def get_saas_backup_status(self) -> Dict[str, Any]:
        """Get SaaS backup status (M365, Google Workspace, etc.)"""
        if not self.is_configured():
            return {
                'total_accounts': 20,
                'failed_backups': 0,
                'failed_percentage': 0.0,
                'note': 'Placeholder data - Datto API credentials required'
            }

        try:
            # Get SaaS Protection backup status
            # Note: This may require different authentication or API endpoint
            # Datto SaaS Protection may use a separate API
            saas_response = self._make_backup_request('GET', '/saas/backups')

            accounts = saas_response.get('accounts', [])
            total_accounts = len(accounts)
            failed_count = 0

            threshold_time = datetime.now() - timedelta(hours=48)

            for account in accounts:
                last_backup = account.get('lastBackupTime')
                if last_backup:
                    last_backup_time = datetime.fromisoformat(last_backup.replace('Z', '+00:00'))
                    if last_backup_time < threshold_time:
                        failed_count += 1

            failed_percentage = (failed_count / total_accounts * 100) if total_accounts > 0 else 0

            return {
                'total_accounts': total_accounts,
                'failed_backups': failed_count,
                'failed_percentage': round(failed_percentage, 2)
            }

        except Exception as e:
            logger.error(f"Failed to get SaaS backup status: {e}")
            # Return placeholder data on error
            return {
                'total_accounts': 20,
                'failed_backups': 0,
                'failed_percentage': 0.0,
                'error': str(e),
                'note': 'Using placeholder data - SaaS API may require separate setup'
            }

    # ===== DATTO RMM API =====

    def get_patch_status(self) -> Dict[str, Any]:
        """Get patch management status"""
        if not self.is_configured():
            return {
                'total_devices': 160,
                'missing_patches': 9,
                'missing_percentage': 5.49,
                'note': 'Placeholder data - Datto RMM API credentials required'
            }

        try:
            # Get all devices
            devices_response = self._make_rmm_request('GET', '/api/v2/account/devices')
            devices = devices_response.get('devices', [])

            total_devices = len(devices)
            devices_missing_patches = 0

            for device in devices:
                device_uid = device.get('uid')
                if not device_uid:
                    continue

                try:
                    # Check patch status for device
                    patches_response = self._make_rmm_request(
                        'GET',
                        f'/api/v2/device/{device_uid}/patches/missing'
                    )
                    missing_patches = patches_response.get('patches', [])

                    # Count devices with more than 5 missing patches
                    if len(missing_patches) > 5:
                        devices_missing_patches += 1

                except Exception as e:
                    logger.warning(f"Failed to check patches for device {device_uid}: {e}")
                    continue

            missing_percentage = (devices_missing_patches / total_devices * 100) if total_devices > 0 else 0

            return {
                'total_devices': total_devices,
                'missing_patches': devices_missing_patches,
                'missing_percentage': round(missing_percentage, 2)
            }

        except Exception as e:
            logger.error(f"Failed to get patch status: {e}")
            return {
                'total_devices': 0,
                'missing_patches': 0,
                'missing_percentage': 0.0,
                'error': str(e)
            }

    def get_windows_devices(self) -> Dict[str, Any]:
        """Get Windows device inventory"""
        if not self.is_configured():
            return {
                'windows_7': 2,
                'windows_10': 126,
                'windows_11': 32,
                'windows_11_eol': 4,  # EOL versions
                'total_windows': 160,
                'note': 'Placeholder data - Datto RMM API credentials required'
            }

        try:
            # Get all devices
            devices_response = self._make_rmm_request('GET', '/api/v2/account/devices')
            devices = devices_response.get('devices', [])

            win7_count = 0
            win10_count = 0
            win11_count = 0
            win11_eol_count = 0

            for device in devices:
                os_info = device.get('operatingSystem', '').lower()

                if 'windows 7' in os_info:
                    win7_count += 1
                elif 'windows 10' in os_info:
                    win10_count += 1
                elif 'windows 11' in os_info:
                    win11_count += 1
                    # Check if it's an EOL version (e.g., early builds)
                    # This would need more specific version checking logic
                    build = device.get('osBuild', '')
                    if build and int(build.split('.')[0]) < 22000:  # Example EOL threshold
                        win11_eol_count += 1

            return {
                'windows_7': win7_count,
                'windows_10': win10_count,
                'windows_11': win11_count,
                'windows_11_eol': win11_eol_count,
                'total_windows': win7_count + win10_count + win11_count
            }

        except Exception as e:
            logger.error(f"Failed to get Windows devices: {e}")
            return {
                'windows_7': 0,
                'windows_10': 0,
                'windows_11': 0,
                'windows_11_eol': 0,
                'total_windows': 0,
                'error': str(e)
            }

    def get_av_status(self) -> Dict[str, Any]:
        """Get antivirus/endpoint protection status"""
        if not self.is_configured():
            return {
                'total_devices': 160,
                'missing_av': 2,
                'missing_percentage': 1.33,
                'note': 'Placeholder data - Datto RMM API credentials required'
            }

        try:
            # Get all devices
            devices_response = self._make_rmm_request('GET', '/api/v2/account/devices')
            devices = devices_response.get('devices', [])

            total_devices = len(devices)
            missing_av_count = 0

            for device in devices:
                device_uid = device.get('uid')
                if not device_uid:
                    continue

                try:
                    # Check AV status for device
                    av_response = self._make_rmm_request(
                        'GET',
                        f'/api/v2/device/{device_uid}/antivirus'
                    )

                    av_installed = av_response.get('installed', False)
                    av_enabled = av_response.get('enabled', False)
                    av_uptodate = av_response.get('upToDate', False)

                    if not (av_installed and av_enabled and av_uptodate):
                        missing_av_count += 1

                except Exception as e:
                    logger.warning(f"Failed to check AV for device {device_uid}: {e}")
                    # Assume missing if we can't check
                    missing_av_count += 1
                    continue

            missing_percentage = (missing_av_count / total_devices * 100) if total_devices > 0 else 0

            return {
                'total_devices': total_devices,
                'missing_av': missing_av_count,
                'missing_percentage': round(missing_percentage, 2)
            }

        except Exception as e:
            logger.error(f"Failed to get AV status: {e}")
            return {
                'total_devices': 0,
                'missing_av': 0,
                'missing_percentage': 0.0,
                'error': str(e)
            }


class DattoReportingService:
    """Service for generating Centralized Services metrics from Datto"""

    def __init__(self, client: DattoClient):
        self.client = client

    def get_centralized_services_metrics(self) -> Dict[str, Any]:
        """Get all centralized services metrics for scorecard

        Returns metrics for:
        - Failed Backups > 48 Hours
        - Failed Backups on Continuity > 7 Days
        - Failed Backups on SAAS > 48 Hours
        - Missing > 5 Patches
        - Total Windows 7/10/11 Devices
        - Missing Hosted AV
        """
        try:
            # Get backup metrics
            failed_48h = self.client.get_failed_backups(hours_threshold=48)
            failed_7days = self.client.get_failed_backups(hours_threshold=168)  # 7 days
            saas_backups = self.client.get_saas_backup_status()

            # Get patch status
            patch_status = self.client.get_patch_status()

            # Get Windows device inventory
            windows_devices = self.client.get_windows_devices()

            # Get AV status
            av_status = self.client.get_av_status()

            return {
                'failed_backups_48h': {
                    'count': failed_48h.get('failed_backups', 0),
                    'percentage': failed_48h.get('failed_percentage', 0),
                    'total_devices': failed_48h.get('total_devices', 0)
                },
                'failed_backups_7days': {
                    'count': failed_7days.get('failed_backups', 0),
                    'percentage': failed_7days.get('failed_percentage', 0),
                    'total_devices': failed_7days.get('total_devices', 0)
                },
                'failed_saas_backups': {
                    'count': saas_backups.get('failed_backups', 0),
                    'percentage': saas_backups.get('failed_percentage', 0),
                    'total_accounts': saas_backups.get('total_accounts', 0)
                },
                'missing_patches': {
                    'count': patch_status.get('missing_patches', 0),
                    'percentage': patch_status.get('missing_percentage', 0),
                    'total_devices': patch_status.get('total_devices', 0)
                },
                'windows_devices': {
                    'windows_7': windows_devices.get('windows_7', 0),
                    'windows_10': windows_devices.get('windows_10', 0),
                    'windows_11': windows_devices.get('windows_11', 0),
                    'windows_11_eol': windows_devices.get('windows_11_eol', 0)
                },
                'missing_av': {
                    'count': av_status.get('missing_av', 0),
                    'percentage': av_status.get('missing_percentage', 0),
                    'total_devices': av_status.get('total_devices', 0)
                },
                'note': 'Using placeholder data - Datto API credentials required for live data'
            }

        except Exception as e:
            logger.error(f"Failed to get centralized services metrics: {e}")
            return {
                'error': str(e),
                'note': 'Failed to retrieve metrics - check Datto API configuration'
            }


def get_datto_client() -> DattoClient:
    """Get Datto client instance"""
    config = DattoConfig.from_env()
    return DattoClient(config)


def get_datto_reporting_service() -> DattoReportingService:
    """Get Datto reporting service instance"""
    client = get_datto_client()
    return DattoReportingService(client)
