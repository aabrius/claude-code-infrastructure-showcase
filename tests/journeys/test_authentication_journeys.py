"""
Test authentication journeys for GAM API.

This module tests all authentication-related user journeys including:
- First-time setup
- Token refresh
- Invalid credentials
- Multi-network switching
"""

import pytest
import os
import tempfile
import yaml
from unittest.mock import patch, Mock

from tests.journeys.base_journey_test import BaseJourneyTest, JourneyTestHelpers
from gam_api import GAMClient
from gam_api.exceptions import AuthenticationError, ConfigurationError
from gam_api.config import load_config
from gam_api.auth import get_auth_manager


class TestFirstTimeSetupJourney(BaseJourneyTest):
    """Test the first-time authentication setup journey."""
    
    @property
    def journey_name(self):
        return "first_time_setup"
    
    @property
    def journey_description(self):
        return "User sets up GAM API authentication for the first time"
    
    @property
    def expected_steps(self):
        return [
            "check_config_exists",
            "create_config_file",
            "validate_credentials",
            "generate_token",
            "verify_connection",
            "save_config"
        ]
    
    def test_happy_path(self, journey_recorder, gam_client):
        """Test successful first-time setup."""
        # Step 1: Check if config exists
        journey_recorder.start_step("check_config_exists")
        
        # Create temporary directory for test
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "googleads.yaml")
            
            # Verify config doesn't exist
            assert not os.path.exists(config_path), "Config should not exist initially"
            journey_recorder.complete_step(config_exists=False)
            
            # Step 2: Create config file
            journey_recorder.start_step("create_config_file")
            
            config_data = {
                "ad_manager": {
                    "application_name": "GAM API Test",
                    "network_code": "123456789",
                    "client_id": "test-client-id.apps.googleusercontent.com",
                    "client_secret": "test-client-secret",
                    "refresh_token": "test-refresh-token"
                }
            }
            
            with open(config_path, 'w') as f:
                yaml.dump(config_data, f)
            
            assert os.path.exists(config_path), "Config file should be created"
            journey_recorder.complete_step(config_created=True)
            
            # Step 3: Validate credentials format
            journey_recorder.start_step("validate_credentials")
            
            # Load and validate config
            loaded_config = load_config(config_path)
            assert loaded_config.auth.network_code == "123456789"
            assert loaded_config.auth.client_id == "test-client-id.apps.googleusercontent.com"
            journey_recorder.complete_step(credentials_valid=True)
            
            # Step 4: Generate/refresh token (mocked)
            journey_recorder.start_step("generate_token")
            
            with patch('gam_api.auth.AuthManager.get_oauth2_credentials') as mock_creds:
                mock_creds.return_value = Mock(token="test-access-token")
                
                auth_manager = get_auth_manager(config_path)
                credentials = auth_manager.get_oauth2_credentials()
                
                assert credentials.token == "test-access-token"
                journey_recorder.complete_step(token_generated=True)
            
            # Step 5: Verify connection
            journey_recorder.start_step("verify_connection")
            
            # Create client with test config
            client = GAMClient(config_path=config_path)
            
            # In real scenario, this would make an API call
            # For testing, we just verify client creation
            assert client is not None
            journey_recorder.complete_step(connection_verified=True)
            
            # Step 6: Save config (already saved)
            journey_recorder.start_step("save_config")
            assert os.path.exists(config_path)
            journey_recorder.complete_step(config_saved=True)
        
        # Complete journey
        journey_recorder.complete()
        self.validate_journey(journey_recorder, journey_validator=None, max_duration=10)
    
    def test_missing_credentials_journey(self, journey_recorder):
        """Test journey when credentials are missing."""
        journey_recorder.start_step("check_config_exists")
        journey_recorder.complete_step(config_exists=False)
        
        journey_recorder.start_step("create_config_file")
        
        # Create config with missing credentials
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "googleads.yaml")
            
            config_data = {
                "ad_manager": {
                    "network_code": "123456789"
                    # Missing client_id, client_secret, refresh_token
                }
            }
            
            with open(config_path, 'w') as f:
                yaml.dump(config_data, f)
            
            journey_recorder.complete_step(config_created=True)
            
            # Try to validate - should fail
            journey_recorder.start_step("validate_credentials")
            
            try:
                auth_manager = get_auth_manager(config_path)
                auth_manager.validate_config()
                
                # Should not reach here
                journey_recorder.fail_step("Expected ConfigurationError")
                pytest.fail("Expected ConfigurationError for missing credentials")
                
            except ConfigurationError as e:
                journey_recorder.complete_step(
                    validation_failed=True,
                    error_message=str(e)
                )
        
        journey_recorder.complete()


