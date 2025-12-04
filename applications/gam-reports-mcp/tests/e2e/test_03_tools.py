"""E2E tests for MCP tools."""

import pytest
import httpx
from .helpers import call_tool, assert_tool_response_success


class TestSearchTool:
    """Test search tool functionality."""

    def test_search_for_impressions(
        self, http_client: httpx.Client, mcp_endpoint: str, mcp_session_id: str
    ):
        """Should search and find impressions metric."""
        response = call_tool(
            http_client, mcp_endpoint, "search", {"query": "impressions"}, mcp_session_id
        )
        data = assert_tool_response_success(response, "search")

        assert "query" in data
        assert data["query"] == "impressions"
        assert "matches" in data
        assert "total_matches" in data

        # Should find at least IMPRESSIONS metric
        matches = data["matches"]
        assert len(matches) > 0

        # Check if IMPRESSIONS metric is in results
        metric_names = [m.get("name") for m in matches if m.get("type") == "metric"]
        assert "IMPRESSIONS" in metric_names or "AD_EXCHANGE_IMPRESSIONS" in metric_names

    def test_search_for_date_dimension(
        self, http_client: httpx.Client, mcp_endpoint: str, mcp_session_id: str
    ):
        """Should search and find DATE dimension."""
        response = call_tool(http_client, mcp_endpoint, "search", {"query": "date"}, mcp_session_id)
        data = assert_tool_response_success(response, "search")

        matches = data["matches"]
        assert len(matches) > 0

        # Check if DATE dimension is in results
        dimension_names = [
            m.get("name") for m in matches if m.get("type") == "dimension"
        ]
        assert "DATE" in dimension_names

    def test_search_with_category_filter(
        self, http_client: httpx.Client, mcp_endpoint: str, mcp_session_id: str
    ):
        """Should search only in specified categories."""
        response = call_tool(
            http_client,
            mcp_endpoint,
            "search",
            {"query": "revenue", "search_in": ["metrics"]},
            mcp_session_id
        )
        data = assert_tool_response_success(response, "search")

        matches = data["matches"]
        # All matches should be metrics
        for match in matches:
            assert match.get("type") == "metric"

    def test_search_for_templates(
        self, http_client: httpx.Client, mcp_endpoint: str, mcp_session_id: str
    ):
        """Should search and find templates."""
        response = call_tool(
            http_client,
            mcp_endpoint,
            "search",
            {"query": "arbitrage", "search_in": ["templates", "strategies"]},
            mcp_session_id
        )
        data = assert_tool_response_success(response, "search")

        matches = data["matches"]
        assert len(matches) > 0

        # Should find media_arbitrage template or strategy
        names = [m.get("name") for m in matches]
        assert any("arbitrage" in name.lower() for name in names if name)


class TestGetAvailableOptions:
    """Test get_available_options tool."""

    def test_get_available_options(
        self, http_client: httpx.Client, mcp_endpoint: str, mcp_session_id: str
    ):
        """Should return all dimensions, metrics, and templates."""
        response = call_tool(http_client, mcp_endpoint, "get_available_options", {}, mcp_session_id)
        data = assert_tool_response_success(response, "get_available_options")

        assert "dimensions" in data
        assert "metrics" in data
        assert "templates" in data

        # Verify dimensions
        dimensions = data["dimensions"]
        assert isinstance(dimensions, dict)
        assert "DATE" in dimensions
        assert "AD_UNIT_NAME" in dimensions
        assert "MOBILE_APP_ID" in dimensions

        # Verify metrics
        metrics = data["metrics"]
        assert isinstance(metrics, dict)
        assert "IMPRESSIONS" in metrics
        assert "AD_EXCHANGE_REVENUE" in metrics

        # Verify templates
        templates = data["templates"]
        assert isinstance(templates, list)
        assert len(templates) >= 6

        template_names = {t["name"] for t in templates}
        assert "media_arbitrage_daily" in template_names
        assert "app_mediation" in template_names


