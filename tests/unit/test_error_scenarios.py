"""
Unit tests for error scenarios and edge cases in the GAM SDK.

Tests comprehensive error handling, edge cases, and boundary conditions
across all SDK components.
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import date, timedelta
import requests

from gam_sdk.client import GAMClient
from gam_sdk.reports import ReportBuilder, ReportResult
from gam_sdk.config import ConfigManager
from gam_sdk.auth import AuthManager as SDKAuthManager
from gam_sdk.exceptions import SDKError, ReportError, ConfigError, AuthError, ValidationError, NetworkError
from gam_api.exceptions import (
    ConfigurationError, 
    AuthenticationError, 
    ReportGenerationError,
    NetworkError as CoreNetworkError
)


class TestSDKClientErrorScenarios:
    """Test error scenarios in GAMClient."""
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_client_initialization_config_not_found(self):
        """Test client initialization when config file is not found."""
        with patch('src.sdk.client.get_config') as mock_get_config:
            mock_get_config.side_effect = FileNotFoundError("Config file not found")
            
            with pytest.raises(ConfigError) as exc_info:
                GAMClient()
            
            assert "Failed to load configuration" in str(exc_info.value)
            assert exc_info.value.error_code == "CONFIG_LOAD_FAILED"
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_client_initialization_invalid_config_format(self):
        """Test client initialization with invalid config format."""
        with patch('src.sdk.client.get_config') as mock_get_config:
            mock_get_config.side_effect = yaml.YAMLError("Invalid YAML format")
            
            with pytest.raises(ConfigError) as exc_info:
                GAMClient()
            
            assert "Failed to load configuration" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_client_initialization_auth_manager_failure(self, mock_config):
        """Test client initialization when AuthManager fails."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager:
            
            mock_get_config.return_value = mock_config
            mock_auth_manager.side_effect = Exception("Auth manager initialization failed")
            
            with pytest.raises(AuthError) as exc_info:
                GAMClient()
            
            assert "Auto-authentication failed" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_ensure_authenticated_network_error(self, mock_config):
        """Test _ensure_authenticated with network error."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager:
            
            mock_get_config.return_value = mock_config
            mock_auth = Mock()
            mock_auth_manager.return_value = mock_auth
            
            client = GAMClient(auto_authenticate=False)
            client._authenticated = False
            
            # Mock network error during credential retrieval
            mock_auth.get_oauth2_credentials.side_effect = requests.ConnectionError("Network unreachable")
            
            with pytest.raises(AuthError) as exc_info:
                client._ensure_authenticated()
            
            assert "Authentication verification failed" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_ensure_authenticated_timeout_error(self, mock_config):
        """Test _ensure_authenticated with timeout error."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager:
            
            mock_get_config.return_value = mock_config
            mock_auth = Mock()
            mock_auth_manager.return_value = mock_auth
            
            client = GAMClient(auto_authenticate=False)
            client._authenticated = False
            
            # Mock timeout during credential retrieval
            mock_auth.get_oauth2_credentials.side_effect = requests.Timeout("Request timeout")
            
            with pytest.raises(AuthError) as exc_info:
                client._ensure_authenticated()
            
            assert "Authentication verification failed" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_test_connection_authentication_failure(self, mock_config):
        """Test test_connection when authentication fails."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager:
            
            mock_get_config.return_value = mock_config
            mock_auth = Mock()
            mock_auth_manager.return_value = mock_auth
            
            client = GAMClient(auto_authenticate=False)
            
            # Mock authentication failure
            with patch.object(client, '_ensure_authenticated', side_effect=AuthError("Auth failed")):
                result = client.test_connection()
                
                assert result['authenticated'] is False
                assert result['overall_status'] == 'unauthenticated'
                assert 'error' in result
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_quick_report_invalid_report_type(self, mock_config):
        """Test quick_report with invalid report type."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager:
            
            mock_get_config.return_value = mock_config
            mock_auth = Mock()
            mock_auth_manager.return_value = mock_auth
            
            client = GAMClient(auto_authenticate=False)
            
            with pytest.raises(ValidationError) as exc_info:
                client.quick_report('invalid_type')
            
            assert "Invalid quick report type" in str(exc_info.value)
            assert exc_info.value.field_name == 'report_type'


