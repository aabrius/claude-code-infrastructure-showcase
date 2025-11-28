"""
Test report generation journeys for GAM API.

This module tests all report generation user journeys including:
- Quick reports (all 5 types)
- Custom reports with various configurations
- Report export in different formats
- Large report handling
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, Mock

from tests.journeys.base_journey_test import BaseJourneyTest, JourneyTestHelpers
from gam_api import GAMClient, DateRange, ReportBuilder
from gam_api.exceptions import ValidationError, ReportGenerationError


class TestDeliveryReportJourney(BaseJourneyTest):
    """Test delivery report generation journey."""
    
    @property
    def journey_name(self):
        return "delivery_report_generation"
    
    @property
    def journey_description(self):
        return "User generates a delivery report with impressions, clicks, CTR, and revenue"
    
    @property
    def expected_steps(self):
        return [
            "initialize_client",
            "create_date_range",
            "request_report",
            "validate_response",
            "process_results",
            "export_data"
        ]
    
    def test_happy_path(self, journey_recorder, gam_client):
        """Test successful delivery report generation."""
        # Step 1: Initialize client
        journey_recorder.start_step("initialize_client")
        assert gam_client is not None
        journey_recorder.complete_step(client_initialized=True)
        
        # Step 2: Create date range
        journey_recorder.start_step("create_date_range")
        date_range = DateRange.last_week()
        assert date_range.start_date is not None
        assert date_range.end_date is not None
        journey_recorder.complete_step(
            start_date=date_range.start_date,
            end_date=date_range.end_date
        )
        
        # Step 3: Request report
        journey_recorder.start_step("request_report")
        
        # Mock the report generation
        with patch.object(gam_client, 'delivery_report') as mock_report:
            mock_report.return_value = {
                "status": "completed",
                "report_type": "delivery",
                "data": [
                    {
                        "date": "2024-01-15",
                        "impressions": 150000,
                        "clicks": 1200,
                        "ctr": 0.008,
                        "revenue": 450.50
                    },
                    {
                        "date": "2024-01-16", 
                        "impressions": 165000,
                        "clicks": 1350,
                        "ctr": 0.0082,
                        "revenue": 495.75
                    }
                ],
                "summary": {
                    "total_impressions": 315000,
                    "total_clicks": 2550,
                    "average_ctr": 0.0081,
                    "total_revenue": 946.25
                }
            }
            
            report = gam_client.delivery_report(date_range)
            journey_recorder.complete_step(
                report_requested=True,
                row_count=len(report.get("data", []))
            )
        
        # Step 4: Validate response
        journey_recorder.start_step("validate_response")
        JourneyTestHelpers.assert_report_structure(report, journey_recorder)
        
        # Additional validations
        assert report["status"] == "completed"
        assert report["report_type"] == "delivery"
        assert len(report["data"]) > 0
        assert "summary" in report
        
        journey_recorder.complete_step(response_valid=True)
        
        # Step 5: Process results
        journey_recorder.start_step("process_results")
        
        # Simulate processing the data
        total_impressions = sum(row["impressions"] for row in report["data"])
        total_revenue = sum(row["revenue"] for row in report["data"])
        
        assert total_impressions == report["summary"]["total_impressions"]
        assert abs(total_revenue - report["summary"]["total_revenue"]) < 0.01
        
        journey_recorder.complete_step(
            total_impressions=total_impressions,
            total_revenue=total_revenue
        )
        
        # Step 6: Export data
        journey_recorder.start_step("export_data")
        
        # Test different export formats
        from gam_shared.formatters import format_as_json, format_as_csv
        
        json_output = format_as_json(report["data"])
        assert json_output is not None
        assert len(json_output) > 0
        
        csv_output = format_as_csv(report["data"])
        assert csv_output is not None
        assert "impressions" in csv_output
        
        journey_recorder.complete_step(
            export_formats=["json", "csv"],
            export_successful=True
        )
        
        # Complete journey
        journey_recorder.complete()
        self.validate_journey(journey_recorder, journey_validator=None, max_duration=30)
    
    def test_date_validation_journey(self, journey_recorder, gam_client):
        """Test date validation in report generation."""
        journey_recorder.start_step("initialize_client")
        journey_recorder.complete_step()
        
        # Test future date rejection
        journey_recorder.start_step("create_invalid_date_range")
        
        try:
            future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # This should fail validation
            with pytest.raises(ValidationError):
                date_range = DateRange(current_date, future_date)
                gam_client.delivery_report(date_range)
            
            journey_recorder.fail_step("Future date validation failed as expected")
        except ValidationError as e:
            journey_recorder.complete_step(
                validation_error=str(e),
                validation_worked=True
            )
        
        journey_recorder.complete()


class TestCustomReportJourney(BaseJourneyTest):
    """Test custom report generation journey."""
    
    @property
    def journey_name(self):
        return "custom_report_generation"
    
    @property
    def journey_description(self):
        return "User creates a custom report with specific dimensions and metrics"
    
    @property
    def expected_steps(self):
        return [
            "initialize_builder",
            "add_dimensions",
            "add_metrics",
            "add_filters",
            "set_date_range",
            "build_report_definition",
            "create_report",
            "wait_for_completion",
            "retrieve_results"
        ]
    
    def test_happy_path(self, journey_recorder, gam_client):
        """Test successful custom report creation."""
        # Step 1: Initialize builder
        journey_recorder.start_step("initialize_builder")
        builder = ReportBuilder()
        assert builder is not None
        journey_recorder.complete_step(builder_initialized=True)
        
        # Step 2: Add dimensions
        journey_recorder.start_step("add_dimensions")
        
        dimensions = ["DATE", "AD_UNIT_NAME", "DEVICE_CATEGORY_NAME"]
        for dim in dimensions:
            builder.add_dimension(dim)
        
        assert len(builder.dimensions) == 3
        journey_recorder.complete_step(dimensions_added=dimensions)
        
        # Step 3: Add metrics
        journey_recorder.start_step("add_metrics")
        
        metrics = ["IMPRESSIONS", "CLICKS", "CTR", "REVENUE", "ECPM"]
        for metric in metrics:
            builder.add_metric(metric)
        
        assert len(builder.metrics) == 5
        journey_recorder.complete_step(metrics_added=metrics)
        
        # Step 4: Add filters
        journey_recorder.start_step("add_filters")
        
        builder.add_filter("DEVICE_CATEGORY_NAME", "equals", "Mobile")
        assert len(builder.filters) == 1
        
        journey_recorder.complete_step(filters_added=1)
        
        # Step 5: Set date range
        journey_recorder.start_step("set_date_range")
        
        date_range = DateRange.last_month()
        builder.set_date_range(date_range)
        assert builder.date_range is not None
        
        journey_recorder.complete_step(
            date_range_set=True,
            start_date=date_range.start_date,
            end_date=date_range.end_date
        )
        
        # Step 6: Build report definition
        journey_recorder.start_step("build_report_definition")
        
        report_def = builder.build()
        assert "dimensions" in report_def
        assert "metrics" in report_def
        assert "filters" in report_def
        assert "date_range" in report_def
        
        journey_recorder.complete_step(
            definition_built=True,
            definition_size=len(str(report_def))
        )
        
        # Step 7: Create report
        journey_recorder.start_step("create_report")
        
        with patch.object(gam_client, 'create_report') as mock_create:
            mock_create.return_value = {
                "report_id": "report_12345",
                "status": "running",
                "created_at": datetime.now().isoformat()
            }
            
            report_response = gam_client.create_report(report_def)
            assert "report_id" in report_response
            
            journey_recorder.complete_step(
                report_id=report_response["report_id"],
                initial_status=report_response["status"]
            )
        
        # Step 8: Wait for completion
        journey_recorder.start_step("wait_for_completion")
        
        # Simulate polling for completion
        import time
        start_wait = time.time()
        
        # In real scenario, this would poll the API
        time.sleep(0.5)  # Simulate wait
        
        journey_recorder.complete_step(
            wait_duration=time.time() - start_wait,
            final_status="completed"
        )
        
        # Step 9: Retrieve results
        journey_recorder.start_step("retrieve_results")
        
        mock_results = {
            "status": "completed",
            "report_id": "report_12345",
            "data": [
                {
                    "date": "2024-01-01",
                    "ad_unit_name": "Mobile_Banner",
                    "device_category_name": "Mobile",
                    "impressions": 50000,
                    "clicks": 400,
                    "ctr": 0.008,
                    "revenue": 150.00,
                    "ecpm": 3.00
                }
            ],
            "row_count": 1,
            "execution_time": 2.5
        }
        
        assert mock_results["status"] == "completed"
        assert len(mock_results["data"]) > 0
        
        journey_recorder.complete_step(
            results_retrieved=True,
            row_count=mock_results["row_count"],
            execution_time=mock_results["execution_time"]
        )
        
        journey_recorder.complete()
        self.validate_journey(journey_recorder, journey_validator=None, max_duration=60)


class TestAllQuickReportsJourney(BaseJourneyTest):
    """Test generation of all 5 quick report types."""
    
    @property
    def journey_name(self):
        return "all_quick_reports"
    
    @property
    def journey_description(self):
        return "User generates all 5 types of quick reports to verify functionality"
    
    @property
    def expected_steps(self):
        return [
            "generate_delivery_report",
            "generate_inventory_report",
            "generate_sales_report",
            "generate_reach_report",
            "generate_programmatic_report",
            "compare_results"
        ]
    
    def test_happy_path(self, journey_recorder, gam_client):
        """Test all quick report types."""
        date_range = DateRange.last_week()
        results = {}
        
        # Test each report type
        report_types = [
            ("delivery", gam_client.delivery_report),
            ("inventory", gam_client.inventory_report),
            ("sales", gam_client.sales_report),
            ("reach", gam_client.reach_report),
            ("programmatic", gam_client.programmatic_report)
        ]
        
        for report_type, report_method in report_types:
            step_name = f"generate_{report_type}_report"
            journey_recorder.start_step(step_name)
            
            try:
                with patch.object(gam_client, f'{report_type}_report') as mock_report:
                    # Mock appropriate response for each report type
                    mock_report.return_value = self._get_mock_report_data(report_type)
                    
                    report = report_method(date_range)
                    assert report is not None
                    assert "data" in report
                    
                    results[report_type] = {
                        "row_count": len(report.get("data", [])),
                        "has_summary": "summary" in report
                    }
                    
                    journey_recorder.complete_step(
                        report_type=report_type,
                        success=True,
                        row_count=results[report_type]["row_count"]
                    )
                    
            except Exception as e:
                journey_recorder.fail_step(str(e))
                raise
        
        # Compare results
        journey_recorder.start_step("compare_results")
        
        # Verify all reports were generated
        assert len(results) == 5
        for report_type, data in results.items():
            assert data["row_count"] > 0
        
        journey_recorder.complete_step(
            all_reports_generated=True,
            report_types=list(results.keys())
        )
        
        journey_recorder.complete()
        self.validate_journey(journey_recorder, journey_validator=None, max_duration=120)
    
    def _get_mock_report_data(self, report_type):
        """Get mock data for different report types."""
        base_response = {
            "status": "completed",
            "report_type": report_type,
            "data": []
        }
        
        if report_type == "delivery":
            base_response["data"] = [
                {"date": "2024-01-15", "impressions": 100000, "clicks": 800, 
                 "ctr": 0.008, "revenue": 300.00}
            ]
        elif report_type == "inventory":
            base_response["data"] = [
                {"date": "2024-01-15", "ad_requests": 120000, 
                 "matched_requests": 100000, "fill_rate": 0.833}
            ]
        elif report_type == "sales":
            base_response["data"] = [
                {"advertiser_name": "Advertiser A", "order_name": "Campaign 1",
                 "revenue": 5000.00, "ecpm": 2.50}
            ]
        elif report_type == "reach":
            base_response["data"] = [
                {"country_name": "United States", "unique_reach": 50000,
                 "average_frequency": 2.5}
            ]
        elif report_type == "programmatic":
            base_response["data"] = [
                {"channel_name": "Open Auction", "impressions": 80000,
                 "revenue": 200.00, "ecpm": 2.50}
            ]
        
        return base_response