"""
Base adapter interface for Google Ad Manager API operations.

This module defines the abstract interface that all GAM API adapters must implement,
ensuring consistent behavior across SOAP and REST adapters.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from datetime import datetime


class APIAdapter(ABC):
    """
    Abstract base class for Google Ad Manager API adapters.
    
    This interface defines the contract that all adapters (SOAP, REST)
    must implement to ensure consistent behavior across different API backends.
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the adapter with configuration.
        
        Args:
            config: Configuration dictionary containing authentication and API settings.
        """
        self.config = config
    
    # Report Operations
    
    @abstractmethod
    def get_reports(self, **filters) -> List[Dict[str, Any]]:
        """
        Get list of reports with optional filtering.
        
        Args:
            **filters: Optional filters (e.g., status, date_range)
            
        Returns:
            List of report dictionaries
            
        Raises:
            APIError: For API-related errors
        """
        pass
    
    @abstractmethod
    def create_report(self, report_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new report job.
        
        Args:
            report_definition: Report configuration including dimensions, metrics, filters
            
        Returns:
            Report job information including ID
            
        Raises:
            ValidationError: For invalid report definition
            APIError: For API-related errors
        """
        pass
    
    @abstractmethod
    def get_report_status(self, report_id: str) -> str:
        """
        Get the current status of a report job.
        
        Args:
            report_id: Report job ID
            
        Returns:
            Status string (e.g., 'COMPLETED', 'IN_PROGRESS', 'FAILED')
            
        Raises:
            NotFoundError: If report not found
            APIError: For API-related errors
        """
        pass
    
    @abstractmethod
    def download_report(self, report_id: str, format: str = 'CSV') -> Union[str, bytes]:
        """
        Download report results.
        
        Args:
            report_id: Report job ID
            format: Output format (CSV, TSV, XML)
            
        Returns:
            Report data as string or bytes
            
        Raises:
            ReportNotReadyError: If report is not completed
            NotFoundError: If report not found
            APIError: For API-related errors
        """
        pass
    
    # Line Item Operations
    
    @abstractmethod
    def manage_line_items(self, operation: str, line_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Manage line items (create, update, delete).
        
        Args:
            operation: Operation type ('CREATE', 'UPDATE', 'DELETE')
            line_items: List of line item configurations
            
        Returns:
            List of processed line items with results
            
        Raises:
            ValidationError: For invalid line item data
            APIError: For API-related errors
        """
        pass
    
    @abstractmethod
    def get_line_items(self, **filters) -> List[Dict[str, Any]]:
        """
        Get line items with optional filtering.
        
        Args:
            **filters: Optional filters (e.g., order_id, status)
            
        Returns:
            List of line item dictionaries
            
        Raises:
            APIError: For API-related errors
        """
        pass
    
    # Inventory Operations
    
    @abstractmethod
    def get_inventory(self, inventory_type: str, **filters) -> List[Dict[str, Any]]:
        """
        Get inventory items (ad units, placements, etc.).
        
        Args:
            inventory_type: Type of inventory ('AD_UNITS', 'PLACEMENTS')
            **filters: Optional filters
            
        Returns:
            List of inventory items
            
        Raises:
            InvalidRequestError: For invalid inventory type
            APIError: For API-related errors
        """
        pass
    
    @abstractmethod
    def create_ad_unit(self, ad_unit_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new ad unit.
        
        Args:
            ad_unit_config: Ad unit configuration
            
        Returns:
            Created ad unit information
            
        Raises:
            ValidationError: For invalid ad unit data
            APIError: For API-related errors
        """
        pass
    
    # Metadata Operations
    
    @abstractmethod
    def get_dimensions(self) -> List[str]:
        """
        Get available report dimensions.
        
        Returns:
            List of dimension names
            
        Raises:
            APIError: For API-related errors
        """
        pass
    
    @abstractmethod
    def get_metrics(self) -> List[str]:
        """
        Get available report metrics.
        
        Returns:
            List of metric names
            
        Raises:
            APIError: For API-related errors
        """
        pass
    
    # Utility Operations
    
    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test API connectivity and authentication.
        
        Returns:
            True if connection successful
            
        Raises:
            AuthError: For authentication failures
            APIError: For other API errors
        """
        pass
    
    @abstractmethod
    def get_network_info(self) -> Dict[str, Any]:
        """
        Get network information.
        
        Returns:
            Network details including code, name, timezone
            
        Raises:
            APIError: For API-related errors
        """
        pass