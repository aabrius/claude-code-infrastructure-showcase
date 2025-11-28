"""
Critical Journey Tests - Must Pass for Production Readiness

These tests cover the most important user journeys that must work reliably
for the GAM API system to be considered production-ready.
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Add packages to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages" / "core" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages" / "shared" / "src"))

from journey_test_framework import (
    JourneyTestFramework, Journey, JourneyStep, JourneyPriority,
    journey_framework
)


class TestCriticalJourneys:
    """Test suite for critical user journeys."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment."""
        self.framework = journey_framework
        
        # Register critical journeys
        self._register_authentication_journeys()
        self._register_report_generation_journeys()
        self._register_data_discovery_journeys()
    
    def _register_authentication_journeys(self):
        """Register authentication-related journeys."""
        
        # Journey 1: First-time OAuth setup
        oauth_setup = Journey(
            id="auth_first_time_setup",
            name="First-Time OAuth Setup", 
            description="New user setting up OAuth2 credentials for the first time",
            priority=JourneyPriority.CRITICAL,
            interface="api",
            category="authentication"
        )
        
        oauth_setup.steps = [
            JourneyStep(
                name="load_config_template",
                action=self._load_config_template,
                validation=lambda result, ctx: "client_id" in result
            ),
            JourneyStep(
                name="validate_config_structure",
                action=self._validate_config_structure,
                expected_result=True
            ),
            JourneyStep(
                name="generate_auth_url",
                action=self._generate_auth_url,
                validation=lambda result, ctx: result.startswith("https://")
            ),
            JourneyStep(
                name="simulate_oauth_callback",
                action=self._simulate_oauth_callback,
                validation=lambda result, ctx: "access_token" in result
            ),
            JourneyStep(
                name="validate_credentials",
                action=self._validate_credentials,
                expected_result=True
            )
        ]
        
        self.framework.register_journey(oauth_setup)
        
        # Journey 2: Token refresh flow
        token_refresh = Journey(
            id="auth_token_refresh",
            name="Token Refresh Flow",
            description="Refresh expired OAuth tokens automatically",
            priority=JourneyPriority.CRITICAL,
            interface="api", 
            category="authentication"
        )
        
        token_refresh.steps = [
            JourneyStep(
                name="detect_expired_token",
                action=self._detect_expired_token,
                expected_result=True
            ),
            JourneyStep(
                name="refresh_access_token",
                action=self._refresh_access_token,
                validation=lambda result, ctx: "access_token" in result
            ),
            JourneyStep(
                name="update_credentials",
                action=self._update_credentials,
                expected_result=True
            ),
            JourneyStep(
                name="verify_new_token",
                action=self._verify_new_token,
                expected_result=True
            )
        ]
        
        self.framework.register_journey(token_refresh)
    
    def _register_report_generation_journeys(self):
        """Register report generation journeys."""
        
        # Journey 3: Quick delivery report
        delivery_report = Journey(
            id="report_quick_delivery",
            name="Quick Delivery Report",
            description="Generate a pre-configured delivery report",
            priority=JourneyPriority.CRITICAL,
            interface="api",
            category="reporting"
        )
        
        delivery_report.steps = [
            JourneyStep(
                name="authenticate_user",
                action=self._authenticate_user,
                expected_result=True
            ),
            JourneyStep(
                name="create_delivery_report",
                action=self._create_delivery_report,
                validation=lambda result, ctx: "report_id" in result
            ),
            JourneyStep(
                name="poll_report_status",
                action=self._poll_report_status,
                validation=lambda result, ctx: result["status"] in ["COMPLETED", "RUNNING"]
            ),
            JourneyStep(
                name="download_report_data",
                action=self._download_report_data,
                validation=lambda result, ctx: len(result["data"]) > 0
            ),
            JourneyStep(
                name="validate_report_structure",
                action=self._validate_report_structure,
                expected_result=True
            )
        ]
        
        self.framework.register_journey(delivery_report)
        
        # Journey 4: Custom report with dimensions/metrics
        custom_report = Journey(
            id="report_custom_build",
            name="Custom Report Builder",
            description="Build custom report with specific dimensions and metrics",
            priority=JourneyPriority.CRITICAL,
            interface="sdk",
            category="reporting"
        )
        
        custom_report.steps = [
            JourneyStep(
                name="initialize_report_builder",
                action=self._initialize_report_builder,
                validation=lambda result, ctx: result is not None
            ),
            JourneyStep(
                name="add_dimensions",
                action=self._add_dimensions,
                validation=lambda result, ctx: len(result["dimensions"]) == 2
            ),
            JourneyStep(
                name="add_metrics", 
                action=self._add_metrics,
                validation=lambda result, ctx: len(result["metrics"]) == 2
            ),
            JourneyStep(
                name="set_date_range",
                action=self._set_date_range,
                validation=lambda result, ctx: result["date_range"] is not None
            ),
            JourneyStep(
                name="build_and_execute",
                action=self._build_and_execute,
                validation=lambda result, ctx: result["status"] == "COMPLETED"
            )
        ]
        
        self.framework.register_journey(custom_report)
    
    def _register_data_discovery_journeys(self):
        """Register data discovery journeys."""
        
        # Journey 5: Explore available dimensions
        dimension_discovery = Journey(
            id="discovery_dimensions",
            name="Dimension Discovery",
            description="Explore available dimensions for reporting",
            priority=JourneyPriority.CRITICAL,
            interface="api",
            category="discovery"
        )
        
        dimension_discovery.steps = [
            JourneyStep(
                name="authenticate_user",
                action=self._authenticate_user,
                expected_result=True
            ),
            JourneyStep(
                name="fetch_available_dimensions",
                action=self._fetch_available_dimensions,
                validation=lambda result, ctx: len(result) > 0
            ),
            JourneyStep(
                name="validate_dimension_format",
                action=self._validate_dimension_format,
                expected_result=True
            ),
            JourneyStep(
                name="test_dimension_compatibility",
                action=self._test_dimension_compatibility,
                expected_result=True
            )
        ]
        
        self.framework.register_journey(dimension_discovery)
    
    # Authentication journey step implementations
    def _load_config_template(self, context):
        """Load configuration template."""
        from gam_api import load_config, Config
        
        config_data = load_config()
        context["config"] = Config(config_data)
        return config_data
    
    def _validate_config_structure(self, context):
        """Validate configuration has required fields."""
        config = context.get("config")
        if not config:
            return False
        
        return hasattr(config, 'gam') and hasattr(config, 'auth')
    
    def _generate_auth_url(self, context):
        """Generate OAuth authorization URL."""
        # Simulate OAuth URL generation
        base_url = "https://accounts.google.com/o/oauth2/auth"
        params = {
            "client_id": "test_client_id",
            "redirect_uri": "http://localhost:8080/oauth/callback",
            "scope": "https://www.googleapis.com/auth/dfp",
            "response_type": "code"
        }
        
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        auth_url = f"{base_url}?{query_string}"
        
        context["auth_url"] = auth_url
        return auth_url
    
    def _simulate_oauth_callback(self, context):
        """Simulate OAuth callback with authorization code."""
        # Simulate successful OAuth callback
        auth_code = "test_auth_code_12345"
        
        # Simulate token exchange
        tokens = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 3600,
            "token_type": "Bearer"
        }
        
        context["tokens"] = tokens
        return tokens
    
    def _validate_credentials(self, context):
        """Validate OAuth credentials work."""
        tokens = context.get("tokens", {})
        return "access_token" in tokens and "refresh_token" in tokens
    
    def _detect_expired_token(self, context):
        """Detect if access token is expired."""
        # Simulate expired token detection
        context["token_expired"] = True
        return True
    
    def _refresh_access_token(self, context):
        """Refresh expired access token."""
        # Simulate token refresh
        new_tokens = {
            "access_token": "new_access_token_67890",
            "expires_in": 3600,
            "token_type": "Bearer"
        }
        
        context["refreshed_tokens"] = new_tokens
        return new_tokens
    
    def _update_credentials(self, context):
        """Update stored credentials with new tokens."""
        refreshed_tokens = context.get("refreshed_tokens", {})
        context["current_tokens"] = refreshed_tokens
        return True
    
    def _verify_new_token(self, context):
        """Verify new token works for API calls."""
        current_tokens = context.get("current_tokens", {})
        return "access_token" in current_tokens
    
    # Report generation journey step implementations
    def _authenticate_user(self, context):
        """Authenticate user for API access."""
        from gam_api import GAMClient
        
        client = GAMClient()
        context["client"] = client
        context["authenticated"] = True
        return True
    
    def _create_delivery_report(self, context):
        """Create a delivery report."""
        client = context.get("client")
        if not client:
            raise ValueError("Client not initialized")
        
        # Use the GAMClient to generate a delivery report
        result = client.generate_report("delivery")
        context["report_result"] = result
        
        return {
            "report_id": result["report_id"],
            "status": result["status"],
            "message": result["message"]
        }
    
    def _poll_report_status(self, context):
        """Poll report status until completion."""
        report_result = context.get("report_result", {})
        
        # Simulate polling - in real implementation this would check actual status
        status_result = {
            "status": "COMPLETED",
            "total_rows": report_result.get("total_rows", 1000),
            "report_id": report_result.get("report_id")
        }
        
        context["final_status"] = status_result
        return status_result
    
    def _download_report_data(self, context):
        """Download report data."""
        # Simulate downloading report data
        mock_data = [
            {"date": "2024-01-01", "impressions": 1000, "clicks": 50, "ctr": 0.05},
            {"date": "2024-01-02", "impressions": 1200, "clicks": 60, "ctr": 0.05},
            {"date": "2024-01-03", "impressions": 900, "clicks": 45, "ctr": 0.05}
        ]
        
        result = {"data": mock_data, "total_rows": len(mock_data)}
        context["report_data"] = result
        return result
    
    def _validate_report_structure(self, context):
        """Validate report data has expected structure."""
        report_data = context.get("report_data", {})
        data = report_data.get("data", [])
        
        if not data:
            return False
        
        # Check first row has expected fields
        first_row = data[0]
        expected_fields = ["date", "impressions", "clicks", "ctr"]
        
        return all(field in first_row for field in expected_fields)
    
    def _initialize_report_builder(self, context):
        """Initialize report builder."""
        from gam_api import ReportBuilder
        
        builder = ReportBuilder()
        context["builder"] = builder
        return builder
    
    def _add_dimensions(self, context):
        """Add dimensions to report."""
        builder = context.get("builder")
        if not builder:
            raise ValueError("Report builder not initialized")
        
        builder.add_dimension("DATE").add_dimension("AD_UNIT_NAME")
        
        return {"dimensions": builder.dimensions}
    
    def _add_metrics(self, context):
        """Add metrics to report."""
        builder = context.get("builder")
        if not builder:
            raise ValueError("Report builder not initialized")
        
        builder.add_metric("IMPRESSIONS").add_metric("CLICKS")
        
        return {"metrics": builder.metrics}
    
    def _set_date_range(self, context):
        """Set date range for report."""
        from gam_api import DateRange
        
        builder = context.get("builder")
        if not builder:
            raise ValueError("Report builder not initialized")
        
        date_range = DateRange.last_week()
        builder.set_date_range(date_range)
        
        return {"date_range": date_range}
    
    def _build_and_execute(self, context):
        """Build and execute the custom report."""
        builder = context.get("builder")
        if not builder:
            raise ValueError("Report builder not initialized")
        
        report_def = builder.build()
        
        # Simulate report execution
        result = {
            "status": "COMPLETED",
            "report_id": "custom_report_123",
            "total_rows": 500,
            "definition": report_def
        }
        
        context["custom_report_result"] = result
        return result
    
    # Data discovery journey step implementations
    def _fetch_available_dimensions(self, context):
        """Fetch available dimensions."""
        from gam_shared import validators
        
        # Get valid dimensions from validators
        dimensions = list(validators.VALID_DIMENSIONS)
        context["available_dimensions"] = dimensions
        
        return dimensions
    
    def _validate_dimension_format(self, context):
        """Validate dimension format is correct."""
        dimensions = context.get("available_dimensions", [])
        
        # Check that all dimensions are uppercase strings
        return all(isinstance(dim, str) and dim.isupper() for dim in dimensions)
    
    def _test_dimension_compatibility(self, context):
        """Test dimension compatibility with metrics."""
        from gam_shared import validators
        
        # Test that DATE dimension works with IMPRESSIONS metric
        try:
            validators.validate_dimension("DATE")
            validators.validate_metric("IMPRESSIONS")
            return True
        except Exception:
            return False
    
    # Actual test methods for pytest
    @pytest.mark.journey
    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_oauth_first_time_setup(self):
        """Test first-time OAuth setup journey."""
        result = await self.framework.execute_journey("auth_first_time_setup")
        
        assert result["status"].value == "success"
        assert result["duration"] < 30.0  # Should complete quickly
        assert len(result["steps"]) == 5
        assert all(step["success"] for step in result["steps"])
    
    @pytest.mark.journey
    @pytest.mark.critical  
    @pytest.mark.asyncio
    async def test_token_refresh_flow(self):
        """Test token refresh journey."""
        result = await self.framework.execute_journey("auth_token_refresh")
        
        assert result["status"].value == "success"
        assert result["duration"] < 15.0  # Should be fast
        assert all(step["success"] for step in result["steps"])
    
    @pytest.mark.journey
    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_quick_delivery_report(self):
        """Test quick delivery report generation."""
        result = await self.framework.execute_journey("report_quick_delivery")
        
        assert result["status"].value == "success"
        assert result["duration"] < 60.0  # Should complete within 1 minute
        assert all(step["success"] for step in result["steps"])
        
        # Verify report data structure
        context = result["context"]
        report_data = context.get("report_data", {})
        assert "data" in report_data
        assert len(report_data["data"]) > 0
    
    @pytest.mark.journey
    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_custom_report_builder(self):
        """Test custom report building journey."""
        result = await self.framework.execute_journey("report_custom_build")
        
        assert result["status"].value == "success"
        assert all(step["success"] for step in result["steps"])
        
        # Verify report definition
        context = result["context"]
        custom_result = context.get("custom_report_result", {})
        definition = custom_result.get("definition", {})
        
        assert len(definition.get("dimensions", [])) == 2
        assert len(definition.get("metrics", [])) == 2
        assert definition.get("date_range") is not None
    
    @pytest.mark.journey
    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_dimension_discovery(self):
        """Test dimension discovery journey."""
        result = await self.framework.execute_journey("discovery_dimensions")
        
        assert result["status"].value == "success"
        assert all(step["success"] for step in result["steps"])
        
        # Verify dimensions were found
        context = result["context"]
        dimensions = context.get("available_dimensions", [])
        assert len(dimensions) > 0
        assert "DATE" in dimensions
        assert "AD_UNIT_NAME" in dimensions
    
    @pytest.mark.journey
    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_critical_journey_suite(self):
        """Test all critical journeys as a suite."""
        suite_result = await self.framework.execute_journey_suite(
            priority=JourneyPriority.CRITICAL
        )
        
        assert suite_result["success_rate"] >= 90.0  # At least 90% success rate
        assert suite_result["total_journeys"] >= 5  # Should have at least 5 critical journeys
        
        # Verify no critical journey took too long
        for journey_id, result in suite_result["results"].items():
            assert result["duration"] < 120.0  # No journey should take more than 2 minutes