class TestReportBuilderErrorScenarios:
    """Test error scenarios in ReportBuilder."""
    
    @pytest.fixture
    def report_builder(self, mock_config):
        """Create a ReportBuilder instance."""
        with patch('src.sdk.reports.ReportGenerator') as mock_generator:
            mock_generator.return_value = Mock()
            mock_auth = Mock()
            return ReportBuilder(mock_config, mock_auth)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_execute_no_dimensions_or_metrics(self, report_builder):
        """Test execute with no dimensions or metrics set."""
        # Test no dimensions
        report_builder._metrics = ['IMPRESSIONS']
        
        with pytest.raises(ValidationError) as exc_info:
            report_builder.execute()
        
        assert "At least one dimension is required" in str(exc_info.value)
        
        # Test no metrics
        report_builder._dimensions = ['DATE']
        report_builder._metrics = []
        
        with pytest.raises(ValidationError) as exc_info:
            report_builder.execute()
        
        assert "At least one metric is required" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_execute_invalid_date_range(self, report_builder):
        """Test execute with invalid date range."""
        report_builder._dimensions = ['DATE']
        report_builder._metrics = ['IMPRESSIONS']
        
        # Test end date before start date
        invalid_start = date(2024, 1, 31)
        invalid_end = date(2024, 1, 1)
        report_builder.date_range(invalid_start, invalid_end)
        
        with pytest.raises(ValidationError) as exc_info:
            report_builder.execute()
        
        assert "End date must be after start date" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_execute_report_generator_timeout(self, report_builder):
        """Test execute when report generator times out."""
        report_builder._dimensions = ['DATE']
        report_builder._metrics = ['IMPRESSIONS']
        
        # Mock timeout during report creation
        from gam_api.exceptions import TimeoutError as CoreTimeoutError
        report_builder._generator.create_report.side_effect = CoreTimeoutError("Operation timed out")
        
        with pytest.raises(ReportError) as exc_info:
            report_builder.execute()
        
        assert "Report generation failed" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_execute_api_quota_exceeded(self, report_builder):
        """Test execute when API quota is exceeded."""
        report_builder._dimensions = ['DATE']
        report_builder._metrics = ['IMPRESSIONS']
        
        # Mock quota exceeded error
        quota_error = requests.HTTPError("429 Quota exceeded")
        quota_error.response = Mock()
        quota_error.response.status_code = 429
        
        report_builder._generator.create_report.side_effect = quota_error
        
        with pytest.raises(ReportError) as exc_info:
            report_builder.execute()
        
        assert "Report generation failed" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_days_back_invalid_value(self, report_builder):
        """Test days_back with invalid values."""
        # Test negative days
        with pytest.raises(ValidationError) as exc_info:
            report_builder.days_back(-5)
        
        assert "Days back must be positive" in str(exc_info.value)
        
        # Test zero days
        with pytest.raises(ValidationError) as exc_info:
            report_builder.days_back(0)
        
        assert "Days back must be positive" in str(exc_info.value)
        
        # Test excessively large value
        with pytest.raises(ValidationError) as exc_info:
            report_builder.days_back(10000)
        
        assert "Days back cannot exceed" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_filter_invalid_operator(self, report_builder):
        """Test filter with invalid operator."""
        with pytest.raises(ValidationError) as exc_info:
            report_builder.filter('AD_UNIT_NAME', 'INVALID_OPERATOR', ['value'])
        
        assert "Invalid filter operator" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_quick_report_type_invalid(self, report_builder):
        """Test quick report with invalid type."""
        with pytest.raises(ValidationError) as exc_info:
            report_builder.quick('nonexistent_type')
        
        assert "Invalid quick report type" in str(exc_info.value)


