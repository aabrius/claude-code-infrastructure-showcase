"""
Pytest configuration and fixtures for GAM API tests.

Extended with journey testing and real credentials support.
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from typing import Dict, Any
from pathlib import Path
import yaml

# Add packages to path for imports
import sys
from pathlib import Path

# Get project root
project_root = Path(__file__).parent.parent

# Add package paths
sys.path.insert(0, str(project_root / "packages" / "core" / "src"))
sys.path.insert(0, str(project_root / "packages" / "sdk" / "src"))
sys.path.insert(0, str(project_root / "packages" / "shared" / "src"))
sys.path.insert(0, str(project_root / "applications" / "api-server"))
sys.path.insert(0, str(project_root / "applications" / "mcp-server"))

# Import from modular structure
from gam_api.config import Config, AuthConfig, APIConfig, CacheConfig, LoggingConfig, DefaultsConfig, UnifiedClientConfig
from gam_api import GAMClient


# ====================
# PYTEST CONFIGURATION
# ====================

def pytest_addoption(parser):
    """Add custom command line options for journey testing."""
    
    parser.addoption(
        "--real-credentials",
        action="store_true",
        default=False,
        help="Use real GAM credentials for testing (requires valid googleads.yaml)"
    )
    
    parser.addoption(
        "--journey-category",
        action="store",
        default=None,
        help="Run only journeys from specific category (authentication, reporting, discovery, etc.)"
    )
    
    parser.addoption(
        "--journey-priority",
        action="store",
        default=None,
        choices=["P0", "P1", "P2"],
        help="Run only journeys with specific priority level"
    )
    
    parser.addoption(
        "--journey-interface",
        action="store", 
        default=None,
        choices=["api", "mcp", "sdk", "cli"],
        help="Run only journeys for specific interface"
    )


def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    
    # Add custom markers for journey testing
    config.addinivalue_line("markers", "journey: mark test as a journey test")
    config.addinivalue_line("markers", "real_credentials: mark test as requiring real GAM credentials")
    config.addinivalue_line("markers", "critical: mark test as critical priority (P0)")
    config.addinivalue_line("markers", "important: mark test as important priority (P1)")
    config.addinivalue_line("markers", "advanced: mark test as advanced priority (P2)")
    config.addinivalue_line("markers", "authentication: mark test as authentication journey")
    config.addinivalue_line("markers", "reporting: mark test as reporting journey")
    config.addinivalue_line("markers", "discovery: mark test as data discovery journey")
    config.addinivalue_line("markers", "performance: mark test as performance journey")
    config.addinivalue_line("markers", "error_handling: mark test as error handling journey")
    
    # Set environment variables based on command line options
    if config.getoption("--real-credentials"):
        os.environ["USE_REAL_GAM_CREDENTIALS"] = "true"
        print("\n🔐 Real credentials testing enabled")
        
        # Validate that real credentials are available
        if not _validate_real_credentials_available():
            pytest.exit("❌ Real credentials requested but googleads.yaml not properly configured")
    else:
        os.environ["USE_REAL_GAM_CREDENTIALS"] = "false"
        print("\n🎭 Mock credentials testing (use --real-credentials for real GAM API testing)")


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on command line options."""
    
    # Filter by journey category
    journey_category = config.getoption("--journey-category")
    if journey_category:
        selected_items = []
        for item in items:
            if journey_category in item.keywords:
                selected_items.append(item)
        items[:] = selected_items
        print(f"🔍 Filtering to {journey_category} journeys: {len(items)} tests")
    
    # Filter by journey priority
    journey_priority = config.getoption("--journey-priority")
    if journey_priority:
        priority_marker = {
            "P0": "critical",
            "P1": "important", 
            "P2": "advanced"
        }.get(journey_priority)
        
        if priority_marker:
            selected_items = []
            for item in items:
                if priority_marker in item.keywords:
                    selected_items.append(item)
            items[:] = selected_items
            print(f"🔍 Filtering to {journey_priority} priority journeys: {len(items)} tests")
    
    # Skip real credential tests if not requested
    if not config.getoption("--real-credentials"):
        skip_real = pytest.mark.skip(reason="Real credentials not requested (use --real-credentials)")
        for item in items:
            if "real_credentials" in item.keywords:
                item.add_marker(skip_real)
    
    # Add timeout for journey tests
    for item in items:
        if "journey" in item.keywords:
            if not hasattr(item, 'timeout'):
                item.add_marker(pytest.mark.timeout(300))  # 5 minutes default