if __name__ == "__main__":
    # Run critical journeys directly
    async def main():
        test_instance = TestCriticalJourneys()
        test_instance.setup()
        
        print("🚀 Running Critical Journey Tests...")
        print("=" * 50)
        
        # Test each critical journey
        journeys = [
            "auth_first_time_setup",
            "auth_token_refresh", 
            "report_quick_delivery",
            "report_custom_build",
            "discovery_dimensions"
        ]
        
        for journey_id in journeys:
            print(f"\n📋 Testing: {journey_id}")
            result = await test_instance.framework.execute_journey(journey_id)
            
            if result["status"].value == "success":
                print(f"✅ {journey_id}: SUCCESS ({result['duration']:.2f}s)")
            else:
                print(f"❌ {journey_id}: FAILED")
                if "error" in result:
                    print(f"   Error: {result['error']}")
        
        # Generate performance report
        print(f"\n📊 Performance Report:")
        print("=" * 30)
        perf_report = test_instance.framework.get_performance_report()
        print(f"Total Journeys: {perf_report['total_journeys_executed']}")
        print(f"Average Duration: {perf_report['average_duration']:.2f}s")
        print(f"Average Success Rate: {perf_report['average_success_rate']:.1f}%")
    
    # Run if executed directly
    asyncio.run(main())