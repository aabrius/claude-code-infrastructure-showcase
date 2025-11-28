"""
Base class for journey testing with common setup and utilities.
"""

import pytest
import os
import sys
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# Add packages to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'packages', 'core', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'packages', 'shared', 'src'))

from gam_api import GAMClient, DateRange, ReportBuilder
from gam_api.exceptions import APIError, AuthenticationError, ValidationError
from gam_shared.logger import get_structured_logger
from tests.fixtures.journeys.journey_recorder import JourneyRecorder, JourneyValidator


class BaseJourneyTest(ABC):
    """Base class for all journey tests."""
    
    @property
    @abstractmethod
    def journey_name(self) -> str:
        """Name of the journey being tested."""
        pass
    
    @property
    @abstractmethod
    def journey_description(self) -> str:
        """Description of the journey."""
        pass
    
    @property
    def expected_steps(self) -> list:
        """List of expected steps in order."""
        return []
    
    @pytest.fixture
    def journey_recorder(self):
        """Create a journey recorder for the test."""
        return JourneyRecorder(
            journey_name=self.journey_name,
            description=self.journey_description
        )
    
    @pytest.fixture
    def journey_validator(self):
        """Create a journey validator."""
        return JourneyValidator()
    
    @pytest.fixture
    def logger(self):
        """Get structured logger for the test."""
        return get_structured_logger(f"journey.{self.journey_name}")
    
    @pytest.fixture
    def test_config(self):
        """Test configuration for journey tests."""
        return {
            "auth": {
                "network_code": "123456789",
                "client_id": "test-client-id",
                "client_secret": "test-client-secret",
                "refresh_token": "test-refresh-token"
            }
        }
    
    @pytest.fixture
    def gam_client(self, test_config):
        """Create a GAM client for testing."""
        # Check if we should use real credentials
        if os.getenv("USE_REAL_CREDENTIALS", "false").lower() == "true":
            return GAMClient()  # Use real googleads.yaml
        else:
            return GAMClient(config=test_config)  # Use test config
    
    def validate_journey(self, journey_recorder, journey_validator, 
                        max_duration: Optional[float] = None):
        """Validate the completed journey."""
        journey = journey_recorder.journey
        is_valid = journey_validator.validate_journey(
            journey=journey,
            expected_steps=self.expected_steps,
            max_duration=max_duration
        )
        
        # Generate metrics
        metrics = journey_recorder.get_metrics()
        print(f"\nJourney Metrics for '{self.journey_name}':")
        print(f"  Total Steps: {metrics['total_steps']}")
        print(f"  Completed: {metrics['completed_steps']}")
        print(f"  Failed: {metrics['failed_steps']}")
        print(f"  Success Rate: {metrics['success_rate']:.1f}%")
        print(f"  Total Duration: {metrics['total_duration']:.2f}s")
        
        assert is_valid, f"Journey validation failed for '{self.journey_name}'"
    
    def handle_step_error(self, journey_recorder, step_name: str, error: Exception):
        """Handle an error in a journey step."""
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error)
        }
        
        if hasattr(error, '__dict__'):
            error_data["error_details"] = error.__dict__
        
        journey_recorder.fail_step(
            error=str(error),
            **error_data
        )
        
        # Re-raise the error for pytest to catch
        raise
    
    @abstractmethod
    def test_happy_path(self, journey_recorder, gam_client):
        """Test the happy path journey."""
        pass
    
    def test_error_recovery(self, journey_recorder, gam_client):
        """Test error recovery in the journey."""
        # Default implementation - can be overridden
        journey_recorder.skip_step(
            "error_recovery",
            "Not implemented for this journey"
        )


class JourneyTestHelpers:
    """Helper functions for journey testing."""
    
    @staticmethod
    def assert_report_structure(report: Dict[str, Any], journey_recorder: JourneyRecorder):
        """Assert that a report has the expected structure."""
        journey_recorder.start_step("validate_report_structure")
        
        try:
            assert isinstance(report, dict), "Report should be a dictionary"
            
            # Check common fields
            common_fields = ["status", "data"]
            for field in common_fields:
                assert field in report, f"Report missing required field: {field}"
            
            # Check data is a list
            assert isinstance(report.get("data"), list), "Report data should be a list"
            
            # If data exists, check first row structure
            if report["data"]:
                first_row = report["data"][0]
                assert isinstance(first_row, dict), "Report rows should be dictionaries"
            
            journey_recorder.complete_step(
                validated_fields=list(report.keys()),
                row_count=len(report.get("data", []))
            )
            
        except Exception as e:
            journey_recorder.fail_step(str(e))
            raise
    
    @staticmethod
    def assert_api_response(response: Any, expected_status: int, 
                           journey_recorder: JourneyRecorder):
        """Assert API response has expected status."""
        journey_recorder.start_step("validate_api_response")
        
        try:
            if hasattr(response, 'status_code'):
                assert response.status_code == expected_status, \
                    f"Expected status {expected_status}, got {response.status_code}"
            
            journey_recorder.complete_step(
                status_code=getattr(response, 'status_code', None)
            )
            
        except Exception as e:
            journey_recorder.fail_step(str(e))
            raise
    
    @staticmethod
    def wait_for_report_completion(report_id: str, gam_client: GAMClient,
                                 journey_recorder: JourneyRecorder,
                                 max_wait: int = 60):
        """Wait for a report to complete."""
        journey_recorder.start_step("wait_for_report_completion")
        
        import time
        start_time = time.time()
        
        try:
            while time.time() - start_time < max_wait:
                # Check report status (implementation depends on API)
                # For now, simulate completion
                time.sleep(1)
                
                # In real implementation, check report.status
                # if report.status == "COMPLETED":
                #     break
            
            journey_recorder.complete_step(
                wait_time=time.time() - start_time,
                report_id=report_id
            )
            
        except Exception as e:
            journey_recorder.fail_step(str(e))
            raise