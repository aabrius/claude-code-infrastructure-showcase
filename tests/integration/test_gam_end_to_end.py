"""
End-to-end integration tests for Google Ad Manager API workflows.
"""

import pytest
import json
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import pandas as pd

# Import from new modular packages
try:
    from gam_api.auth import AuthManager
    from gam_api.client import GAMClient
    from gam_api.reports import ReportGenerator
    from gam_api.config import Config, get_config
    from gam_api.exceptions import APIError, AuthenticationError
    from gam_api.models import ReportType, ReportStatus
    from gam_sdk.client import GAMClient as SDKClient
    from gam_shared.formatters import get_formatter
except ImportError:
    # Fallback to legacy imports for compatibility
    from src.core.auth import AuthManager
    from src.core.client import GAMClient
    from src.core.reports import ReportGenerator
    from src.core.config import Config, get_config
    from src.core.exceptions import APIError, AuthenticationError
    from src.core.models import ReportType, ReportStatus
    from src.sdk.client import GAMClient as SDKClient
    from src.utils.formatters import get_formatter


class TestEndToEndReportGeneration:
    """End-to-end tests for complete report generation workflow."""
    
    @pytest.fixture
    def mock_full_config(self):
        """Create a complete mock configuration."""
        return {
            'auth': {
                'network_code': '123456789',
                'client_id': 'test-client-id',
                'client_secret': 'test-client-secret',
                'refresh_token': 'test-refresh-token'
            },
            'api': {
                'prefer_rest': True,
                'timeout': 120
            },
            'cache': {
                'enabled': True,
                'ttl': 3600
            },
            'defaults': {
                'days_back': 30,
                'format': 'json'
            }
        }
    
    @pytest.fixture
    def mock_report_data(self):
        """Create mock report data."""
        return {
            'rows': [
                ['2024-01-01', 'Homepage Banner', '10000', '50', '0.5', '5.0'],
                ['2024-01-01', 'Sidebar Ad', '5000', '30', '0.6', '6.0'],
                ['2024-01-02', 'Homepage Banner', '12000', '65', '0.54', '5.4'],
                ['2024-01-02', 'Sidebar Ad', '5500', '35', '0.64', '6.4']
            ],
            'dimensions': ['DATE', 'AD_UNIT_NAME'],
            'metrics': ['IMPRESSIONS', 'CLICKS', 'CTR', 'CPM'],
            'total_rows': 4
        }
    
    def test_complete_report_workflow(self, mock_full_config, mock_report_data):
        """Test complete workflow from auth to report download."""
        with patch('src.core.auth.AuthManager') as MockAuthManager:
            with patch('src.core.client.GAMClient') as MockGAMClient:
                # Setup auth manager
                mock_auth = Mock()
                mock_auth.validate_credentials.return_value = True
                mock_auth.get_credentials.return_value = {
                    'access_token': 'test-access-token',
                    'refresh_token': 'test-refresh-token'
                }
                MockAuthManager.return_value = mock_auth
                
                # Setup GAM client
                mock_client = Mock()
                mock_client.test_connection.return_value = True
                
                # Mock report service
                mock_report_service = Mock()
                mock_report_service.runReportJob.return_value = {'id': 'job-123'}
                mock_report_service.getReportJobStatus.side_effect = [
                    'IN_PROGRESS',
                    'IN_PROGRESS',
                    'COMPLETED'
                ]
                
                # Mock report downloader
                mock_downloader = Mock()
                mock_downloader.DownloadReportToList.return_value = mock_report_data['rows']
                
                mock_client.get_service.return_value = mock_report_service
                MockGAMClient.return_value = mock_client
                
                with patch('src.core.reports.ReportDownloader', return_value=mock_downloader):
                    # Execute workflow
                    config = Config(**mock_full_config)
                    client = GAMClient(config)
                    generator = ReportGenerator(client, config)
                    
                    # Generate report
                    result = generator.generate_quick_report('delivery', days_back=7)
                    
                    # Verify workflow steps
                    assert mock_auth.validate_credentials.called
                    assert mock_client.test_connection.called
                    assert mock_report_service.runReportJob.called
                    assert mock_report_service.getReportJobStatus.call_count >= 1
                    assert mock_downloader.DownloadReportToList.called
                    
                    # Verify result
                    assert result is not None
                    assert result.total_rows == 4
                    assert len(result.data) == 4
    
    def test_workflow_with_authentication_failure(self, mock_full_config):
        """Test workflow when authentication fails."""
        with patch('src.core.auth.AuthManager') as MockAuthManager:
            mock_auth = Mock()
            mock_auth.validate_credentials.return_value = False
            mock_auth.get_credentials.side_effect = AuthenticationError("Invalid credentials")
            MockAuthManager.return_value = mock_auth
            
            config = Config(**mock_full_config)
            
            with pytest.raises(AuthenticationError):
                client = GAMClient(config)
                client.test_connection()
    
    def test_workflow_with_report_failure(self, mock_full_config):
        """Test workflow when report generation fails."""
        with patch('src.core.auth.AuthManager') as MockAuthManager:
            with patch('src.core.client.GAMClient') as MockGAMClient:
                # Setup successful auth
                mock_auth = Mock()
                mock_auth.validate_credentials.return_value = True
                MockAuthManager.return_value = mock_auth
                
                # Setup client with failing report service
                mock_client = Mock()
                mock_report_service = Mock()
                mock_report_service.runReportJob.side_effect = APIError("Report quota exceeded")
                mock_client.get_service.return_value = mock_report_service
                MockGAMClient.return_value = mock_client
                
                config = Config(**mock_full_config)
                generator = ReportGenerator(mock_client, config)
                
                with pytest.raises(APIError) as exc_info:
                    generator.generate_quick_report('delivery')
                
                assert "Report quota exceeded" in str(exc_info.value)
    
    def test_workflow_with_timeout(self, mock_full_config):
        """Test workflow with report timeout."""
        with patch('src.core.auth.AuthManager') as MockAuthManager:
            with patch('src.core.client.GAMClient') as MockGAMClient:
                # Setup auth
                mock_auth = Mock()
                MockAuthManager.return_value = mock_auth
                
                # Setup client with slow report
                mock_client = Mock()
                mock_report_service = Mock()
                mock_report_service.runReportJob.return_value = {'id': 'job-slow'}
                mock_report_service.getReportJobStatus.return_value = 'IN_PROGRESS'  # Never completes
                mock_client.get_service.return_value = mock_report_service
                MockGAMClient.return_value = mock_client
                
                config = Config(**mock_full_config)
                generator = ReportGenerator(mock_client, config)
                
                with patch('time.sleep'):  # Speed up test
                    with pytest.raises(Exception) as exc_info:
                        generator.wait_for_report('job-slow', timeout=1, poll_interval=0.1)
                
                assert "timeout" in str(exc_info.value).lower()


