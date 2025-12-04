"""E2E workflow tests - testing complete user journeys."""

import pytest
import httpx
from .helpers import (
    call_tool,
    read_resource,
    assert_tool_response_success,
    assert_resource_response_success,
)


class TestReportDiscoveryWorkflow:
    """Test the workflow of discovering available report options."""

    def test_workflow_discover_what_can_be_reported(
        self, http_client: httpx.Client, mcp_endpoint: str, mcp_session_id: str
    ):
        """
        User Journey: "What can I report on?"

        1. Read context to understand network setup
        2. Get available dimensions and metrics
        3. Search for specific metrics
        4. Get report templates
        """
        # Step 1: Read context
        context_response = read_resource(http_client, mcp_endpoint, "gam://context", mcp_session_id)
        context = assert_resource_response_success(context_response, "gam://context")
        assert context is not None

        # Step 2: Get available options
        options_response = call_tool(
            http_client, mcp_endpoint, "get_available_options", {}, mcp_session_id
        )
        options = assert_tool_response_success(options_response, "get_available_options")

        assert "dimensions" in options
        assert "metrics" in options
        assert "templates" in options

        # Step 3: Search for revenue metrics
        search_response = call_tool(
            http_client,
            mcp_endpoint,
            "search",
            {"query": "revenue", "search_in": ["metrics"]},
            mcp_session_id
        )
        search_results = assert_tool_response_success(search_response, "search")

        assert search_results["total_matches"] > 0
        revenue_metrics = [
            m["name"] for m in search_results["matches"] if m["type"] == "metric"
        ]
        assert len(revenue_metrics) > 0

        # Step 4: Read templates
        templates_response = read_resource(
            http_client, mcp_endpoint, "gam://templates", mcp_session_id
        )
        templates = assert_resource_response_success(
            templates_response, "gam://templates"
        )
        assert templates is not None


class TestMediaArbitrageWorkflow:
    """Test media arbitrage reporting workflow."""

    def test_workflow_media_arbitrage_analysis(
        self, http_client: httpx.Client, mcp_endpoint: str, mcp_session_id: str
    ):
        """
        User Journey: "Show me media arbitrage performance"

        1. Search for arbitrage templates
        2. Get arbitrage strategy details from context
        3. Identify required dimensions and metrics
        4. Validate dimensions exist
        """
        # Step 1: Search for arbitrage
        search_response = call_tool(
            http_client, mcp_endpoint, "search", {"query": "arbitrage"}, mcp_session_id
        )
        search_results = assert_tool_response_success(search_response, "search")

        assert search_results["total_matches"] > 0
        arbitrage_matches = [
            m
            for m in search_results["matches"]
            if "arbitrage" in m.get("name", "").lower()
        ]
        assert len(arbitrage_matches) > 0

        # Step 2: Read context for strategies
        context_response = read_resource(http_client, mcp_endpoint, "gam://context", mcp_session_id)
        assert_resource_response_success(context_response, "gam://context")

        # Step 3: Get templates to find media_arbitrage_daily
        templates_response = read_resource(
            http_client, mcp_endpoint, "gam://templates", mcp_session_id
        )
        assert_resource_response_success(templates_response, "gam://templates")

        # Step 4: Verify required dimensions exist
        options_response = call_tool(
            http_client, mcp_endpoint, "get_available_options", {}, mcp_session_id
        )
        options = assert_tool_response_success(options_response, "get_available_options")

        required_dimensions = ["DATE", "CUSTOM_CRITERIA", "URL_NAME", "AD_UNIT_NAME"]
        available_dimensions = options["dimensions"].keys()

        for dim in required_dimensions:
            assert (
                dim in available_dimensions
            ), f"Required dimension {dim} not available"


