"""
Unit tests for the core GAM client module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import os

from gam_api.client import GAMClient
from gam_api.exceptions import (
    APIError, 
    AuthenticationError, 
    ConfigurationError,
    NetworkError
)


class TestGAMClient:
    """Test cases for GAMClient class."""
    
    def test_init_with_config(self, mock_config, mock_auth_manager):
        """Test client initialization with configuration."""
        with patch('src.core.client.AuthManager') as MockAuthManager:
            MockAuthManager.return_value = mock_auth_manager
            
            client = GAMClient(config=mock_config)
            
            assert client.config == mock_config
            assert client.network_code == "123456789"
            assert client._auth_manager == mock_auth_manager
    
    def test_init_without_config(self, mock_config, mock_auth_manager):
        """Test client initialization without explicit config."""
        with patch('src.core.client.get_auth_manager', return_value=mock_auth_manager):
            with patch('src.core.client.load_config', return_value=mock_config):
                
                client = GAMClient()
                
                assert client.config == mock_config
                assert client.auth_manager.network_code == "123456789"
    
    def test_init_with_invalid_config(self):
        """Test client initialization with invalid configuration."""
        with patch('src.core.client.get_config') as mock_get_config:
            mock_get_config.side_effect = ConfigurationError("Invalid config")
            
            with pytest.raises(ConfigurationError):
                GAMClient()
    
    def test_test_connection_success(self, mock_config, mock_auth_manager):
        """Test successful connection validation."""
        with patch('src.core.client.AuthManager') as MockAuthManager:
            MockAuthManager.return_value = mock_auth_manager
            
            # Mock the SOAP client
            mock_soap_client = Mock()
            mock_network_service = Mock()
            mock_network_service.getCurrentNetwork.return_value = {
                'id': '123456789',
                'networkCode': '123456789',
                'displayName': 'Test Network'
            }
            mock_soap_client.GetService.return_value = mock_network_service
            mock_auth_manager.get_soap_client.return_value = mock_soap_client
            
            client = GAMClient(config=mock_config)
            result = client.test_connection()
            
            assert result is True
            mock_network_service.getCurrentNetwork.assert_called_once()
    
    def test_test_connection_failure(self, mock_config, mock_auth_manager):
        """Test connection validation failure."""
        with patch('src.core.client.AuthManager') as MockAuthManager:
            MockAuthManager.return_value = mock_auth_manager
            
            # Mock the SOAP client to raise an error
            mock_soap_client = Mock()
            mock_network_service = Mock()
            mock_network_service.getCurrentNetwork.side_effect = Exception("Network error")
            mock_soap_client.GetService.return_value = mock_network_service
            mock_auth_manager.get_soap_client.return_value = mock_soap_client
            
            client = GAMClient(config=mock_config)
            
            with pytest.raises(NetworkError):
                client.test_connection()
    
    def test_get_service_soap(self, mock_config, mock_auth_manager):
        """Test getting a SOAP service."""
        with patch('src.core.client.AuthManager') as MockAuthManager:
            MockAuthManager.return_value = mock_auth_manager
            
            mock_soap_client = Mock()
            mock_service = Mock()
            mock_soap_client.GetService.return_value = mock_service
            mock_auth_manager.get_soap_client.return_value = mock_soap_client
            
            client = GAMClient(config=mock_config)
            service = client.get_service('ReportService')
            
            assert service == mock_service
            mock_soap_client.GetService.assert_called_with('ReportService', version='v202408')
    
    def test_get_service_with_version(self, mock_config, mock_auth_manager):
        """Test getting a service with specific version."""
        with patch('src.core.client.AuthManager') as MockAuthManager:
            MockAuthManager.return_value = mock_auth_manager
            
            mock_soap_client = Mock()
            mock_service = Mock()
            mock_soap_client.GetService.return_value = mock_service
            mock_auth_manager.get_soap_client.return_value = mock_soap_client
            
            client = GAMClient(config=mock_config)
            service = client.get_service('LineItemService', version='v202402')
            
            assert service == mock_service
            mock_soap_client.GetService.assert_called_with('LineItemService', version='v202402')
    
    def test_get_service_authentication_error(self, mock_config, mock_auth_manager):
        """Test service retrieval with authentication error."""
        with patch('src.core.client.AuthManager') as MockAuthManager:
            MockAuthManager.return_value = mock_auth_manager
            
            mock_auth_manager.get_soap_client.side_effect = AuthenticationError("Invalid credentials")
            
            client = GAMClient(config=mock_config)
            
            with pytest.raises(AuthenticationError):
                client.get_service('ReportService')
    
    def test_execute_query(self, mock_config, mock_auth_manager):
        """Test executing a query with statement builder."""
        with patch('src.core.client.AuthManager') as MockAuthManager:
            MockAuthManager.return_value = mock_auth_manager
            
            # Mock service and statement builder
            mock_service = Mock()
            mock_service.getReportsByStatement.return_value = {
                'totalResultSetSize': 2,
                'results': [
                    {'id': '1', 'name': 'Report 1'},
                    {'id': '2', 'name': 'Report 2'}
                ]
            }
            
            mock_soap_client = Mock()
            mock_soap_client.GetService.return_value = mock_service
            
            # Mock statement builder
            mock_statement_builder = Mock()
            mock_statement = Mock()
            mock_statement.ToStatement.return_value = {'query': 'SELECT * FROM Report'}
            mock_statement_builder.return_value = mock_statement
            mock_soap_client.StatementBuilder = mock_statement_builder
            
            mock_auth_manager.get_soap_client.return_value = mock_soap_client
            
            client = GAMClient(config=mock_config)
            
            # Execute query
            results = client.execute_query(
                service_name='ReportService',
                method_name='getReportsByStatement',
                query='SELECT * FROM Report WHERE status = "ACTIVE"'
            )
            
            assert len(results) == 2
            assert results[0]['name'] == 'Report 1'
            mock_service.getReportsByStatement.assert_called_once()
    
    def test_create_report_job(self, mock_config, mock_auth_manager):
        """Test creating a report job."""
        with patch('src.core.client.AuthManager') as MockAuthManager:
            MockAuthManager.return_value = mock_auth_manager
            
            mock_report_service = Mock()
            mock_report_service.runReportJob.return_value = {
                'id': 'report-123',
                'reportJob': {
                    'id': 'job-123',
                    'reportQuery': {
                        'dimensions': ['DATE'],
                        'columns': ['IMPRESSIONS']
                    }
                }
            }
            
            mock_soap_client = Mock()
            mock_soap_client.GetService.return_value = mock_report_service
            mock_auth_manager.get_soap_client.return_value = mock_soap_client
            
            client = GAMClient(config=mock_config)
            
            report_job = {
                'reportQuery': {
                    'dimensions': ['DATE'],
                    'columns': ['IMPRESSIONS'],
                    'dateRangeType': 'YESTERDAY'
                }
            }
            
            result = client.create_report_job(report_job)
            
            assert result['id'] == 'report-123'
            mock_report_service.runReportJob.assert_called_with(report_job)
    
    def test_get_report_download_url(self, mock_config, mock_auth_manager):
        """Test getting report download URL."""
        with patch('src.core.client.AuthManager') as MockAuthManager:
            MockAuthManager.return_value = mock_auth_manager
            
            mock_report_service = Mock()
            mock_report_service.getReportDownloadURL.return_value = {
                'downloadUrl': 'https://example.com/download/report-123'
            }
            
            mock_soap_client = Mock()
            mock_soap_client.GetService.return_value = mock_report_service
            mock_auth_manager.get_soap_client.return_value = mock_soap_client
            
            client = GAMClient(config=mock_config)
            
            url = client.get_report_download_url('report-123', 'CSV_DUMP')
            
            assert url == 'https://example.com/download/report-123'
            mock_report_service.getReportDownloadURL.assert_called_with('report-123', 'CSV_DUMP')
    
    def test_network_code_property(self, mock_config, mock_auth_manager):
        """Test network code property."""
        with patch('src.core.client.AuthManager') as MockAuthManager:
            MockAuthManager.return_value = mock_auth_manager
            
            client = GAMClient(config=mock_config)
            
            assert client.network_code == "123456789"
    
    def test_version_property(self, mock_config, mock_auth_manager):
        """Test API version property."""
        with patch('src.core.client.AuthManager') as MockAuthManager:
            MockAuthManager.return_value = mock_auth_manager
            
            client = GAMClient(config=mock_config)
            client._version = 'v202408'
            
            assert client.version == 'v202408'
    
    def test_context_manager(self, mock_config, mock_auth_manager):
        """Test using client as context manager."""
        with patch('src.core.client.AuthManager') as MockAuthManager:
            MockAuthManager.return_value = mock_auth_manager
            
            with GAMClient(config=mock_config) as client:
                assert isinstance(client, GAMClient)
                assert client.network_code == "123456789"
    
    def test_retry_on_network_error(self, mock_config, mock_auth_manager):
        """Test retry logic on network errors."""
        with patch('src.core.client.AuthManager') as MockAuthManager:
            MockAuthManager.return_value = mock_auth_manager
            
            mock_service = Mock()
            # First two calls fail, third succeeds
            mock_service.getCurrentNetwork.side_effect = [
                NetworkError("Connection failed"),
                NetworkError("Connection failed"),
                {'id': '123456789', 'networkCode': '123456789'}
            ]
            
            mock_soap_client = Mock()
            mock_soap_client.GetService.return_value = mock_service
            mock_auth_manager.get_soap_client.return_value = mock_soap_client
            
            client = GAMClient(config=mock_config)
            
            with patch('time.sleep'):  # Mock sleep to speed up test
                result = client.test_connection()
            
            assert result is True
            assert mock_service.getCurrentNetwork.call_count == 3
    
    def test_cache_service_instances(self, mock_config, mock_auth_manager):
        """Test that service instances are cached."""
        with patch('src.core.client.AuthManager') as MockAuthManager:
            MockAuthManager.return_value = mock_auth_manager
            
            mock_soap_client = Mock()
            mock_service = Mock()
            mock_soap_client.GetService.return_value = mock_service
            mock_auth_manager.get_soap_client.return_value = mock_soap_client
            
            client = GAMClient(config=mock_config)
            
            # Get service twice
            service1 = client.get_service('ReportService')
            service2 = client.get_service('ReportService')
            
            # Should be the same instance (cached)
            assert service1 is service2
            # GetService should only be called once
            mock_soap_client.GetService.assert_called_once()
    
    def test_handle_api_error(self, mock_config, mock_auth_manager):
        """Test handling GAM API errors."""
        with patch('src.core.client.AuthManager') as MockAuthManager:
            MockAuthManager.return_value = mock_auth_manager
            
            mock_service = Mock()
            # Simulate GAM API error
            error = Exception()
            error.fault = Mock()
            error.fault.detail = Mock()
            error.fault.detail.ApiExceptionFault = Mock()
            error.fault.detail.ApiExceptionFault.errors = [
                {
                    'reason': 'QUOTA_EXCEEDED',
                    'errorString': 'Daily quota exceeded'
                }
            ]
            mock_service.runReportJob.side_effect = error
            
            mock_soap_client = Mock()
            mock_soap_client.GetService.return_value = mock_service
            mock_auth_manager.get_soap_client.return_value = mock_soap_client
            
            client = GAMClient(config=mock_config)
            
            with pytest.raises(APIError) as exc_info:
                client.create_report_job({'reportQuery': {}})
            
            assert 'QUOTA_EXCEEDED' in str(exc_info.value)