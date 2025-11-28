"""
Unit tests for the GAMUnifiedClient with intelligent API selection.

Tests cover:
- Configuration validation and error handling
- Adapter initialization with graceful degradation
- API selection strategy
- Fallback mechanisms
- Performance tracking
- Error scenarios
"""

import pytest
import asyncio
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from typing import Dict, Any

try:
    from src.core.unified import GAMUnifiedClient, UnifiedClientConfig
    from src.core.unified.strategy import APIType, OperationType, APISelectionStrategy
    from src.core.unified.fallback import FallbackManager
    from src.core.exceptions import (
        APIError, ConfigurationError, InvalidRequestError, 
        AuthenticationError, QuotaExceededError
    )
    from src.core.adapters.soap.soap_adapter import SOAPAdapter
    from src.core.adapters.rest.rest_adapter import RESTAdapter
except ImportError as e:
    pytest.skip(f"Unified client dependencies not available: {e}", allow_module_level=True)


class TestUnifiedClientInitialization:
    """Test client initialization and configuration validation"""
    
    def test_init_with_valid_config(self):
        """Test initialization with valid configuration"""
        config = {
            'auth': {
                'network_code': '123456',
                'client_id': 'test-client-id',
                'client_secret': 'test-secret',
                'refresh_token': 'test-token'
            },
            'api': {'prefer_rest': True},
            'cache': {'enabled': True},
            'defaults': {'days_back': 30}
        }
        
        with patch('src.core.unified.client.SOAPAdapter'), \
             patch('src.core.unified.client.RESTAdapter'):
            client = GAMUnifiedClient(config)
            
            assert client.network_code == '123456'
            assert client.unified_config.api_preference is None
            assert isinstance(client.strategy, APISelectionStrategy)
            assert isinstance(client.fallback_manager, FallbackManager)
    
    def test_init_with_placeholder_credentials(self):
        """Test initialization with placeholder credentials shows warnings"""
        config = {
            'auth': {
                'network_code': 'YOUR_NETWORK_CODE_HERE',
                'client_id': 'YOUR_CLIENT_ID_HERE',
                'client_secret': 'YOUR_CLIENT_SECRET_HERE',
                'refresh_token': 'YOUR_REFRESH_TOKEN_HERE'
            }
        }
        
        with pytest.raises(ConfigurationError) as exc_info:
            client = GAMUnifiedClient(config)
        
        assert "Network code not configured" in str(exc_info.value)
    
    def test_init_with_missing_network_code(self):
        """Test initialization fails without network code"""
        config = {
            'auth': {
                'client_id': 'test-client',
                'client_secret': 'test-secret',
                'refresh_token': 'test-token'
            }
        }
        
        with pytest.raises(ConfigurationError) as exc_info:
            client = GAMUnifiedClient(config)
        
        assert "auth.network_code" in str(exc_info.value)
    
    def test_init_with_unified_config(self):
        """Test initialization with custom unified config"""
        config = {
            'auth': {'network_code': '123456'}
        }
        
        unified_config = UnifiedClientConfig(
            api_preference='soap',
            max_retries=5,
            enable_fallback=False
        )
        
        with patch('src.core.unified.client.SOAPAdapter'), \
             patch('src.core.unified.client.RESTAdapter'):
            client = GAMUnifiedClient(config, unified_config)
            
            assert client.unified_config.api_preference == 'soap'
            assert client.unified_config.max_retries == 5
            assert client.unified_config.enable_fallback is False


class TestAdapterInitialization:
    """Test adapter initialization and graceful degradation"""
    
    def test_soap_adapter_initialization_failure(self):
        """Test graceful handling of SOAP adapter initialization failure"""
        config = {
            'auth': {'network_code': '123456'}
        }
        
        with patch('src.core.unified.client.SOAPAdapter') as mock_soap:
            mock_soap.side_effect = Exception("SOAP init failed")
            
            with patch('src.core.unified.client.RESTAdapter'):
                client = GAMUnifiedClient(config)
                
                # Should not raise error
                assert client.soap_adapter is None
                assert not client.has_soap
    
    def test_rest_adapter_initialization_failure(self):
        """Test graceful handling of REST adapter initialization failure"""
        config = {
            'auth': {'network_code': '123456'}
        }
        
        with patch('src.core.unified.client.RESTAdapter') as mock_rest:
            mock_rest.side_effect = Exception("REST init failed")
            
            with patch('src.core.unified.client.SOAPAdapter'):
                client = GAMUnifiedClient(config)
                
                # Should not raise error
                assert client.rest_adapter is None
                assert not client.has_rest
    
    def test_both_adapters_fail(self):
        """Test error when both adapters fail to initialize"""
        config = {
            'auth': {'network_code': '123456'}
        }
        
        with patch('src.core.unified.client.SOAPAdapter') as mock_soap, \
             patch('src.core.unified.client.RESTAdapter') as mock_rest:
            mock_soap.side_effect = Exception("SOAP failed")
            mock_rest.side_effect = Exception("REST failed")
            
            with pytest.raises(ConfigurationError) as exc_info:
                client = GAMUnifiedClient(config)
            
            assert "No API adapters available" in str(exc_info.value)
    
    def test_preference_adjustment_when_adapter_unavailable(self):
        """Test API preference adjusts when preferred adapter not available"""
        config = {
            'auth': {'network_code': '123456'}
        }
        
        unified_config = UnifiedClientConfig(api_preference='soap')
        
        with patch('src.core.unified.client.SOAPAdapter') as mock_soap, \
             patch('src.core.unified.client.RESTAdapter'):
            mock_soap.side_effect = Exception("SOAP not available")
            
            client = GAMUnifiedClient(config, unified_config)
            
            # Preference should be adjusted to REST
            assert client.unified_config.api_preference == 'rest'


