"""
Unified Google Ad Manager Client

This module provides a unified interface that intelligently selects between
SOAP and REST APIs based on operation type, with automatic fallback and
retry mechanisms.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass

from ..adapters.base import APIAdapter
from ..adapters.soap.soap_adapter import SOAPAdapter
from ..adapters.rest.rest_adapter import RESTAdapter
from ..config import Config, UnifiedClientConfig
from ..exceptions import (
    APIError, AuthenticationError, ConfigurationError,
    InvalidRequestError
)
from .strategy import (
    APISelectionStrategy, APIType, OperationType, 
    OperationContext, PerformanceMetrics
)
from .fallback import FallbackManager, RetryConfig


logger = logging.getLogger(__name__)


@dataclass
class UnifiedClientConfig:
    """Configuration for unified client behavior"""
    api_preference: Optional[str] = None
    enable_fallback: bool = True
    enable_performance_tracking: bool = True
    performance_threshold: float = 0.8
    complexity_threshold: int = 10
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: float = 60.0
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_multiplier: float = 2.0


class GAMUnifiedClient:
    """
    Unified Google Ad Manager Client with intelligent API selection.
    
    This client automatically chooses between SOAP and REST APIs based on:
    - Operation type and capabilities
    - Performance metrics and reliability
    - Configuration preferences
    - Context-specific rules (complexity, bulk operations, etc.)
    
    Features:
    - Smart API selection with fallback support
    - Automatic retry with exponential backoff
    - Performance tracking and optimization
    - Circuit breaker protection
    - Comprehensive error handling and aggregation
    - Context preservation across retry attempts
    """
    
    def __init__(
        self, 
        config: Optional[Union[Dict[str, Any], Config]] = None,
        unified_config: Optional[UnifiedClientConfig] = None
    ):
        """
        Initialize unified GAM client.
        
        Args:
            config: GAM API configuration (credentials, network code, etc.)
            unified_config: Unified client behavior configuration
        """
        # Load and validate configuration
        if isinstance(config, dict):
            # For dict config, we'll store it directly and use it as needed
            self.config_dict = config
            # Create a minimal config object for compatibility
            from types import SimpleNamespace
            self.config = SimpleNamespace(
                auth=SimpleNamespace(**config.get('auth', {})),
                api=SimpleNamespace(**config.get('api', {})),
                cache=SimpleNamespace(**config.get('cache', {})),
                logging=SimpleNamespace(**config.get('logging', {})),
                defaults=SimpleNamespace(**config.get('defaults', {})),
                unified=unified_config or UnifiedClientConfig(),
                to_dict=lambda: self.config_dict
            )
        elif hasattr(config, 'to_dict'):
            self.config = config
            self.config_dict = config.to_dict()
        else:
            from ..config import load_config
            self.config = load_config()
            self.config_dict = self.config.to_dict() if self.config else {}
        
        self.unified_config = unified_config or UnifiedClientConfig()
        
        # Initialize API adapters
        self._soap_adapter: Optional[SOAPAdapter] = None
        self._rest_adapter: Optional[RESTAdapter] = None
        
        # Initialize strategy and fallback managers
        strategy_config = self._build_strategy_config()
        self.strategy = APISelectionStrategy(strategy_config)
        
        fallback_config = self._build_fallback_config()
        self.fallback_manager = FallbackManager(fallback_config)
        
        # Track client metrics
        self.client_metrics = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'fallback_operations': 0,
            'api_usage': {api.value: 0 for api in APIType},
            'operation_usage': {op.value: 0 for op in OperationType},
            'avg_response_time': 0.0,
            'start_time': time.time()
        }
        
        # Validate configuration and adapters
        self._validate_configuration()
        
        logger.info(
            f"GAMUnifiedClient initialized with preference: {self.unified_config.api_preference}"
        )
    
    @property
    def network_code(self) -> str:
        """Get the network code from configuration"""
        return self.config.auth.network_code
    
    @property
    def has_soap(self) -> bool:
        """Check if SOAP adapter is available"""
        try:
            return self.soap_adapter is not None
        except Exception:
            return False
    
    @property
    def has_rest(self) -> bool:
        """Check if REST adapter is available"""
        try:
            return self.rest_adapter is not None
        except Exception:
            return False
    
    @property
    def soap_adapter(self) -> Optional[SOAPAdapter]:
        """Get or create SOAP adapter with graceful error handling"""
        if self._soap_adapter is None:
            try:
                self._soap_adapter = SOAPAdapter(self.config_dict)
                logger.info("SOAP adapter initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize SOAP adapter: {e}")
                logger.info("SOAP operations will not be available")
                # Don't set _soap_adapter to prevent repeated initialization attempts
        return self._soap_adapter
    
    @property
    def rest_adapter(self) -> Optional[RESTAdapter]:
        """Get or create REST adapter with graceful error handling"""
        if self._rest_adapter is None:
            try:
                self._rest_adapter = RESTAdapter(self.config_dict)
                logger.info("REST adapter initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize REST adapter: {e}")
                logger.info("REST operations will not be available")
                # Don't set _rest_adapter to prevent repeated initialization attempts
        return self._rest_adapter
    
    # Core unified methods
    
    async def execute_operation(
        self,
        operation: OperationType,
        method_name: str,
        **kwargs
    ) -> Any:
        """
        Execute an operation with intelligent API selection and fallback.
        
        Args:
            operation: Type of operation being performed
            method_name: Name of the method to call on the adapter
            **kwargs: Arguments to pass to the method
            
        Returns:
            Result from the API call
        """
        start_time = time.time()
        self.client_metrics['total_operations'] += 1
        self.client_metrics['operation_usage'][operation.value] += 1
        
        try:
            # Create operation context
            context = OperationContext(
                operation=operation,
                params=kwargs,
                complexity_score=self._calculate_complexity_score(kwargs),
                user_preference=self._parse_user_preference(kwargs.pop('api_preference', None))
            )
            
            # Select APIs using strategy
            primary_api, fallback_api = self.strategy.select_api(context)
            
            logger.debug(
                f"Executing {operation.value} with primary: {primary_api.value}, "
                f"fallback: {fallback_api.value if fallback_api else None}"
            )
            
            # Get adapter methods
            primary_adapter = self._get_adapter(primary_api)
            fallback_adapter = self._get_adapter(fallback_api) if fallback_api else None
            
            # Check adapter availability
            if primary_adapter is None and fallback_adapter is None:
                raise APIError(
                    f"No adapters available for operation {operation.value}. "
                    "Please check your authentication configuration."
                )
            elif primary_adapter is None and fallback_adapter:
                # Switch to fallback if primary not available
                logger.warning(
                    f"Primary adapter {primary_api.value} not available, using {fallback_api.value}"
                )
                primary_adapter, fallback_adapter = fallback_adapter, None
                primary_api, fallback_api = fallback_api, None
            
            primary_method = getattr(primary_adapter, method_name, None) if primary_adapter else None
            fallback_method = getattr(fallback_adapter, method_name, None) if fallback_adapter else None
            
            if not primary_method:
                raise InvalidRequestError(
                    f"Method {method_name} not available on {primary_api.value} adapter"
                )
            
            # Execute with fallback
            result = await self.fallback_manager.execute_with_fallback(
                primary_api=primary_api,
                fallback_api=fallback_api,
                operation=operation,
                primary_func=lambda: primary_method(**kwargs),
                fallback_func=lambda: fallback_method(**kwargs) if fallback_method else None,
                params=kwargs
            )
            
            # Record success metrics
            response_time = time.time() - start_time
            self.client_metrics['successful_operations'] += 1
            self.client_metrics['api_usage'][primary_api.value] += 1
            self._update_response_time(response_time)
            
            # Record performance for strategy optimization
            self.strategy.record_performance(
                api=primary_api,
                operation=operation,
                success=True,
                response_time=response_time
            )
            
            logger.debug(
                f"Operation {operation.value} completed successfully in {response_time:.2f}s"
            )
            
            return result
            
        except Exception as error:
            # Record failure metrics
            response_time = time.time() - start_time
            self.client_metrics['failed_operations'] += 1
            self._update_response_time(response_time)
            
            # Record performance for strategy optimization
            used_api = getattr(error, 'api_used', primary_api)
            self.strategy.record_performance(
                api=used_api,
                operation=operation,
                success=False,
                response_time=response_time,
                error=error
            )
            
            logger.error(
                f"Operation {operation.value} failed after {response_time:.2f}s: {error}"
            )
            
            raise error
    
    # Report Operations
    
    async def create_report(self, report_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new report job"""
        return await self.execute_operation(
            OperationType.CREATE_REPORT,
            'create_report',
            report_definition=report_definition
        )
    
    async def get_report(self, report_id: str) -> Dict[str, Any]:
        """Get report information"""
        return await self.execute_operation(
            OperationType.GET_REPORT,
            'get_report',
            report_id=report_id
        )
    
    async def list_reports(self, **filters) -> List[Dict[str, Any]]:
        """List available reports"""
        return await self.execute_operation(
            OperationType.LIST_REPORTS,
            'get_reports',
            **filters
        )
    
    async def get_report_status(self, report_id: str) -> str:
        """Get report status"""
        return await self.execute_operation(
            OperationType.GET_REPORT_STATUS,
            'get_report_status',
            report_id=report_id
        )
    
    async def download_report(self, report_id: str, format: str = 'CSV') -> Union[str, bytes]:
        """Download report results"""
        return await self.execute_operation(
            OperationType.DOWNLOAD_REPORT,
            'download_report',
            report_id=report_id,
            format=format
        )
    
    async def delete_report(self, report_id: str) -> bool:
        """Delete a report"""
        return await self.execute_operation(
            OperationType.DELETE_REPORT,
            'delete_report',
            report_id=report_id
        )

    async def run_report(self, report_id: str, date_override: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run an existing report.

        Args:
            report_id: Report ID or resource name
            date_override: Optional date range override

        Returns:
            Operation result with execution status
        """
        return await self.execute_operation(
            OperationType.RUN_REPORT,
            'run_report',
            report_name=report_id
        )

    async def update_report(self, report_id: str, update_body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing report.

        Args:
            report_id: Report ID or resource name
            update_body: Fields to update

        Returns:
            Updated report data
        """
        return await self.execute_operation(
            OperationType.UPDATE_REPORT,
            'update_report',
            report_id=report_id,
            update_body=update_body
        )
    
    # Line Item Operations
    
    async def get_line_items(self, **filters) -> List[Dict[str, Any]]:
        """Get line items with filtering"""
        return await self.execute_operation(
            OperationType.GET_LINE_ITEMS,
            'get_line_items',
            **filters
        )
    
    async def create_line_item(self, line_item: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new line item"""
        return await self.execute_operation(
            OperationType.CREATE_LINE_ITEM,
            'create_line_item',
            line_item_config=line_item
        )
    
    async def update_line_item(self, line_item_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing line item"""
        return await self.execute_operation(
            OperationType.UPDATE_LINE_ITEM,
            'update_line_item',
            line_item_id=line_item_id,
            updates=updates
        )
    
    async def delete_line_item(self, line_item_id: str) -> bool:
        """Delete a line item"""
        return await self.execute_operation(
            OperationType.DELETE_LINE_ITEM,
            'delete_line_item',
            line_item_id=line_item_id
        )
    
    # Inventory Operations
    
    async def get_ad_units(self, **filters) -> List[Dict[str, Any]]:
        """Get ad units with filtering"""
        return await self.execute_operation(
            OperationType.GET_AD_UNITS,
            'get_inventory',
            inventory_type='AD_UNITS',
            **filters
        )
    
    async def create_ad_unit(self, ad_unit: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new ad unit"""
        return await self.execute_operation(
            OperationType.CREATE_AD_UNIT,
            'create_ad_unit',
            ad_unit_config=ad_unit
        )
    
    # Metadata Operations
    
    async def get_dimensions(self) -> List[str]:
        """Get available report dimensions"""
        return await self.execute_operation(
            OperationType.GET_DIMENSIONS,
            'get_dimensions'
        )
    
    async def get_metrics(self) -> List[str]:
        """Get available report metrics"""
        return await self.execute_operation(
            OperationType.GET_METRICS,
            'get_metrics'
        )
    
    async def get_dimension_values(self, dimension: str, **filters) -> List[str]:
        """Get available values for a dimension"""
        return await self.execute_operation(
            OperationType.GET_DIMENSION_VALUES,
            'get_dimension_values',
            dimension=dimension,
            **filters
        )
    
    # Network Operations
    
    async def get_network_info(self) -> Dict[str, Any]:
        """Get network information"""
        return await self.execute_operation(
            OperationType.GET_NETWORK_INFO,
            'get_network_info'
        )
    
    async def test_connection(self) -> bool:
        """Test API connectivity"""
        return await self.execute_operation(
            OperationType.TEST_CONNECTION,
            'test_connection'
        )
    
    # Synchronous wrapper methods
    
    def create_report_sync(self, report_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous version of create_report"""
        return asyncio.run(self.create_report(report_definition))
    
    def get_report_sync(self, report_id: str) -> Dict[str, Any]:
        """Synchronous version of get_report"""
        return asyncio.run(self.get_report(report_id))
    
    def list_reports_sync(self, **filters) -> List[Dict[str, Any]]:
        """Synchronous version of list_reports"""
        return asyncio.run(self.list_reports(**filters))
    
    def get_line_items_sync(self, **filters) -> List[Dict[str, Any]]:
        """Synchronous version of get_line_items"""
        return asyncio.run(self.get_line_items(**filters))

    def test_connection_sync(self) -> bool:
        """Synchronous version of test_connection"""
        return asyncio.run(self.test_connection())

    def run_report_sync(self, report_id: str, date_override: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Synchronous version of run_report"""
        return asyncio.run(self.run_report(report_id, date_override))

    def update_report_sync(self, report_id: str, update_body: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous version of update_report"""
        return asyncio.run(self.update_report(report_id, update_body))
    
    # Management and Monitoring
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        strategy_stats = self.strategy.get_performance_summary()
        fallback_stats = self.fallback_manager.get_fallback_stats()
        
        return {
            'client_metrics': self.client_metrics.copy(),
            'strategy_performance': strategy_stats,
            'fallback_statistics': fallback_stats,
            'uptime': time.time() - self.client_metrics['start_time']
        }
    
    def reset_performance_stats(self):
        """Reset all performance statistics"""
        self.client_metrics = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'fallback_operations': 0,
            'api_usage': {api.value: 0 for api in APIType},
            'operation_usage': {op.value: 0 for op in OperationType},
            'avg_response_time': 0.0,
            'start_time': time.time()
        }
        self.strategy = APISelectionStrategy(self._build_strategy_config())
        self.fallback_manager.reset_stats()
    
    def configure_api_preference(self, preference: Optional[str], operation: Optional[str] = None):
        """
        Configure API preference globally or for specific operations.
        
        Args:
            preference: 'soap', 'rest', or None for auto-selection
            operation: Specific operation name, or None for global preference
        """
        if operation:
            # TODO: Implement per-operation preferences
            logger.warning("Per-operation preferences not yet implemented")
        else:
            self.unified_config.api_preference = preference
            self.strategy.global_preference = self.strategy._parse_api_preference(preference)
            logger.info(f"Global API preference set to: {preference}")
    
    # Helper methods
    
    def _get_adapter(self, api_type: Optional[APIType]) -> Optional[APIAdapter]:
        """Get adapter instance for API type with availability check"""
        if api_type == APIType.SOAP:
            adapter = self.soap_adapter
            if adapter is None:
                logger.warning("SOAP adapter requested but not available")
            return adapter
        elif api_type == APIType.REST:
            adapter = self.rest_adapter
            if adapter is None:
                logger.warning("REST adapter requested but not available")
            return adapter
        return None
    
    def _calculate_complexity_score(self, params: Dict[str, Any]) -> int:
        """Calculate complexity score for operation context"""
        score = 0
        
        # Check common complexity indicators
        if 'filters' in params:
            filters = params['filters']
            if isinstance(filters, (list, tuple)):
                score += len(filters)
            elif isinstance(filters, dict):
                score += len(filters)
        
        if 'limit' in params:
            limit = params.get('limit', 0)
            if limit > 1000:
                score += 5
            elif limit > 100:
                score += 2
        
        if 'batch_size' in params:
            batch_size = params.get('batch_size', 0)
            score += batch_size // 10
        
        # Check for bulk operation indicators
        bulk_indicators = ['bulk', 'batch', 'mass']
        for key, value in params.items():
            if any(indicator in str(key).lower() or indicator in str(value).lower() 
                   for indicator in bulk_indicators):
                score += 3
        
        return score
    
    def _parse_user_preference(self, preference: Any) -> Optional[APIType]:
        """Parse user API preference from request"""
        if not preference:
            return None
        
        preference_str = str(preference).lower()
        if preference_str in ('rest', 'rest_api'):
            return APIType.REST
        elif preference_str in ('soap', 'soap_api'):
            return APIType.SOAP
        
        return None
    
    def _build_strategy_config(self) -> Dict[str, Any]:
        """Build configuration for API selection strategy"""
        return {
            'api_preference': self.unified_config.api_preference,
            'enable_performance_tracking': self.unified_config.enable_performance_tracking,
            'performance_threshold': self.unified_config.performance_threshold,
            'complexity_threshold': self.unified_config.complexity_threshold
        }
    
    def _build_fallback_config(self) -> Dict[str, Any]:
        """Build configuration for fallback manager"""
        return {
            'circuit_breaker_threshold': self.unified_config.circuit_breaker_threshold,
            'circuit_breaker_timeout': self.unified_config.circuit_breaker_timeout,
            'max_retries': self.unified_config.max_retries,
            'base_delay': self.unified_config.base_delay,
            'max_delay': self.unified_config.max_delay,
            'backoff_multiplier': self.unified_config.backoff_multiplier
        }
    
    def _update_response_time(self, response_time: float):
        """Update average response time metric"""
        total_ops = self.client_metrics['total_operations']
        current_avg = self.client_metrics['avg_response_time']
        
        # Calculate moving average
        self.client_metrics['avg_response_time'] = (
            (current_avg * (total_ops - 1) + response_time) / total_ops
        )
    
    def _validate_configuration(self):
        """Validate configuration and check adapter availability"""
        errors = []
        warnings = []
        
        # Check required configuration fields
        if not hasattr(self.config, 'auth') or not hasattr(self.config.auth, 'network_code'):
            errors.append("Missing required configuration: auth.network_code")
        elif not self.config.auth.network_code or self.config.auth.network_code == 'YOUR_NETWORK_CODE_HERE':
            errors.append("Network code not configured (found placeholder value)")
        
        # Check authentication credentials
        auth_config = getattr(self.config, 'auth', None)
        if auth_config:
            if not hasattr(auth_config, 'client_id') or not auth_config.client_id or auth_config.client_id == 'YOUR_CLIENT_ID_HERE':
                warnings.append("Client ID not configured - OAuth2 authentication will not work")
            if not hasattr(auth_config, 'client_secret') or not auth_config.client_secret or auth_config.client_secret == 'YOUR_CLIENT_SECRET_HERE':
                warnings.append("Client secret not configured - OAuth2 authentication will not work")
            if not hasattr(auth_config, 'refresh_token') or not auth_config.refresh_token or auth_config.refresh_token == 'YOUR_REFRESH_TOKEN_HERE':
                warnings.append("Refresh token not configured - OAuth2 authentication will not work")
        
        # Test adapter availability
        soap_available = False
        rest_available = False
        
        try:
            if self.soap_adapter is not None:
                soap_available = True
        except Exception as e:
            warnings.append(f"SOAP adapter not available: {e}")
        
        try:
            if self.rest_adapter is not None:
                rest_available = True
        except Exception as e:
            warnings.append(f"REST adapter not available: {e}")
        
        # Check if at least one adapter is available
        if not soap_available and not rest_available:
            errors.append("No API adapters available - check authentication configuration")
        elif not soap_available:
            warnings.append("SOAP adapter not available - some operations may not work")
        elif not rest_available:
            warnings.append("REST adapter not available - some operations may not work")
        
        # Log validation results
        if errors:
            for error in errors:
                logger.error(f"Configuration error: {error}")
            raise ConfigurationError(
                f"Configuration validation failed:\n" + "\n".join(f"- {e}" for e in errors)
            )
        
        if warnings:
            for warning in warnings:
                logger.warning(f"Configuration warning: {warning}")
        
        # Log adapter availability
        logger.info(f"Adapter availability - SOAP: {soap_available}, REST: {rest_available}")
        
        # Adjust preference if necessary
        if self.unified_config.api_preference == 'soap' and not soap_available:
            logger.warning("SOAP preference set but SOAP not available - will use REST")
            self.unified_config.api_preference = 'rest'
        elif self.unified_config.api_preference == 'rest' and not rest_available:
            logger.warning("REST preference set but REST not available - will use SOAP")
            self.unified_config.api_preference = 'soap'
    
    # Context manager support
    
    def __enter__(self):
        """Enter context manager"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager"""
        # Clean up resources if needed
        if self._soap_adapter:
            # SOAP adapter cleanup
            pass
        if self._rest_adapter:
            # REST adapter cleanup  
            pass


# Factory function for easy instantiation
def create_unified_client(
    config_path: Optional[str] = None,
    api_preference: Optional[str] = None,
    **unified_options
) -> GAMUnifiedClient:
    """
    Factory function to create a unified GAM client.
    
    Args:
        config_path: Path to configuration file
        api_preference: Default API preference ('soap', 'rest', or None)
        **unified_options: Additional unified client options
        
    Returns:
        Configured GAMUnifiedClient instance
    """
    from ..config import load_config
    
    config = load_config(config_path)
    
    unified_config = UnifiedClientConfig(
        api_preference=api_preference,
        **unified_options
    )
    
    return GAMUnifiedClient(config, unified_config)