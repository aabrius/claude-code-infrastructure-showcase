"""
Journey Recorder for tracking and validating user journeys through the GAM API system.

This module provides tools to record, validate, and report on complete user journeys,
ensuring all paths through the system work correctly.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class StepStatus(Enum):
    """Status of a journey step."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class JourneyStep:
    """Represents a single step in a user journey."""
    name: str
    status: StepStatus = StepStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    
    @property
    def duration(self) -> Optional[float]:
        """Calculate step duration in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary."""
        return {
            "name": self.name,
            "status": self.status.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "data": self.data,
            "error": self.error
        }


@dataclass
class Journey:
    """Represents a complete user journey."""
    name: str
    description: str = ""
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    steps: List[JourneyStep] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration(self) -> Optional[float]:
        """Calculate total journey duration."""
        if self.end_time:
            return self.end_time - self.start_time
        return None
    
    @property
    def status(self) -> StepStatus:
        """Determine overall journey status."""
        if any(step.status == StepStatus.FAILED for step in self.steps):
            return StepStatus.FAILED
        elif all(step.status == StepStatus.COMPLETED for step in self.steps):
            return StepStatus.COMPLETED
        elif any(step.status == StepStatus.IN_PROGRESS for step in self.steps):
            return StepStatus.IN_PROGRESS
        else:
            return StepStatus.PENDING
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert journey to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "status": self.status.value,
            "steps": [step.to_dict() for step in self.steps],
            "metadata": self.metadata,
            "timestamp": datetime.fromtimestamp(self.start_time).isoformat()
        }


class JourneyRecorder:
    """Records and tracks user journeys for testing and validation."""
    
    def __init__(self, journey_name: str, description: str = "", 
                 output_dir: str = "tests/reports/journeys"):
        """
        Initialize journey recorder.
        
        Args:
            journey_name: Name of the journey being recorded
            description: Description of the journey
            output_dir: Directory to save journey reports
        """
        self.journey = Journey(name=journey_name, description=description)
        self.current_step: Optional[JourneyStep] = None
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def start_step(self, step_name: str, **data) -> JourneyStep:
        """
        Start recording a new step.
        
        Args:
            step_name: Name of the step
            **data: Additional data to record with the step
            
        Returns:
            The created step
        """
        # Complete current step if exists
        if self.current_step and self.current_step.status == StepStatus.IN_PROGRESS:
            self.complete_step()
        
        # Create new step
        step = JourneyStep(
            name=step_name,
            status=StepStatus.IN_PROGRESS,
            start_time=time.time(),
            data=data
        )
        
        self.journey.steps.append(step)
        self.current_step = step
        return step
    
    def record_step(self, step_name: str, **data) -> JourneyStep:
        """Alias for start_step for backward compatibility."""
        return self.start_step(step_name, **data)
    
    def complete_step(self, **data) -> Optional[JourneyStep]:
        """
        Complete the current step.
        
        Args:
            **data: Additional data to merge with step data
            
        Returns:
            The completed step
        """
        if not self.current_step:
            return None
        
        self.current_step.end_time = time.time()
        self.current_step.status = StepStatus.COMPLETED
        self.current_step.data.update(data)
        
        completed_step = self.current_step
        self.current_step = None
        return completed_step
    
    def fail_step(self, error: str, **data) -> Optional[JourneyStep]:
        """
        Mark the current step as failed.
        
        Args:
            error: Error message
            **data: Additional failure data
            
        Returns:
            The failed step
        """
        if not self.current_step:
            return None
        
        self.current_step.end_time = time.time()
        self.current_step.status = StepStatus.FAILED
        self.current_step.error = error
        self.current_step.data.update(data)
        
        failed_step = self.current_step
        self.current_step = None
        return failed_step
    
    def skip_step(self, step_name: str, reason: str) -> JourneyStep:
        """
        Record a skipped step.
        
        Args:
            step_name: Name of the skipped step
            reason: Reason for skipping
            
        Returns:
            The skipped step
        """
        step = JourneyStep(
            name=step_name,
            status=StepStatus.SKIPPED,
            data={"reason": reason}
        )
        self.journey.steps.append(step)
        return step
    
    def add_metadata(self, **metadata) -> None:
        """Add metadata to the journey."""
        self.journey.metadata.update(metadata)
    
    def complete(self, **metadata) -> Journey:
        """
        Complete the journey recording.
        
        Args:
            **metadata: Final metadata to add
            
        Returns:
            The completed journey
        """
        # Complete current step if exists
        if self.current_step and self.current_step.status == StepStatus.IN_PROGRESS:
            self.complete_step()
        
        self.journey.end_time = time.time()
        self.journey.metadata.update(metadata)
        
        # Save journey report
        self._save_report()
        
        return self.journey
    
    def _save_report(self) -> Path:
        """Save journey report to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.journey.name}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(self.journey.to_dict(), f, indent=2)
        
        # Also save latest version
        latest_filepath = self.output_dir / f"{self.journey.name}_latest.json"
        with open(latest_filepath, 'w') as f:
            json.dump(self.journey.to_dict(), f, indent=2)
        
        return filepath
    
    def assert_step_completed(self, step_name: str) -> None:
        """Assert that a specific step was completed successfully."""
        step = self._find_step(step_name)
        assert step is not None, f"Step '{step_name}' not found in journey"
        assert step.status == StepStatus.COMPLETED, \
            f"Step '{step_name}' not completed. Status: {step.status.value}"
    
    def assert_journey_completed(self) -> None:
        """Assert that the entire journey completed successfully."""
        assert self.journey.status == StepStatus.COMPLETED, \
            f"Journey not completed. Status: {self.journey.status.value}"
    
    def _find_step(self, step_name: str) -> Optional[JourneyStep]:
        """Find a step by name."""
        for step in self.journey.steps:
            if step.name == step_name:
                return step
        return None
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get journey metrics."""
        completed_steps = sum(1 for s in self.journey.steps 
                            if s.status == StepStatus.COMPLETED)
        failed_steps = sum(1 for s in self.journey.steps 
                         if s.status == StepStatus.FAILED)
        
        return {
            "total_steps": len(self.journey.steps),
            "completed_steps": completed_steps,
            "failed_steps": failed_steps,
            "skipped_steps": sum(1 for s in self.journey.steps 
                               if s.status == StepStatus.SKIPPED),
            "success_rate": (completed_steps / len(self.journey.steps) * 100) 
                          if self.journey.steps else 0,
            "total_duration": self.journey.duration,
            "average_step_duration": sum(s.duration or 0 for s in self.journey.steps) 
                                   / len(self.journey.steps) if self.journey.steps else 0
        }