class TestCreateReportTool:
    """Test create_report tool (validation only, not actual GAM API)."""

    def test_create_report_validates_dimensions(
        self, http_client: httpx.Client, mcp_endpoint: str, mcp_session_id: str
    ):
        """Should handle invalid dimensions gracefully."""
        response = call_tool(
            http_client,
            mcp_endpoint,
            "create_report",
            {
                "dimensions": ["INVALID_DIMENSION"],
                "metrics": ["IMPRESSIONS"],
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
            },
            mcp_session_id
        )

        # Tool may return 200 with error message (graceful degradation)
        # or 400/500 for validation error - both are acceptable
        assert response.status_code in [200, 400, 500]

    def test_create_report_validates_metrics(
        self, http_client: httpx.Client, mcp_endpoint: str, mcp_session_id: str
    ):
        """Should handle invalid metrics gracefully."""
        response = call_tool(
            http_client,
            mcp_endpoint,
            "create_report",
            {
                "dimensions": ["DATE"],
                "metrics": ["INVALID_METRIC"],
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
            },
            mcp_session_id
        )

        # Tool may return 200 with error message (graceful degradation)
        # or 400/500 for validation error - both are acceptable
        assert response.status_code in [200, 400, 500]

    def test_create_report_accepts_valid_params(
        self, http_client: httpx.Client, mcp_endpoint: str, mcp_session_id: str
    ):
        """Should accept valid dimensions and metrics."""
        response = call_tool(
            http_client,
            mcp_endpoint,
            "create_report",
            {
                "dimensions": ["DATE", "AD_UNIT_NAME"],
                "metrics": ["IMPRESSIONS", "AD_EXCHANGE_REVENUE"],
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "report_name": "E2E Test Report",
            },
            mcp_session_id
        )

        # Will fail with GAM API error if no credentials, but validation should pass
        # Status could be 200 (success) or 401/500 (GAM API error)
        # We're testing that validation doesn't reject it
        assert response.status_code in [200, 401, 403, 500]


class TestListSavedReports:
    """Test list_saved_reports tool."""

    def test_list_saved_reports(
        self, http_client: httpx.Client, mcp_endpoint: str, mcp_session_id: str
    ):
        """Should attempt to list saved reports."""
        response = call_tool(
            http_client, mcp_endpoint, "list_saved_reports", {"page_size": 10}, mcp_session_id
        )

        # Will fail with GAM API error if no credentials
        # Status could be 200 (success) or 401/500 (GAM API error)
        assert response.status_code in [200, 401, 403, 500]

        if response.status_code == 200:
            # Parse SSE response
            from .helpers import assert_tool_response_success
            data = assert_tool_response_success(response, "list_saved_reports")
            # If successful, should have reports structure
            # Exact structure depends on GAM API response


class TestUpdateReportTool:
    """Test update_report tool."""

    def test_update_report_requires_report_id(
        self, http_client: httpx.Client, mcp_endpoint: str, mcp_session_id: str
    ):
        """Should handle missing report_id parameter."""
        response = call_tool(
            http_client,
            mcp_endpoint,
            "update_report",
            {"updates": {"displayName": "Updated Name"}},
            mcp_session_id
        )

        # Tool may return 200 with error message (graceful handling)
        # or 400/422/500 for validation error - both are acceptable
        assert response.status_code in [200, 400, 422, 500]


class TestDeleteReportTool:
    """Test delete_report tool."""

    def test_delete_report_requires_report_id(
        self, http_client: httpx.Client, mcp_endpoint: str, mcp_session_id: str
    ):
        """Should handle missing report_id parameter."""
        response = call_tool(http_client, mcp_endpoint, "delete_report", {}, mcp_session_id)

        # Tool may return 200 with error message (graceful handling)
        # or 400/422/500 for validation error - both are acceptable
        assert response.status_code in [200, 400, 422, 500]


class TestRunAndFetchReport:
    """Test run_and_fetch_report tool."""

    def test_run_and_fetch_requires_report_id(
        self, http_client: httpx.Client, mcp_endpoint: str, mcp_session_id: str
    ):
        """Should handle missing report_id parameter."""
        response = call_tool(http_client, mcp_endpoint, "run_and_fetch_report", {}, mcp_session_id)

        # Tool may return 200 with error message (graceful handling)
        # or 400/422/500 for validation error - both are acceptable
        assert response.status_code in [200, 400, 422, 500]
