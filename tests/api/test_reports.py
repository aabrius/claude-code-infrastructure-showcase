"""
API tests for report endpoints.
"""

import pytest
import json
from unittest.mock import patch, Mock


class TestQuickReportsEndpoint:
    """Test quick reports endpoint."""
    
    def test_quick_report_success(self, api_client, mock_report_generator):
        """Test successful quick report generation."""
        with patch('src.api.routes.reports.ReportGenerator', return_value=mock_report_generator):
            payload = {
                "report_type": "delivery",
                "days_back": 30,
                "format": "json"
            }
            
            response = api_client.post(
                "/api/v1/reports/quick",
                json=payload,
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["report_type"] == "delivery"
            assert data["days_back"] == 30
            assert data["total_rows"] == 100
            assert "dimensions" in data
            assert "metrics" in data
            assert "data" in data
    
    def test_quick_report_validation_error(self, api_client):
        """Test quick report with validation error."""
        payload = {
            "report_type": "invalid_type",  # Invalid report type
            "days_back": 30
        }
        
        response = api_client.post(
            "/api/v1/reports/quick",
            json=payload,
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data
    
    def test_quick_report_missing_auth(self, api_client):
        """Test quick report without authentication."""
        payload = {
            "report_type": "delivery",
            "days_back": 30
        }
        
        response = api_client.post("/api/v1/reports/quick", json=payload)
        
        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "authentication_error"
    
    def test_quick_report_invalid_days_back(self, api_client):
        """Test quick report with invalid days_back value."""
        payload = {
            "report_type": "delivery",
            "days_back": 500  # Exceeds maximum
        }
        
        response = api_client.post(
            "/api/v1/reports/quick",
            json=payload,
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_quick_report_csv_format(self, api_client, mock_report_generator):
        """Test quick report with CSV format."""
        with patch('src.api.routes.reports.ReportGenerator', return_value=mock_report_generator):
            with patch('src.api.routes.reports.get_formatter') as mock_get_formatter:
                mock_formatter = Mock()
                mock_formatter.format.return_value = "DATE,AD_UNIT_NAME,IMPRESSIONS\n2024-01-01,Unit1,1000"
                mock_get_formatter.return_value = mock_formatter
                
                payload = {
                    "report_type": "delivery",
                    "days_back": 7,
                    "format": "csv"
                }
                
                response = api_client.post(
                    "/api/v1/reports/quick",
                    json=payload,
                    headers={"X-API-Key": "test-api-key"}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert isinstance(data["data"], str)  # CSV should be string


class TestCustomReportsEndpoint:
    """Test custom reports endpoint."""
    
    def test_custom_report_success(self, api_client, mock_report_generator):
        """Test successful custom report creation."""
        with patch('src.api.routes.reports.ReportGenerator', return_value=mock_report_generator):
            with patch('src.api.routes.reports.validate_dimensions_list') as mock_validate_dims:
                with patch('src.api.routes.reports.validate_metrics_list') as mock_validate_metrics:
                    mock_validate_dims.return_value = ["DATE", "AD_UNIT_NAME"]
                    mock_validate_metrics.return_value = ["TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS"]
                    
                    # Mock report object
                    mock_report = Mock()
                    mock_report.id = "test-report-123"
                    mock_report.name = "Test Custom Report"
                    mock_report.status.value = "PENDING"
                    mock_report.created_at = "2024-01-01T12:00:00"
                    
                    mock_report_generator.create_report.return_value = mock_report
                    
                    payload = {
                        "name": "Test Custom Report",
                        "dimensions": ["DATE", "AD_UNIT_NAME"],
                        "metrics": ["TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS"],
                        "report_type": "HISTORICAL",
                        "days_back": 7,
                        "run_immediately": False
                    }
                    
                    response = api_client.post(
                        "/api/v1/reports/custom",
                        json=payload,
                        headers={"X-API-Key": "test-api-key"}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    
                    assert data["action"] == "created"
                    assert data["report_id"] == "test-report-123"
                    assert data["name"] == "Test Custom Report"
                    assert data["status"] == "PENDING"
    
    def test_custom_report_run_immediately(self, api_client, mock_report_generator):
        """Test custom report with immediate execution."""
        with patch('src.api.routes.reports.ReportGenerator', return_value=mock_report_generator):
            with patch('src.api.routes.reports.validate_dimensions_list') as mock_validate_dims:
                with patch('src.api.routes.reports.validate_metrics_list') as mock_validate_metrics:
                    mock_validate_dims.return_value = ["DATE"]
                    mock_validate_metrics.return_value = ["TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS"]
                    
                    # Mock report and result objects
                    mock_report = Mock()
                    mock_report.id = "test-report-456"
                    mock_report.name = "Immediate Report"
                    mock_report.status.value = "COMPLETED"
                    mock_report.created_at = "2024-01-01T12:00:00"
                    
                    mock_result = Mock()
                    mock_result.total_rows = 50
                    mock_result.execution_time = 1.5
                    
                    mock_report_generator.create_report.return_value = mock_report
                    mock_report_generator.run_report.return_value = mock_report
                    mock_report_generator.fetch_results.return_value = mock_result
                    
                    payload = {
                        "name": "Immediate Report",
                        "dimensions": ["DATE"],
                        "metrics": ["TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS"],
                        "run_immediately": True
                    }
                    
                    response = api_client.post(
                        "/api/v1/reports/custom",
                        json=payload,
                        headers={"X-API-Key": "test-api-key"}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    
                    assert data["action"] == "created_and_executed"
                    assert data["total_rows"] == 50
                    assert data["execution_time"] == 1.5
    
    def test_custom_report_validation_error(self, api_client):
        """Test custom report with invalid dimensions/metrics."""
        with patch('src.api.routes.reports.validate_dimensions_list') as mock_validate:
            mock_validate.side_effect = Exception("Invalid dimension")
            
            payload = {
                "name": "Invalid Report",
                "dimensions": ["INVALID_DIMENSION"],
                "metrics": ["INVALID_METRIC"]
            }
            
            response = api_client.post(
                "/api/v1/reports/custom",
                json=payload,
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 400
            data = response.json()
            assert "Invalid dimension" in data["detail"]


class TestListReportsEndpoint:
    """Test list reports endpoint."""
    
    def test_list_reports_success(self, api_client, mock_report_generator):
        """Test successful report listing."""
        with patch('src.api.routes.reports.ReportGenerator', return_value=mock_report_generator):
            response = api_client.get(
                "/api/v1/reports",
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["total_reports"] == 2
            assert len(data["reports"]) == 2
            assert data["page"] == 1
            assert data["page_size"] == 20
            
            # Check report structure
            report = data["reports"][0]
            assert "id" in report
            assert "name" in report
    
    def test_list_reports_pagination(self, api_client, mock_report_generator):
        """Test report listing with pagination."""
        with patch('src.api.routes.reports.ReportGenerator', return_value=mock_report_generator):
            response = api_client.get(
                "/api/v1/reports?limit=1&page=2",
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["page"] == 2
            assert data["page_size"] == 1
    
    def test_list_reports_invalid_pagination(self, api_client):
        """Test report listing with invalid pagination parameters."""
        response = api_client.get(
            "/api/v1/reports?limit=200&page=0",  # Invalid values
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert response.status_code == 422


class TestQuickReportTypesEndpoint:
    """Test quick report types endpoint."""
    
    def test_get_quick_report_types(self, api_client):
        """Test getting available quick report types."""
        with patch('src.api.routes.reports.list_quick_report_types') as mock_list_types:
            mock_list_types.return_value = {
                "delivery": {"description": "Delivery metrics"},
                "inventory": {"description": "Inventory analysis"}
            }
            
            response = api_client.get(
                "/api/v1/reports/quick-types",
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert "quick_report_types" in data["data"]
            assert "delivery" in data["data"]["quick_report_types"]
            assert "inventory" in data["data"]["quick_report_types"]