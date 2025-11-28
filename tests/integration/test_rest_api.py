"""
Integration tests for REST API endpoints.
"""

import pytest
import json
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from src.api.main import create_app
from src.core.exceptions import APIError, AuthenticationError, ValidationError
from src.core.models import ReportStatus, ReportType


class TestHealthEndpoints:
    """Integration tests for health check endpoints."""
    
    @pytest.fixture
    def test_client(self):
        """Create test client."""
        app = create_app()
        return TestClient(app)
    
    def test_health_check(self, test_client):
        """Test basic health check endpoint."""
        response = test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_status_endpoint(self, test_client):
        """Test detailed status endpoint."""
        with patch('src.api.routes.health.get_auth_manager') as mock_get_auth:
            mock_auth = Mock()
            mock_auth.validate_credentials.return_value = True
            mock_get_auth.return_value = mock_auth
            
            response = test_client.get(
                "/api/v1/status",
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] == "healthy"
            assert data["services"]["api"] == "running"
            assert data["services"]["authentication"] == "configured"
            assert "gam_connection" in data["services"]
            assert "config_loaded" in data["checks"]
    
    def test_status_without_auth(self, test_client):
        """Test status endpoint without authentication."""
        response = test_client.get("/api/v1/status")
        
        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "authentication_error"
    
    def test_version_endpoint(self, test_client):
        """Test version endpoint."""
        response = test_client.get(
            "/api/v1/version",
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "version" in data
        assert "api_version" in data
        assert "gam_api_version" in data
        assert data["api_version"] == "v1"


class TestMetadataEndpoints:
    """Integration tests for metadata endpoints."""
    
    @pytest.fixture
    def test_client(self):
        """Create test client with mocked dependencies."""
        app = create_app()
        return TestClient(app)
    
    def test_get_dimensions_metrics(self, test_client):
        """Test getting dimensions and metrics."""
        response = test_client.get(
            "/api/v1/metadata/dimensions-metrics",
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "dimensions" in data
        assert "metrics" in data
        assert len(data["dimensions"]) > 0
        assert len(data["metrics"]) > 0
        
        # Check dimension structure
        dimension = data["dimensions"][0]
        assert "name" in dimension
        assert "description" in dimension
        assert "category" in dimension
    
    def test_get_dimensions_only(self, test_client):
        """Test getting dimensions only."""
        response = test_client.get(
            "/api/v1/metadata/dimensions-metrics?type=dimensions",
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "dimensions" in data
        assert "metrics" not in data
    
    def test_get_metrics_only(self, test_client):
        """Test getting metrics only."""
        response = test_client.get(
            "/api/v1/metadata/dimensions-metrics?type=metrics",
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "metrics" in data
        assert "dimensions" not in data
    
    def test_get_metadata_with_category_filter(self, test_client):
        """Test getting metadata with category filter."""
        response = test_client.get(
            "/api/v1/metadata/dimensions-metrics?category=time",
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned dimensions should be in time category
        for dim in data.get("dimensions", []):
            assert dim["category"].lower() == "time"
    
    def test_get_common_combinations(self, test_client):
        """Test getting common dimension-metric combinations."""
        response = test_client.get(
            "/api/v1/metadata/combinations",
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "combinations" in data
        assert len(data["combinations"]) > 0
        
        # Check combination structure
        combo = data["combinations"][0]
        assert "name" in combo
        assert "description" in combo
        assert "dimensions" in combo
        assert "metrics" in combo
        assert isinstance(combo["dimensions"], list)
        assert isinstance(combo["metrics"], list)
    
    def test_metadata_caching(self, test_client):
        """Test that metadata endpoints use caching."""
        # First request
        response1 = test_client.get(
            "/api/v1/metadata/dimensions-metrics",
            headers={"X-API-Key": "test-api-key"}
        )
        
        # Second request (should be cached)
        response2 = test_client.get(
            "/api/v1/metadata/dimensions-metrics",
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Data should be identical (from cache)
        assert response1.json() == response2.json()


class TestReportEndpoints:
    """Integration tests for report endpoints."""
    
    @pytest.fixture
    def test_client(self):
        """Create test client."""
        app = create_app()
        return TestClient(app)
    
    @pytest.fixture
    def mock_report_generator(self):
        """Mock report generator."""
        generator = Mock()
        
        # Mock quick report result
        mock_result = Mock()
        mock_result.total_rows = 100
        mock_result.data = [
            ['2024-01-01', 'Ad Unit 1', '1000', '50'],
            ['2024-01-02', 'Ad Unit 1', '1500', '75']
        ]
        mock_result.dimension_headers = ['DATE', 'AD_UNIT_NAME']
        mock_result.metric_headers = ['IMPRESSIONS', 'CLICKS']
        mock_result.execution_time = 2.5
        
        generator.generate_quick_report.return_value = mock_result
        
        # Mock list reports
        generator.list_reports.return_value = [
            {
                'reportId': 'report-1',
                'displayName': 'Delivery Report',
                'reportType': 'delivery',
                'createdAt': '2024-01-01T10:00:00Z'
            },
            {
                'reportId': 'report-2',
                'displayName': 'Inventory Report',
                'reportType': 'inventory',
                'createdAt': '2024-01-02T10:00:00Z'
            }
        ]
        
        return generator
    
    def test_quick_report_all_types(self, test_client, mock_report_generator):
        """Test all quick report types."""
        with patch('src.api.routes.reports.ReportGenerator', return_value=mock_report_generator):
            report_types = ["delivery", "inventory", "sales", "reach", "programmatic"]
            
            for report_type in report_types:
                response = test_client.post(
                    "/api/v1/reports/quick",
                    json={
                        "report_type": report_type,
                        "days_back": 7
                    },
                    headers={"X-API-Key": "test-api-key"}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["report_type"] == report_type
                assert data["total_rows"] == 100
    
    def test_quick_report_date_validation(self, test_client):
        """Test date validation in quick reports."""
        # Test invalid days_back
        response = test_client.post(
            "/api/v1/reports/quick",
            json={
                "report_type": "delivery",
                "days_back": 400  # Too many days
            },
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert response.status_code == 422
    
    def test_quick_report_format_options(self, test_client, mock_report_generator):
        """Test different output formats for quick reports."""
        with patch('src.api.routes.reports.ReportGenerator', return_value=mock_report_generator):
            formats = ["json", "csv", "xlsx"]
            
            for format_type in formats:
                with patch('src.api.routes.reports.get_formatter') as mock_formatter:
                    formatter = Mock()
                    if format_type == "csv":
                        formatter.format.return_value = "DATE,IMPRESSIONS\n2024-01-01,1000"
                    else:
                        formatter.format.return_value = {"formatted": True}
                    mock_formatter.return_value = formatter
                    
                    response = test_client.post(
                        "/api/v1/reports/quick",
                        json={
                            "report_type": "delivery",
                            "days_back": 7,
                            "format": format_type
                        },
                        headers={"X-API-Key": "test-api-key"}
                    )
                    
                    assert response.status_code == 200
    
    def test_custom_report_creation(self, test_client):
        """Test custom report creation with various options."""
        with patch('src.api.routes.reports.ReportGenerator') as MockGenerator:
            mock_generator = Mock()
            mock_report = Mock()
            mock_report.id = "custom-report-123"
            mock_report.name = "Custom Test Report"
            mock_report.status = ReportStatus.PENDING
            mock_report.created_at = datetime.now()
            
            mock_generator.return_value.create_report.return_value = mock_report
            
            with patch('src.api.routes.reports.validate_dimensions_list') as mock_validate_dims:
                with patch('src.api.routes.reports.validate_metrics_list') as mock_validate_metrics:
                    mock_validate_dims.return_value = ["DATE", "AD_UNIT_NAME"]
                    mock_validate_metrics.return_value = ["IMPRESSIONS", "CLICKS"]
                    
                    response = test_client.post(
                        "/api/v1/reports/custom",
                        json={
                            "name": "Custom Test Report",
                            "dimensions": ["DATE", "AD_UNIT_NAME"],
                            "metrics": ["IMPRESSIONS", "CLICKS"],
                            "report_type": "HISTORICAL",
                            "days_back": 30,
                            "filters": [
                                {
                                    "field": "AD_UNIT_NAME",
                                    "operator": "contains",
                                    "value": "Mobile"
                                }
                            ]
                        },
                        headers={"X-API-Key": "test-api-key"}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert data["report_id"] == "custom-report-123"
                    assert data["name"] == "Custom Test Report"
    
    def test_list_reports_with_pagination(self, test_client, mock_report_generator):
        """Test report listing with pagination."""
        with patch('src.api.routes.reports.ReportGenerator', return_value=mock_report_generator):
            # Test different page sizes
            page_sizes = [10, 20, 50]
            
            for page_size in page_sizes:
                response = test_client.get(
                    f"/api/v1/reports?limit={page_size}&page=1",
                    headers={"X-API-Key": "test-api-key"}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["page_size"] == page_size
                assert data["page"] == 1
    
    def test_report_error_handling(self, test_client):
        """Test error handling in report endpoints."""
        with patch('src.api.routes.reports.ReportGenerator') as MockGenerator:
            mock_generator = Mock()
            mock_generator.generate_quick_report.side_effect = APIError("API quota exceeded")
            MockGenerator.return_value = mock_generator
            
            response = test_client.post(
                "/api/v1/reports/quick",
                json={
                    "report_type": "delivery",
                    "days_back": 7
                },
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 500
            data = response.json()
            assert "API quota exceeded" in data["detail"]
    
    def test_get_report_by_id(self, test_client):
        """Test getting specific report by ID."""
        # This endpoint returns 501 Not Implemented
        response = test_client.get(
            "/api/v1/reports/report-123",
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert response.status_code == 501
        data = response.json()
        assert data["error"] == "not_implemented"
    
    def test_update_report(self, test_client):
        """Test updating report."""
        # This endpoint returns 501 Not Implemented
        response = test_client.put(
            "/api/v1/reports/report-123",
            json={"name": "Updated Report Name"},
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert response.status_code == 501
    
    def test_delete_report(self, test_client):
        """Test deleting report."""
        # This endpoint returns 501 Not Implemented
        response = test_client.delete(
            "/api/v1/reports/report-123",
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert response.status_code == 501


class TestAuthenticationIntegration:
    """Integration tests for API authentication."""
    
    @pytest.fixture
    def test_client(self):
        """Create test client."""
        app = create_app()
        return TestClient(app)
    
    def test_api_key_required(self, test_client):
        """Test that API key is required for protected endpoints."""
        endpoints = [
            ("/api/v1/reports/quick", "POST"),
            ("/api/v1/reports", "GET"),
            ("/api/v1/metadata/dimensions-metrics", "GET"),
            ("/api/v1/status", "GET")
        ]
        
        for endpoint, method in endpoints:
            if method == "GET":
                response = test_client.get(endpoint)
            else:
                response = test_client.post(endpoint, json={})
            
            assert response.status_code == 401
            data = response.json()
            assert data["error"] == "authentication_error"
    
    def test_invalid_api_key(self, test_client):
        """Test invalid API key."""
        response = test_client.get(
            "/api/v1/reports",
            headers={"X-API-Key": "invalid-key"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "authentication_error"
    
    def test_api_key_in_different_formats(self, test_client):
        """Test API key in different header formats."""
        # Test with Bearer token format
        response = test_client.get(
            "/api/v1/version",
            headers={"Authorization": "Bearer test-api-key"}
        )
        
        # Should still require X-API-Key header
        assert response.status_code == 401


class TestErrorHandlingIntegration:
    """Integration tests for error handling."""
    
    @pytest.fixture
    def test_client(self):
        """Create test client."""
        app = create_app()
        return TestClient(app)
    
    def test_404_not_found(self, test_client):
        """Test 404 error for non-existent endpoint."""
        response = test_client.get(
            "/api/v1/nonexistent",
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert response.status_code == 404
    
    def test_method_not_allowed(self, test_client):
        """Test 405 error for wrong HTTP method."""
        response = test_client.patch(
            "/api/v1/reports/quick",
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert response.status_code == 405
    
    def test_validation_error_format(self, test_client):
        """Test validation error response format."""
        response = test_client.post(
            "/api/v1/reports/quick",
            json={
                "report_type": 123,  # Should be string
                "days_back": "seven"  # Should be int
            },
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        
        # FastAPI validation error structure
        if isinstance(data["detail"], list):
            assert len(data["detail"]) > 0
            assert "loc" in data["detail"][0]
            assert "msg" in data["detail"][0]
    
    def test_internal_server_error(self, test_client):
        """Test 500 error handling."""
        with patch('src.api.routes.reports.ReportGenerator') as MockGenerator:
            MockGenerator.side_effect = Exception("Unexpected error")
            
            response = test_client.post(
                "/api/v1/reports/quick",
                json={
                    "report_type": "delivery",
                    "days_back": 7
                },
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data


class TestCORSAndMiddleware:
    """Integration tests for CORS and middleware."""
    
    @pytest.fixture
    def test_client(self):
        """Create test client."""
        app = create_app()
        return TestClient(app)
    
    def test_cors_headers(self, test_client):
        """Test CORS headers are present."""
        response = test_client.options(
            "/api/v1/reports",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
        )
        
        # Check for CORS headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
    
    def test_request_id_header(self, test_client):
        """Test that request ID is added to responses."""
        response = test_client.get("/health")
        
        # Check for request ID header
        assert "x-request-id" in response.headers