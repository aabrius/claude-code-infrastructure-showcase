"""
Journey Testing Framework for GAM API System

This framework provides comprehensive testing for complete user journeys
across all interfaces (MCP, REST API, Python SDK, CLI).
"""

import asyncio
import json
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from enum import Enum
import pytest
from pathlib import Path


class JourneyPriority(Enum):
    """Journey priority levels for testing."""
    CRITICAL = "P0"      # Must work perfectly
    IMPORTANT = "P1"     # Should work reliably  
    ADVANCED = "P2"      # Nice to have


class JourneyStatus(Enum):
    """Journey execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class JourneyStep:
    """Individual step within a journey."""
    name: str
    action: Callable
    expected_result: Any = None
    timeout: float = 30.0
    retry_count: int = 0
    validation: Optional[Callable] = None
    cleanup: Optional[Callable] = None


@dataclass
class JourneyMetrics:
    """Performance and reliability metrics for a journey."""
    start_time: float = 0.0
    end_time: float = 0.0
    duration: float = 0.0
    memory_usage: float = 0.0
    api_calls: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    errors: List[str] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate based on errors."""
        total_operations = self.api_calls
        if total_operations == 0:
            return 100.0
        return ((total_operations - len(self.errors)) / total_operations) * 100


@dataclass
class Journey:
    """Complete user journey definition."""
    id: str
    name: str
    description: str
    priority: JourneyPriority
    interface: str  # "mcp", "api", "sdk", "cli"
    category: str   # "authentication", "reporting", "discovery", etc.
    steps: List[JourneyStep] = field(default_factory=list)
    preconditions: List[Callable] = field(default_factory=list)
    postconditions: List[Callable] = field(default_factory=list)
    test_data: Dict[str, Any] = field(default_factory=dict)
    expected_duration: float = 60.0
    tags: List[str] = field(default_factory=list)