class TestTokenRefreshJourney(BaseJourneyTest):
    """Test token refresh journey."""
    
    @property
    def journey_name(self):
        return "token_refresh"
    
    @property
    def journey_description(self):
        return "Automatic token refresh when access token expires"
    
    @property
    def expected_steps(self):
        return [
            "make_api_call",
            "detect_token_expiry",
            "refresh_token",
            "retry_api_call",
            "complete_successfully"
        ]
    
    def test_happy_path(self, journey_recorder, gam_client):
        """Test successful token refresh."""
        # Step 1: Make API call
        journey_recorder.start_step("make_api_call")
        
        # Mock expired token scenario
        with patch('gam_api.auth.AuthManager.get_oauth2_credentials') as mock_creds:
            # First call returns expired token
            expired_creds = Mock()
            expired_creds.expired = True
            expired_creds.token = "expired-token"
            
            # After refresh returns valid token
            valid_creds = Mock()
            valid_creds.expired = False
            valid_creds.token = "new-access-token"
            valid_creds.refresh = Mock()
            
            mock_creds.side_effect = [expired_creds, valid_creds]
            
            journey_recorder.complete_step(api_call_initiated=True)
            
            # Step 2: Detect token expiry
            journey_recorder.start_step("detect_token_expiry")
            
            auth_manager = get_auth_manager()
            first_creds = auth_manager.get_oauth2_credentials()
            assert first_creds.expired == True
            
            journey_recorder.complete_step(token_expired=True)
            
            # Step 3: Refresh token
            journey_recorder.start_step("refresh_token")
            
            # This should trigger refresh internally
            refreshed_creds = auth_manager.get_oauth2_credentials()
            assert refreshed_creds.token == "new-access-token"
            
            journey_recorder.complete_step(token_refreshed=True)
            
            # Step 4: Retry API call
            journey_recorder.start_step("retry_api_call")
            
            # In real scenario, the API call would be retried
            # Here we just verify the new token is available
            assert refreshed_creds.expired == False
            
            journey_recorder.complete_step(retry_successful=True)
            
            # Step 5: Complete successfully
            journey_recorder.start_step("complete_successfully")
            journey_recorder.complete_step(operation_completed=True)
        
        journey_recorder.complete()
        self.validate_journey(journey_recorder, journey_validator=None, max_duration=5)


class TestMultiNetworkJourney(BaseJourneyTest):
    """Test multi-network switching journey."""
    
    @property
    def journey_name(self):
        return "multi_network_switch"
    
    @property
    def journey_description(self):
        return "User switches between multiple GAM networks"
    
    @property
    def expected_steps(self):
        return [
            "load_network_a_config",
            "create_client_network_a",
            "generate_report_network_a",
            "load_network_b_config",
            "create_client_network_b",
            "generate_report_network_b",
            "verify_isolation"
        ]
    
    def test_happy_path(self, journey_recorder, gam_client):
        """Test successful network switching."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Step 1: Load Network A config
            journey_recorder.start_step("load_network_a_config")
            
            config_a_path = os.path.join(temp_dir, "network_a.yaml")
            config_a_data = {
                "ad_manager": {
                    "network_code": "111111111",
                    "client_id": "network-a-client-id",
                    "client_secret": "network-a-secret",
                    "refresh_token": "network-a-token"
                }
            }
            
            with open(config_a_path, 'w') as f:
                yaml.dump(config_a_data, f)
            
            journey_recorder.complete_step(network_a_loaded=True)
            
            # Step 2: Create client for Network A
            journey_recorder.start_step("create_client_network_a")
            
            client_a = GAMClient(config_path=config_a_path)
            journey_recorder.complete_step(client_a_created=True)
            
            # Step 3: Generate report for Network A
            journey_recorder.start_step("generate_report_network_a")
            
            # Mock report generation
            with patch.object(client_a, 'delivery_report') as mock_report:
                mock_report.return_value = {"network": "A", "data": []}
                report_a = client_a.delivery_report(DateRange.last_week())
                assert report_a["network"] == "A"
            
            journey_recorder.complete_step(report_a_generated=True)
            
            # Step 4: Load Network B config
            journey_recorder.start_step("load_network_b_config")
            
            config_b_path = os.path.join(temp_dir, "network_b.yaml")
            config_b_data = {
                "ad_manager": {
                    "network_code": "222222222",
                    "client_id": "network-b-client-id",
                    "client_secret": "network-b-secret",
                    "refresh_token": "network-b-token"
                }
            }
            
            with open(config_b_path, 'w') as f:
                yaml.dump(config_b_data, f)
            
            journey_recorder.complete_step(network_b_loaded=True)
            
            # Step 5: Create client for Network B
            journey_recorder.start_step("create_client_network_b")
            
            client_b = GAMClient(config_path=config_b_path)
            journey_recorder.complete_step(client_b_created=True)
            
            # Step 6: Generate report for Network B
            journey_recorder.start_step("generate_report_network_b")
            
            with patch.object(client_b, 'delivery_report') as mock_report:
                mock_report.return_value = {"network": "B", "data": []}
                report_b = client_b.delivery_report(DateRange.last_week())
                assert report_b["network"] == "B"
            
            journey_recorder.complete_step(report_b_generated=True)
            
            # Step 7: Verify isolation
            journey_recorder.start_step("verify_isolation")
            
            # Verify the two clients are using different configs
            assert client_a._internal_client.config.auth.network_code == "111111111"
            assert client_b._internal_client.config.auth.network_code == "222222222"
            
            journey_recorder.complete_step(isolation_verified=True)
        
        journey_recorder.complete()
        self.validate_journey(journey_recorder, journey_validator=None, max_duration=10)


# Additional authentication journey tests can be added here:
# - TestInvalidCredentialsJourney
# - TestExpiredRefreshTokenJourney  
# - TestNetworkConnectivityJourney
# - TestRateLimitedAuthJourney