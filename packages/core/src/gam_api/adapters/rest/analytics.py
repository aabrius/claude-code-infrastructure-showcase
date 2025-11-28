"""
Advanced analytics module for REST adapter.

Provides high-level analytics methods for common GAM reporting patterns,
including quick reports, custom analytics, and batch operations.
"""

import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from enum import Enum

from ...models import ReportType, DateRange, ReportDefinition
from ...exceptions import ValidationError, ReportError
from .rest_adapter import RESTAdapter

logger = logging.getLogger(__name__)


class QuickReportType(Enum):
    """Enumeration of available quick report types."""
    DELIVERY = "delivery"
    INVENTORY = "inventory"
    SALES = "sales"
    REACH = "reach"
    PROGRAMMATIC = "programmatic"


class ExportFormat(Enum):
    """Supported export formats."""
    JSON = "JSON"
    CSV = "CSV"
    TSV = "TSV"
    EXCEL = "EXCEL"


class RESTAnalytics:
    """
    Advanced analytics layer for REST adapter.
    
    Provides convenient methods for common reporting patterns and analytics workflows.
    """
    
    def __init__(self, adapter: RESTAdapter):
        """
        Initialize analytics with REST adapter.
        
        Args:
            adapter: RESTAdapter instance
        """
        self.adapter = adapter
        logger.debug("RESTAnalytics initialized")
    
    def get_quick_report_types(self) -> List[str]:
        """
        Get available quick report types.
        
        Returns:
            List of quick report type names
        """
        return [qrt.value for qrt in QuickReportType]
    
    def generate_delivery_report(
        self,
        date_range: Dict[str, str],
        dimensions: Optional[List[str]] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
        format: str = "JSON"
    ) -> Dict[str, Any]:
        """
        Generate delivery report with impressions, clicks, CTR, revenue metrics.
        
        Args:
            date_range: Dictionary with 'start_date' and 'end_date'
            dimensions: Optional list of dimensions (defaults to common delivery dimensions)
            filters: Optional list of filters
            format: Export format (JSON, CSV, TSV)
            
        Returns:
            Report data in requested format
        """
        if dimensions is None:
            dimensions = [
                "DATE",
                "AD_UNIT_NAME", 
                "ADVERTISER_NAME",
                "ORDER_NAME",
                "LINE_ITEM_NAME"
            ]
        
        metrics = [
            "IMPRESSIONS",
            "CLICKS", 
            "CTR",
            "REVENUE",
            "ECPM"
        ]
        
        report_def = self._build_report_definition(
            name="Delivery Report",
            dimensions=dimensions,
            metrics=metrics,
            date_range=date_range,
            filters=filters
        )
        
        return self._execute_report(report_def, format)
    
    def generate_inventory_report(
        self,
        date_range: Dict[str, str],
        dimensions: Optional[List[str]] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
        format: str = "JSON"
    ) -> Dict[str, Any]:
        """
        Generate inventory report with ad requests, fill rate, match rate metrics.
        
        Args:
            date_range: Dictionary with 'start_date' and 'end_date'
            dimensions: Optional list of dimensions
            filters: Optional list of filters  
            format: Export format
            
        Returns:
            Report data in requested format
        """
        if dimensions is None:
            dimensions = [
                "DATE",
                "AD_UNIT_NAME",
                "DEVICE_CATEGORY_NAME",
                "COUNTRY_NAME"
            ]
        
        metrics = [
            "AD_REQUESTS",
            "MATCHED_REQUESTS",
            "FILL_RATE",
            "IMPRESSIONS",
            "REVENUE"
        ]
        
        report_def = self._build_report_definition(
            name="Inventory Report", 
            dimensions=dimensions,
            metrics=metrics,
            date_range=date_range,
            filters=filters
        )
        
        return self._execute_report(report_def, format)
    
    def generate_sales_report(
        self,
        date_range: Dict[str, str],
        dimensions: Optional[List[str]] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
        format: str = "JSON"
    ) -> Dict[str, Any]:
        """
        Generate sales report with revenue, eCPM by advertiser and order.
        
        Args:
            date_range: Dictionary with 'start_date' and 'end_date'
            dimensions: Optional list of dimensions
            filters: Optional list of filters
            format: Export format
            
        Returns:
            Report data in requested format
        """
        if dimensions is None:
            dimensions = [
                "DATE",
                "ADVERTISER_NAME",
                "ORDER_NAME",
                "SALESPERSON_NAME"
            ]
        
        metrics = [
            "REVENUE",
            "IMPRESSIONS",
            "ECPM",
            "CLICKS",
            "CTR"
        ]
        
        report_def = self._build_report_definition(
            name="Sales Report",
            dimensions=dimensions, 
            metrics=metrics,
            date_range=date_range,
            filters=filters
        )
        
        return self._execute_report(report_def, format)
    
    def generate_reach_report(
        self,
        date_range: Dict[str, str],
        dimensions: Optional[List[str]] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
        format: str = "JSON"
    ) -> Dict[str, Any]:
        """
        Generate reach report with unique reach, frequency by country and device.
        
        Args:
            date_range: Dictionary with 'start_date' and 'end_date'
            dimensions: Optional list of dimensions
            filters: Optional list of filters
            format: Export format
            
        Returns:
            Report data in requested format
        """
        if dimensions is None:
            dimensions = [
                "DATE",
                "COUNTRY_NAME",
                "DEVICE_CATEGORY_NAME",
                "AGE_RANGE"
            ]
        
        metrics = [
            "UNIQUE_REACH",
            "FREQUENCY", 
            "IMPRESSIONS",
            "REVENUE"
        ]
        
        report_def = self._build_report_definition(
            name="Reach Report",
            dimensions=dimensions,
            metrics=metrics,
            date_range=date_range,
            filters=filters
        )
        
        return self._execute_report(report_def, format)
    
    def generate_programmatic_report(
        self,
        date_range: Dict[str, str],
        dimensions: Optional[List[str]] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
        format: str = "JSON"
    ) -> Dict[str, Any]:
        """
        Generate programmatic report with programmatic channel performance.
        
        Args:
            date_range: Dictionary with 'start_date' and 'end_date' 
            dimensions: Optional list of dimensions
            filters: Optional list of filters
            format: Export format
            
        Returns:
            Report data in requested format
        """
        if dimensions is None:
            dimensions = [
                "DATE",
                "PROGRAMMATIC_CHANNEL_NAME",
                "DEMAND_CHANNEL_NAME",
                "DEVICE_CATEGORY_NAME"
            ]
        
        metrics = [
            "PROGRAMMATIC_IMPRESSIONS",
            "PROGRAMMATIC_REVENUE", 
            "PROGRAMMATIC_ECPM",
            "FILL_RATE"
        ]
        
        report_def = self._build_report_definition(
            name="Programmatic Report",
            dimensions=dimensions,
            metrics=metrics,
            date_range=date_range, 
            filters=filters
        )
        
        return self._execute_report(report_def, format)
    
    def generate_quick_report(
        self,
        report_type: str,
        date_range: Dict[str, str],
        dimensions: Optional[List[str]] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
        format: str = "JSON"
    ) -> Dict[str, Any]:
        """
        Generate quick report by type.
        
        Args:
            report_type: Type of report (delivery, inventory, sales, reach, programmatic)
            date_range: Dictionary with 'start_date' and 'end_date'
            dimensions: Optional list of dimensions
            filters: Optional list of filters
            format: Export format
            
        Returns:
            Report data in requested format
        """
        report_type_lower = report_type.lower()
        
        if report_type_lower == QuickReportType.DELIVERY.value:
            return self.generate_delivery_report(date_range, dimensions, filters, format)
        elif report_type_lower == QuickReportType.INVENTORY.value:
            return self.generate_inventory_report(date_range, dimensions, filters, format)
        elif report_type_lower == QuickReportType.SALES.value:
            return self.generate_sales_report(date_range, dimensions, filters, format)
        elif report_type_lower == QuickReportType.REACH.value:
            return self.generate_reach_report(date_range, dimensions, filters, format)
        elif report_type_lower == QuickReportType.PROGRAMMATIC.value:
            return self.generate_programmatic_report(date_range, dimensions, filters, format)
        else:
            raise ValidationError(
                f"Unknown report type: {report_type}. "
                f"Available types: {', '.join(self.get_quick_report_types())}"
            )
    
    def generate_custom_report(
        self,
        name: str,
        dimensions: List[str],
        metrics: List[str],
        date_range: Dict[str, str],
        filters: Optional[List[Dict[str, Any]]] = None,
        format: str = "JSON"
    ) -> Dict[str, Any]:
        """
        Generate custom report with specific dimensions and metrics.
        
        Args:
            name: Report name
            dimensions: List of dimension names
            metrics: List of metric names
            date_range: Dictionary with 'start_date' and 'end_date'
            filters: Optional list of filters
            format: Export format
            
        Returns:
            Report data in requested format
        """
        report_def = self._build_report_definition(
            name=name,
            dimensions=dimensions,
            metrics=metrics,
            date_range=date_range,
            filters=filters
        )
        
        return self._execute_report(report_def, format)
    
    def validate_dimensions_metrics(
        self,
        dimensions: List[str],
        metrics: List[str]
    ) -> Dict[str, Any]:
        """
        Validate that dimensions and metrics are available and compatible.
        
        Args:
            dimensions: List of dimension names to validate
            metrics: List of metric names to validate
            
        Returns:
            Validation result with available dimensions/metrics
        """
        available_dimensions = set(self.adapter.get_dimensions())
        available_metrics = set(self.adapter.get_metrics())
        
        invalid_dimensions = set(dimensions) - available_dimensions
        invalid_metrics = set(metrics) - available_metrics
        
        result = {
            "valid": len(invalid_dimensions) == 0 and len(invalid_metrics) == 0,
            "available_dimensions": list(available_dimensions),
            "available_metrics": list(available_metrics),
            "invalid_dimensions": list(invalid_dimensions),
            "invalid_metrics": list(invalid_metrics)
        }
        
        if not result["valid"]:
            logger.warning(f"Invalid dimensions: {invalid_dimensions}")
            logger.warning(f"Invalid metrics: {invalid_metrics}")
        
        return result
    
    def get_common_combinations(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Get common dimension-metric combinations for different report types.
        
        Returns:
            Dictionary of report types with their common combinations
        """
        return {
            "delivery": {
                "dimensions": ["DATE", "AD_UNIT_NAME", "ADVERTISER_NAME", "ORDER_NAME"],
                "metrics": ["IMPRESSIONS", "CLICKS", "CTR", "REVENUE", "ECPM"]
            },
            "inventory": {
                "dimensions": ["DATE", "AD_UNIT_NAME", "DEVICE_CATEGORY_NAME"],
                "metrics": ["AD_REQUESTS", "MATCHED_REQUESTS", "FILL_RATE", "IMPRESSIONS"]
            },
            "sales": {
                "dimensions": ["DATE", "ADVERTISER_NAME", "ORDER_NAME", "SALESPERSON_NAME"],
                "metrics": ["REVENUE", "IMPRESSIONS", "ECPM", "CLICKS", "CTR"]
            },
            "reach": {
                "dimensions": ["DATE", "COUNTRY_NAME", "DEVICE_CATEGORY_NAME", "AGE_RANGE"],
                "metrics": ["UNIQUE_REACH", "FREQUENCY", "IMPRESSIONS", "REVENUE"]
            },
            "programmatic": {
                "dimensions": ["DATE", "PROGRAMMATIC_CHANNEL_NAME", "DEMAND_CHANNEL_NAME"],
                "metrics": ["PROGRAMMATIC_IMPRESSIONS", "PROGRAMMATIC_REVENUE", "PROGRAMMATIC_ECPM"]
            }
        }
    
    def batch_generate_reports(
        self,
        report_configs: List[Dict[str, Any]],
        concurrent_limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple reports in batch with concurrency control.
        
        Args:
            report_configs: List of report configuration dictionaries
            concurrent_limit: Maximum number of concurrent report generations
            
        Returns:
            List of report results
        """
        import concurrent.futures
        import time
        
        results = []
        
        def generate_single_report(config):
            try:
                if 'type' in config:
                    # Quick report
                    return self.generate_quick_report(
                        config['type'],
                        config['date_range'],
                        config.get('dimensions'),
                        config.get('filters'),
                        config.get('format', 'JSON')
                    )
                else:
                    # Custom report
                    return self.generate_custom_report(
                        config['name'],
                        config['dimensions'],
                        config['metrics'],
                        config['date_range'],
                        config.get('filters'),
                        config.get('format', 'JSON')
                    )
            except Exception as e:
                logger.error(f"Failed to generate report {config.get('name', 'unknown')}: {e}")
                return {"error": str(e), "config": config}
        
        # Execute with thread pool to respect rate limits
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_limit) as executor:
            future_to_config = {
                executor.submit(generate_single_report, config): config 
                for config in report_configs
            }
            
            for future in concurrent.futures.as_completed(future_to_config):
                config = future_to_config[future]
                try:
                    result = future.result()
                    result['config'] = config
                    results.append(result)
                except Exception as e:
                    logger.error(f"Report generation failed for {config}: {e}")
                    results.append({"error": str(e), "config": config})
                
                # Small delay to be respectful of API limits
                time.sleep(0.5)
        
        return results
    
    def _build_report_definition(
        self,
        name: str,
        dimensions: List[str],
        metrics: List[str], 
        date_range: Dict[str, str],
        filters: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Build report definition dictionary for GAM REST API.
        
        Args:
            name: Report name
            dimensions: List of dimension names
            metrics: List of metric names
            date_range: Dictionary with 'start_date' and 'end_date'
            filters: Optional list of filters
            
        Returns:
            Report definition dictionary
        """
        # Validate inputs
        if not dimensions:
            raise ValidationError("At least one dimension is required")
        if not metrics:
            raise ValidationError("At least one metric is required")
        if 'start_date' not in date_range or 'end_date' not in date_range:
            raise ValidationError("Date range must include 'start_date' and 'end_date'")
        
        # Build report definition
        report_def = {
            "displayName": name,
            "reportDefinition": {
                "dimensions": dimensions,
                "metrics": metrics,
                "dateRange": {
                    "startDate": date_range['start_date'],
                    "endDate": date_range['end_date']
                }
            }
        }
        
        # Add filters if provided
        if filters:
            report_def["reportDefinition"]["filters"] = filters
        
        return report_def
    
    def _execute_report(
        self,
        report_definition: Dict[str, Any],
        format: str = "JSON",
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Execute report generation and return results.
        
        Args:
            report_definition: Report definition dictionary
            format: Export format
            timeout: Maximum wait time for report completion
            
        Returns:
            Report execution result
        """
        try:
            # Create and run report
            operation_id = self.adapter.create_and_run_report(report_definition)
            
            # Wait for completion
            final_status = self.adapter.wait_for_report(operation_id, timeout)
            
            if final_status == 'FAILED':
                raise ReportError(f"Report generation failed: {operation_id}")
            
            # Download results
            report_data = self.adapter.download_report(operation_id, format)
            
            return {
                "status": "completed",
                "operation_id": operation_id,
                "data": report_data,
                "format": format,
                "report_name": report_definition.get('displayName', 'Unknown')
            }
            
        except Exception as e:
            logger.error(f"Report execution failed: {e}")
            return {
                "status": "failed", 
                "error": str(e),
                "report_name": report_definition.get('displayName', 'Unknown')
            }
    
    def get_report_status_monitoring(self, operation_ids: List[str]) -> Dict[str, str]:
        """
        Monitor status of multiple reports in real-time.
        
        Args:
            operation_ids: List of operation IDs to monitor
            
        Returns:
            Dictionary mapping operation IDs to their current status
        """
        status_map = {}
        
        for operation_id in operation_ids:
            try:
                status = self.adapter.get_report_status(operation_id)
                status_map[operation_id] = status
            except Exception as e:
                logger.error(f"Failed to get status for {operation_id}: {e}")
                status_map[operation_id] = "ERROR"
        
        return status_map