def _validate_real_credentials_available() -> bool:
    """Validate that real credentials are properly configured."""
    try:
        config_path = Path("googleads.yaml")
        if not config_path.exists():
            print("❌ googleads.yaml not found")
            return False
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        ad_manager_config = config.get('ad_manager', {})
        
        # Check required fields
        required_fields = ['client_id', 'client_secret', 'refresh_token', 'network_code']
        for field in required_fields:
            value = ad_manager_config.get(field, '')
            if not value or value.startswith('INSERT_'):
                print(f"❌ Invalid or missing {field} in googleads.yaml")
                print("   Run: python generate_new_token.py to set up credentials")
                return False
        
        print("✅ Real credentials configuration validated")
        return True
        
    except Exception as e:
        print(f"❌ Error validating credentials: {e}")
        return False


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Add custom summary information to test results."""
    
    # Add journey testing summary
    if hasattr(terminalreporter, 'stats'):
        journey_tests = []
        for phase in ['passed', 'failed', 'skipped']:
            if phase in terminalreporter.stats:
                for item in terminalreporter.stats[phase]:
                    if hasattr(item, 'keywords') and 'journey' in item.keywords:
                        journey_tests.append((phase, item))
        
        if journey_tests:
            terminalreporter.write_sep("=", "Journey Testing Summary")
            
            # Group by status
            by_status = {}
            for status, item in journey_tests:
                if status not in by_status:
                    by_status[status] = []
                by_status[status].append(item)
            
            for status, items in by_status.items():
                status_icon = {"passed": "✅", "failed": "❌", "skipped": "⚠️"}.get(status, "❓")
                terminalreporter.write_line(f"{status_icon} {status.title()}: {len(items)} journey tests")
            
            # Add credential type info
            creds_type = "Real GAM Credentials" if config.getoption("--real-credentials") else "Mock Credentials"
            terminalreporter.write_line(f"🔐 Credential Type: {creds_type}")


# ==================
# JOURNEY FIXTURES  
# ==================

@pytest.fixture(scope="session")
def real_credentials_enabled():
    """Fixture to check if real credentials are enabled."""
    return os.getenv("USE_REAL_GAM_CREDENTIALS", "false").lower() == "true"


@pytest.fixture(scope="session") 
def gam_credentials_config():
    """Fixture to provide GAM credentials configuration."""
    if os.getenv("USE_REAL_GAM_CREDENTIALS", "false").lower() == "true":
        try:
            with open("googleads.yaml", 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config.get('ad_manager', {})
        except Exception:
            return None
    else:
        # Return mock configuration
        return {
            "client_id": "mock_client_id",
            "client_secret": "mock_client_secret",
            "refresh_token": "mock_refresh_token",
            "network_code": "123456789",
            "application_name": "Mock GAM Client"
        }


@pytest.fixture(scope="function")
def journey_test_framework():
    """Fixture to provide journey testing framework."""
    import sys
    sys.path.append(str(Path(__file__).parent / "journeys"))
    
    from journey_test_framework import JourneyTestFramework
    return JourneyTestFramework()


@pytest.fixture(scope="function")
def real_gam_client(gam_credentials_config):
    """Fixture to provide real or mock GAM client based on configuration."""
    if os.getenv("USE_REAL_GAM_CREDENTIALS", "false").lower() == "true":
        # Import real credentials manager
        import sys
        sys.path.append(str(Path(__file__).parent / "journeys"))
        
        from real_credentials_test import RealCredentialsManager
        
        try:
            credentials_manager = RealCredentialsManager()
            return credentials_manager.get_gam_client()
        except Exception as e:
            pytest.skip(f"Real GAM client creation failed: {e}")
    else:
        # Return mock GAM client from existing fixture
        return mock_gam_client()


# =======================
# EXISTING FIXTURES
# =======================


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    return Config(
        auth=AuthConfig(
            network_code="123456789",
            client_id="test_client_id",
            client_secret="test_client_secret",
            refresh_token="test_refresh_token"
        ),
        api=APIConfig(
            prefer_rest=True,
            timeout=30
        ),
        cache=CacheConfig(
            enabled=True,
            directory="test_cache",
            ttl=300
        ),
        logging=LoggingConfig(
            level="INFO",
            directory="test_logs",
            file="test.log"
        ),
        defaults=DefaultsConfig(
            days_back=30,
            format="json",
            max_rows_preview=10,
            max_pages=5,
            timeout=300
        ),
        unified=UnifiedClientConfig(
            api_preference='rest',
            enable_fallback=True,
            enable_performance_tracking=True
        )
    )


@pytest.fixture
def mock_auth_manager():
    """Create a mock authentication manager."""
    try:
        from gam_api.auth import AuthManager
    except ImportError:
        from legacy.src.core.auth import AuthManager
    
    auth_manager = Mock()
    auth_manager.validate_config.return_value = True
    auth_manager.get_oauth2_credentials.return_value = {
        'client_id': 'test_client_id',
        'client_secret': 'test_client_secret',
        'refresh_token': 'test_refresh_token'
    }
    auth_manager.get_credentials_and_network.return_value = (
        {'access_token': 'test-token'},
        'test-network-code'
    )
    auth_manager.network_code = '123456789'
    yield auth_manager


@pytest.fixture
def mock_gam_client():
    """Create a mock GAM client."""
    client = Mock()
    client.test_connection.return_value = True
    client.network_code = "123456789"
    client.unified_client = Mock()
    client.soap_client = Mock()
    client.rest_session = Mock()
    yield client


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing."""
    config_data = {
        'ad_manager': {
            'network_code': '123456789',
            'client_id': 'test_client_id',
            'client_secret': 'test_client_secret',
            'refresh_token': 'test_refresh_token'
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    os.unlink(temp_path)


@pytest.fixture
def sample_report_data():
    """Sample report data for testing."""
    return {
        'total_rows': 100,
        'dimension_headers': ['DATE', 'AD_UNIT_NAME'],
        'metric_headers': ['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 'TOTAL_LINE_ITEM_LEVEL_CLICKS'],
        'rows': [
            ['2024-01-01', 'Ad Unit 1', '1000', '50'],
            ['2024-01-01', 'Ad Unit 2', '2000', '100'],
            ['2024-01-02', 'Ad Unit 1', '1500', '75'],
        ],
        'execution_time': 2.5
    }


@pytest.fixture
def api_client():
    """Create a test client for FastAPI."""
    from fastapi.testclient import TestClient
    try:
        from gam_api_server.main import create_app
    except ImportError:
        from legacy.src.api.main import create_app
    
    # Create app with test configuration
    app = create_app()
    
    # Mock authentication for tests
    with patch('src.api.auth.get_api_key_auth') as mock_auth:
        mock_auth.return_value = 'test-api-key'
        client = TestClient(app)
        yield client


@pytest.fixture(autouse=True)
def reset_config():
    """Reset configuration before each test."""
    try:
        from gam_api.config import reset_config
    except (ImportError, AttributeError):
        # Fallback - create a mock reset function
        def reset_config():
            pass
    reset_config()
    yield
    reset_config()


@pytest.fixture
def mock_report_generator():
    """Mock report generator for testing."""
    try:
        from gam_api.reports import ReportGenerator
    except ImportError:
        from legacy.src.core.reports import ReportGenerator
    
    generator = Mock(spec=ReportGenerator)
    
    # Mock return values
    mock_result = Mock()
    mock_result.total_rows = 100
    mock_result.dimension_headers = ['DATE', 'AD_UNIT_NAME']
    mock_result.metric_headers = ['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS']
    mock_result.execution_time = 2.5
    mock_result.data = [
        ['2024-01-01', 'Ad Unit 1', '1000'],
        ['2024-01-02', 'Ad Unit 2', '2000']
    ]
    
    generator.generate_quick_report.return_value = mock_result
    generator.create_report.return_value = Mock(id='test-report-id', name='Test Report')
    generator.list_reports.return_value = [
        {'reportId': 'report1', 'displayName': 'Report 1'},
        {'reportId': 'report2', 'displayName': 'Report 2'}
    ]
    
    yield generator


@pytest.fixture(scope="session")
def test_env():
    """Set up test environment variables."""
    original_env = os.environ.copy()
    
    # Set test environment variables
    test_vars = {
        'GAM_NETWORK_CODE': '123456789',
        'GAM_CLIENT_ID': 'test_client_id',
        'GAM_CLIENT_SECRET': 'test_client_secret',
        'GAM_REFRESH_TOKEN': 'test_refresh_token',
        'API_KEYS': 'test-api-key-1,test-api-key-2'
    }
    
    os.environ.update(test_vars)
    
    yield test_vars
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


# SDK-specific fixtures
@pytest.fixture
def mock_sdk_client():
    """Create a mock SDK client for testing."""
    try:
        from gam_sdk.client import GAMClient
    except ImportError:
        from legacy.src.sdk.client import GAMClient
    with patch('gam_sdk.client.GAMClient.__init__', return_value=None):
        client = Mock(spec=GAMClient)
        client.network_code = "123456789"
        client.is_authenticated = True
        client.test_connection.return_value = {
            'authenticated': True,
            'network_code': '123456789',
            'overall_status': 'healthy'
        }
        yield client


@pytest.fixture
def mock_report_result():
    """Create a mock ReportResult for testing."""
    try:
        from gam_sdk.reports import ReportResult
    except ImportError:
        from legacy.src.sdk.reports import ReportResult
    
    # Sample data structure
    rows = [
        {
            'dimensionValues': ['2024-01-01', 'Ad Unit 1'],
            'metricValueGroups': [{'primaryValues': ['1000', '50']}]
        },
        {
            'dimensionValues': ['2024-01-01', 'Ad Unit 2'],
            'metricValueGroups': [{'primaryValues': ['2000', '100']}]
        }
    ]
    
    dimension_headers = ['DATE', 'AD_UNIT_NAME']
    metric_headers = ['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 'TOTAL_LINE_ITEM_LEVEL_CLICKS']
    metadata = {'generated_at': '2024-01-01T00:00:00'}
    
    return ReportResult(rows, dimension_headers, metric_headers, metadata)


@pytest.fixture
def mock_oauth_credentials():
    """Mock OAuth2 credentials for testing."""
    credentials = Mock()
    credentials.expired = False
    credentials.expiry = None
    credentials.refresh_token = 'test_refresh_token'
    credentials.token = 'test_access_token'
    credentials.refresh = Mock()
    credentials.scopes = [
        'https://www.googleapis.com/auth/dfp',
        'https://www.googleapis.com/auth/admanager'
    ]
    return credentials


@pytest.fixture
def temp_report_file():
    """Create a temporary file for report export testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def sample_network_info():
    """Sample network information for testing."""
    return {
        'id': '123456789',
        'networkCode': '123456789',
        'displayName': 'Test Network',
        'timeZone': 'America/New_York',
        'currencyCode': 'USD',
        'effectiveRootAdUnitId': '987654321',
        'isTest': True
    }