class TestReportResultErrorScenarios:
    """Test error scenarios in ReportResult."""
    
    @pytest.fixture
    def empty_report_result(self):
        """Create an empty ReportResult."""
        return ReportResult([], [], [], {})
    
    @pytest.fixture
    def malformed_report_result(self):
        """Create a ReportResult with malformed data."""
        rows = [
            {'dimensionValues': ['2024-01-01'], 'metricValueGroups': []},  # Missing metrics
            {'dimensionValues': [], 'metricValueGroups': [{'primaryValues': ['1000']}]},  # Missing dimensions
        ]
        return ReportResult(rows, ['DATE'], ['IMPRESSIONS'], {})
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_to_dataframe_empty_result(self, empty_report_result):
        """Test to_dataframe with empty result."""
        df = empty_report_result.to_dataframe()
        
        assert len(df) == 0
        assert list(df.columns) == []
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_to_dataframe_malformed_data(self, malformed_report_result):
        """Test to_dataframe with malformed data."""
        # Should handle malformed data gracefully
        df = malformed_report_result.to_dataframe()
        
        assert len(df) == 2
        # Should fill missing values appropriately
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_export_to_invalid_path(self, sample_report_data):
        """Test export to invalid file path."""
        rows = [
            {
                'dimensionValues': ['2024-01-01', 'Ad Unit 1'],
                'metricValueGroups': [{'primaryValues': ['1000', '50']}]
            }
        ]
        result = ReportResult(rows, ['DATE', 'AD_UNIT_NAME'], ['IMPRESSIONS', 'CLICKS'], {})
        
        # Test invalid directory
        invalid_path = '/nonexistent/directory/file.csv'
        
        with pytest.raises(ReportError) as exc_info:
            result.to_csv(invalid_path)
        
        assert "Failed to export report" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_export_permission_denied(self, sample_report_data):
        """Test export when permission is denied."""
        rows = [
            {
                'dimensionValues': ['2024-01-01', 'Ad Unit 1'],
                'metricValueGroups': [{'primaryValues': ['1000', '50']}]
            }
        ]
        result = ReportResult(rows, ['DATE', 'AD_UNIT_NAME'], ['IMPRESSIONS', 'CLICKS'], {})
        
        # Mock permission error
        with patch('pandas.DataFrame.to_csv', side_effect=PermissionError("Permission denied")):
            with pytest.raises(ReportError) as exc_info:
                result.to_csv('/tmp/test.csv')
            
            assert "Failed to export report" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_filter_invalid_function(self, sample_report_data):
        """Test filter with invalid function."""
        rows = [
            {
                'dimensionValues': ['2024-01-01', 'Ad Unit 1'],
                'metricValueGroups': [{'primaryValues': ['1000', '50']}]
            }
        ]
        result = ReportResult(rows, ['DATE', 'AD_UNIT_NAME'], ['IMPRESSIONS', 'CLICKS'], {})
        
        # Test with function that raises exception
        def bad_filter(row):
            raise ValueError("Filter error")
        
        with pytest.raises(ReportError) as exc_info:
            result.filter(bad_filter)
        
        assert "Filter operation failed" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_sort_invalid_column(self, sample_report_data):
        """Test sort with non-existent column."""
        rows = [
            {
                'dimensionValues': ['2024-01-01', 'Ad Unit 1'],
                'metricValueGroups': [{'primaryValues': ['1000', '50']}]
            }
        ]
        result = ReportResult(rows, ['DATE', 'AD_UNIT_NAME'], ['IMPRESSIONS', 'CLICKS'], {})
        
        with pytest.raises(ReportError) as exc_info:
            result.sort('NONEXISTENT_COLUMN')
        
        assert "Sort operation failed" in str(exc_info.value)


class TestConfigManagerErrorScenarios:
    """Test error scenarios in ConfigManager."""
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_load_from_corrupted_yaml(self):
        """Test loading from corrupted YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [unclosed")
            corrupted_path = f.name
        
        try:
            manager = ConfigManager()
            
            with pytest.raises(ConfigError) as exc_info:
                manager.load_from_file(corrupted_path)
            
            assert "Failed to load configuration" in str(exc_info.value)
            
        finally:
            os.unlink(corrupted_path)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_load_from_corrupted_json(self):
        """Test loading from corrupted JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"invalid": json, "content"}')
            corrupted_path = f.name
        
        try:
            manager = ConfigManager()
            
            with pytest.raises(ConfigError) as exc_info:
                manager.load_from_file(corrupted_path)
            
            assert "Failed to load configuration" in str(exc_info.value)
            
        finally:
            os.unlink(corrupted_path)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_save_to_readonly_directory(self):
        """Test saving to read-only directory."""
        manager = ConfigManager()
        manager.set('test.key', 'test_value')
        
        # Try to save to root directory (should fail with permission error)
        readonly_path = '/etc/readonly_config.yaml'
        
        with pytest.raises(ConfigError) as exc_info:
            manager.save_to_file(readonly_path)
        
        assert "Failed to save configuration" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_validate_missing_required_fields(self, mock_config):
        """Test validation with missing required fields."""
        manager = ConfigManager(mock_config)
        
        # Mock missing network code
        with patch.object(manager, 'get', side_effect=lambda key, default=None: None if 'network_code' in key else 'value'):
            
            with pytest.raises(ConfigError) as exc_info:
                manager.validate()
            
            assert "Configuration validation failed" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_test_connection_network_failure(self, mock_config):
        """Test connection test with network failure."""
        manager = ConfigManager(mock_config)
        
        with patch('src.sdk.config.AuthManager') as mock_auth_manager:
            mock_auth = Mock()
            mock_auth_manager.return_value = mock_auth
            
            # Mock network failure
            mock_auth.get_oauth2_credentials.side_effect = requests.ConnectionError("Network error")
            
            with pytest.raises(ConfigError) as exc_info:
                manager.test_connection()
            
            assert "Connection test failed" in str(exc_info.value)