class JourneyValidator:
    """Validates journeys against expected patterns."""
    
    def __init__(self):
        self.validations: List[Dict[str, Any]] = []
    
    def validate_journey(self, journey: Journey, 
                        expected_steps: List[str],
                        max_duration: Optional[float] = None) -> bool:
        """
        Validate a journey against expectations.
        
        Args:
            journey: Journey to validate
            expected_steps: List of expected step names in order
            max_duration: Maximum allowed duration in seconds
            
        Returns:
            True if valid, False otherwise
        """
        validation = {
            "journey": journey.name,
            "timestamp": datetime.now().isoformat(),
            "expected_steps": expected_steps,
            "actual_steps": [s.name for s in journey.steps],
            "errors": []
        }
        
        # Check all expected steps are present
        actual_step_names = [s.name for s in journey.steps]
        for expected in expected_steps:
            if expected not in actual_step_names:
                validation["errors"].append(f"Missing expected step: {expected}")
        
        # Check duration
        if max_duration and journey.duration and journey.duration > max_duration:
            validation["errors"].append(
                f"Journey took too long: {journey.duration:.2f}s > {max_duration}s"
            )
        
        # Check for failures
        failed_steps = [s for s in journey.steps if s.status == StepStatus.FAILED]
        for step in failed_steps:
            validation["errors"].append(f"Step failed: {step.name} - {step.error}")
        
        validation["valid"] = len(validation["errors"]) == 0
        self.validations.append(validation)
        
        return validation["valid"]
    
    def generate_report(self, output_file: str = "journey_validation_report.json"):
        """Generate validation report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_validations": len(self.validations),
            "passed": sum(1 for v in self.validations if v["valid"]),
            "failed": sum(1 for v in self.validations if not v["valid"]),
            "validations": self.validations
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report