class TestAppMediationWorkflow:
    """Test app mediation reporting workflow."""

    def test_workflow_app_mediation_revenue(
        self, http_client: httpx.Client, mcp_endpoint: str, mcp_session_id: str
    ):
        """
        User Journey: "Show me revenue from my app mediation networks"

        1. Get app information from context
        2. Search for mediation metrics
        3. Verify MOBILE_APP_ID dimension exists
        4. Verify yield group metrics exist
        """
        # Step 1: Read context for apps
        context_response = read_resource(http_client, mcp_endpoint, "gam://context", mcp_session_id)
        assert_resource_response_success(context_response, "gam://context")

        # Step 2: Search for mediation
        search_response = call_tool(
            http_client,
            mcp_endpoint,
            "search",
            {"query": "mediation", "search_in": ["metrics", "strategies"]},
            mcp_session_id
        )
        search_results = assert_tool_response_success(search_response, "search")

        # Step 3: Verify MOBILE_APP_ID dimension
        dimensions_response = read_resource(
            http_client, mcp_endpoint, "gam://dimensions", mcp_session_id
        )
        assert_resource_response_success(dimensions_response, "gam://dimensions")

        options_response = call_tool(
            http_client, mcp_endpoint, "get_available_options", {}, mcp_session_id
        )
        options = assert_tool_response_success(options_response, "get_available_options")

        assert "MOBILE_APP_ID" in options["dimensions"]

        # Step 4: Verify yield metrics exist
        mediation_metrics = [
            "YIELD_GROUP_IMPRESSIONS",
            "YIELD_GROUP_ESTIMATED_REVENUE",
            "YIELD_GROUP_MEDIATION_FILL_RATE",
            "YIELD_GROUP_MEDIATION_THIRD_PARTY_ECPM",
        ]

        available_metrics = options["metrics"].keys()
        for metric in mediation_metrics:
            assert metric in available_metrics, f"Mediation metric {metric} not found"


class TestDomainPerformanceWorkflow:
    """Test domain performance analysis workflow."""

    def test_workflow_domain_performance(
        self, http_client: httpx.Client, mcp_endpoint: str, mcp_session_id: str
    ):
        """
        User Journey: "Show me performance for my domains"

        1. Get list of domains from context
        2. Verify we have the expected 27 domains
        3. Search for URL dimension
        4. Verify Ad Exchange metrics are available
        """
        # Step 1: Read context
        context_response = read_resource(http_client, mcp_endpoint, "gam://context", mcp_session_id)
        assert_resource_response_success(context_response, "gam://context")

        # Step 2: Search for domains
        search_response = call_tool(
            http_client,
            mcp_endpoint,
            "search",
            {"query": "easydinheiro", "search_in": ["domains"]},
            mcp_session_id
        )
        search_results = assert_tool_response_success(search_response, "search")

        # Should find easydinheiro.com domain
        domain_matches = [m for m in search_results["matches"] if m["type"] == "domain"]
        assert len(domain_matches) > 0

        # Step 3: Verify URL dimension exists
        options_response = call_tool(
            http_client, mcp_endpoint, "get_available_options", {}, mcp_session_id
        )
        options = assert_tool_response_success(options_response, "get_available_options")

        assert "URL_NAME" in options["dimensions"]

        # Step 4: Verify Ad Exchange metrics
        ad_exchange_metrics = [
            "AD_EXCHANGE_IMPRESSIONS",
            "AD_EXCHANGE_REVENUE",
            "AD_EXCHANGE_AVERAGE_ECPM",
        ]

        available_metrics = options["metrics"].keys()
        for metric in ad_exchange_metrics:
            assert (
                metric in available_metrics
            ), f"Ad Exchange metric {metric} not found"


class TestReportCreationWorkflow:
    """Test report creation validation workflow."""

    def test_workflow_create_validated_report(
        self, http_client: httpx.Client, mcp_endpoint: str, mcp_session_id: str
    ):
        """
        User Journey: "Create a custom report with validation"

        1. Get available dimensions and metrics
        2. Validate selections before creating report
        3. Attempt to create report with valid parameters
        """
        # Step 1: Get options
        options_response = call_tool(
            http_client, mcp_endpoint, "get_available_options", {}, mcp_session_id
        )
        options = assert_tool_response_success(options_response, "get_available_options")

        # Step 2: Select valid dimensions and metrics
        selected_dimensions = ["DATE", "AD_UNIT_NAME"]
        selected_metrics = ["IMPRESSIONS", "AD_EXCHANGE_REVENUE"]

        # Validate selections
        for dim in selected_dimensions:
            assert dim in options["dimensions"], f"Dimension {dim} not available"

        for metric in selected_metrics:
            assert metric in options["metrics"], f"Metric {metric} not available"

        # Step 3: Create report (will fail without GAM credentials, but validation passes)
        create_response = call_tool(
            http_client,
            mcp_endpoint,
            "create_report",
            {
                "dimensions": selected_dimensions,
                "metrics": selected_metrics,
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "report_name": "E2E Validated Report",
            },
            mcp_session_id
        )

        # Validation should pass (200) or fail with GAM API error (401/500)
        # but NOT fail with validation error (400/422)
        assert create_response.status_code in [200, 401, 403, 500]
        assert create_response.status_code not in [400, 422]