class TestAPISelection:
    """Test API selection and operation execution"""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock client with both adapters available"""
        config = {
            'auth': {'network_code': '123456'}
        }
        
        with patch('src.core.unified.client.SOAPAdapter') as mock_soap, \
             patch('src.core.unified.client.RESTAdapter') as mock_rest:
            
            # Create mock adapter instances
            soap_instance = MagicMock()
            rest_instance = MagicMock()
            
            mock_soap.return_value = soap_instance
            mock_rest.return_value = rest_instance
            
            client = GAMUnifiedClient(config)
            
            # Set up the adapter instances
            client._soap_adapter = soap_instance
            client._rest_adapter = rest_instance
            
            return client
    
    @pytest.mark.asyncio
    async def test_execute_operation_with_rest_preference(self, mock_client):
        """Test operation execution with REST preference"""
        # Set up mock method
        mock_client._rest_adapter.create_report = AsyncMock(
            return_value={'reportId': '123', 'status': 'PENDING'}
        )
        
        result = await mock_client.execute_operation(
            OperationType.CREATE_REPORT,
            'create_report',
            report_definition={'name': 'Test Report'}
        )
        
        assert result['reportId'] == '123'
        mock_client._rest_adapter.create_report.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_operation_with_soap_only(self, mock_client):
        """Test operation that only works with SOAP"""
        # Set up mock method
        mock_client._soap_adapter.get_line_items = AsyncMock(
            return_value=[{'id': '1', 'name': 'Line Item 1'}]
        )
        
        result = await mock_client.execute_operation(
            OperationType.GET_LINE_ITEMS,
            'get_line_items'
        )
        
        assert len(result) == 1
        assert result[0]['name'] == 'Line Item 1'
        mock_client._soap_adapter.get_line_items.assert_called_once()
    
    @pytest.mark.asyncio 
    async def test_execute_operation_with_fallback(self, mock_client):
        """Test fallback when primary adapter fails"""
        # Set up REST to fail, SOAP to succeed
        mock_client._rest_adapter.create_report = AsyncMock(
            side_effect=APIError("REST API failed")
        )
        mock_client._soap_adapter.create_report = AsyncMock(
            return_value={'reportId': '456', 'status': 'PENDING'}
        )
        
        result = await mock_client.execute_operation(
            OperationType.CREATE_REPORT,
            'create_report',
            report_definition={'name': 'Test Report'}
        )
        
        assert result['reportId'] == '456'
        mock_client._rest_adapter.create_report.assert_called_once()
        mock_client._soap_adapter.create_report.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_operation_no_adapters(self):
        """Test error when no adapters are available"""
        config = {
            'auth': {'network_code': '123456'}
        }
        
        with patch('src.core.unified.client.SOAPAdapter') as mock_soap, \
             patch('src.core.unified.client.RESTAdapter') as mock_rest:
            mock_soap.side_effect = Exception("SOAP failed")
            mock_rest.side_effect = Exception("REST failed")
            
            # Force creation despite errors
            with patch.object(GAMUnifiedClient, '_validate_configuration'):
                client = GAMUnifiedClient(config)
                client._soap_adapter = None
                client._rest_adapter = None
                
                with pytest.raises(APIError) as exc_info:
                    await client.execute_operation(
                        OperationType.CREATE_REPORT,
                        'create_report'
                    )
                
                assert "No adapters available" in str(exc_info.value)


class TestPerformanceTracking:
    """Test performance tracking and metrics"""
    
    @pytest.fixture
    def client(self):
        """Create client with mocked adapters"""
        config = {
            'auth': {'network_code': '123456'}
        }
        
        with patch('src.core.unified.client.SOAPAdapter'), \
             patch('src.core.unified.client.RESTAdapter'):
            return GAMUnifiedClient(config)
    
    def test_initial_metrics(self, client):
        """Test initial performance metrics"""
        metrics = client.get_performance_summary()
        
        assert metrics['client_metrics']['total_operations'] == 0
        assert metrics['client_metrics']['successful_operations'] == 0
        assert metrics['client_metrics']['failed_operations'] == 0
        assert all(count == 0 for count in metrics['client_metrics']['api_usage'].values())
    
    @pytest.mark.asyncio
    async def test_success_metrics_tracking(self, client):
        """Test metrics tracking for successful operations"""
        # Mock successful operation
        with patch.object(client, '_get_adapter') as mock_get_adapter:
            mock_adapter = MagicMock()
            mock_adapter.test_connection = AsyncMock(return_value=True)
            mock_get_adapter.return_value = mock_adapter
            
            await client.execute_operation(
                OperationType.TEST_CONNECTION,
                'test_connection'
            )
            
            metrics = client.get_performance_summary()
            assert metrics['client_metrics']['total_operations'] == 1
            assert metrics['client_metrics']['successful_operations'] == 1
            assert metrics['client_metrics']['failed_operations'] == 0
    
    @pytest.mark.asyncio
    async def test_failure_metrics_tracking(self, client):
        """Test metrics tracking for failed operations"""
        # Mock failed operation
        with patch.object(client, '_get_adapter') as mock_get_adapter:
            mock_adapter = MagicMock()
            mock_adapter.test_connection = AsyncMock(
                side_effect=APIError("Connection failed")
            )
            mock_get_adapter.return_value = mock_adapter
            
            with pytest.raises(APIError):
                await client.execute_operation(
                    OperationType.TEST_CONNECTION,
                    'test_connection'
                )
            
            metrics = client.get_performance_summary()
            assert metrics['client_metrics']['total_operations'] == 1
            assert metrics['client_metrics']['successful_operations'] == 0
            assert metrics['client_metrics']['failed_operations'] == 1
    
    def test_reset_performance_stats(self, client):
        """Test resetting performance statistics"""
        # Modify some metrics
        client.client_metrics['total_operations'] = 100
        client.client_metrics['successful_operations'] = 80
        
        # Reset
        client.reset_performance_stats()
        
        # Check reset
        assert client.client_metrics['total_operations'] == 0
        assert client.client_metrics['successful_operations'] == 0


class TestSyncMethods:
    """Test synchronous wrapper methods"""
    
    @pytest.fixture
    def client(self):
        """Create client with mocked adapters"""
        config = {
            'auth': {'network_code': '123456'}
        }
        
        with patch('src.core.unified.client.SOAPAdapter'), \
             patch('src.core.unified.client.RESTAdapter'):
            return GAMUnifiedClient(config)
    
    def test_create_report_sync(self, client):
        """Test synchronous create_report method"""
        with patch.object(client, 'create_report') as mock_async:
            mock_async.return_value = asyncio.coroutine(
                lambda: {'reportId': '123'}
            )()
            
            result = client.create_report_sync({'name': 'Test'})
            
            assert result['reportId'] == '123'
    
    def test_test_connection_sync(self, client):
        """Test synchronous test_connection method"""
        with patch.object(client, 'test_connection') as mock_async:
            mock_async.return_value = asyncio.coroutine(lambda: True)()
            
            result = client.test_connection_sync()
            
            assert result is True


class TestComplexityScoring:
    """Test operation complexity scoring"""
    
    @pytest.fixture
    def client(self):
        """Create client instance"""
        config = {
            'auth': {'network_code': '123456'}
        }
        
        with patch('src.core.unified.client.SOAPAdapter'), \
             patch('src.core.unified.client.RESTAdapter'):
            return GAMUnifiedClient(config)
    
    def test_simple_operation_score(self, client):
        """Test complexity score for simple operation"""
        score = client._calculate_complexity_score({
            'name': 'Test Report'
        })
        
        assert score == 0
    
    def test_complex_operation_score(self, client):
        """Test complexity score for complex operation"""
        score = client._calculate_complexity_score({
            'filters': ['filter1', 'filter2', 'filter3'],
            'limit': 5000,
            'batch_size': 100
        })
        
        assert score > 10  # Should be high complexity
    
    def test_bulk_operation_detection(self, client):
        """Test bulk operation detection"""
        score = client._calculate_complexity_score({
            'bulk_update': True,
            'items': ['item1', 'item2']
        })
        
        assert score >= 3  # Bulk indicator adds points


class TestConfigurationValidation:
    """Test configuration validation enhancements"""
    
    def test_validation_with_empty_credentials(self):
        """Test validation catches empty credentials"""
        config = {
            'auth': {
                'network_code': '123456',
                'client_id': '',
                'client_secret': '',
                'refresh_token': ''
            }
        }
        
        with patch('src.core.unified.client.SOAPAdapter'), \
             patch('src.core.unified.client.RESTAdapter'):
            # Should not raise error but log warnings
            client = GAMUnifiedClient(config)
            assert client is not None
    
    def test_validation_with_partial_credentials(self):
        """Test validation with partial credentials"""
        config = {
            'auth': {
                'network_code': '123456',
                'client_id': 'test-client',
                'client_secret': '',  # Missing secret
                'refresh_token': 'test-token'
            }
        }
        
        with patch('src.core.unified.client.SOAPAdapter'), \
             patch('src.core.unified.client.RESTAdapter'):
            # Should initialize but with warnings
            client = GAMUnifiedClient(config)
            assert client is not None