class TestSDKIntegrationFlow:
    """End-to-end tests for SDK usage."""
    
    def test_sdk_fluent_api_workflow(self):
        """Test complete workflow using SDK fluent API."""
        with patch('src.sdk.client.get_config') as mock_get_config:
            with patch('src.sdk.client.GAMClient._initialize_client') as mock_init:
                with patch('src.sdk.client.ReportGenerator') as MockGenerator:
                    # Setup mocks
                    mock_config = Mock()
                    mock_get_config.return_value = mock_config
                    
                    mock_gam_client = Mock()
                    mock_init.return_value = mock_gam_client
                    
                    mock_generator = Mock()
                    mock_result = Mock()
                    mock_result.total_rows = 100
                    mock_result.to_dataframe.return_value = pd.DataFrame({
                        'DATE': ['2024-01-01', '2024-01-02'],
                        'IMPRESSIONS': [1000, 2000]
                    })
                    mock_generator.generate_quick_report.return_value = mock_result
                    MockGenerator.return_value = mock_generator
                    
                    # Use SDK fluent API
                    client = SDKClient()
                    report = (client
                        .quick_report('delivery')
                        .with_date_range(days_back=7)
                        .with_filters({'ad_unit': 'Mobile'})
                        .run())
                    
                    # Verify workflow
                    assert mock_generator.generate_quick_report.called
                    assert report.total_rows == 100
                    
                    # Test data export
                    df = report.to_dataframe()
                    assert len(df) == 2
                    assert 'IMPRESSIONS' in df.columns
    
    def test_sdk_custom_report_workflow(self):
        """Test custom report creation via SDK."""
        with patch('src.sdk.client.get_config') as mock_get_config:
            with patch('src.sdk.client.GAMClient._initialize_client') as mock_init:
                with patch('src.sdk.client.ReportGenerator') as MockGenerator:
                    # Setup mocks
                    mock_config = Mock()
                    mock_get_config.return_value = mock_config
                    
                    mock_generator = Mock()
                    mock_report = Mock()
                    mock_report.id = 'custom-123'
                    mock_report.status = ReportStatus.COMPLETED
                    mock_generator.create_report.return_value = mock_report
                    MockGenerator.return_value = mock_generator
                    
                    # Create custom report
                    client = SDKClient()
                    report = (client
                        .custom_report('Sales Analysis')
                        .with_dimensions(['DATE', 'ADVERTISER_NAME'])
                        .with_metrics(['REVENUE', 'ECPM'])
                        .with_date_range(start_date='2024-01-01', end_date='2024-01-31')
                        .create())
                    
                    # Verify
                    assert mock_generator.create_report.called
                    assert report.id == 'custom-123'
                    
                    # Check call arguments
                    call_args = mock_generator.create_report.call_args[1]
                    assert call_args['name'] == 'Sales Analysis'
                    assert 'DATE' in call_args['dimensions']
                    assert 'REVENUE' in call_args['metrics']


