"""Unit tests for MCP response models."""

import pytest
from datetime import datetime


class TestReportResponse:
    """Tests for ReportResponse model."""

    def test_report_response_serialization(self):
        """Test ReportResponse serializes correctly."""
        from applications.mcp_server.models.responses import ReportResponse

        response = ReportResponse(
            success=True,
            report_type="delivery",
            total_rows=100,
            dimensions=["DATE", "AD_UNIT_NAME"],
            metrics=["IMPRESSIONS", "CLICKS"],
        )

        data = response.model_dump()

        assert data["success"] is True
        assert data["report_type"] == "delivery"
        assert data["total_rows"] == 100
        assert len(data["dimensions"]) == 2

    def test_report_response_json(self):
        """Test ReportResponse converts to JSON."""
        from applications.mcp_server.models.responses import ReportResponse

        response = ReportResponse(
            success=True,
            report_type="inventory",
            total_rows=50,
        )

        json_str = response.model_dump_json()

        assert '"success":true' in json_str
        assert '"report_type":"inventory"' in json_str


class TestErrorResponse:
    """Tests for ErrorResponse model."""

    def test_error_response_creation(self):
        """Test ErrorResponse creation."""
        from applications.mcp_server.models.responses import ErrorResponse

        error = ErrorResponse.create(
            error_type="ValidationError",
            message="Invalid dimension",
            error_code="VAL_001",
            suggestions=["Check valid dimensions"],
        )

        data = error.model_dump()

        assert data["success"] is False
        assert data["error"]["type"] == "ValidationError"
        assert data["error"]["code"] == "VAL_001"
        assert len(data["error"]["suggestions"]) == 1
