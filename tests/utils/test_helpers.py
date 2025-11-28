"""
Test utilities and helper functions.

Provides common testing utilities, assertion helpers, and test data generators.
"""

import os
import tempfile
import shutil
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from unittest.mock import Mock, patch, MagicMock
from contextlib import contextmanager
import pytest


class TestDataGenerator:
    """Generate test data for various scenarios."""
    
    @staticmethod
    def create_temp_config_file(config_data: Dict[str, Any], format: str = 'yaml') -> str:
        """Create a temporary configuration file."""
        if format == 'yaml':
            suffix = '.yaml'
            content = yaml.dump(config_data, default_flow_style=False)
        elif format == 'json':
            suffix = '.json'
            content = json.dumps(config_data, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
            f.write(content)
            return f.name
    
    @staticmethod
    def create_temp_directory() -> str:
        """Create a temporary directory."""
        return tempfile.mkdtemp()
    
    @staticmethod
    def create_sample_csv_file(headers: List[str], rows: List[List[str]]) -> str:
        """Create a sample CSV file."""
        import csv
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
            return f.name
    
    @staticmethod
    def create_sample_report_data(num_rows: int = 10) -> Dict[str, Any]:
        """Create sample report data structure."""
        rows = []
        for i in range(num_rows):
            rows.append({
                'dimensionValues': [f'2024-01-{(i % 31) + 1:02d}', f'Ad Unit {i}'],
                'metricValueGroups': [{'primaryValues': [str(1000 + i * 100), str(50 + i * 5)]}]
            })
        
        return {
            'rows': rows,
            'dimension_headers': ['DATE', 'AD_UNIT_NAME'],
            'metric_headers': ['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 'TOTAL_LINE_ITEM_LEVEL_CLICKS'],
            'metadata': {
                'generated_at': '2024-01-01T00:00:00Z',
                'total_rows': len(rows)
            }
        }


class MockBuilder:
    """Builder for creating complex mock objects."""
    
    def __init__(self):
        self.mock = Mock()
        self.specs = []
    
    def with_spec(self, spec_class):
        """Add a spec to the mock."""
        self.specs.append(spec_class)
        return self
    
    def with_attribute(self, name: str, value: Any):
        """Add an attribute to the mock."""
        setattr(self.mock, name, value)
        return self
    
    def with_method(self, name: str, return_value: Any = None, side_effect: Any = None):
        """Add a method to the mock."""
        method = Mock()
        if return_value is not None:
            method.return_value = return_value
        if side_effect is not None:
            method.side_effect = side_effect
        setattr(self.mock, name, method)
        return self
    
    def with_property(self, name: str, value: Any):
        """Add a property to the mock."""
        type(self.mock).name = Mock(return_value=value)
        return self
    
    def build(self) -> Mock:
        """Build the final mock object."""
        if self.specs:
            # Create new mock with specs
            final_mock = Mock(spec=self.specs)
            # Copy attributes and methods
            for attr_name in dir(self.mock):
                if not attr_name.startswith('_'):
                    setattr(final_mock, attr_name, getattr(self.mock, attr_name))
            return final_mock
        return self.mock


class APIResponseMocker:
    """Helper for mocking API responses."""
    
    def __init__(self):
        self.patches = []
    
    def mock_soap_client(self, responses: Dict[str, Any]):
        """Mock SOAP client responses."""
        mock_client = Mock()
        
        if 'get_network' in responses:
            mock_network_service = Mock()
            mock_network_service.getCurrentNetwork.return_value = responses['get_network']
            mock_client.GetService.return_value = mock_network_service
        
        if 'create_report_job' in responses:
            mock_report_service = Mock()
            mock_report_service.runReportJob.return_value = responses['create_report_job']
            mock_client.GetService.return_value = mock_report_service
        
        return mock_client
    
    def mock_rest_session(self, responses: Dict[str, Any]):
        """Mock REST session responses."""
        mock_session = Mock()
        
        # Configure responses based on URL patterns
        def mock_request(method, url, **kwargs):
            response = Mock()
            
            if 'networks' in url and url.endswith('networks'):
                response.json.return_value = responses.get('get_network', {})
                response.status_code = 200
            elif 'reports' in url and method.upper() == 'POST':
                if url.endswith(':run'):
                    response.json.return_value = responses.get('run_report', {})
                else:
                    response.json.return_value = responses.get('create_report', {})
                response.status_code = 200
            elif 'operations' in url:
                response.json.return_value = responses.get('check_operation', {})
                response.status_code = 200
            elif 'fetchRows' in url:
                response.json.return_value = responses.get('fetch_results', {})
                response.status_code = 200
            else:
                response.status_code = 404
                response.json.return_value = {'error': 'Not found'}
            
            return response
        
        mock_session.request.side_effect = mock_request
        mock_session.get.side_effect = lambda url, **kwargs: mock_request('GET', url, **kwargs)
        mock_session.post.side_effect = lambda url, **kwargs: mock_request('POST', url, **kwargs)
        
        return mock_session
    
    @contextmanager
    def patch_api_calls(self, soap_responses: Dict[str, Any] = None, rest_responses: Dict[str, Any] = None):
        """Context manager for patching API calls."""
        patches = []
        
        if soap_responses:
            soap_patch = patch('src.core.auth.AuthManager.get_soap_client')
            mock_soap = soap_patch.start()
            mock_soap.return_value = self.mock_soap_client(soap_responses)
            patches.append(soap_patch)
        
        if rest_responses:
            rest_patch = patch('src.core.auth.AuthManager.get_rest_session')
            mock_rest = rest_patch.start()
            mock_rest.return_value = self.mock_rest_session(rest_responses)
            patches.append(rest_patch)
        
        try:
            yield
        finally:
            for patch_obj in patches:
                patch_obj.stop()


class AssertionHelpers:
    """Custom assertion helpers for testing."""
    
    @staticmethod
    def assert_valid_report_result(result, expected_rows: int = None, expected_cols: int = None):
        """Assert that a ReportResult is valid."""
        from src.sdk.reports import ReportResult
        
        assert isinstance(result, ReportResult), "Expected ReportResult instance"
        assert hasattr(result, 'rows'), "ReportResult should have rows attribute"
        assert hasattr(result, 'dimension_headers'), "ReportResult should have dimension_headers"
        assert hasattr(result, 'metric_headers'), "ReportResult should have metric_headers"
        assert hasattr(result, 'metadata'), "ReportResult should have metadata"
        
        if expected_rows is not None:
            assert len(result) == expected_rows, f"Expected {expected_rows} rows, got {len(result)}"
        
        if expected_cols is not None:
            assert result.column_count == expected_cols, f"Expected {expected_cols} columns, got {result.column_count}"
    
    @staticmethod
    def assert_valid_config_manager(config_manager):
        """Assert that a ConfigManager is valid."""
        from src.sdk.config import ConfigManager
        
        assert isinstance(config_manager, ConfigManager), "Expected ConfigManager instance"
        assert hasattr(config_manager, 'get'), "ConfigManager should have get method"
        assert hasattr(config_manager, 'set'), "ConfigManager should have set method"
        assert hasattr(config_manager, 'validate'), "ConfigManager should have validate method"
    
    @staticmethod
    def assert_valid_auth_manager(auth_manager):
        """Assert that an AuthManager is valid."""
        from src.sdk.auth import AuthManager as SDKAuthManager
        
        assert isinstance(auth_manager, SDKAuthManager), "Expected SDK AuthManager instance"
        assert hasattr(auth_manager, 'check_status'), "AuthManager should have check_status method"
        assert hasattr(auth_manager, 'is_authenticated'), "AuthManager should have is_authenticated method"
        assert hasattr(auth_manager, 'refresh_if_needed'), "AuthManager should have refresh_if_needed method"
    
    @staticmethod
    def assert_fluent_interface(obj, method_name: str):
        """Assert that a method returns self for fluent interface."""
        method = getattr(obj, method_name)
        result = method() if callable(method) else method
        assert result is obj, f"Method {method_name} should return self for fluent interface"
    
    @staticmethod
    def assert_error_contains(exception, expected_message: str, expected_code: str = None):
        """Assert that an exception contains expected message and code."""
        assert expected_message in str(exception.value), f"Expected '{expected_message}' in error message"
        
        if expected_code and hasattr(exception.value, 'error_code'):
            assert exception.value.error_code == expected_code, f"Expected error code '{expected_code}'"


class TestEnvironment:
    """Manage test environment setup and teardown."""
    
    def __init__(self):
        self.temp_files = []
        self.temp_dirs = []
        self.env_vars = {}
        self.original_env = {}
    
    def add_temp_file(self, file_path: str):
        """Register a temporary file for cleanup."""
        self.temp_files.append(file_path)
    
    def add_temp_dir(self, dir_path: str):
        """Register a temporary directory for cleanup."""
        self.temp_dirs.append(dir_path)
    
    def set_env_var(self, name: str, value: str):
        """Set an environment variable."""
        if name in os.environ:
            self.original_env[name] = os.environ[name]
        else:
            self.original_env[name] = None
        
        os.environ[name] = value
        self.env_vars[name] = value
    
    def cleanup(self):
        """Clean up all temporary resources."""
        # Clean up files
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except Exception:
                pass  # Ignore cleanup errors
        
        # Clean up directories
        for dir_path in self.temp_dirs:
            try:
                if os.path.exists(dir_path):
                    shutil.rmtree(dir_path)
            except Exception:
                pass  # Ignore cleanup errors
        
        # Restore environment variables
        for name, original_value in self.original_env.items():
            if original_value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = original_value
        
        # Clear tracking
        self.temp_files.clear()
        self.temp_dirs.clear()
        self.env_vars.clear()
        self.original_env.clear()


@contextmanager
def test_environment():
    """Context manager for test environment."""
    env = TestEnvironment()
    try:
        yield env
    finally:
        env.cleanup()


class PerformanceTimer:
    """Simple performance timer for tests."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """Start the timer."""
        import time
        self.start_time = time.time()
    
    def stop(self):
        """Stop the timer."""
        import time
        self.end_time = time.time()
    
    @property
    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time is None:
            return 0.0
        if self.end_time is None:
            import time
            return time.time() - self.start_time
        return self.end_time - self.start_time
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


def skip_if_no_credentials():
    """Skip test if no real credentials are available."""
    return pytest.mark.skipif(
        not os.getenv('GAM_REFRESH_TOKEN'),
        reason="No real credentials available"
    )


def requires_network():
    """Mark test as requiring network access."""
    return pytest.mark.network


def slow_test():
    """Mark test as slow."""
    return pytest.mark.slow


def performance_test():
    """Mark test as performance test."""
    return pytest.mark.performance


class ExtendedTestHelpers:
    """Extended test helper functions."""
    
    @staticmethod
    @contextmanager
    def capture_logs(logger_name: str = None):
        """Capture log messages during test."""
        import logging
        from io import StringIO
        
        log_buffer = StringIO()
        handler = logging.StreamHandler(log_buffer)
        
        logger = logging.getLogger(logger_name) if logger_name else logging.getLogger()
        original_level = logger.level
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        
        try:
            yield log_buffer
        finally:
            logger.removeHandler(handler)
            logger.setLevel(original_level)
    
    @staticmethod
    def mock_report_generator_response(report_type: str = 'delivery', rows: int = 100):
        """Create a complete mock report generator response."""
        from tests.fixtures.mock_data import MockDataGenerator
        
        report_data = MockDataGenerator.generate_complete_report(report_type, days=7)
        
        response = Mock()
        response.total_rows = report_data['total_rows']
        response.data = report_data['data']
        response.dimension_headers = report_data['dimension_headers']
        response.metric_headers = report_data['metric_headers']
        response.execution_time = report_data['execution_time']
        
        return response
    
    @staticmethod
    def assert_dataframe_structure(df, expected_columns: List[str] = None, min_rows: int = 1):
        """Assert pandas DataFrame has expected structure."""
        import pandas as pd
        
        assert isinstance(df, pd.DataFrame), "Expected pandas DataFrame"
        assert len(df) >= min_rows, f"Expected at least {min_rows} rows, got {len(df)}"
        
        if expected_columns:
            assert list(df.columns) == expected_columns, \
                f"Expected columns {expected_columns}, got {list(df.columns)}"
    
    @staticmethod
    def create_mock_unified_client():
        """Create a mock unified client with common methods."""
        mock_client = Mock()
        
        # Add async methods
        async def mock_create_report(*args, **kwargs):
            return {'report_id': 'test-123', 'status': 'PENDING'}
        
        async def mock_get_report_status(*args, **kwargs):
            return 'COMPLETED'
        
        async def mock_download_report(*args, **kwargs):
            from tests.fixtures.mock_data import MockDataGenerator
            return MockDataGenerator.generate_complete_report('delivery')
        
        mock_client.create_report = Mock(side_effect=mock_create_report)
        mock_client.get_report_status = Mock(side_effect=mock_get_report_status)
        mock_client.download_report = Mock(side_effect=mock_download_report)
        
        return mock_client
    
    @staticmethod
    def validate_mcp_response(response: str, expected_success: bool = True):
        """Validate MCP tool response format."""
        try:
            data = json.loads(response)
            
            if expected_success:
                assert data.get('success', False) is True, "MCP response should indicate success"
                assert 'error' not in data, "Success response should not contain error"
            else:
                assert data.get('success', True) is False, "MCP response should indicate failure"
                assert 'error' in data, "Error response should contain error details"
            
            return data
        except json.JSONDecodeError:
            # Response might be CSV or other format
            return response
    
    @staticmethod
    def create_test_cache_manager():
        """Create a test cache manager with temporary storage."""
        try:
            from gam_shared.cache import CacheBackend as CacheManager
        except ImportError:
            from src.utils.cache import CacheManager
        
        temp_dir = tempfile.mkdtemp()
        cache = CacheManager(cache_dir=temp_dir, ttl=60)
        
        # Add cleanup method
        def cleanup():
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        cache.cleanup = cleanup
        return cache
    
    @staticmethod
    def compare_report_data(actual: List[List[str]], expected: List[List[str]], tolerance: float = 0.01):
        """Compare report data with tolerance for numeric values."""
        assert len(actual) == len(expected), f"Row count mismatch: {len(actual)} vs {len(expected)}"
        
        for i, (actual_row, expected_row) in enumerate(zip(actual, expected)):
            assert len(actual_row) == len(expected_row), \
                f"Column count mismatch in row {i}: {len(actual_row)} vs {len(expected_row)}"
            
            for j, (actual_val, expected_val) in enumerate(zip(actual_row, expected_row)):
                # Try numeric comparison with tolerance
                try:
                    actual_num = float(actual_val.strip('$%,'))
                    expected_num = float(expected_val.strip('$%,'))
                    
                    assert abs(actual_num - expected_num) <= tolerance * abs(expected_num), \
                        f"Numeric value mismatch at [{i},{j}]: {actual_val} vs {expected_val}"
                except (ValueError, AttributeError):
                    # Fall back to string comparison
                    assert actual_val == expected_val, \
                        f"Value mismatch at [{i},{j}]: {actual_val} vs {expected_val}"