class TestCLIIntegrationFlow:
    """End-to-end tests for CLI interface."""
    
    def test_cli_report_generation(self):
        """Test report generation via CLI commands."""
        from click.testing import CliRunner
        
        with patch('src.cli.main.get_config') as mock_get_config:
            with patch('src.cli.main.ReportGenerator') as MockGenerator:
                # Setup mocks
                mock_config = Mock()
                mock_get_config.return_value = mock_config
                
                mock_generator = Mock()
                mock_result = Mock()
                mock_result.total_rows = 50
                mock_result.data = [['2024-01-01', '1000']]
                mock_generator.generate_quick_report.return_value = mock_result
                MockGenerator.return_value = mock_generator
                
                # Import CLI after patching
                from src.cli.main import cli
                
                runner = CliRunner()
                result = runner.invoke(cli, ['quick-report', 'delivery', '--days-back', '7'])
                
                # Verify
                assert result.exit_code == 0
                assert mock_generator.generate_quick_report.called
    
    def test_cli_error_handling(self):
        """Test CLI error handling."""
        from click.testing import CliRunner
        
        with patch('src.cli.main.get_config') as mock_get_config:
            # Config loading fails
            mock_get_config.side_effect = Exception("Config not found")
            
            from src.cli.main import cli
            
            runner = CliRunner()
            result = runner.invoke(cli, ['quick-report', 'delivery'])
            
            assert result.exit_code != 0
            assert "Config not found" in result.output