class TestAuthManagerErrorScenarios:
    """Test error scenarios in AuthManager."""
    
    @pytest.fixture
    def auth_manager(self, mock_config):
        """Create an AuthManager instance."""
        mock_core_auth = Mock()
        return SDKAuthManager(mock_config, mock_core_auth)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_check_status_credential_corruption(self, auth_manager):
        """Test check_status with corrupted credentials."""
        # Mock corrupted credentials that cause unexpected errors
        auth_manager._core_auth.get_oauth2_credentials.side_effect = ValueError("Corrupted token data")
        
        result = auth_manager.check_status()
        
        assert result is auth_manager
        assert auth_manager._status['authenticated'] is False
        assert any('Credential check failed' in error for error in auth_manager._status['errors'])
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_refresh_if_needed_network_error(self, auth_manager, mock_oauth_credentials):
        """Test refresh_if_needed with network error during refresh."""
        mock_oauth_credentials.expired = True
        mock_oauth_credentials.refresh.side_effect = requests.ConnectionError("Network unreachable")
        auth_manager._credentials = mock_oauth_credentials
        auth_manager._core_auth._get_request.return_value = Mock()
        
        with pytest.raises(AuthError) as exc_info:
            auth_manager.refresh_if_needed()
        
        assert "Failed to refresh credentials" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_refresh_if_needed_invalid_response(self, auth_manager, mock_oauth_credentials):
        """Test refresh_if_needed with invalid server response."""
        mock_oauth_credentials.expired = True
        # Mock invalid response from Google's servers
        mock_oauth_credentials.refresh.side_effect = ValueError("Invalid response format")
        auth_manager._credentials = mock_oauth_credentials
        auth_manager._core_auth._get_request.return_value = Mock()
        
        with pytest.raises(AuthError) as exc_info:
            auth_manager.refresh_if_needed()
        
        assert "Failed to refresh credentials" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_login_browser_not_available(self, auth_manager):
        """Test login when browser is not available."""
        with patch('src.sdk.auth.webbrowser.open', side_effect=Exception("No browser available")):
            
            with pytest.raises(AuthError) as exc_info:
                auth_manager.login()
            
            assert "Login flow failed" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_logout_token_revocation_network_error(self, auth_manager, mock_oauth_credentials):
        """Test logout with network error during token revocation."""
        auth_manager._credentials = mock_oauth_credentials
        
        with patch('src.sdk.auth.requests.post', side_effect=requests.ConnectionError("Network error")):
            # Should still succeed (logout locally)
            result = auth_manager.logout(revoke_token=True)
            
            assert result is auth_manager
            assert auth_manager._credentials is None
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_test_connection_both_apis_timeout(self, auth_manager):
        """Test connection test when both APIs timeout."""
        with patch.object(auth_manager, 'is_authenticated', return_value=True):
            # Mock SOAP timeout
            auth_manager._core_auth.get_soap_client.side_effect = requests.Timeout("SOAP timeout")
            
            # Mock REST timeout
            mock_session = Mock()
            mock_session.get.side_effect = requests.Timeout("REST timeout")
            auth_manager._core_auth.get_rest_session.return_value = mock_session
            
            with pytest.raises(NetworkError) as exc_info:
                auth_manager.test_connection()
            
            assert "Both API connections failed" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.error
    def test_validate_scopes_malformed_credentials(self, auth_manager):
        """Test validate_scopes with malformed credentials."""
        mock_credentials = Mock()
        # Mock credentials without scopes attribute
        del mock_credentials.scopes
        auth_manager._credentials = mock_credentials
        
        # Should handle gracefully
        result = auth_manager.validate_scopes()
        assert result is auth_manager


