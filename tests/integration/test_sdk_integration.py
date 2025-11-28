"""
Integration tests for the GAM SDK.

Tests the SDK components working together with mocked API responses,
ensuring the fluent API design works correctly in real-world scenarios.
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import date, timedelta
from pathlib import Path

from gam_sdk.client import GAMClient
from gam_sdk.reports import ReportBuilder, ReportResult
from gam_sdk.config import ConfigManager
from gam_sdk.auth import AuthManager as SDKAuthManager
from gam_sdk.exceptions import SDKError, ReportError, ConfigError, AuthError


class TestSDKEndToEndReportGeneration:
    """Test end-to-end report generation workflows."""
    
    @pytest.fixture
    def mock_api_responses(self):
        """Mock API responses for report generation."""
        return {
            'create_report': {
                'name': 'networks/123456789/reports/test-report-123',
                'displayName': 'Test Delivery Report',
                'reportDefinition': {
                    'dimensions': ['DATE', 'AD_UNIT_NAME'],
                    'metrics': ['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 'TOTAL_LINE_ITEM_LEVEL_CLICKS'],
                    'dateRange': {
                        'startDate': '2024-01-01',
                        'endDate': '2024-01-31'
                    }
                }
            },
            'run_report': {
                'name': 'operations/test-operation-123',
                'done': False,
                'metadata': {
                    'reportName': 'networks/123456789/reports/test-report-123'
                }
            },
            'check_operation_done': {
                'name': 'operations/test-operation-123',
                'done': True,
                'response': {
                    'reportResult': {
                        'name': 'networks/123456789/reports/test-report-123/results/result-123'
                    }
                }
            },
            'fetch_results': {
                'rows': [
                    {
                        'dimensionValues': ['2024-01-01', 'Ad Unit 1'],
                        'metricValueGroups': [{'primaryValues': ['1000', '50']}]
                    },
                    {
                        'dimensionValues': ['2024-01-02', 'Ad Unit 2'],
                        'metricValueGroups': [{'primaryValues': ['2000', '100']}]
                    }
                ],
                'metadata': {
                    'generated_at': '2024-01-01T00:00:00Z'
                }
            }
        }
    
    @pytest.mark.integration
    @pytest.mark.sdk
    def test_quick_delivery_report_workflow(self, mock_config, mock_api_responses):
        """Test complete quick delivery report workflow."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager, \
             patch('src.sdk.reports.generate_quick_report') as mock_generate:
            
            # Setup mocks
            mock_get_config.return_value = mock_config
            mock_auth = Mock()
            mock_auth_manager.return_value = mock_auth
            
            # Mock report result
            rows = mock_api_responses['fetch_results']['rows']
            result = ReportResult(
                rows,
                ['DATE', 'AD_UNIT_NAME'],
                ['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 'TOTAL_LINE_ITEM_LEVEL_CLICKS'],
                mock_api_responses['fetch_results']['metadata']
            )
            mock_generate.return_value = result
            
            # Test the workflow
            client = GAMClient(auto_authenticate=False)
            report = client.quick_report('delivery', days_back=30)
            
            # Verify result
            assert isinstance(report, ReportResult)
            assert len(report) == 2
            assert report.dimension_headers == ['DATE', 'AD_UNIT_NAME']
            assert report.metric_headers == ['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 'TOTAL_LINE_ITEM_LEVEL_CLICKS']
            
            # Verify API was called correctly
            mock_generate.assert_called_once_with('delivery', 30)
    
    @pytest.mark.integration
    @pytest.mark.sdk
    def test_custom_report_fluent_workflow(self, mock_config, mock_api_responses):
        """Test custom report creation with fluent API."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager, \
             patch('src.sdk.reports.ReportGenerator') as mock_generator_class:
            
            # Setup mocks
            mock_get_config.return_value = mock_config
            mock_auth = Mock()
            mock_auth_manager.return_value = mock_auth
            
            # Mock report generator
            mock_generator = Mock()
            mock_generator_class.return_value = mock_generator
            
            # Mock report creation workflow
            mock_report = Mock()
            mock_report.id = 'test-report-123'
            mock_report.name = 'networks/123456789/reports/test-report-123'
            
            mock_generator.create_report.return_value = mock_report
            mock_generator.run_report.return_value = mock_report
            
            # Mock result
            rows = mock_api_responses['fetch_results']['rows']
            result = ReportResult(
                rows,
                ['DATE', 'AD_UNIT_NAME'],
                ['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS'],
                mock_api_responses['fetch_results']['metadata']
            )
            mock_generator.fetch_results.return_value = result
            
            # Test fluent workflow
            client = GAMClient(auto_authenticate=False)
            report = (client
                     .reports()
                     .dimensions('DATE', 'AD_UNIT_NAME')
                     .metrics('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS')
                     .last_30_days()
                     .name('Custom Test Report')
                     .execute())
            
            # Verify result
            assert isinstance(report, ReportResult)
            assert len(report) == 2
            
            # Verify generator calls
            mock_generator.create_report.assert_called_once()
            mock_generator.run_report.assert_called_once_with(mock_report)
            mock_generator.fetch_results.assert_called_once_with(mock_report)
    
    @pytest.mark.integration
    @pytest.mark.sdk
    def test_report_data_manipulation_workflow(self, mock_config, mock_api_responses):
        """Test report data manipulation and export workflow."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager, \
             patch('src.sdk.reports.generate_quick_report') as mock_generate:
            
            # Setup mocks
            mock_get_config.return_value = mock_config
            mock_auth = Mock()
            mock_auth_manager.return_value = mock_auth
            
            # Create test data with more varied values for filtering/sorting
            rows = [
                {
                    'dimensionValues': ['2024-01-01', 'Mobile Ad Unit'],
                    'metricValueGroups': [{'primaryValues': ['5000', '250']}]
                },
                {
                    'dimensionValues': ['2024-01-02', 'Desktop Ad Unit'],
                    'metricValueGroups': [{'primaryValues': ['1000', '50']}]
                },
                {
                    'dimensionValues': ['2024-01-03', 'Tablet Ad Unit'],
                    'metricValueGroups': [{'primaryValues': ['3000', '150']}]
                }
            ]
            
            result = ReportResult(
                rows,
                ['DATE', 'AD_UNIT_NAME'],
                ['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 'TOTAL_LINE_ITEM_LEVEL_CLICKS'],
                {'generated_at': '2024-01-01T00:00:00Z'}
            )
            mock_generate.return_value = result
            
            # Test the workflow
            client = GAMClient(auto_authenticate=False)
            report = client.quick_report('delivery')
            
            # Test data manipulation
            filtered = report.filter(
                lambda row: row.get('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 0) > 2000
            )
            assert len(filtered) == 2  # Should exclude the 1000 impressions row
            
            sorted_report = filtered.sort('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', ascending=False)
            df = sorted_report.to_dataframe()
            assert df.iloc[0]['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS'] == 5000
            assert df.iloc[1]['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS'] == 3000
            
            # Test export functionality
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                csv_path = f.name
            
            try:
                sorted_report.to_csv(csv_path)
                assert os.path.exists(csv_path)
                
                # Verify exported data
                import pandas as pd
                exported_df = pd.read_csv(csv_path)
                assert len(exported_df) == 2
                assert exported_df.iloc[0]['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS'] == 5000
                
            finally:
                os.unlink(csv_path)


class TestSDKConfigurationIntegration:
    """Test SDK configuration management integration."""
    
    @pytest.mark.integration
    @pytest.mark.sdk
    def test_config_load_validate_save_workflow(self, mock_config):
        """Test complete configuration workflow."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager:
            
            # Setup mocks
            mock_get_config.return_value = mock_config
            mock_auth = Mock()
            mock_auth_manager.return_value = mock_auth
            
            # Test configuration workflow
            client = GAMClient(auto_authenticate=False)
            config = client.config()
            
            # Test configuration updates
            result = (config
                     .set('gam.network_code', '987654321')
                     .set('api.timeout', 60)
                     .validate())
            
            assert result is config
            assert config.has_pending_changes()
            
            changes = config.get_pending_changes()
            assert 'gam.network_code' in changes
            assert changes['gam.network_code'] == '987654321'
            assert 'api.timeout' in changes
            assert changes['api.timeout'] == 60
    
    @pytest.mark.integration
    @pytest.mark.sdk
    def test_config_file_operations_workflow(self, mock_config):
        """Test configuration file operations workflow."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager:
            
            # Setup mocks
            mock_get_config.return_value = mock_config
            mock_auth = Mock()
            mock_auth_manager.return_value = mock_auth
            
            client = GAMClient(auto_authenticate=False)
            config = client.config()
            
            # Create test configuration
            config.set('test.setting', 'test_value')
            
            # Test save to file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml_path = f.name
            
            try:
                config.save_to_file(yaml_path, format='yaml')
                assert os.path.exists(yaml_path)
                
                # Test load from file
                new_config = ConfigManager()
                new_config.load_from_file(yaml_path)
                
                assert 'test.setting' in new_config.get_pending_changes()
                assert new_config.get_pending_changes()['test.setting'] == 'test_value'
                
            finally:
                os.unlink(yaml_path)


class TestSDKAuthenticationIntegration:
    """Test SDK authentication integration."""
    
    @pytest.mark.integration
    @pytest.mark.sdk
    def test_auth_status_refresh_workflow(self, mock_config, mock_oauth_credentials):
        """Test authentication status checking and refresh workflow."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager:
            
            # Setup mocks
            mock_get_config.return_value = mock_config
            mock_core_auth = Mock()
            mock_auth_manager.return_value = mock_core_auth
            
            # Mock valid credentials
            mock_core_auth.get_oauth2_credentials.return_value = mock_oauth_credentials
            
            client = GAMClient(auto_authenticate=False)
            auth = client.auth()
            
            # Test authentication workflow
            result = (auth
                     .check_status()
                     .refresh_if_needed()
                     .validate_scopes())
            
            assert result is auth
            
            # Verify status was checked
            status = auth.get_status()
            assert status is not None
            assert status['authenticated'] is True
            assert status['credentials_present'] is True
    
    @pytest.mark.integration
    @pytest.mark.sdk
    def test_auth_connection_test_workflow(self, mock_config, sample_network_info):
        """Test authentication and connection testing workflow."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager:
            
            # Setup mocks
            mock_get_config.return_value = mock_config
            mock_core_auth = Mock()
            mock_auth_manager.return_value = mock_core_auth
            
            # Mock authentication success
            mock_credentials = Mock()
            mock_credentials.expired = False
            mock_core_auth.get_oauth2_credentials.return_value = mock_credentials
            
            # Mock SOAP API success
            mock_soap_client = Mock()
            mock_network_service = Mock()
            mock_network_service.getCurrentNetwork.return_value = sample_network_info
            mock_soap_client.GetService.return_value = mock_network_service
            mock_core_auth.get_soap_client.return_value = mock_soap_client
            
            # Mock REST API success
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_session.get.return_value = mock_response
            mock_core_auth.get_rest_session.return_value = mock_session
            
            client = GAMClient(auto_authenticate=False)
            
            # Test connection through client
            connection_result = client.test_connection()
            assert connection_result['authenticated'] is True
            assert connection_result['overall_status'] == 'healthy'
            
            # Test connection through auth manager
            auth = client.auth()
            auth_result = auth.test_connection()
            assert auth_result is auth


class TestSDKErrorHandlingIntegration:
    """Test SDK error handling in integrated scenarios."""
    
    @pytest.mark.integration
    @pytest.mark.sdk
    def test_report_generation_error_propagation(self, mock_config):
        """Test error propagation through report generation workflow."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager, \
             patch('src.sdk.reports.ReportGenerator') as mock_generator_class:
            
            # Setup mocks
            mock_get_config.return_value = mock_config
            mock_auth = Mock()
            mock_auth_manager.return_value = mock_auth
            
            # Mock generator that fails
            mock_generator = Mock()
            mock_generator_class.return_value = mock_generator
            
            from src.core.exceptions import ReportGenerationError
            mock_generator.create_report.side_effect = ReportGenerationError("API Error")
            
            client = GAMClient(auto_authenticate=False)
            
            # Test error propagation
            with pytest.raises(ReportError) as exc_info:
                (client
                 .reports()
                 .dimensions('DATE')
                 .metrics('IMPRESSIONS')
                 .last_7_days()
                 .execute())
            
            assert "Report generation failed" in str(exc_info.value)
            assert exc_info.value.error_code == "GENERATION_FAILED"
    
    @pytest.mark.integration
    @pytest.mark.sdk
    def test_authentication_error_propagation(self, mock_config):
        """Test authentication error propagation through SDK."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager:
            
            # Setup mocks
            mock_get_config.return_value = mock_config
            mock_auth = Mock()
            mock_auth_manager.return_value = mock_auth
            
            # Mock authentication failure
            from src.core.exceptions import AuthenticationError
            mock_auth.get_oauth2_credentials.side_effect = AuthenticationError("Auth failed")
            
            client = GAMClient(auto_authenticate=True)
            
            # Should raise SDK AuthError
            with pytest.raises(AuthError) as exc_info:
                client._ensure_authenticated()
            
            assert "Authentication verification failed" in str(exc_info.value)
    
    @pytest.mark.integration
    @pytest.mark.sdk
    def test_configuration_error_propagation(self):
        """Test configuration error propagation through SDK."""
        with patch('src.sdk.client.get_config') as mock_get_config:
            
            from src.core.exceptions import ConfigurationError
            mock_get_config.side_effect = ConfigurationError("Config not found")
            
            # Should raise SDK ConfigError
            with pytest.raises(ConfigError) as exc_info:
                GAMClient()
            
            assert "Failed to load configuration" in str(exc_info.value)


class TestSDKContextManagerIntegration:
    """Test SDK context manager integration."""
    
    @pytest.mark.integration
    @pytest.mark.sdk
    def test_context_manager_with_report_generation(self, mock_config):
        """Test context manager usage with report generation."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager, \
             patch('src.sdk.reports.generate_quick_report') as mock_generate:
            
            # Setup mocks
            mock_get_config.return_value = mock_config
            mock_auth = Mock()
            mock_auth_manager.return_value = mock_auth
            
            # Mock successful report
            rows = [
                {
                    'dimensionValues': ['2024-01-01', 'Ad Unit 1'],
                    'metricValueGroups': [{'primaryValues': ['1000', '50']}]
                }
            ]
            result = ReportResult(
                rows,
                ['DATE', 'AD_UNIT_NAME'],
                ['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 'TOTAL_LINE_ITEM_LEVEL_CLICKS'],
                {'generated_at': '2024-01-01T00:00:00Z'}
            )
            mock_generate.return_value = result
            
            # Test context manager usage
            with GAMClient(auto_authenticate=False) as client:
                report = client.quick_report('delivery')
                assert isinstance(report, ReportResult)
                assert len(report) == 1
            
            # Context manager should exit cleanly


class TestSDKPerformanceIntegration:
    """Test SDK performance characteristics."""
    
    @pytest.mark.integration
    @pytest.mark.sdk
    @pytest.mark.performance
    def test_large_dataset_handling(self, mock_config):
        """Test SDK handling of large datasets."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager, \
             patch('src.sdk.reports.generate_quick_report') as mock_generate:
            
            # Setup mocks
            mock_get_config.return_value = mock_config
            mock_auth = Mock()
            mock_auth_manager.return_value = mock_auth
            
            # Create large dataset (1000 rows)
            rows = []
            for i in range(1000):
                rows.append({
                    'dimensionValues': [f'2024-01-{(i % 31) + 1:02d}', f'Ad Unit {i}'],
                    'metricValueGroups': [{'primaryValues': [str(1000 + i), str(50 + i)]}]
                })
            
            result = ReportResult(
                rows,
                ['DATE', 'AD_UNIT_NAME'],
                ['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 'TOTAL_LINE_ITEM_LEVEL_CLICKS'],
                {'generated_at': '2024-01-01T00:00:00Z'}
            )
            mock_generate.return_value = result
            
            client = GAMClient(auto_authenticate=False)
            report = client.quick_report('delivery')
            
            # Test that large dataset is handled efficiently
            assert len(report) == 1000
            
            # Test filtering performance
            filtered = report.filter(
                lambda row: row.get('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 0) > 1500
            )
            assert len(filtered) < 1000
            
            # Test DataFrame conversion performance
            df = report.to_dataframe()
            assert len(df) == 1000
            assert df.shape[1] == 4  # 2 dimensions + 2 metrics
    
    @pytest.mark.integration
    @pytest.mark.sdk
    def test_multiple_concurrent_operations(self, mock_config):
        """Test SDK handling of multiple operations."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager:
            
            # Setup mocks
            mock_get_config.return_value = mock_config
            mock_auth = Mock()
            mock_auth_manager.return_value = mock_auth
            
            client = GAMClient(auto_authenticate=False)
            
            # Test multiple configuration operations
            config = client.config()
            config.set('setting1', 'value1')
            config.set('setting2', 'value2')
            config.set('setting3', 'value3')
            
            assert config.has_pending_changes()
            changes = config.get_pending_changes()
            assert len(changes) == 3
            
            # Test multiple auth operations
            auth = client.auth()
            # Multiple calls should return the same instance (cached)
            auth2 = client.auth()
            assert auth is auth2