"""
API tests for health and status endpoints.
"""

import pytest
from unittest.mock import patch


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check_success(self, api_client):
        """Test successful health check."""
        with patch('src.core.auth.get_auth_manager') as mock_get_auth:
            with patch('src.core.client.get_gam_client') as mock_get_client:
                # Mock successful authentication and connection
                mock_auth = mock_get_auth.return_value
                mock_auth.validate_config.return_value = True
                
                mock_client = mock_get_client.return_value
                mock_client.test_connection.return_value = True
                
                response = api_client.get("/api/v1/health")
                
                assert response.status_code == 200
                data = response.json()
                
                assert data["status"] == "healthy"
                assert data["gam_connection"] == "healthy"
                assert "components" in data
                assert data["components"]["api"] == "healthy"
                assert data["components"]["gam_connection"] == "healthy"
    
    def test_health_check_gam_failure(self, api_client):
        """Test health check with GAM connection failure."""
        with patch('src.core.auth.get_auth_manager') as mock_get_auth:
            # Mock authentication failure
            mock_auth = mock_get_auth.return_value
            mock_auth.validate_config.side_effect = Exception("Auth failed")
            
            response = api_client.get("/api/v1/health")
            
            assert response.status_code == 200  # Health endpoint doesn't fail
            data = response.json()
            
            assert data["status"] == "degraded"
            assert data["gam_connection"] == "unhealthy"
            assert data["components"]["api"] == "healthy"
            assert data["components"]["gam_connection"] == "unhealthy"
    
    def test_health_check_fields(self, api_client):
        """Test health check response structure."""
        response = api_client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Required fields
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "gam_connection" in data
        assert "components" in data
        
        # Version should be set
        assert data["version"] == "1.0.0"


class TestStatusEndpoint:
    """Test detailed status endpoint."""
    
    def test_status_success(self, api_client):
        """Test successful status check."""
        with patch('src.api.auth.AuthManager') as mock_auth_manager_class:
            mock_auth_manager = mock_auth_manager_class.return_value
            mock_auth_manager.validate_gam_auth.return_value = True
            mock_auth_manager.get_auth_status.return_value = {
                "gam_auth": "valid",
                "config_loaded": True
            }
            
            response = api_client.get("/api/v1/status")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["api_status"] == "running"
            assert data["gam_status"] == "healthy"
            assert data["auth_status"] == "healthy"
            assert data["config_status"] == "healthy"
            assert "uptime" in data
            assert data["version"] == "1.0.0"
    
    def test_status_gam_unhealthy(self, api_client):
        """Test status with unhealthy GAM connection."""
        with patch('src.api.auth.AuthManager') as mock_auth_manager_class:
            mock_auth_manager = mock_auth_manager_class.return_value
            mock_auth_manager.validate_gam_auth.return_value = False
            mock_auth_manager.get_auth_status.return_value = {
                "gam_auth": "invalid",
                "config_loaded": True
            }
            
            response = api_client.get("/api/v1/status")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["gam_status"] == "unhealthy"
            assert data["auth_status"] == "unhealthy"
    
    def test_status_config_issues(self, api_client):
        """Test status with configuration issues."""
        with patch('src.api.auth.AuthManager') as mock_auth_manager_class:
            mock_auth_manager = mock_auth_manager_class.return_value
            mock_auth_manager.validate_gam_auth.return_value = False
            mock_auth_manager.get_auth_status.return_value = {
                "gam_auth": "invalid",
                "config_loaded": False,
                "config_error": "Missing config file"
            }
            
            response = api_client.get("/api/v1/status")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["config_status"] == "unhealthy"
    
    def test_status_error_handling(self, api_client):
        """Test status endpoint error handling."""
        with patch('src.api.auth.AuthManager') as mock_auth_manager_class:
            mock_auth_manager_class.side_effect = Exception("Auth manager error")
            
            response = api_client.get("/api/v1/status")
            
            assert response.status_code == 500
            data = response.json()
            
            assert data["error"] == "internal_error"
            assert "message" in data


class TestVersionEndpoint:
    """Test version endpoint."""
    
    def test_version_info(self, api_client):
        """Test version information endpoint."""
        response = api_client.get("/api/v1/version")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "data" in data
        
        version_data = data["data"]
        assert version_data["api_version"] == "1.0.0"
        assert "python_version" in version_data
        assert "platform" in version_data
        assert "startup_time" in version_data
        assert "uptime_seconds" in version_data
    
    def test_version_uptime(self, api_client):
        """Test that uptime is a positive number."""
        response = api_client.get("/api/v1/version")
        
        assert response.status_code == 200
        data = response.json()
        
        uptime = data["data"]["uptime_seconds"]
        assert isinstance(uptime, (int, float))
        assert uptime >= 0