class TestEdgeCaseScenarios:
    """Test edge cases and boundary conditions."""
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.edge_case
    def test_extremely_large_report_data(self):
        """Test handling of extremely large report datasets."""
        # Create very large dataset (10,000 rows)
        rows = []
        for i in range(10000):
            rows.append({
                'dimensionValues': [f'2024-01-{(i % 31) + 1:02d}', f'Ad Unit {i}'],
                'metricValueGroups': [{'primaryValues': [str(1000000 + i), str(50000 + i)]}]
            })
        
        result = ReportResult(
            rows,
            ['DATE', 'AD_UNIT_NAME'],
            ['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 'TOTAL_LINE_ITEM_LEVEL_CLICKS'],
            {'total_rows': len(rows)}
        )
        
        # Should handle large dataset without memory issues
        assert len(result) == 10000
        
        # Test DataFrame conversion with large data
        df = result.to_dataframe()
        assert len(df) == 10000
        
        # Test filtering with large data
        filtered = result.filter(lambda row: row.get('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 0) > 1005000)
        assert len(filtered) < 10000
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.edge_case
    def test_unicode_and_special_characters(self):
        """Test handling of Unicode and special characters."""
        rows = [
            {
                'dimensionValues': ['2024-01-01', 'Åd Ünit with émojis 🚀'],
                'metricValueGroups': [{'primaryValues': ['1000', '50']}]
            },
            {
                'dimensionValues': ['2024-01-02', 'Unit with "quotes" and \\ backslashes'],
                'metricValueGroups': [{'primaryValues': ['2000', '100']}]
            },
            {
                'dimensionValues': ['2024-01-03', '中文广告单元'],
                'metricValueGroups': [{'primaryValues': ['3000', '150']}]
            }
        ]
        
        result = ReportResult(
            rows,
            ['DATE', 'AD_UNIT_NAME'],
            ['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 'TOTAL_LINE_ITEM_LEVEL_CLICKS'],
            {}
        )
        
        # Should handle Unicode properly
        df = result.to_dataframe()
        assert len(df) == 3
        
        # Test CSV export with Unicode
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            csv_path = f.name
        
        try:
            result.to_csv(csv_path)
            assert os.path.exists(csv_path)
            
            # Verify Unicode is preserved
            import pandas as pd
            imported_df = pd.read_csv(csv_path)
            assert '🚀' in imported_df.iloc[0]['AD_UNIT_NAME']
            
        finally:
            os.unlink(csv_path)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.edge_case
    def test_null_and_empty_values(self):
        """Test handling of null and empty values."""
        rows = [
            {
                'dimensionValues': ['2024-01-01', ''],  # Empty string
                'metricValueGroups': [{'primaryValues': ['1000', '0']}]
            },
            {
                'dimensionValues': ['2024-01-02', None],  # None value
                'metricValueGroups': [{'primaryValues': ['', '50']}]  # Empty metric
            },
            {
                'dimensionValues': ['', ''],  # All empty dimensions
                'metricValueGroups': [{'primaryValues': ['0', '0']}]
            }
        ]
        
        result = ReportResult(
            rows,
            ['DATE', 'AD_UNIT_NAME'],
            ['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 'TOTAL_LINE_ITEM_LEVEL_CLICKS'],
            {}
        )
        
        # Should handle null/empty values gracefully
        df = result.to_dataframe()
        assert len(df) == 3
        
        # Check that null values are handled properly
        assert df.iloc[1]['AD_UNIT_NAME'] is None or pd.isna(df.iloc[1]['AD_UNIT_NAME'])
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.edge_case
    def test_date_boundary_conditions(self, mock_config):
        """Test date boundary conditions."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager, \
             patch('src.sdk.reports.ReportGenerator') as mock_generator_class:
            
            mock_get_config.return_value = mock_config
            mock_auth = Mock()
            mock_auth_manager.return_value = mock_auth
            mock_generator = Mock()
            mock_generator_class.return_value = mock_generator
            
            client = GAMClient(auto_authenticate=False)
            builder = client.reports()
            
            # Test leap year dates
            leap_start = date(2024, 2, 29)  # Valid leap year date
            leap_end = date(2024, 3, 1)
            
            result = builder.date_range(leap_start, leap_end)
            assert result._date_range.start_date == leap_start
            assert result._date_range.end_date == leap_end
            
            # Test year boundary
            year_start = date(2023, 12, 31)
            year_end = date(2024, 1, 1)
            
            result = builder.date_range(year_start, year_end)
            assert result._date_range.start_date == year_start
            assert result._date_range.end_date == year_end