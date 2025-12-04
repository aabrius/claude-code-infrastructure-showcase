"""E2E tests for MCP resources."""

import json
import pytest
import httpx
from .helpers import read_resource, assert_resource_response_success


class TestContextResource:
    """Test gam://context resource."""

    def test_read_context_resource(
        self, http_client: httpx.Client, mcp_endpoint: str, mcp_session_id: str
    ):
        """Should read context resource with network, domains, apps, and strategies."""
        response = read_resource(http_client, mcp_endpoint, "gam://context", mcp_session_id)
        data = assert_resource_response_success(response, "gam://context")

        # Parse the contents (should be JSON string)
        if "contents" in data:
            contents = data["contents"]
            if isinstance(contents, list) and len(contents) > 0:
                content = contents[0]
                if "text" in content:
                    context = json.loads(content["text"])
                else:
                    context = json.loads(str(contents))
            else:
                context = json.loads(str(data))
        else:
            context = data

        # Verify structure
        assert "network" in context
        assert "domains" in context
        assert "apps" in context
        assert "ad_strategies" in context

        # Verify domains (should have 27)
        domains = context["domains"]
        assert isinstance(domains, list)
        assert len(domains) == 27, f"Expected 27 domains, got {len(domains)}"

        # Verify apps (should have 2)
        apps = context["apps"]
        assert isinstance(apps, list)
        assert len(apps) == 2, f"Expected 2 apps, got {len(apps)}"

        # Verify Android app
        android_app = next((a for a in apps if a["platform"] == "android"), None)
        assert android_app is not None
        assert android_app["app_id"] == "br.com.plusdin.plusdin_mobile"

        # Verify iOS app
        ios_app = next((a for a in apps if a["platform"] == "ios"), None)
        assert ios_app is not None
        assert ios_app["app_id"] == "6443685698"

        # Verify ad strategies (should have 3)
        strategies = context["ad_strategies"]
        assert isinstance(strategies, list)
        assert len(strategies) == 3, f"Expected 3 strategies, got {len(strategies)}"

        strategy_names = {s["name"] for s in strategies}
        assert "media_arbitrage" in strategy_names
        assert "open_auction" in strategy_names
        assert "app_mediation" in strategy_names


class TestDimensionsResource:
    """Test gam://dimensions resource."""

    def test_read_dimensions_resource(
        self, http_client: httpx.Client, mcp_endpoint: str, mcp_session_id: str
    ):
        """Should read dimensions resource with all available dimensions."""
        response = read_resource(http_client, mcp_endpoint, "gam://dimensions", mcp_session_id)
        data = assert_resource_response_success(response, "gam://dimensions")

        # Parse contents
        if "contents" in data:
            contents = data["contents"]
            if isinstance(contents, list) and len(contents) > 0:
                content = contents[0]
                if "text" in content:
                    dimensions = json.loads(content["text"])
                else:
                    dimensions = json.loads(str(contents))
            else:
                dimensions = json.loads(str(data))
        else:
            dimensions = data

        # Verify structure - dimensions are organized by category
        # Expected: {"time": [...], "inventory": [...], ...}
        assert isinstance(dimensions, dict), "Dimensions should be a dict"
        assert len(dimensions) > 0, "Should have at least one category"

        # Verify some categories exist
        assert "time" in dimensions or "inventory" in dimensions

        # Collect all dimensions from all categories
        all_dims = {}
        for category_dims in dimensions.values():
            if isinstance(category_dims, list):
                for dim in category_dims:
                    all_dims[dim["name"]] = dim

        # Verify some key dimensions exist
        assert "DATE" in all_dims
        assert "AD_UNIT_NAME" in all_dims
        assert "MOBILE_APP_ID" in all_dims
        assert "CUSTOM_CRITERIA" in all_dims

        # Verify dimension has required fields
        date_dim = all_dims["DATE"]
        assert "name" in date_dim
        assert "description" in date_dim
        assert "use_case" in date_dim

    def test_dimensions_organized_by_category(
        self, http_client: httpx.Client, mcp_endpoint: str, mcp_session_id: str
    ):
        """Dimensions should be organized by category."""
        response = read_resource(http_client, mcp_endpoint, "gam://dimensions", mcp_session_id)
        data = assert_resource_response_success(response, "gam://dimensions")

        # Parse contents
        if "contents" in data:
            contents = data["contents"]
            if isinstance(contents, list) and len(contents) > 0:
                content = contents[0]
                if "text" in content:
                    dimensions = json.loads(content["text"])
                else:
                    dimensions = json.loads(str(contents))
            else:
                dimensions = json.loads(str(data))
        else:
            dimensions = data

        # Dimensions ARE the categorized structure (no wrapper)
        # Expected: {"time": [...], "inventory": [...], "programmatic": [...]}
        assert isinstance(dimensions, dict)
        assert "time" in dimensions
        assert "inventory" in dimensions
        assert "programmatic" in dimensions

        # Verify each category contains dimension objects
        assert isinstance(dimensions["time"], list)
        assert len(dimensions["time"]) > 0
        assert "name" in dimensions["time"][0]


