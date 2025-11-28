"""
SOAP API adapter for Google Ad Manager API.

This adapter implements the APIAdapter interface using the mature
Google Ad Manager SOAP API for complete feature coverage.
"""

import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import tempfile
import yaml

from ..base import APIAdapter
from ...exceptions import (
    GAMError, APIError, InvalidRequestError, QuotaExceededError,
    ConfigurationError, AuthenticationError, ReportError
)

# Import SOAP client from googleads
try:
    from googleads import ad_manager
    from googleads.ad_manager import StatementBuilder
except ImportError:
    raise ImportError("googleads package is required for SOAP adapter")

logger = logging.getLogger(__name__)


class SOAPAdapter(APIAdapter):
    """
    SOAP API adapter for Google Ad Manager API.
    
    This adapter provides complete access to all GAM operations using
    the mature SOAP API. It supports all operations including line items,
    inventory management, and advanced reporting features not available in REST.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize SOAP adapter with configuration.
        
        Args:
            config: Configuration dictionary with auth credentials and network code
        """
        super().__init__(config)
        self._soap_client = None
        self._services = {}  # Cache for SOAP services
        self._network_code = None
        
        # Initialize authentication
        self._init_authentication()
    
    def _init_authentication(self):
        """Initialize SOAP client authentication."""
        # Validate required configuration
        required_fields = ['network_code', 'client_id', 'client_secret', 'refresh_token']
        missing_fields = [field for field in required_fields if not self.config.get(field)]
        
        if missing_fields:
            raise ConfigurationError(f"Missing required config fields: {', '.join(missing_fields)}")
        
        self._network_code = self.config['network_code']
        
        # Create legacy format configuration for googleads library
        legacy_config = {
            'ad_manager': {
                'application_name': self.config.get('application_name', 'GAM SOAP Adapter'),
                'network_code': self._network_code,
                'client_id': self.config['client_id'],
                'client_secret': self.config['client_secret'],
                'refresh_token': self.config['refresh_token']
            }
        }
        
        # Write to temporary file (googleads requires YAML file)
        import os
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(legacy_config, f)
                temp_file = f.name
            
            # Initialize SOAP client
            self._soap_client = ad_manager.AdManagerClient.LoadFromStorage(temp_file)
            logger.info("Successfully initialized SOAP client")
        except Exception as e:
            raise AuthenticationError(f"Failed to initialize SOAP client: {e}")
        finally:
            # Clean up temporary file
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                    logger.debug("Cleaned up temporary config file")
                except Exception:
                    pass  # Ignore cleanup errors
    
    def _get_service(self, service_name: str):
        """
        Get or create a SOAP service with caching.
        
        Args:
            service_name: Name of the service (e.g., 'ReportService')
            
        Returns:
            SOAP service instance
        """
        if service_name not in self._services:
            try:
                self._services[service_name] = self._soap_client.GetService(service_name)
                logger.debug(f"Created SOAP service: {service_name}")
            except Exception as e:
                raise APIError(f"Failed to create service {service_name}: {e}")
        
        return self._services[service_name]
    
    def _handle_soap_error(self, error: Exception) -> None:
        """
        Handle SOAP API errors and convert to appropriate exceptions.
        
        Args:
            error: Original SOAP exception
            
        Raises:
            Appropriate GAMError subclass
        """
        error_str = str(error)
        
        if "Authentication" in error_str or "Unauthorized" in error_str:
            raise AuthenticationError(f"SOAP authentication failed: {error_str}")
        elif "QuotaExceeded" in error_str or "RateExceeded" in error_str:
            raise QuotaExceededError(f"SOAP quota exceeded: {error_str}")
        elif "InvalidRequest" in error_str or "ValidationError" in error_str:
            raise InvalidRequestError(f"SOAP request invalid: {error_str}")
        elif "NotFound" in error_str:
            raise InvalidRequestError(f"SOAP resource not found: {error_str}")
        else:
            raise APIError(f"SOAP API error: {error_str}")
    
    # Report Operations
    
    def get_reports(self, **filters) -> List[Dict[str, Any]]:
        """Get list of reports with optional filtering."""
        try:
            report_service = self._get_service('ReportService')
            
            # Build statement for filtering
            statement_builder = StatementBuilder()
            
            if 'job_id' in filters:
                statement_builder.Where('id = :jobId').WithBindVariable('jobId', filters['job_id'])
            if 'status' in filters:
                statement_builder.Where('status = :status').WithBindVariable('status', filters['status'])
            
            statement_builder.OrderBy('id', ascending=False).Limit(500)
            
            reports = []
            max_iterations = 100  # Prevent infinite loops
            iterations = 0
            
            while iterations < max_iterations:
                response = report_service.getReportJobsByStatement(statement_builder.ToStatement())
                
                if 'results' in response and len(response['results']):
                    for report_job in response['results']:
                        reports.append(self._convert_report_job(report_job))
                    statement_builder.offset += len(response['results'])
                    iterations += 1
                else:
                    break
                    
            if iterations >= max_iterations:
                logger.warning(f"Pagination reached maximum iterations ({max_iterations})")
            
            return reports
            
        except Exception as e:
            self._handle_soap_error(e)
    
    def create_report(self, report_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new report job."""
        try:
            report_service = self._get_service('ReportService')
            
            # Convert report definition to SOAP format
            report_job = {
                'reportQuery': {
                    'dimensions': report_definition.get('dimensions', []),
                    'adUnitView': report_definition.get('adUnitView', 'HIERARCHICAL'),
                    'columns': report_definition.get('metrics', []),
                    'dateRangeType': report_definition.get('dateRangeType', 'CUSTOM_DATE'),
                    'startDate': self._format_date(report_definition.get('startDate')),
                    'endDate': self._format_date(report_definition.get('endDate')),
                }
            }
            
            # Add optional filters
            if 'dimensionFilters' in report_definition:
                report_job['reportQuery']['dimensionFilters'] = report_definition['dimensionFilters']
            
            # Run report job
            report_job_response = report_service.runReportJob(report_job)
            
            return self._convert_report_job(report_job_response)
            
        except Exception as e:
            self._handle_soap_error(e)
    
    def get_report_status(self, report_id: str) -> str:
        """Get the current status of a report job."""
        try:
            report_service = self._get_service('ReportService')
            report_job = report_service.getReportJob(int(report_id))
            
            return report_job['reportJobStatus']
            
        except Exception as e:
            self._handle_soap_error(e)
    
    def download_report(self, report_id: str, format: str = 'CSV') -> Union[str, bytes]:
        """Download report results."""
        try:
            report_service = self._get_service('ReportService')
            
            # Check if report is ready
            report_job = report_service.getReportJob(int(report_id))
            if report_job['reportJobStatus'] != 'COMPLETED':
                raise ReportError(f"Report {report_id} is not ready. Status: {report_job['reportJobStatus']}")
            
            # Download report
            export_format = 'CSV_DUMP' if format == 'CSV' else format
            report_downloader = report_service.getReportDownloader(int(report_id), export_format)
            
            # Download as string
            report_data = report_downloader.DownloadReportToString()
            
            return report_data
            
        except Exception as e:
            self._handle_soap_error(e)
    
    # Line Item Operations
    
    def manage_line_items(self, operation: str, line_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Manage line items (create, update, delete)."""
        try:
            line_item_service = self._get_service('LineItemService')
            
            # Process in batches for better performance
            batch_size = 100
            results = []
            
            for i in range(0, len(line_items), batch_size):
                batch = line_items[i:i + batch_size]
                
                if operation == 'CREATE':
                    batch_results = line_item_service.createLineItems(batch)
                elif operation == 'UPDATE':
                    batch_results = line_item_service.updateLineItems(batch)
                elif operation == 'DELETE':
                    # SOAP doesn't support delete, archive instead
                    for item in batch:
                        item['isArchived'] = True
                    batch_results = line_item_service.updateLineItems(batch)
                else:
                    raise InvalidRequestError(f"Invalid operation: {operation}")
                
                results.extend(batch_results)
            
            return [self._convert_line_item(item) for item in results]
            
        except Exception as e:
            self._handle_soap_error(e)
    
    def get_line_items(self, **filters) -> List[Dict[str, Any]]:
        """Get line items with optional filtering."""
        try:
            line_item_service = self._get_service('LineItemService')
            
            statement_builder = StatementBuilder()
            
            if 'order_id' in filters:
                statement_builder.Where('orderId = :orderId').WithBindVariable('orderId', filters['order_id'])
            if 'status' in filters:
                statement_builder.Where('status = :status').WithBindVariable('status', filters['status'])
            
            statement_builder.OrderBy('id', ascending=False).Limit(500)
            
            line_items = []
            max_iterations = 100  # Prevent infinite loops
            iterations = 0
            
            while iterations < max_iterations:
                response = line_item_service.getLineItemsByStatement(statement_builder.ToStatement())
                
                if 'results' in response and len(response['results']):
                    for line_item in response['results']:
                        line_items.append(self._convert_line_item(line_item))
                    statement_builder.offset += len(response['results'])
                    iterations += 1
                else:
                    break
                    
            if iterations >= max_iterations:
                logger.warning(f"Line items pagination reached maximum iterations ({max_iterations})")
            
            return line_items
            
        except Exception as e:
            self._handle_soap_error(e)
    
    # Inventory Operations
    
    def get_inventory(self, inventory_type: str, **filters) -> List[Dict[str, Any]]:
        """Get inventory items (ad units, placements, etc.)."""
        try:
            if inventory_type == 'AD_UNITS':
                return self._get_ad_units(**filters)
            elif inventory_type == 'PLACEMENTS':
                return self._get_placements(**filters)
            else:
                raise InvalidRequestError(f"Invalid inventory type: {inventory_type}")
                
        except Exception as e:
            self._handle_soap_error(e)
    
    def _get_ad_units(self, **filters) -> List[Dict[str, Any]]:
        """Get ad units with filtering."""
        inventory_service = self._get_service('InventoryService')
        
        statement_builder = StatementBuilder()
        
        if 'parent_id' in filters:
            statement_builder.Where('parentId = :parentId').WithBindVariable('parentId', filters['parent_id'])
        
        statement_builder.OrderBy('id', ascending=True).Limit(500)
        
        ad_units = []
        max_iterations = 100  # Prevent infinite loops
        iterations = 0
        
        while iterations < max_iterations:
            response = inventory_service.getAdUnitsByStatement(statement_builder.ToStatement())
            
            if 'results' in response and len(response['results']):
                for ad_unit in response['results']:
                    ad_units.append(self._convert_ad_unit(ad_unit))
                statement_builder.offset += len(response['results'])
                iterations += 1
            else:
                break
                
        if iterations >= max_iterations:
            logger.warning(f"Ad units pagination reached maximum iterations ({max_iterations})")
        
        return ad_units
    
    def _get_placements(self, **filters) -> List[Dict[str, Any]]:
        """Get placements with filtering."""
        placement_service = self._get_service('PlacementService')
        
        statement_builder = StatementBuilder()
        statement_builder.OrderBy('id', ascending=True).Limit(500)
        
        placements = []
        max_iterations = 100  # Prevent infinite loops
        iterations = 0
        
        while iterations < max_iterations:
            response = placement_service.getPlacementsByStatement(statement_builder.ToStatement())
            
            if 'results' in response and len(response['results']):
                for placement in response['results']:
                    placements.append(self._convert_placement(placement))
                statement_builder.offset += len(response['results'])
                iterations += 1
            else:
                break
                
        if iterations >= max_iterations:
            logger.warning(f"Placements pagination reached maximum iterations ({max_iterations})")
        
        return placements
    
    def create_ad_unit(self, ad_unit_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new ad unit."""
        try:
            inventory_service = self._get_service('InventoryService')
            
            # Create ad unit
            ad_units = inventory_service.createAdUnits([ad_unit_config])
            
            return self._convert_ad_unit(ad_units[0])
            
        except Exception as e:
            self._handle_soap_error(e)
    
    # Metadata Operations
    
    def get_dimensions(self) -> List[str]:
        """Get available report dimensions."""
        # SOAP API doesn't have a direct way to get dimensions
        # Return common dimensions
        return [
            'DATE', 'HOUR', 'DAY_OF_WEEK', 'WEEK', 'MONTH', 'MONTH_AND_YEAR',
            'AD_UNIT_ID', 'AD_UNIT_NAME', 'ADVERTISER_ID', 'ADVERTISER_NAME',
            'ORDER_ID', 'ORDER_NAME', 'LINE_ITEM_ID', 'LINE_ITEM_NAME',
            'CREATIVE_ID', 'CREATIVE_NAME', 'CREATIVE_SIZE', 'CREATIVE_TYPE',
            'COUNTRY_NAME', 'DEVICE_CATEGORY_NAME', 'PLACEMENT_ID', 'PLACEMENT_NAME'
        ]
    
    def get_metrics(self) -> List[str]:
        """Get available report metrics."""
        # SOAP API doesn't have a direct way to get metrics
        # Return common metrics
        return [
            'AD_SERVER_IMPRESSIONS', 'AD_SERVER_CLICKS', 'AD_SERVER_CTR',
            'AD_SERVER_CPM_AND_CPC_REVENUE', 'AD_SERVER_AVERAGE_ECPM',
            'AD_EXCHANGE_IMPRESSIONS', 'AD_EXCHANGE_CLICKS', 'AD_EXCHANGE_CTR',
            'AD_EXCHANGE_REVENUE', 'AD_EXCHANGE_AVERAGE_ECPM',
            'TOTAL_IMPRESSIONS', 'TOTAL_CLICKS', 'TOTAL_CTR',
            'TOTAL_CPM_AND_CPC_REVENUE', 'TOTAL_AVERAGE_ECPM',
            'TOTAL_REVENUE', 'AD_SERVER_REVENUE'  # Added missing metrics
        ]
    
    # Utility Operations
    
    def test_connection(self) -> bool:
        """Test API connectivity and authentication."""
        try:
            network_service = self._get_service('NetworkService')
            network = network_service.getCurrentNetwork()
            logger.info(f"Successfully connected to network: {network['displayName']} ({network['networkCode']})")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get network information."""
        try:
            network_service = self._get_service('NetworkService')
            network = network_service.getCurrentNetwork()
            
            return {
                'id': network['id'],
                'network_code': network['networkCode'],
                'display_name': network['displayName'],
                'time_zone': network['timeZone'],
                'currency_code': network['currencyCode']
            }
            
        except Exception as e:
            self._handle_soap_error(e)
    
    # Helper methods for data conversion
    
    def _convert_report_job(self, report_job: Dict[str, Any]) -> Dict[str, Any]:
        """Convert SOAP report job to standard format."""
        return {
            'id': str(report_job['id']),
            'status': report_job['reportJobStatus'],
            'report_query': report_job.get('reportQuery', {}),
            'created_at': None  # SOAP doesn't provide creation time
        }
    
    def _convert_line_item(self, line_item: Dict[str, Any]) -> Dict[str, Any]:
        """Convert SOAP line item to standard format."""
        return {
            'id': str(line_item['id']),
            'name': line_item['name'],
            'order_id': str(line_item['orderId']),
            'status': line_item['status'],
            'priority': line_item['priority'],
            'start_date': self._datetime_to_string(line_item['startDateTime']),
            'end_date': self._datetime_to_string(line_item['endDateTime']),
            'is_archived': line_item.get('isArchived', False)
        }
    
    def _convert_ad_unit(self, ad_unit: Dict[str, Any]) -> Dict[str, Any]:
        """Convert SOAP ad unit to standard format."""
        return {
            'id': str(ad_unit['id']),
            'name': ad_unit['name'],
            'ad_unit_code': ad_unit['adUnitCode'],
            'parent_id': str(ad_unit.get('parentId')) if ad_unit.get('parentId') else None,
            'status': ad_unit['status'],
            'ad_unit_sizes': ad_unit.get('adUnitSizes', [])
        }
    
    def _convert_placement(self, placement: Dict[str, Any]) -> Dict[str, Any]:
        """Convert SOAP placement to standard format."""
        return {
            'id': str(placement['id']),
            'name': placement['name'],
            'status': placement['status'],
            'targeted_ad_unit_ids': [str(id) for id in placement.get('targetedAdUnitIds', [])]
        }
    
    def _format_date(self, date_str: str) -> Dict[str, Any]:
        """Format date string to SOAP date object."""
        if not date_str:
            return None
        
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return {
            'year': date_obj.year,
            'month': date_obj.month,
            'day': date_obj.day
        }
    
    def _datetime_to_string(self, datetime_obj: Dict[str, Any]) -> str:
        """Convert SOAP datetime object to string."""
        if not datetime_obj:
            return None
        
        date = datetime_obj.get('date', {})
        return f"{date.get('year')}-{str(date.get('month')).zfill(2)}-{str(date.get('day')).zfill(2)}"