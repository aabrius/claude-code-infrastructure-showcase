"""
Unit tests for the API Selection Strategy.

Tests cover:
- Operation matrix mapping
- Context-based API selection
- Performance-based decisions
- User preference handling
- Fallback determination
"""

import pytest
from unittest.mock import Mock, patch
import time

try:
    from src.core.unified.strategy import (
        APISelectionStrategy, APIType, OperationType, 
        OperationContext, PerformanceMetrics
    )
except ImportError as e:
    pytest.skip(f"Strategy dependencies not available: {e}", allow_module_level=True)


class TestAPISelectionStrategy:
    """Test the API selection strategy logic"""
    
    @pytest.fixture
    def strategy(self):
        """Create a strategy instance with default config"""
        return APISelectionStrategy()
    
    def test_default_operation_mapping(self, strategy):
        """Test default API preferences for different operations"""
        # Reports should prefer REST
        context = OperationContext(
            operation=OperationType.CREATE_REPORT,
            params={}
        )
        primary, fallback = strategy.select_api(context)
        assert primary == APIType.REST
        assert fallback == APIType.SOAP
        
        # Line items should use SOAP only
        context = OperationContext(
            operation=OperationType.GET_LINE_ITEMS,
            params={}
        )
        primary, fallback = strategy.select_api(context)
        assert primary == APIType.SOAP
        assert fallback is None
        
        # Metadata should prefer REST
        context = OperationContext(
            operation=OperationType.GET_DIMENSIONS,
            params={}
        )
        primary, fallback = strategy.select_api(context)
        assert primary == APIType.REST
        assert fallback == APIType.SOAP
    
    def test_user_preference_override(self, strategy):
        """Test user preference overrides default selection"""
        context = OperationContext(
            operation=OperationType.CREATE_REPORT,
            params={},
            user_preference=APIType.SOAP
        )
        
        primary, fallback = strategy.select_api(context)
        assert primary == APIType.SOAP
        assert fallback == APIType.REST
    
    def test_global_preference(self):
        """Test global API preference configuration"""
        config = {'api_preference': 'soap'}
        strategy = APISelectionStrategy(config)
        
        context = OperationContext(
            operation=OperationType.CREATE_REPORT,
            params={}
        )
        
        primary, fallback = strategy.select_api(context)
        assert primary == APIType.SOAP
        assert fallback == APIType.REST
    
    def test_complexity_based_selection(self, strategy):
        """Test high complexity operations prefer SOAP"""
        # High complexity score
        context = OperationContext(
            operation=OperationType.CREATE_REPORT,
            params={},
            complexity_score=15  # Above threshold
        )
        
        primary, fallback = strategy.select_api(context)
        assert primary == APIType.SOAP
        assert fallback == APIType.REST
    
    def test_bulk_operation_detection(self, strategy):
        """Test bulk operations prefer SOAP"""
        # Simulate bulk operation
        with patch.object(strategy, '_is_bulk_operation', return_value=True):
            context = OperationContext(
                operation=OperationType.CREATE_REPORT,
                params={'limit': 1000}
            )
            
            primary, fallback = strategy.select_api(context)
            assert primary == APIType.SOAP
    
    def test_metadata_operation_preference(self, strategy):
        """Test metadata operations always prefer REST"""
        # Even with high complexity, metadata should use REST
        context = OperationContext(
            operation=OperationType.GET_METRICS,
            params={},
            complexity_score=20
        )
        
        primary, fallback = strategy.select_api(context)
        assert primary == APIType.REST
        assert fallback == APIType.SOAP


class TestPerformanceTracking:
    """Test performance-based API selection"""
    
    @pytest.fixture
    def strategy(self):
        """Create strategy with performance tracking enabled"""
        config = {
            'enable_performance_tracking': True,
            'performance_threshold': 0.8
        }
        return APISelectionStrategy(config)
    
    def test_record_performance_success(self, strategy):
        """Test recording successful operation performance"""
        strategy.record_performance(
            api=APIType.REST,
            operation=OperationType.CREATE_REPORT,
            success=True,
            response_time=1.5
        )
        
        metrics = strategy.performance_metrics[APIType.REST]
        assert metrics.total_requests == 1
        assert metrics.success_rate == 1.0
        assert metrics.avg_response_time == 1.5
        assert metrics.error_count == 0
    
    def test_record_performance_failure(self, strategy):
        """Test recording failed operation performance"""
        strategy.record_performance(
            api=APIType.REST,
            operation=OperationType.CREATE_REPORT,
            success=False,
            response_time=0.5,
            error=Exception("API Error")
        )
        
        metrics = strategy.performance_metrics[APIType.REST]
        assert metrics.total_requests == 1
        assert metrics.success_rate == 0.0
        assert metrics.error_count == 1
    
    def test_performance_based_switching(self, strategy):
        """Test switching APIs based on poor performance"""
        # Record multiple failures for REST
        for _ in range(10):
            strategy.record_performance(
                api=APIType.REST,
                operation=OperationType.CREATE_REPORT,
                success=False,
                response_time=0.1
            )
        
        # Record good performance for SOAP
        for _ in range(5):
            strategy.record_performance(
                api=APIType.SOAP,
                operation=OperationType.CREATE_REPORT,
                success=True,
                response_time=2.0
            )
        
        # Now REST should not be selected due to poor performance
        context = OperationContext(
            operation=OperationType.CREATE_REPORT,
            params={}
        )
        
        primary, fallback = strategy.select_api(context)
        # Should switch to SOAP due to REST's poor performance
        assert primary == APIType.SOAP
    
    def test_performance_summary(self, strategy):
        """Test getting performance summary"""
        # Record some metrics
        strategy.record_performance(
            api=APIType.REST,
            operation=OperationType.CREATE_REPORT,
            success=True,
            response_time=1.0
        )
        strategy.record_performance(
            api=APIType.SOAP,
            operation=OperationType.GET_LINE_ITEMS,
            success=True,
            response_time=2.0
        )
        
        summary = strategy.get_performance_summary()
        
        assert 'rest' in summary
        assert 'soap' in summary
        assert summary['rest']['success_rate'] == 1.0
        assert summary['soap']['success_rate'] == 1.0


