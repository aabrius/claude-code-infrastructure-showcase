"""
Unified client for Google Ad Manager API.
Provides a consistent interface for both SOAP and REST APIs.

This module serves as a backward compatibility layer that wraps
the new unified client implementation with intelligent API selection.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from google.auth.transport.requests import AuthorizedSession

from .auth import AuthManager, get_auth_manager
from .config import load_config
from .exceptions import (
    APIError, InvalidRequestError, QuotaExceededError
)
from .models import Report, ReportDefinition, ReportStatus
from .unified import GAMUnifiedClient, create_unified_client

logger = logging.getLogger(__name__)

# Constants for REST API  
API_BASE_URL = "https://admanager.googleapis.com/v1"


class GAMClient:
    """
    Unified client for Google Ad Manager API operations.
    
    This class provides backward compatibility for existing code while
    utilizing the new unified client implementation underneath.
    """
    
    def __init__(self, auth_manager: Optional[AuthManager] = None, config: Optional[Any] = None):
        """
        Initialize GAM client.
        
        Args:
            auth_manager: Optional AuthManager instance. If not provided,
                         uses the default singleton instance.
            config: Optional configuration override
        """
        self.auth_manager = auth_manager or get_auth_manager()
        
        # Load configuration
        if config is None:
            self.config = load_config()
        else:
            from .config import Config
            if isinstance(config, dict):
                # Convert dict to Config object if needed
                self.config = Config(**config)
            else:
                self.config = config
        
        # Initialize unified client
        self._unified_client = GAMUnifiedClient(self.config)
        
        # Legacy properties for backward compatibility
        self._soap_client: Optional[Any] = None
        self._rest_session: Optional[AuthorizedSession] = None
    
    @property
    def soap_client(self):
        """Get or create SOAP API client."""
        if self._soap_client is None:
            self._soap_client = self._unified_client.soap_adapter.soap_client
        return self._soap_client
    
    @property
    def rest_session(self) -> AuthorizedSession:
        """Get or create REST API session."""
        if self._rest_session is None:
            credentials = self.auth_manager.get_oauth2_credentials()
            self._rest_session = AuthorizedSession(credentials)
        return self._rest_session
    
    @property
    def network_code(self) -> str:
        """Get network code from auth manager."""
        return self.auth_manager.network_code
    
    @property
    def unified_client(self) -> GAMUnifiedClient:
        """Get unified client instance."""
        return self._unified_client
    
    def _handle_rest_response(self, response) -> Dict[str, Any]:
        """
        Handle REST API response and raise appropriate exceptions.
        
        Args:
            response: requests Response object
            
        Returns:
            Parsed JSON response
            
        Raises:
            APIError: For various API errors
        """
        try:
            response.raise_for_status()
            return response.json()
        except Exception as e:
            error_data = {}
            try:
                error_data = response.json()
            except:
                pass
            
            status_code = response.status_code
            error_message = error_data.get('error', {}).get('message', str(e))
            error_code = error_data.get('error', {}).get('status', '')
            
            # Handle specific error cases
            if status_code == 400:
                raise InvalidRequestError(error_message, status_code, error_code)
            elif status_code == 429:
                raise QuotaExceededError("API quota exceeded. Please wait before retrying.", status_code, error_code)
            elif status_code == 401:
                raise APIError("Authentication failed. Please check your credentials.", status_code, error_code)
            else:
                raise APIError(f"API request failed: {error_message}", status_code, error_code)
    
    # REST API Methods - Delegated to unified client
    
    def create_report_rest(self, report_definition: ReportDefinition, display_name: str) -> Report:
        """
        Create a report using REST API.
        
        Args:
            report_definition: Report definition
            display_name: Display name for the report
            
        Returns:
            Report object with ID and metadata
        """
        # Delegate to unified client with REST preference
        result = self._unified_client.create_report_sync({
            "displayName": display_name,
            "reportDefinition": report_definition.to_dict() if hasattr(report_definition, 'to_dict') else report_definition,
            "api_preference": "rest"  # Force REST API usage
        })
        
        # Convert to legacy Report object for backward compatibility
        report = Report(
            id=result.get('reportId'),
            name=result.get('displayName', display_name),
            definition=report_definition,
            status=ReportStatus.PENDING,
            network_code=self.network_code
        )
        
        # Store the full resource name for later use
        report.result_resource_name = result.get('name')
        
        logger.info(f"Created report: {report.id} - {report.name}")
        return report
    
    def run_report_rest(self, report: Report) -> str:
        """
        Run a report using REST API.
        
        Args:
            report: Report object to run
            
        Returns:
            Operation ID for tracking progress
        """
        if not report.result_resource_name:
            raise InvalidRequestError("Report must be created before running")
        
        url = f"{API_BASE_URL}/{report.result_resource_name}:run"
        
        response = self.rest_session.post(url)
        data = self._handle_rest_response(response)
        
        operation_id = data.get('name')
        report.operation_id = operation_id
        report.status = ReportStatus.RUNNING
        
        logger.info(f"Started report execution: {operation_id}")
        return operation_id
    
    def check_operation_status_rest(self, operation_id: str) -> Dict[str, Any]:
        """
        Check the status of a report operation.
        
        Args:
            operation_id: Operation ID to check
            
        Returns:
            Operation status data
        """
        url = f"{API_BASE_URL}/{operation_id}"
        
        response = self.rest_session.get(url)
        return self._handle_rest_response(response)
    
    def fetch_report_results_rest(self, result_resource_name: str, page_token: Optional[str] = None, page_size: int = 100) -> Dict[str, Any]:
        """
        Fetch report results using REST API.
        
        Args:
            result_resource_name: Resource name for the results
            page_token: Token for pagination
            page_size: Number of results per page
            
        Returns:
            Report results data
        """
        url = f"{API_BASE_URL}/{result_resource_name}:fetchRows"
        params = {}
        
        if page_token:
            params['pageToken'] = page_token
        if page_size:
            params['pageSize'] = page_size
        
        response = self.rest_session.get(url, params=params)
        return self._handle_rest_response(response)
    
    def list_reports_rest(self, page_size: int = 50, page_token: Optional[str] = None) -> Dict[str, Any]:
        """
        List available reports using REST API.
        
        Args:
            page_size: Number of reports per page
            page_token: Token for pagination
            
        Returns:
            List of reports with metadata
        """
        url = f"{API_BASE_URL}/networks/{self.network_code}/reports"
        params = {}
        
        if page_size:
            params['pageSize'] = page_size
        if page_token:
            params['pageToken'] = page_token
        
        response = self.rest_session.get(url, params=params)
        return self._handle_rest_response(response)
    
    def get_report_rest(self, report_name: str) -> Dict[str, Any]:
        """
        Get a specific report by name using REST API.
        
        Args:
            report_name: Full resource name of the report
            
        Returns:
            Report data
        """
        url = f"{API_BASE_URL}/{report_name}"
        
        response = self.rest_session.get(url)
        return self._handle_rest_response(response)
    
    # SOAP API Methods (for backwards compatibility)
    
    def get_report_service(self):
        """Get SOAP API report service."""
        return self.soap_client.GetService('ReportService')
    
    def get_network_service(self):
        """Get SOAP API network service."""
        return self.soap_client.GetService('NetworkService')
    
    def get_inventory_service(self):
        """Get SOAP API inventory service."""
        return self.soap_client.GetService('InventoryService')
    
    def get_line_item_service(self):
        """Get SOAP API line item service."""
        return self.soap_client.GetService('LineItemService')
    
    # High-level convenience methods
    
    def test_connection(self) -> bool:
        """
        Test API connection and authentication.
        
        Returns:
            True if connection is successful
        """
        try:
            # Test REST API
            self.list_reports_rest(page_size=1)
            
            # Test SOAP API
            network_service = self.get_network_service()
            network_service.getCurrentNetwork()
            
            logger.info("API connection test successful")
            return True
        except Exception as e:
            logger.error(f"API connection test failed: {e}")
            return False
    
    def get_current_network(self) -> Dict[str, Any]:
        """
        Get current network information.
        
        Returns:
            Network information dictionary
        """
        try:
            network_service = self.get_network_service()
            network = network_service.getCurrentNetwork()
            
            return {
                'id': network['id'],
                'networkCode': network['networkCode'],
                'displayName': network.get('displayName', ''),
                'timeZone': network.get('timeZone', ''),
                'currencyCode': network.get('currencyCode', '')
            }
        except Exception as e:
            logger.error(f"Failed to get network information: {e}")
            raise APIError(f"Failed to get network information: {e}")
    
    # Unified Client Convenience Methods
    
    def create_report_unified(self, report_definition: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Create a report using the unified client with intelligent API selection.
        
        Args:
            report_definition: Report configuration
            **kwargs: Additional options (api_preference, etc.)
            
        Returns:
            Report data from the optimal API
        """
        return self._unified_client.create_report_sync(report_definition, **kwargs)
    
    def list_reports_unified(self, **kwargs) -> List[Dict[str, Any]]:
        """
        List reports using the unified client with intelligent API selection.
        
        Args:
            **kwargs: Filter options and preferences
            
        Returns:
            List of reports from the optimal API
        """
        return self._unified_client.list_reports_sync(**kwargs)
    
    def get_line_items_unified(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Get line items using the unified client (automatically uses SOAP).
        
        Args:
            **kwargs: Filter options
            
        Returns:
            List of line items
        """
        return self._unified_client.get_line_items_sync(**kwargs)
    
    def test_connection_unified(self) -> bool:
        """
        Test connection using the unified client.
        
        Returns:
            True if connection successful
        """
        return self._unified_client.test_connection_sync()
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get performance summary from the unified client.
        
        Returns:
            Performance metrics and statistics
        """
        return self._unified_client.get_performance_summary()
    
    def configure_api_preference(self, preference: Optional[str]):
        """
        Configure API preference for the unified client.
        
        Args:
            preference: 'soap', 'rest', or None for auto-selection
        """
        self._unified_client.configure_api_preference(preference)


# Factory function for easy instantiation
def get_gam_client(config_path: Optional[str] = None, **options) -> GAMClient:
    """
    Factory function to get a GAM client instance.
    
    Args:
        config_path: Path to configuration file
        **options: Additional client options
        
    Returns:
        Configured GAMClient instance
    """
    return GAMClient(config=load_config(config_path) if config_path else None)


# Re-export for backward compatibility
__all__ = ["GAMClient", "get_gam_client"]