class JourneyTestFramework:
    """Main framework for executing and managing journey tests."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the journey testing framework."""
        self.config = config or {}
        self.journeys: Dict[str, Journey] = {}
        self.results: Dict[str, Dict[str, Any]] = {}
        self.metrics: Dict[str, JourneyMetrics] = {}
        self.test_data_dir = Path("tests/journeys/data")
        self.results_dir = Path("tests/journeys/results")
        
        # Ensure directories exist
        self.test_data_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def register_journey(self, journey: Journey):
        """Register a journey for testing."""
        self.journeys[journey.id] = journey
    
    def load_journeys_from_config(self, config_path: str):
        """Load journey definitions from YAML/JSON configuration."""
        config_file = Path(config_path)
        if config_file.suffix == '.json':
            with open(config_file) as f:
                config_data = json.load(f)
        else:
            # YAML loading would go here
            raise NotImplementedError("YAML loading not implemented yet")
        
        for journey_config in config_data.get('journeys', []):
            journey = self._create_journey_from_config(journey_config)
            self.register_journey(journey)
    
    def _create_journey_from_config(self, config: Dict[str, Any]) -> Journey:
        """Create a Journey object from configuration."""
        # This would be implemented to parse configuration
        # For now, return a basic journey
        return Journey(
            id=config['id'],
            name=config['name'], 
            description=config.get('description', ''),
            priority=JourneyPriority(config.get('priority', 'P2')),
            interface=config.get('interface', 'api'),
            category=config.get('category', 'general')
        )
    
    async def execute_journey(self, journey_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a complete journey and return results."""
        if journey_id not in self.journeys:
            raise ValueError(f"Journey {journey_id} not found")
        
        journey = self.journeys[journey_id]
        context = context or {}
        metrics = JourneyMetrics()
        
        # Record start time
        metrics.start_time = time.time()
        
        try:
            # Execute preconditions
            await self._execute_preconditions(journey, context)
            
            # Execute journey steps
            step_results = []
            for i, step in enumerate(journey.steps):
                step_result = await self._execute_step(step, context, metrics)
                step_results.append(step_result)
                
                # Stop on failure unless configured to continue
                if not step_result.get('success', False) and not self.config.get('continue_on_failure', False):
                    break
            
            # Execute postconditions
            await self._execute_postconditions(journey, context)
            
            # Calculate final metrics
            metrics.end_time = time.time()
            metrics.duration = metrics.end_time - metrics.start_time
            
            # Determine overall success
            success = all(result.get('success', False) for result in step_results)
            
            result = {
                'journey_id': journey_id,
                'status': JourneyStatus.SUCCESS if success else JourneyStatus.FAILED,
                'duration': metrics.duration,
                'steps': step_results,
                'metrics': metrics,
                'timestamp': datetime.utcnow().isoformat(),
                'context': context
            }
            
            # Store results
            self.results[journey_id] = result
            self.metrics[journey_id] = metrics
            
            return result
            
        except Exception as e:
            metrics.end_time = time.time()
            metrics.duration = metrics.end_time - metrics.start_time
            metrics.errors.append(str(e))
            
            result = {
                'journey_id': journey_id,
                'status': JourneyStatus.FAILED,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'duration': metrics.duration,
                'timestamp': datetime.utcnow().isoformat(),
                'context': context
            }
            
            self.results[journey_id] = result
            return result
    
    async def _execute_preconditions(self, journey: Journey, context: Dict[str, Any]):
        """Execute journey preconditions."""
        for precondition in journey.preconditions:
            await self._call_async_or_sync(precondition, context)
    
    async def _execute_postconditions(self, journey: Journey, context: Dict[str, Any]):
        """Execute journey postconditions."""
        for postcondition in journey.postconditions:
            await self._call_async_or_sync(postcondition, context)
    
    async def _execute_step(self, step: JourneyStep, context: Dict[str, Any], metrics: JourneyMetrics) -> Dict[str, Any]:
        """Execute a single journey step."""
        step_start = time.time()
        
        try:
            # Execute the step action
            result = await self._call_async_or_sync(step.action, context)
            
            # Validate result if validator provided
            if step.validation:
                validation_result = await self._call_async_or_sync(step.validation, result, context)
                if not validation_result:
                    raise AssertionError(f"Step validation failed for {step.name}")
            
            # Check expected result if provided
            if step.expected_result is not None:
                if result != step.expected_result:
                    raise AssertionError(f"Expected {step.expected_result}, got {result}")
            
            step_duration = time.time() - step_start
            
            return {
                'step': step.name,
                'success': True,
                'result': result,
                'duration': step_duration,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            step_duration = time.time() - step_start
            metrics.errors.append(f"{step.name}: {str(e)}")
            
            return {
                'step': step.name,
                'success': False,
                'error': str(e),
                'duration': step_duration,
                'timestamp': datetime.utcnow().isoformat()
            }
        
        finally:
            # Execute cleanup if provided
            if step.cleanup:
                try:
                    await self._call_async_or_sync(step.cleanup, context)
                except Exception as cleanup_error:
                    metrics.errors.append(f"{step.name} cleanup: {str(cleanup_error)}")
    
    async def _call_async_or_sync(self, func: Callable, *args, **kwargs):
        """Call a function whether it's async or sync."""
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    
    async def execute_journey_suite(self, priority: JourneyPriority = None, 
                                   interface: str = None, 
                                   category: str = None,
                                   tags: List[str] = None) -> Dict[str, Any]:
        """Execute multiple journeys based on filters."""
        # Filter journeys
        filtered_journeys = self._filter_journeys(priority, interface, category, tags)
        
        # Execute journeys
        suite_results = {}
        for journey_id in filtered_journeys:
            result = await self.execute_journey(journey_id)
            suite_results[journey_id] = result
        
        # Generate suite summary
        suite_summary = self._generate_suite_summary(suite_results)
        
        # Save results
        self._save_suite_results(suite_summary)
        
        return suite_summary
    
    def _filter_journeys(self, priority: JourneyPriority = None, 
                        interface: str = None, 
                        category: str = None,
                        tags: List[str] = None) -> List[str]:
        """Filter journeys based on criteria."""
        filtered = []
        
        for journey_id, journey in self.journeys.items():
            # Filter by priority
            if priority and journey.priority != priority:
                continue
                
            # Filter by interface
            if interface and journey.interface != interface:
                continue
                
            # Filter by category
            if category and journey.category != category:
                continue
                
            # Filter by tags
            if tags and not any(tag in journey.tags for tag in tags):
                continue
            
            filtered.append(journey_id)
        
        return filtered
    
    def _generate_suite_summary(self, suite_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics for journey suite."""
        total_journeys = len(suite_results)
        successful_journeys = sum(1 for result in suite_results.values() 
                                if result.get('status') == JourneyStatus.SUCCESS)
        
        total_duration = sum(result.get('duration', 0) for result in suite_results.values())
        
        return {
            'total_journeys': total_journeys,
            'successful_journeys': successful_journeys,
            'failed_journeys': total_journeys - successful_journeys,
            'success_rate': (successful_journeys / total_journeys * 100) if total_journeys > 0 else 0,
            'total_duration': total_duration,
            'average_duration': total_duration / total_journeys if total_journeys > 0 else 0,
            'results': suite_results,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _save_suite_results(self, summary: Dict[str, Any]):
        """Save journey suite results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.results_dir / f"journey_suite_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
    
    def get_journey_metrics(self, journey_id: str) -> Optional[JourneyMetrics]:
        """Get metrics for a specific journey."""
        return self.metrics.get(journey_id)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report across all journeys."""
        if not self.metrics:
            return {"message": "No journey metrics available"}
        
        durations = [metrics.duration for metrics in self.metrics.values()]
        success_rates = [metrics.success_rate for metrics in self.metrics.values()]
        
        return {
            'total_journeys_executed': len(self.metrics),
            'average_duration': sum(durations) / len(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'average_success_rate': sum(success_rates) / len(success_rates),
            'journey_details': {
                journey_id: {
                    'duration': metrics.duration,
                    'success_rate': metrics.success_rate,
                    'api_calls': metrics.api_calls,
                    'cache_hits': metrics.cache_hits,
                    'errors': len(metrics.errors)
                }
                for journey_id, metrics in self.metrics.items()
            }
        }


# Pytest integration
class JourneyTestPlugin:
    """Pytest plugin for journey testing."""
    
    def __init__(self):
        self.framework = JourneyTestFramework()
    
    def pytest_configure(self, config):
        """Configure pytest for journey testing."""
        config.addinivalue_line("markers", "journey: mark test as a journey test")
        config.addinivalue_line("markers", "critical: mark test as critical priority")
        config.addinivalue_line("markers", "performance: mark test as performance test")
    
    def pytest_collection_modifyitems(self, config, items):
        """Modify test collection for journey tests."""
        for item in items:
            if "journey" in item.keywords:
                # Add timeout for journey tests
                if not hasattr(item, 'timeout'):
                    item.add_marker(pytest.mark.timeout(300))  # 5 minute default timeout


# Example journey factory functions
def create_authentication_journey() -> Journey:
    """Create authentication journey for testing."""
    return Journey(
        id="auth_oauth_flow",
        name="OAuth Authentication Flow",
        description="Complete OAuth2 authentication flow for new user",
        priority=JourneyPriority.CRITICAL,
        interface="api",
        category="authentication",
        steps=[
            JourneyStep(
                name="load_config",
                action=lambda ctx: {"client_id": "test_client", "client_secret": "test_secret"}
            ),
            JourneyStep(
                name="request_auth_url",
                action=lambda ctx: "https://accounts.google.com/oauth/authorize?..."
            ),
            JourneyStep(
                name="exchange_code_for_token",
                action=lambda ctx: {"access_token": "test_token", "refresh_token": "test_refresh"}
            ),
            JourneyStep(
                name="validate_credentials",
                action=lambda ctx: True,
                expected_result=True
            )
        ],
        expected_duration=30.0,
        tags=["auth", "oauth", "critical"]
    )


def create_quick_report_journey() -> Journey:
    """Create quick report generation journey."""
    return Journey(
        id="quick_report_delivery",
        name="Generate Delivery Report",
        description="Generate a quick delivery report using pre-configured settings",
        priority=JourneyPriority.CRITICAL,
        interface="api",
        category="reporting",
        steps=[
            JourneyStep(
                name="authenticate",
                action=lambda ctx: {"authenticated": True}
            ),
            JourneyStep(
                name="request_delivery_report",
                action=lambda ctx: {
                    "report_id": "report_123",
                    "status": "RUNNING",
                    "request_time": datetime.utcnow().isoformat()
                }
            ),
            JourneyStep(
                name="poll_report_status",
                action=lambda ctx: {"status": "COMPLETED", "total_rows": 1000}
            ),
            JourneyStep(
                name="download_results",
                action=lambda ctx: {"data": [{"date": "2024-01-01", "impressions": 1000}]}
            )
        ],
        expected_duration=60.0,
        tags=["reporting", "delivery", "critical"]
    )


# Global framework instance for easy access
journey_framework = JourneyTestFramework()