class TestContextRules:
    """Test context-based decision rules"""
    
    @pytest.fixture
    def strategy(self):
        """Create strategy instance"""
        return APISelectionStrategy()
    
    def test_parse_api_preference(self, strategy):
        """Test parsing API preference strings"""
        assert strategy._parse_api_preference('rest') == APIType.REST
        assert strategy._parse_api_preference('REST') == APIType.REST
        assert strategy._parse_api_preference('rest_api') == APIType.REST
        assert strategy._parse_api_preference('soap') == APIType.SOAP
        assert strategy._parse_api_preference('SOAP') == APIType.SOAP
        assert strategy._parse_api_preference('soap_api') == APIType.SOAP
        assert strategy._parse_api_preference('invalid') is None
        assert strategy._parse_api_preference(None) is None
    
    def test_is_api_supported(self, strategy):
        """Test checking if operation is supported by API"""
        # Reports supported by both
        assert strategy._is_api_supported(OperationType.CREATE_REPORT, APIType.REST)
        assert strategy._is_api_supported(OperationType.CREATE_REPORT, APIType.SOAP)
        
        # Line items only supported by SOAP
        assert strategy._is_api_supported(OperationType.GET_LINE_ITEMS, APIType.SOAP)
        assert not strategy._is_api_supported(OperationType.GET_LINE_ITEMS, APIType.REST)
    
    def test_get_fallback_api(self, strategy):
        """Test getting fallback API for operations"""
        # Report operations
        assert strategy._get_fallback_api(OperationType.CREATE_REPORT, APIType.REST) == APIType.SOAP
        assert strategy._get_fallback_api(OperationType.CREATE_REPORT, APIType.SOAP) == APIType.REST
        
        # Line item operations (no fallback)
        assert strategy._get_fallback_api(OperationType.GET_LINE_ITEMS, APIType.SOAP) is None
    
    def test_is_bulk_operation(self, strategy):
        """Test bulk operation detection"""
        # High limit indicates bulk
        context = OperationContext(
            operation=OperationType.CREATE_REPORT,
            params={'limit': 500}
        )
        assert strategy._is_bulk_operation(context)
        
        # Batch size indicates bulk
        context = OperationContext(
            operation=OperationType.CREATE_REPORT,
            params={'batch_size': 50}
        )
        assert strategy._is_bulk_operation(context)
        
        # Keywords indicate bulk
        context = OperationContext(
            operation=OperationType.CREATE_REPORT,
            params={'bulk_update': True}
        )
        assert strategy._is_bulk_operation(context)
        
        # Normal operation
        context = OperationContext(
            operation=OperationType.CREATE_REPORT,
            params={'name': 'Test Report'}
        )
        assert not strategy._is_bulk_operation(context)
    
    def test_is_metadata_operation(self, strategy):
        """Test metadata operation detection"""
        assert strategy._is_metadata_operation(OperationType.GET_DIMENSIONS)
        assert strategy._is_metadata_operation(OperationType.GET_METRICS)
        assert strategy._is_metadata_operation(OperationType.GET_DIMENSION_VALUES)
        assert not strategy._is_metadata_operation(OperationType.CREATE_REPORT)
        assert not strategy._is_metadata_operation(OperationType.GET_LINE_ITEMS)


class TestEdgeCases:
    """Test edge cases and error scenarios"""
    
    def test_unsupported_operation(self):
        """Test handling of operations not in matrix"""
        strategy = APISelectionStrategy()
        
        # Create a mock operation not in matrix
        mock_operation = Mock()
        mock_operation.value = 'UNKNOWN_OPERATION'
        
        context = OperationContext(
            operation=mock_operation,
            params={}
        )
        
        # Should use default (REST, SOAP)
        primary, fallback = strategy.select_api(context)
        assert primary == APIType.REST
        assert fallback == APIType.SOAP
    
    def test_disabled_performance_tracking(self):
        """Test behavior when performance tracking is disabled"""
        config = {'enable_performance_tracking': False}
        strategy = APISelectionStrategy(config)
        
        # Record performance (should be ignored)
        strategy.record_performance(
            api=APIType.REST,
            operation=OperationType.CREATE_REPORT,
            success=False,
            response_time=1.0
        )
        
        # Metrics should not be updated
        metrics = strategy.performance_metrics[APIType.REST]
        assert metrics.total_requests == 0
        assert metrics.success_rate == 1.0