class TestAPIToMCPIntegration:
    """End-to-end tests for API to MCP tool integration."""
    
    @pytest.mark.asyncio
    async def test_api_calls_mcp_tool(self):
        """Test REST API endpoint that uses MCP tool."""
        from fastapi.testclient import TestClient
        from src.api.main import create_app
        
        with patch('src.mcp.fastmcp_server.get_auth_manager') as mock_auth:
            with patch('src.mcp.fastmcp_server.ReportGenerator') as MockGenerator:
                # Setup mocks
                mock_auth.return_value = Mock()
                
                mock_generator = Mock()
                mock_result = Mock()
                mock_result.total_rows = 25
                mock_result.data = []
                mock_generator.generate_quick_report.return_value = mock_result
                MockGenerator.return_value = mock_generator
                
                # Test API endpoint that could call MCP tool
                app = create_app()
                client = TestClient(app)
                
                response = client.post(
                    "/api/v1/reports/quick",
                    json={
                        "report_type": "delivery",
                        "days_back": 7
                    },
                    headers={"X-API-Key": "test-key"}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["total_rows"] == 25


class TestFormattersIntegration:
    """End-to-end tests for data formatting."""
    
    def test_report_formatting_pipeline(self):
        """Test complete formatting pipeline for reports."""
        # Create sample report data
        report_data = {
            'data': [
                ['2024-01-01', 'Ad Unit 1', '1000', '50'],
                ['2024-01-02', 'Ad Unit 1', '1200', '60']
            ],
            'dimension_headers': ['DATE', 'AD_UNIT_NAME'],
            'metric_headers': ['IMPRESSIONS', 'CLICKS'],
            'total_rows': 2
        }
        
        # Test JSON formatter
        json_formatter = get_formatter('json')
        json_output = json_formatter.format(report_data)
        
        # Should be valid JSON
        parsed = json.loads(json_output) if isinstance(json_output, str) else json_output
        assert 'data' in parsed
        assert 'headers' in parsed
        
        # Test CSV formatter
        csv_formatter = get_formatter('csv')
        csv_output = csv_formatter.format(report_data)
        
        # Should contain headers and data
        assert 'DATE,AD_UNIT_NAME,IMPRESSIONS,CLICKS' in csv_output
        assert '2024-01-01,Ad Unit 1,1000,50' in csv_output
    
    def test_error_formatting(self):
        """Test error response formatting."""
        error_data = {
            'error': 'API_ERROR',
            'message': 'Rate limit exceeded',
            'details': {
                'retry_after': 60,
                'quota_remaining': 0
            }
        }
        
        # Format as JSON
        formatter = get_formatter('json')
        formatted = formatter.format(error_data)
        
        if isinstance(formatted, str):
            parsed = json.loads(formatted)
        else:
            parsed = formatted
            
        assert parsed['error'] == 'API_ERROR'
        assert 'retry_after' in parsed.get('details', {})


class TestCachingIntegration:
    """End-to-end tests for caching functionality."""
    
    def test_metadata_caching_workflow(self):
        """Test that metadata is properly cached across requests."""
        try:
            from gam_shared.cache import get_cache
            get_cache_manager = get_cache  # Alias for compatibility
        except ImportError:
            from src.utils.cache import get_cache_manager
        
        with patch('src.core.client.GAMClient') as MockClient:
            # Setup mock client
            mock_client = Mock()
            mock_service = Mock()
            
            # First call returns dimensions
            mock_service.getDimensions.return_value = [
                {'name': 'DATE', 'description': 'Date dimension'},
                {'name': 'AD_UNIT_NAME', 'description': 'Ad unit name'}
            ]
            
            mock_client.get_service.return_value = mock_service
            MockClient.return_value = mock_client
            
            # Clear cache
            cache_manager = get_cache_manager()
            cache_manager.clear()
            
            # First request (cache miss)
            from src.core.metadata import get_dimensions
            dims1 = get_dimensions()
            
            # Second request (cache hit)
            dims2 = get_dimensions()
            
            # Service should only be called once
            assert mock_service.getDimensions.call_count == 1
            
            # Results should be identical
            assert dims1 == dims2
    
    def test_report_result_caching(self):
        """Test report result caching."""
        try:
            from gam_shared.cache import get_cache
            get_cache_manager = get_cache  # Alias for compatibility
        except ImportError:
            from src.utils.cache import get_cache_manager
        
        cache_manager = get_cache_manager()
        cache_manager.clear()
        
        # Cache report result
        report_key = "report_delivery_7days_2024-01-01"
        report_data = {
            'total_rows': 100,
            'data': [['2024-01-01', '1000']],
            'cached_at': datetime.now().isoformat()
        }
        
        cache_manager.set(report_key, report_data, ttl=3600)
        
        # Retrieve from cache
        cached_data = cache_manager.get(report_key)
        
        assert cached_data is not None
        assert cached_data['total_rows'] == 100
        assert cached_data['cached_at'] is not None


class TestErrorRecoveryIntegration:
    """End-to-end tests for error recovery mechanisms."""
    
    def test_automatic_retry_on_failure(self):
        """Test automatic retry logic on transient failures."""
        with patch('src.core.client.GAMClient') as MockClient:
            mock_client = Mock()
            mock_service = Mock()
            
            # First two calls fail, third succeeds
            mock_service.runReportJob.side_effect = [
                Exception("Network error"),
                Exception("Timeout"),
                {'id': 'job-123'}
            ]
            
            mock_client.get_service.return_value = mock_service
            MockClient.return_value = mock_client
            
            # Execute with retry
            from src.core.retry import with_retry
            
            @with_retry(max_attempts=3)
            def create_report():
                service = mock_client.get_service('ReportService')
                return service.runReportJob({})
            
            result = create_report()
            
            assert result['id'] == 'job-123'
            assert mock_service.runReportJob.call_count == 3
    
    def test_circuit_breaker_activation(self):
        """Test circuit breaker pattern for failing services."""
        from src.core.circuit_breaker import CircuitBreaker
        
        breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=1)
        
        # Simulate failures
        for i in range(3):
            try:
                with breaker:
                    raise Exception("Service unavailable")
            except:
                pass
        
        # Circuit should be open
        assert breaker.is_open
        
        # Next call should fail immediately
        with pytest.raises(Exception) as exc_info:
            with breaker:
                pass  # Won't execute
        
        assert "Circuit breaker is open" in str(exc_info.value)