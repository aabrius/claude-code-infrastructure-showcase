"""
Functional integration test for the unified client.

This test validates the unified client works end-to-end with mock adapters.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from gam_api.unified import GAMUnifiedClient, UnifiedClientConfig
from gam_api.exceptions import APIError, ConfigurationError


class TestUnifiedIntegration:
    """Test unified client integration functionality"""
    
    def test_client_creation_with_mock_config(self):
        """Test creating client with minimal mock configuration"""
        config = {
            'auth': {
                'network_code': '123456',
                'client_id': 'test-client',
                'client_secret': 'test-secret',
                'refresh_token': 'test-token'
            }
        }
        
        # Mock the adapters to prevent actual initialization
        with patch('gam_api.unified.client.SOAPAdapter') as mock_soap, \
             patch('gam_api.unified.client.RESTAdapter') as mock_rest:
            
            # Create mock adapter instances
            soap_instance = Mock()
            rest_instance = Mock()
            mock_soap.return_value = soap_instance
            mock_rest.return_value = rest_instance
            
            # Create client
            client = GAMUnifiedClient(config)
            
            # Verify client was created successfully
            assert client is not None
            assert client.network_code == '123456'
            assert client.has_soap
            assert client.has_rest
    
    def test_client_with_placeholder_config_fails(self):
        """Test client creation fails with placeholder configuration"""
        config = {
            'auth': {
                'network_code': 'YOUR_NETWORK_CODE_HERE',
                'client_id': 'YOUR_CLIENT_ID_HERE',
                'client_secret': 'YOUR_CLIENT_SECRET_HERE',
                'refresh_token': 'YOUR_REFRESH_TOKEN_HERE'
            }
        }
        
        with pytest.raises(ConfigurationError) as exc_info:
            GAMUnifiedClient(config)
        
        assert "Network code not configured" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_api_selection_and_execution(self):
        """Test API selection and operation execution"""
        config = {
            'auth': {
                'network_code': '123456',
                'client_id': 'test-client',
                'client_secret': 'test-secret',
                'refresh_token': 'test-token'
            }
        }
        
        with patch('gam_api.unified.client.SOAPAdapter') as mock_soap, \
             patch('gam_api.unified.client.RESTAdapter') as mock_rest:
            
            # Create mock adapter instances with methods
            soap_instance = Mock()
            rest_instance = Mock()
            
            # Mock specific methods
            rest_instance.create_report = AsyncMock(
                return_value={'reportId': '123', 'status': 'PENDING'}
            )
            soap_instance.get_line_items = AsyncMock(
                return_value=[{'id': '1', 'name': 'Test Line Item'}]
            )
            
            mock_soap.return_value = soap_instance
            mock_rest.return_value = rest_instance
            
            # Create client
            client = GAMUnifiedClient(config)
            
            # Force adapter instances
            client._soap_adapter = soap_instance
            client._rest_adapter = rest_instance
            
            # Test report creation (should use REST)
            with patch.object(client.strategy, 'select_api') as mock_select:
                from gam_api.unified.strategy import APIType, OperationType
                
                # Mock strategy to return REST for reports
                mock_select.return_value = (APIType.REST, APIType.SOAP)
                
                # Mock fallback manager to just call primary
                with patch.object(client.fallback_manager, 'execute_with_fallback') as mock_fallback:
                    mock_fallback.return_value = {'reportId': '123', 'status': 'PENDING'}
                    
                    result = await client.create_report({
                        'displayName': 'Test Report'
                    })
                    
                    assert result['reportId'] == '123'
                    mock_select.assert_called_once()
                    mock_fallback.assert_called_once()
    
    def test_performance_tracking(self):
        """Test performance tracking functionality"""
        config = {
            'auth': {
                'network_code': '123456',
                'client_id': 'test-client',
                'client_secret': 'test-secret',
                'refresh_token': 'test-token'
            }
        }
        
        with patch('gam_api.unified.client.SOAPAdapter'), \
             patch('gam_api.unified.client.RESTAdapter'):
            
            client = GAMUnifiedClient(config)
            
            # Get initial performance summary
            stats = client.get_performance_summary()
            
            # Verify structure
            assert 'client_metrics' in stats
            assert 'strategy_performance' in stats
            assert 'fallback_statistics' in stats
            assert stats['client_metrics']['total_operations'] == 0
            assert stats['client_metrics']['successful_operations'] == 0
            assert stats['client_metrics']['failed_operations'] == 0
    
    def test_configuration_validation(self):
        """Test configuration validation catches issues"""
        # Missing network code
        config = {
            'auth': {
                'client_id': 'test-client',
                'client_secret': 'test-secret',
                'refresh_token': 'test-token'
            }
        }
        
        with pytest.raises(ConfigurationError) as exc_info:
            GAMUnifiedClient(config)
        
        assert "auth.network_code" in str(exc_info.value)
    
    def test_adapter_availability_checks(self):
        """Test adapter availability properties"""
        config = {
            'auth': {
                'network_code': '123456',
                'client_id': 'test-client',
                'client_secret': 'test-secret',
                'refresh_token': 'test-token'
            }
        }
        
        with patch('gam_api.unified.client.SOAPAdapter') as mock_soap, \
             patch('gam_api.unified.client.RESTAdapter') as mock_rest:
            
            # Test with both adapters working
            mock_soap.return_value = Mock()
            mock_rest.return_value = Mock()
            
            client = GAMUnifiedClient(config)
            assert client.has_soap
            assert client.has_rest
        
        # Test with SOAP failing
        with patch('gam_api.unified.client.SOAPAdapter') as mock_soap, \
             patch('gam_api.unified.client.RESTAdapter') as mock_rest:
            
            mock_soap.side_effect = Exception("SOAP failed")
            mock_rest.return_value = Mock()
            
            client = GAMUnifiedClient(config)
            assert not client.has_soap
            assert client.has_rest
    
    def test_unified_config_integration(self):
        """Test integration with UnifiedClientConfig"""
        config = {
            'auth': {
                'network_code': '123456',
                'client_id': 'test-client',
                'client_secret': 'test-secret',
                'refresh_token': 'test-token'
            }
        }
        
        unified_config = UnifiedClientConfig(
            api_preference='soap',
            max_retries=5,
            enable_fallback=False
        )
        
        with patch('gam_api.unified.client.SOAPAdapter'), \
             patch('gam_api.unified.client.RESTAdapter'):
            
            client = GAMUnifiedClient(config, unified_config)
            
            assert client.unified_config.api_preference == 'soap'
            assert client.unified_config.max_retries == 5
            assert client.unified_config.enable_fallback is False
    
    def test_context_manager_support(self):
        """Test context manager functionality"""
        config = {
            'auth': {
                'network_code': '123456',
                'client_id': 'test-client',
                'client_secret': 'test-secret',
                'refresh_token': 'test-token'
            }
        }
        
        with patch('gam_api.unified.client.SOAPAdapter'), \
             patch('gam_api.unified.client.RESTAdapter'):
            
            # Test context manager usage
            with GAMUnifiedClient(config) as client:
                assert client is not None
                assert hasattr(client, 'network_code')
            
            # Should complete without errors


def test_factory_function():
    """Test the factory function for creating clients"""
    from gam_api.unified import create_unified_client

    # Mock the load_config function from config module
    with patch('gam_api.config.load_config') as mock_load_config, \
         patch('gam_api.unified.client.SOAPAdapter'), \
         patch('gam_api.unified.client.RESTAdapter'):
        
        # Mock config
        mock_config = Mock()
        mock_config.auth.network_code = '123456'
        mock_config.to_dict.return_value = {
            'auth': {'network_code': '123456'}
        }
        mock_load_config.return_value = mock_config
        
        client = create_unified_client(api_preference='rest')
        
        assert client is not None
        assert client.unified_config.api_preference == 'rest'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])