class TestMetricsResource:
    """Test gam://metrics resource."""

    def test_read_metrics_resource(
        self, http_client: httpx.Client, mcp_endpoint: str, mcp_session_id: str
    ):
        """Should read metrics resource with all available metrics."""
        response = read_resource(http_client, mcp_endpoint, "gam://metrics", mcp_session_id)
        data = assert_resource_response_success(response, "gam://metrics")

        # Parse contents
        if "contents" in data:
            contents = data["contents"]
            if isinstance(contents, list) and len(contents) > 0:
                content = contents[0]
                if "text" in content:
                    metrics = json.loads(content["text"])
                else:
                    metrics = json.loads(str(contents))
            else:
                metrics = json.loads(str(data))
        else:
            metrics = data

        # Verify structure - metrics are organized by category
        # Expected: {"core": [...], "revenue": [...], ...}
        assert isinstance(metrics, dict), "Metrics should be a dict"
        assert len(metrics) > 0, "Should have at least one category"

        # Verify some categories exist
        assert "core" in metrics or "revenue" in metrics

        # Collect all metrics from all categories
        all_metrics = {}
        for category_metrics in metrics.values():
            if isinstance(category_metrics, list):
                for metric in category_metrics:
                    all_metrics[metric["name"]] = metric

        # Verify some key metrics exist
        assert "IMPRESSIONS" in all_metrics
        assert "AD_EXCHANGE_REVENUE" in all_metrics
        assert "AD_EXCHANGE_IMPRESSIONS" in all_metrics

        # Verify metric has required fields
        impressions = all_metrics["IMPRESSIONS"]
        assert "name" in impressions
        assert "description" in impressions
        assert "data_format" in impressions


class TestTemplatesResource:
    """Test gam://templates resource."""

    def test_read_templates_resource(
        self, http_client: httpx.Client, mcp_endpoint: str, mcp_session_id: str
    ):
        """Should read templates resource with report templates."""
        response = read_resource(http_client, mcp_endpoint, "gam://templates", mcp_session_id)
        data = assert_resource_response_success(response, "gam://templates")

        # Parse contents
        if "contents" in data:
            contents = data["contents"]
            if isinstance(contents, list) and len(contents) > 0:
                content = contents[0]
                if "text" in content:
                    templates = json.loads(content["text"])
                else:
                    templates = json.loads(str(contents))
            else:
                templates = json.loads(str(data))
        else:
            templates = data

        # Verify structure - templates are returned as direct array
        # Expected: [{...}, {...}]
        assert isinstance(templates, list), "Templates should be a list"
        assert len(templates) >= 6, f"Expected at least 6 templates, got {len(templates)}"

        # Verify template structure
        for template in templates:
            assert "name" in template
            assert "description" in template
            assert "dimensions" in template
            assert "metrics" in template

        # Verify specific templates exist
        template_names = {t["name"] for t in templates}
        assert "media_arbitrage_daily" in template_names
        assert "app_performance" in template_names
        assert "app_mediation" in template_names
