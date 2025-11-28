"""
API Selection Strategy for Unified GAM Client

This module implements intelligent API selection based on operation type,
performance metrics, and configuration preferences.
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Any, Tuple, List
from collections import defaultdict, deque


logger = logging.getLogger(__name__)


class APIType(Enum):
    """Available API types"""
    SOAP = "soap"
    REST = "rest"


class OperationType(Enum):
    """GAM operation types with their characteristics"""
    
    # Report Operations
    CREATE_REPORT = "create_report"
    GET_REPORT = "get_report"
    LIST_REPORTS = "list_reports"
    GET_REPORT_STATUS = "get_report_status"
    DOWNLOAD_REPORT = "download_report"
    DELETE_REPORT = "delete_report"
    
    # Line Item Operations
    GET_LINE_ITEMS = "get_line_items"
    CREATE_LINE_ITEM = "create_line_item"
    UPDATE_LINE_ITEM = "update_line_item"
    DELETE_LINE_ITEM = "delete_line_item"
    
    # Inventory Operations
    GET_AD_UNITS = "get_ad_units"
    CREATE_AD_UNIT = "create_ad_unit"
    UPDATE_AD_UNIT = "update_ad_unit"
    DELETE_AD_UNIT = "delete_ad_unit"
    
    # Metadata Operations
    GET_DIMENSIONS = "get_dimensions"
    GET_METRICS = "get_metrics"
    GET_DIMENSION_VALUES = "get_dimension_values"
    
    # Network Operations
    GET_NETWORK_INFO = "get_network_info"
    TEST_CONNECTION = "test_connection"


@dataclass
class OperationContext:
    """Context information for API selection decisions"""
    operation: OperationType
    params: Dict[str, Any]
    estimated_size: Optional[int] = None
    complexity_score: Optional[int] = None
    user_preference: Optional[APIType] = None


@dataclass
class PerformanceMetrics:
    """Performance tracking for API operations"""
    success_rate: float = 1.0
    avg_response_time: float = 0.0
    error_count: int = 0
    total_requests: int = 0
    last_success: Optional[float] = None
    last_failure: Optional[float] = None


class APISelectionStrategy:
    """
    Intelligent API selection strategy based on operation type,
    performance metrics, and configuration preferences.
    """
    
    # Operation-to-API mapping based on capabilities and performance
    OPERATION_MATRIX = {
        # Reports - REST preferred for better performance and features
        OperationType.CREATE_REPORT: (APIType.REST, APIType.SOAP),
        OperationType.GET_REPORT: (APIType.REST, APIType.SOAP),
        OperationType.LIST_REPORTS: (APIType.REST, APIType.SOAP),
        OperationType.GET_REPORT_STATUS: (APIType.REST, APIType.SOAP),
        OperationType.DOWNLOAD_REPORT: (APIType.REST, APIType.SOAP),
        OperationType.DELETE_REPORT: (APIType.REST, APIType.SOAP),
        
        # Line Items - SOAP only (not available in REST v1)
        OperationType.GET_LINE_ITEMS: (APIType.SOAP, None),
        OperationType.CREATE_LINE_ITEM: (APIType.SOAP, None),
        OperationType.UPDATE_LINE_ITEM: (APIType.SOAP, None),
        OperationType.DELETE_LINE_ITEM: (APIType.SOAP, None),
        
        # Inventory - SOAP preferred (more complete feature set)
        OperationType.GET_AD_UNITS: (APIType.SOAP, APIType.REST),
        OperationType.CREATE_AD_UNIT: (APIType.SOAP, None),
        OperationType.UPDATE_AD_UNIT: (APIType.SOAP, None),
        OperationType.DELETE_AD_UNIT: (APIType.SOAP, None),
        
        # Metadata - REST preferred (faster, cacheable)
        OperationType.GET_DIMENSIONS: (APIType.REST, APIType.SOAP),
        OperationType.GET_METRICS: (APIType.REST, APIType.SOAP),
        OperationType.GET_DIMENSION_VALUES: (APIType.REST, APIType.SOAP),
        
        # Network - REST preferred (simpler, modern)
        OperationType.GET_NETWORK_INFO: (APIType.REST, APIType.SOAP),
        OperationType.TEST_CONNECTION: (APIType.REST, APIType.SOAP),
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize API selection strategy.
        
        Args:
            config: Configuration dictionary with preferences
        """
        self.config = config or {}
        self.performance_metrics: Dict[APIType, PerformanceMetrics] = {
            APIType.SOAP: PerformanceMetrics(),
            APIType.REST: PerformanceMetrics()
        }
        
        # Configuration options
        self.global_preference = self._parse_api_preference(
            self.config.get('api_preference')
        )
        self.enable_performance_tracking = self.config.get(
            'enable_performance_tracking', True
        )
        self.performance_threshold = self.config.get(
            'performance_threshold', 0.8
        )
        self.complexity_threshold = self.config.get(
            'complexity_threshold', 10
        )
        
        # Performance tracking
        self.response_times: Dict[APIType, deque] = {
            APIType.SOAP: deque(maxlen=100),
            APIType.REST: deque(maxlen=100)
        }
        
        logger.info(
            f"APISelectionStrategy initialized with preference: {self.global_preference}"
        )
    
    def select_api(self, context: OperationContext) -> Tuple[APIType, Optional[APIType]]:
        """
        Select the best API for the given operation context.
        
        Args:
            context: Operation context with details
            
        Returns:
            Tuple of (primary_api, fallback_api)
        """
        operation = context.operation
        
        # Check for user preference override
        if context.user_preference:
            primary = context.user_preference
            fallback = self._get_fallback_api(operation, primary)
            logger.debug(
                f"Using user preference {primary.value} for {operation.value}"
            )
            return primary, fallback
        
        # Check for global preference override
        if self.global_preference:
            if self._is_api_supported(operation, self.global_preference):
                fallback = self._get_fallback_api(operation, self.global_preference)
                logger.debug(
                    f"Using global preference {self.global_preference.value} for {operation.value}"
                )
                return self.global_preference, fallback
        
        # Get default API preferences from matrix
        primary_api, fallback_api = self.OPERATION_MATRIX.get(
            operation, (APIType.REST, APIType.SOAP)
        )
        
        # Apply context-based adjustments
        primary_api, fallback_api = self._apply_context_rules(
            context, primary_api, fallback_api
        )
        
        # Apply performance-based adjustments
        if self.enable_performance_tracking:
            primary_api, fallback_api = self._apply_performance_rules(
                operation, primary_api, fallback_api
            )
        
        logger.debug(
            f"Selected {primary_api.value} (fallback: {fallback_api.value if fallback_api else None}) "
            f"for {operation.value}"
        )
        
        return primary_api, fallback_api
    
    def _apply_context_rules(
        self, 
        context: OperationContext, 
        primary: APIType, 
        fallback: Optional[APIType]
    ) -> Tuple[APIType, Optional[APIType]]:
        """Apply context-based decision rules"""
        
        # Large or complex operations prefer SOAP
        if context.complexity_score and context.complexity_score > self.complexity_threshold:
            if self._is_api_supported(context.operation, APIType.SOAP):
                logger.debug(
                    f"High complexity ({context.complexity_score}) - preferring SOAP"
                )
                return APIType.SOAP, primary if primary != APIType.SOAP else fallback
        
        # Bulk operations prefer SOAP
        if self._is_bulk_operation(context):
            if self._is_api_supported(context.operation, APIType.SOAP):
                logger.debug("Bulk operation detected - preferring SOAP")
                return APIType.SOAP, primary if primary != APIType.SOAP else fallback
        
        # Frequent metadata operations prefer REST (caching)
        if self._is_metadata_operation(context.operation):
            if self._is_api_supported(context.operation, APIType.REST):
                logger.debug("Metadata operation - preferring REST for caching")
                return APIType.REST, primary if primary != APIType.REST else fallback
        
        return primary, fallback
    
    def _apply_performance_rules(
        self,
        operation: OperationType,
        primary: APIType,
        fallback: Optional[APIType]
    ) -> Tuple[APIType, Optional[APIType]]:
        """Apply performance-based decision rules"""
        
        primary_metrics = self.performance_metrics[primary]
        
        # If primary API is performing poorly, try fallback
        if (primary_metrics.success_rate < self.performance_threshold and 
            fallback and self._is_api_supported(operation, fallback)):
            
            fallback_metrics = self.performance_metrics[fallback]
            if fallback_metrics.success_rate > primary_metrics.success_rate:
                logger.warning(
                    f"Primary API {primary.value} success rate {primary_metrics.success_rate:.2f} "
                    f"below threshold - switching to {fallback.value}"
                )
                return fallback, primary
        
        return primary, fallback
    
    def record_performance(
        self, 
        api: APIType, 
        operation: OperationType,
        success: bool, 
        response_time: float,
        error: Optional[Exception] = None
    ):
        """Record performance metrics for API operations"""
        
        if not self.enable_performance_tracking:
            return
        
        metrics = self.performance_metrics[api]
        current_time = time.time()
        
        metrics.total_requests += 1
        
        if success:
            metrics.last_success = current_time
            self.response_times[api].append(response_time)
            
            # Update average response time
            times = list(self.response_times[api])
            metrics.avg_response_time = sum(times) / len(times)
            
        else:
            metrics.error_count += 1
            metrics.last_failure = current_time
            
            logger.warning(
                f"API {api.value} failed for {operation.value}: {error}"
            )
        
        # Update success rate
        metrics.success_rate = (
            (metrics.total_requests - metrics.error_count) / metrics.total_requests
        )
        
        logger.debug(
            f"Performance update - {api.value}: {metrics.success_rate:.2f} success rate, "
            f"{metrics.avg_response_time:.2f}s avg response"
        )
    
    def get_performance_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary of performance metrics"""
        return {
            api.value: {
                'success_rate': metrics.success_rate,
                'avg_response_time': metrics.avg_response_time,
                'error_count': metrics.error_count,
                'total_requests': metrics.total_requests,
                'last_success': metrics.last_success,
                'last_failure': metrics.last_failure
            }
            for api, metrics in self.performance_metrics.items()
        }
    
    def _is_api_supported(self, operation: OperationType, api: APIType) -> bool:
        """Check if API supports the operation"""
        primary, fallback = self.OPERATION_MATRIX.get(operation, (None, None))
        return api in (primary, fallback)
    
    def _get_fallback_api(
        self, 
        operation: OperationType, 
        primary: APIType
    ) -> Optional[APIType]:
        """Get fallback API for operation"""
        matrix_primary, matrix_fallback = self.OPERATION_MATRIX.get(
            operation, (None, None)
        )
        
        if primary == matrix_primary:
            return matrix_fallback
        elif primary == matrix_fallback:
            return matrix_primary
        else:
            # If primary is not in matrix, return matrix primary as fallback
            return matrix_primary
    
    def _is_bulk_operation(self, context: OperationContext) -> bool:
        """Detect if operation is bulk/batch"""
        params = context.params
        
        # Check for common bulk indicators
        bulk_indicators = [
            params.get('limit', 0) > 100,
            params.get('batch_size', 0) > 1,
            'bulk' in str(params).lower(),
            'batch' in str(params).lower(),
        ]
        
        return any(bulk_indicators)
    
    def _is_metadata_operation(self, operation: OperationType) -> bool:
        """Check if operation is metadata-related"""
        metadata_ops = {
            OperationType.GET_DIMENSIONS,
            OperationType.GET_METRICS,
            OperationType.GET_DIMENSION_VALUES
        }
        return operation in metadata_ops
    
    def _parse_api_preference(self, preference: Any) -> Optional[APIType]:
        """Parse API preference from configuration"""
        if not preference:
            return None
        
        preference_str = str(preference).lower()
        if preference_str in ('rest', 'rest_api'):
            return APIType.REST
        elif preference_str in ('soap', 'soap_api'):
            return APIType.SOAP
        
        return None