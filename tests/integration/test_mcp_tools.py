"""
Integration tests for MCP tools.
"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from datetime import datetime, timedelta

# Import from new modular location
import sys
from pathlib import Path

# Add the MCP server application to path
mcp_server_path = Path(__file__).parent.parent.parent / "applications" / "mcp-server"
sys.path.insert(0, str(mcp_server_path))

from fastmcp_server import (
    gam_quick_report,
    gam_create_report,
    gam_list_reports,
    gam_get_dimensions_metrics,
    gam_get_common_combinations,
    gam_get_quick_report_types
)

try:
    from gam_api.exceptions import GAMError, ValidationError
    from gam_api.models import ReportType, ReportStatus
except ImportError:
    # Fallback to legacy imports
    from src.core.exceptions import GAMError, ValidationError
    from src.core.models import ReportType, ReportStatus


class TestGAMQuickReport:
    """Integration tests for gam_quick_report tool."""
    
    @pytest.fixture
    def mock_report_generator(self):
        """Mock report generator for testing."""
        with patch('fastmcp_server.ReportGenerator') as MockGenerator:
            mock_instance = Mock()
            MockGenerator.return_value = mock_instance
            
            # Mock result
            mock_result = Mock()
            mock_result.total_rows = 100
            mock_result.data = [
                ['2024-01-01', 'Ad Unit 1', '1000', '50'],
                ['2024-01-01', 'Ad Unit 2', '2000', '100']
            ]
            mock_result.dimension_headers = ['DATE', 'AD_UNIT_NAME']
            mock_result.metric_headers = ['IMPRESSIONS', 'CLICKS']
            mock_result.execution_time = 2.5
            
            mock_instance.generate_quick_report.return_value = mock_result
            
            yield mock_instance
    
    @pytest.mark.asyncio
    @patch('fastmcp_server.get_auth_manager')
    async def test_quick_report_success(self, mock_get_auth, mock_report_generator):
        """Test successful quick report generation."""
        mock_get_auth.return_value = Mock()  # Valid auth manager
        
        # Call the async MCP tool function
        result = await gam_quick_report.fn(
            report_type="delivery",
            days_back=7,
            format="json"
        )
        
        result_data = json.loads(result)
        assert result_data["success"] is True
        assert result_data["report_type"] == "delivery"
        assert result_data["days_back"] == 7
        assert result_data["total_rows"] == 100
        assert "data" in result_data
        
        # Verify report generator was called correctly
        mock_report_generator.generate_quick_report.assert_called_once_with("delivery", 7)
    
    @patch('fastmcp_server.get_auth_manager')
    def test_quick_report_all_types(self, mock_get_auth, mock_report_generator):
        """Test all quick report types."""
        mock_get_auth.return_value = Mock()
        
        report_types = ["delivery", "inventory", "sales", "reach", "programmatic"]
        
        for report_type in report_types:
            result = gam_quick_report(
                report_type=report_type,
                days_back=30,
                format="json"
            )
            
            result_data = json.loads(result)
            assert result_data["success"] is True
            assert result_data["report_type"] == report_type
    
    @patch('fastmcp_server.get_auth_manager')
    def test_quick_report_csv_format(self, mock_get_auth, mock_report_generator):
        """Test quick report with CSV format."""
        mock_get_auth.return_value = Mock()
        
        with patch('fastmcp_server.get_formatter') as mock_get_formatter:
            mock_formatter = Mock()
            mock_formatter.format.return_value = "DATE,AD_UNIT_NAME,IMPRESSIONS,CLICKS\n2024-01-01,Ad Unit 1,1000,50"
            mock_get_formatter.return_value = mock_formatter
            
            result = gam_quick_report(
                report_type="delivery",
                days_back=7,
                format="csv"
            )
            
            assert "DATE,AD_UNIT_NAME,IMPRESSIONS,CLICKS" in result
            mock_get_formatter.assert_called_with("csv")
    
    @patch('fastmcp_server.get_auth_manager')
    def test_quick_report_no_auth(self, mock_get_auth):
        """Test quick report without authentication."""
        mock_get_auth.return_value = None  # No auth manager
        
        result = gam_quick_report(
            report_type="delivery",
            days_back=7,
            format="json"
        )
        
        result_data = json.loads(result)
        assert result_data["success"] is False
        assert "Google Ad Manager not configured" in result_data["error"]
    
    @patch('fastmcp_server.get_auth_manager')
    def test_quick_report_error_handling(self, mock_get_auth, mock_report_generator):
        """Test error handling in quick report."""
        mock_get_auth.return_value = Mock()
        mock_report_generator.generate_quick_report.side_effect = GAMError("API Error")
        
        result = gam_quick_report(
            report_type="delivery",
            days_back=7,
            format="json"
        )
        
        result_data = json.loads(result)
        assert result_data["success"] is False
        assert "API Error" in result_data["error"]


class TestGAMCreateReport:
    """Integration tests for gam_create_report tool."""
    
    @pytest.fixture
    def mock_report_generator(self):
        """Mock report generator for testing."""
        with patch('fastmcp_server.ReportGenerator') as MockGenerator:
            mock_instance = Mock()
            MockGenerator.return_value = mock_instance
            
            # Mock create_report response
            mock_instance.create_report.return_value = {
                "report_id": "report-123",
                "status": "PENDING",
                "created_at": datetime.now().isoformat()
            }
            
            yield mock_instance
    
    @patch('fastmcp_server.get_auth_manager')
    def test_create_report_success(self, mock_get_auth, mock_report_generator):
        """Test successful report creation."""
        mock_get_auth.return_value = Mock()
        
        result = gam_create_report(
            name="Test Report",
            dimensions=["DATE", "AD_UNIT_NAME"],
            metrics=["IMPRESSIONS", "CLICKS"],
            start_date="2024-01-01",
            end_date="2024-01-31",
            save_definition=False
        )
        
        result_data = json.loads(result)
        assert result_data["success"] is True
        assert result_data["report_id"] == "report-123"
        assert result_data["status"] == "PENDING"
        
        # Verify create_report was called with correct params
        call_args = mock_report_generator.create_report.call_args[0][0]
        assert call_args["name"] == "Test Report"
        assert call_args["dimensions"] == ["DATE", "AD_UNIT_NAME"]
        assert call_args["metrics"] == ["IMPRESSIONS", "CLICKS"]
    
    @patch('fastmcp_server.get_auth_manager')
    def test_create_report_with_filters(self, mock_get_auth, mock_report_generator):
        """Test report creation with filters."""
        mock_get_auth.return_value = Mock()
        
        result = gam_create_report(
            name="Filtered Report",
            dimensions=["DATE", "ADVERTISER_NAME"],
            metrics=["REVENUE", "ECPM"],
            start_date="2024-01-01",
            end_date="2024-01-31",
            filters=[
                {"field": "ADVERTISER_NAME", "operator": "equals", "value": "Test Advertiser"}
            ],
            save_definition=False
        )
        
        result_data = json.loads(result)
        assert result_data["success"] is True
        
        # Verify filters were passed
        call_args = mock_report_generator.create_report.call_args[0][0]
        assert len(call_args["filters"]) == 1
        assert call_args["filters"][0]["field"] == "ADVERTISER_NAME"
    
    @patch('fastmcp_server.get_auth_manager')
    def test_create_report_validation_error(self, mock_get_auth):
        """Test report creation with invalid parameters."""
        mock_get_auth.return_value = Mock()
        
        with patch('fastmcp_server.validate_dimensions_list') as mock_validate:
            mock_validate.side_effect = ValidationError("Invalid dimension: INVALID_DIM")
            
            result = gam_create_report(
                name="Invalid Report",
                dimensions=["INVALID_DIM"],
                metrics=["IMPRESSIONS"],
                start_date="2024-01-01",
                end_date="2024-01-31",
                save_definition=False
            )
            
            result_data = json.loads(result)
            assert result_data["success"] is False
            assert "Invalid dimension" in result_data["error"]
    
    @patch('fastmcp_server.get_auth_manager')
    def test_create_report_save_definition(self, mock_get_auth, mock_report_generator):
        """Test saving report definition."""
        mock_get_auth.return_value = Mock()
        
        result = gam_create_report(
            name="Saved Report",
            dimensions=["DATE"],
            metrics=["IMPRESSIONS"],
            start_date="2024-01-01",
            end_date="2024-01-31",
            save_definition=True
        )
        
        result_data = json.loads(result)
        assert result_data["success"] is True
        assert result_data.get("definition_saved") is True


class TestGAMListReports:
    """Integration tests for gam_list_reports tool."""
    
    @pytest.fixture
    def mock_report_generator(self):
        """Mock report generator for testing."""
        with patch('fastmcp_server.ReportGenerator') as MockGenerator:
            mock_instance = Mock()
            MockGenerator.return_value = mock_instance
            
            # Mock list_reports response
            mock_instance.list_reports.return_value = [
                {
                    "report_id": "report-1",
                    "name": "Delivery Report",
                    "type": "delivery",
                    "created_at": "2024-01-01T10:00:00Z",
                    "last_run": "2024-01-31T10:00:00Z"
                },
                {
                    "report_id": "report-2",
                    "name": "Inventory Report",
                    "type": "inventory",
                    "created_at": "2024-01-02T10:00:00Z",
                    "last_run": "2024-01-30T10:00:00Z"
                }
            ]
            
            yield mock_instance
    
    @patch('fastmcp_server.get_auth_manager')
    def test_list_reports_success(self, mock_get_auth, mock_report_generator):
        """Test successful report listing."""
        mock_get_auth.return_value = Mock()
        
        result = gam_list_reports(limit=10)
        
        result_data = json.loads(result)
        assert result_data["success"] is True
        assert len(result_data["reports"]) == 2
        assert result_data["reports"][0]["name"] == "Delivery Report"
        assert result_data["reports"][1]["name"] == "Inventory Report"
    
    @patch('fastmcp_server.get_auth_manager')
    def test_list_reports_with_filters(self, mock_get_auth, mock_report_generator):
        """Test listing reports with filters."""
        mock_get_auth.return_value = Mock()
        
        # Test with report type filter
        mock_report_generator.list_reports.return_value = [
            {
                "report_id": "report-1",
                "name": "Delivery Report",
                "type": "delivery"
            }
        ]
        
        result = gam_list_reports(
            limit=5,
            report_type="delivery",
            search="delivery"
        )
        
        result_data = json.loads(result)
        assert result_data["success"] is True
        assert len(result_data["reports"]) == 1
        assert result_data["reports"][0]["type"] == "delivery"
    
    @patch('fastmcp_server.get_auth_manager')
    def test_list_reports_empty(self, mock_get_auth, mock_report_generator):
        """Test listing reports when none exist."""
        mock_get_auth.return_value = Mock()
        mock_report_generator.list_reports.return_value = []
        
        result = gam_list_reports()
        
        result_data = json.loads(result)
        assert result_data["success"] is True
        assert len(result_data["reports"]) == 0
        assert result_data["total"] == 0


class TestGAMGetDimensionsMetrics:
    """Integration tests for gam_get_dimensions_metrics tool."""
    
    @patch('fastmcp_server.get_auth_manager')
    def test_get_dimensions_metrics_both(self, mock_get_auth):
        """Test getting both dimensions and metrics."""
        mock_get_auth.return_value = Mock()
        
        result = gam_get_dimensions_metrics(
            report_type="HISTORICAL",
            category="both"
        )
        
        result_data = json.loads(result)
        assert result_data["success"] is True
        assert "dimensions" in result_data
        assert "metrics" in result_data
        assert len(result_data["dimensions"]) > 0
        assert len(result_data["metrics"]) > 0
    
    @patch('fastmcp_server.get_auth_manager')
    def test_get_dimensions_only(self, mock_get_auth):
        """Test getting dimensions only."""
        mock_get_auth.return_value = Mock()
        
        result = gam_get_dimensions_metrics(
            report_type="HISTORICAL",
            category="dimensions"
        )
        
        result_data = json.loads(result)
        assert result_data["success"] is True
        assert "dimensions" in result_data
        assert "metrics" not in result_data
        assert len(result_data["dimensions"]) > 0
    
    @patch('fastmcp_server.get_auth_manager')
    def test_get_metrics_only(self, mock_get_auth):
        """Test getting metrics only."""
        mock_get_auth.return_value = Mock()
        
        result = gam_get_dimensions_metrics(
            report_type="HISTORICAL",
            category="metrics"
        )
        
        result_data = json.loads(result)
        assert result_data["success"] is True
        assert "metrics" in result_data
        assert "dimensions" not in result_data
        assert len(result_data["metrics"]) > 0
    
    @patch('fastmcp_server.get_auth_manager')
    def test_get_dimensions_metrics_reach_type(self, mock_get_auth):
        """Test getting dimensions/metrics for REACH report type."""
        mock_get_auth.return_value = Mock()
        
        result = gam_get_dimensions_metrics(
            report_type="REACH",
            category="metrics"
        )
        
        result_data = json.loads(result)
        assert result_data["success"] is True
        assert "metrics" in result_data
        
        # Check for reach-specific metrics
        metric_names = [m["name"] for m in result_data["metrics"]]
        assert any("UNIQUE_REACH" in name for name in metric_names)


class TestGAMGetCommonCombinations:
    """Integration tests for gam_get_common_combinations tool."""
    
    @patch('fastmcp_server.get_auth_manager')
    def test_get_common_combinations(self, mock_get_auth):
        """Test getting common dimension-metric combinations."""
        mock_get_auth.return_value = Mock()
        
        result = gam_get_common_combinations()
        
        result_data = json.loads(result)
        assert result_data["success"] is True
        assert "combinations" in result_data
        assert len(result_data["combinations"]) > 0
        
        # Verify structure of combinations
        for combo in result_data["combinations"]:
            assert "name" in combo
            assert "description" in combo
            assert "dimensions" in combo
            assert "metrics" in combo
            assert isinstance(combo["dimensions"], list)
            assert isinstance(combo["metrics"], list)
    
    @patch('fastmcp_server.get_auth_manager')
    def test_common_combinations_categories(self, mock_get_auth):
        """Test that common combinations cover various categories."""
        mock_get_auth.return_value = Mock()
        
        result = gam_get_common_combinations()
        
        result_data = json.loads(result)
        combo_names = [c["name"] for c in result_data["combinations"]]
        
        # Check for expected categories
        assert any("delivery" in name.lower() for name in combo_names)
        assert any("inventory" in name.lower() for name in combo_names)
        assert any("revenue" in name.lower() or "sales" in name.lower() for name in combo_names)


class TestGAMGetQuickReportTypes:
    """Integration tests for gam_get_quick_report_types tool."""
    
    @patch('fastmcp_server.get_auth_manager')
    def test_get_quick_report_types(self, mock_get_auth):
        """Test getting quick report types."""
        mock_get_auth.return_value = Mock()
        
        result = gam_get_quick_report_types()
        
        result_data = json.loads(result)
        assert result_data["success"] is True
        assert "report_types" in result_data
        assert len(result_data["report_types"]) == 5  # 5 quick report types
        
        # Verify all expected types
        type_names = [rt["type"] for rt in result_data["report_types"]]
        assert "delivery" in type_names
        assert "inventory" in type_names
        assert "sales" in type_names
        assert "reach" in type_names
        assert "programmatic" in type_names
    
    @patch('fastmcp_server.get_auth_manager')
    def test_quick_report_types_structure(self, mock_get_auth):
        """Test structure of quick report type information."""
        mock_get_auth.return_value = Mock()
        
        result = gam_get_quick_report_types()
        
        result_data = json.loads(result)
        
        for report_type in result_data["report_types"]:
            assert "type" in report_type
            assert "name" in report_type
            assert "description" in report_type
            assert "default_dimensions" in report_type
            assert "default_metrics" in report_type
            assert isinstance(report_type["default_dimensions"], list)
            assert isinstance(report_type["default_metrics"], list)


class TestGAMRunReport:
    """Integration tests for gam_quick_report tool."""
    
    @pytest.fixture
    def mock_report_generator(self):
        """Mock report generator for testing."""
        with patch('fastmcp_server.ReportGenerator') as MockGenerator:
            mock_instance = Mock()
            MockGenerator.return_value = mock_instance
            
            # Mock run_report response
            mock_instance.run_report.return_value = {
                "report_id": "report-123",
                "execution_id": "exec-456",
                "status": "IN_PROGRESS",
                "started_at": datetime.now().isoformat()
            }
            
            yield mock_instance
    
    @patch('fastmcp_server.get_auth_manager')
    def test_run_report_success(self, mock_get_auth, mock_report_generator):
        """Test running an existing report."""
        mock_get_auth.return_value = Mock()
        
        result = gam_quick_report(
            report_id="report-123",
            override_date_range=True,
            start_date="2024-01-01",
            end_date="2024-01-31"
        )
        
        result_data = json.loads(result)
        assert result_data["success"] is True
        assert result_data["report_id"] == "report-123"
        assert result_data["execution_id"] == "exec-456"
        assert result_data["status"] == "IN_PROGRESS"
    
    @patch('fastmcp_server.get_auth_manager')
    def test_run_report_no_override(self, mock_get_auth, mock_report_generator):
        """Test running report without date override."""
        mock_get_auth.return_value = Mock()
        
        result = gam_quick_report(
            report_id="report-789",
            override_date_range=False
        )
        
        result_data = json.loads(result)
        assert result_data["success"] is True
        
        # Verify run_report was called without date override
        call_args = mock_report_generator.run_report.call_args[1]
        assert "date_override" not in call_args or call_args["date_override"] is None
    
    @patch('fastmcp_server.get_auth_manager')
    def test_run_report_invalid_id(self, mock_get_auth, mock_report_generator):
        """Test running report with invalid ID."""
        mock_get_auth.return_value = Mock()
        mock_report_generator.run_report.side_effect = GAMError("Report not found")
        
        result = gam_quick_report(
            report_id="invalid-id",
            override_date_range=False
        )
        
        result_data = json.loads(result)
        assert result_data["success"] is False
        assert "Report not found" in result_data["error"]


class TestMCPAuthenticationIntegration:
    """Integration tests for MCP authentication."""
    
    def test_auth_disabled_by_default(self):
        """Test that authentication is disabled by default."""
        with patch.dict('os.environ', {}, clear=True):
            # Remove MCP_AUTH_ENABLED if set
            if 'MCP_AUTH_ENABLED' in os.environ:
                del os.environ['MCP_AUTH_ENABLED']
            
            # Import should not set up auth
            from src.mcp import fastmcp_server
            assert fastmcp_server.auth_provider is None
    
    def test_auth_enabled_with_env_var(self):
        """Test enabling authentication via environment variable."""
        with patch.dict('os.environ', {'MCP_AUTH_ENABLED': 'true'}):
            # Re-import to pick up env var
            import importlib
            import fastmcp_server
            importlib.reload(fastmcp_server)
            
            # Auth should be configured
            assert fastmcp_server.auth_provider is not None


class TestMCPErrorHandling:
    """Integration tests for MCP error handling."""
    
    @patch('fastmcp_server.get_auth_manager')
    def test_handle_authentication_error(self, mock_get_auth):
        """Test handling authentication errors."""
        mock_get_auth.side_effect = Exception("Authentication failed")
        
        result = gam_quick_report(
            report_type="delivery",
            days_back=7,
            format="json"
        )
        
        result_data = json.loads(result)
        assert result_data["success"] is False
        assert "Google Ad Manager not configured" in result_data["error"]
    
    @patch('fastmcp_server.get_auth_manager')
    def test_handle_unexpected_error(self, mock_get_auth):
        """Test handling unexpected errors."""
        mock_get_auth.return_value = Mock()
        
        with patch('fastmcp_server.ReportGenerator') as MockGenerator:
            MockGenerator.side_effect = Exception("Unexpected error")
            
            result = gam_quick_report(
                report_type="delivery",
                days_back=7,
                format="json"
            )
            
            result_data = json.loads(result)
            assert result_data["success"] is False
            assert "Unexpected error" in result_data["error"]