"""
Journey Test Runner - Execute all journey tests and generate comprehensive reports.

This script runs all journey tests and produces:
1. Individual journey reports
2. Aggregated journey metrics
3. Coverage report
4. Recommendations for improvements
"""

import os
import sys
import json
import pytest
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import argparse

# Add packages to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'packages', 'core', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'packages', 'shared', 'src'))


class JourneyTestRunner:
    """Runs journey tests and generates reports."""
    
    def __init__(self, output_dir: str = "tests/reports/journeys"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "journeys": {},
            "summary": {},
            "recommendations": []
        }
    
    def run_all_journeys(self, categories: List[str] = None):
        """Run all journey tests or specific categories."""
        test_files = []
        
        if categories:
            # Run specific categories
            for category in categories:
                test_file = f"tests/journeys/test_{category}_journeys.py"
                if os.path.exists(test_file):
                    test_files.append(test_file)
        else:
            # Run all journey tests
            journey_dir = Path("tests/journeys")
            test_files = list(journey_dir.glob("test_*_journeys.py"))
        
        print(f"Running {len(test_files)} journey test files...")
        
        for test_file in test_files:
            self._run_journey_file(str(test_file))
        
        # Generate summary
        self._generate_summary()
        
        # Generate recommendations
        self._generate_recommendations()
        
        # Save comprehensive report
        self._save_report()
    
    def _run_journey_file(self, test_file: str):
        """Run a single journey test file."""
        print(f"\nRunning: {test_file}")
        
        # Run pytest with JSON report
        json_report = self.output_dir / f"{Path(test_file).stem}_report.json"
        
        result = pytest.main([
            test_file,
            "--json-report",
            f"--json-report-file={json_report}",
            "-v",
            "--tb=short"
        ])
        
        # Parse results
        if json_report.exists():
            with open(json_report) as f:
                test_results = json.load(f)
                self._parse_test_results(test_file, test_results)
        
        # Also check for journey reports
        self._collect_journey_reports(test_file)
    
    def _parse_test_results(self, test_file: str, results: Dict[str, Any]):
        """Parse pytest JSON results."""
        category = Path(test_file).stem.replace("test_", "").replace("_journeys", "")
        
        self.results["journeys"][category] = {
            "file": test_file,
            "duration": results.get("duration", 0),
            "tests": {
                "total": results["summary"].get("total", 0),
                "passed": results["summary"].get("passed", 0),
                "failed": results["summary"].get("failed", 0),
                "skipped": results["summary"].get("skipped", 0)
            },
            "test_details": []
        }
        
        # Extract individual test results
        for test in results.get("tests", []):
            test_detail = {
                "name": test["nodeid"].split("::")[-1],
                "outcome": test["outcome"],
                "duration": test.get("duration", 0)
            }
            
            if test["outcome"] == "failed":
                test_detail["error"] = test.get("call", {}).get("longrepr", "Unknown error")
            
            self.results["journeys"][category]["test_details"].append(test_detail)
    
    def _collect_journey_reports(self, test_file: str):
        """Collect individual journey recorder reports."""
        journey_reports_dir = self.output_dir
        category = Path(test_file).stem.replace("test_", "").replace("_journeys", "")
        
        # Look for journey report files
        journey_files = list(journey_reports_dir.glob("*_latest.json"))
        
        for journey_file in journey_files:
            with open(journey_file) as f:
                journey_data = json.load(f)
                
                # Add to results
                if category not in self.results["journeys"]:
                    self.results["journeys"][category] = {"journey_runs": []}
                
                if "journey_runs" not in self.results["journeys"][category]:
                    self.results["journeys"][category]["journey_runs"] = []
                
                self.results["journeys"][category]["journey_runs"].append({
                    "name": journey_data["name"],
                    "status": journey_data["status"],
                    "duration": journey_data.get("duration", 0),
                    "steps": len(journey_data.get("steps", [])),
                    "timestamp": journey_data.get("timestamp")
                })
    
    def _generate_summary(self):
        """Generate summary statistics."""
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_duration = 0
        
        for category, data in self.results["journeys"].items():
            if "tests" in data:
                total_tests += data["tests"]["total"]
                total_passed += data["tests"]["passed"]
                total_failed += data["tests"]["failed"]
                total_duration += data.get("duration", 0)
        
        self.results["summary"] = {
            "total_categories": len(self.results["journeys"]),
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "success_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0,
            "total_duration": total_duration,
            "average_duration": total_duration / total_tests if total_tests > 0 else 0
        }
    
    def _generate_recommendations(self):
        """Generate recommendations based on test results."""
        recommendations = []
        
        # Check success rate
        success_rate = self.results["summary"]["success_rate"]
        if success_rate < 100:
            recommendations.append({
                "priority": "high",
                "category": "reliability",
                "message": f"Journey success rate is {success_rate:.1f}%. Investigate failing journeys.",
                "action": "Fix failing tests before proceeding with UI development"
            })
        
        # Check for missing journey categories
        expected_categories = [
            "authentication", "report_generation", "api", "mcp", 
            "sdk", "error_handling", "performance"
        ]
        
        tested_categories = set(self.results["journeys"].keys())
        missing_categories = set(expected_categories) - tested_categories
        
        if missing_categories:
            recommendations.append({
                "priority": "medium",
                "category": "coverage",
                "message": f"Missing journey tests for: {', '.join(missing_categories)}",
                "action": "Create journey tests for missing categories"
            })
        
        # Check performance
        avg_duration = self.results["summary"].get("average_duration", 0)
        if avg_duration > 30:
            recommendations.append({
                "priority": "low",
                "category": "performance",
                "message": f"Average test duration is {avg_duration:.1f}s. Consider optimization.",
                "action": "Optimize slow-running journey tests"
            })
        
        self.results["recommendations"] = recommendations
    
    def _save_report(self):
        """Save the comprehensive report."""
        report_file = self.output_dir / "journey_test_summary.json"
        
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nJourney test report saved to: {report_file}")
        
        # Also generate a markdown summary
        self._generate_markdown_summary()
    
    def _generate_markdown_summary(self):
        """Generate a markdown summary report."""
        md_file = self.output_dir / "journey_test_summary.md"
        
        with open(md_file, 'w') as f:
            f.write("# Journey Test Summary Report\n\n")
            f.write(f"Generated: {self.results['timestamp']}\n\n")
            
            # Summary
            f.write("## Summary\n\n")
            summary = self.results["summary"]
            f.write(f"- **Total Categories**: {summary['total_categories']}\n")
            f.write(f"- **Total Tests**: {summary['total_tests']}\n")
            f.write(f"- **Passed**: {summary['total_passed']}\n")
            f.write(f"- **Failed**: {summary['total_failed']}\n")
            f.write(f"- **Success Rate**: {summary['success_rate']:.1f}%\n")
            f.write(f"- **Total Duration**: {summary['total_duration']:.1f}s\n\n")
            
            # Journey Results
            f.write("## Journey Results\n\n")
            for category, data in self.results["journeys"].items():
                f.write(f"### {category.title()} Journeys\n\n")
                
                if "tests" in data:
                    tests = data["tests"]
                    f.write(f"- Tests: {tests['passed']}/{tests['total']} passed\n")
                    f.write(f"- Duration: {data.get('duration', 0):.1f}s\n\n")
                    
                    # Test details
                    if data.get("test_details"):
                        f.write("| Test | Status | Duration |\n")
                        f.write("|------|--------|----------|\n")
                        
                        for test in data["test_details"]:
                            status_icon = "✅" if test["outcome"] == "passed" else "❌"
                            f.write(f"| {test['name']} | {status_icon} {test['outcome']} | {test['duration']:.2f}s |\n")
                        
                        f.write("\n")
            
            # Recommendations
            if self.results["recommendations"]:
                f.write("## Recommendations\n\n")
                
                for rec in sorted(self.results["recommendations"], 
                               key=lambda x: ["high", "medium", "low"].index(x["priority"])):
                    icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}[rec["priority"]]
                    f.write(f"{icon} **{rec['priority'].title()} Priority** - {rec['category'].title()}\n")
                    f.write(f"   - {rec['message']}\n")
                    f.write(f"   - **Action**: {rec['action']}\n\n")
        
        print(f"Markdown summary saved to: {md_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run GAM API journey tests"
    )
    parser.add_argument(
        "--categories",
        nargs="+",
        help="Specific journey categories to test",
        choices=["authentication", "report_generation", "api", "mcp", "sdk", "error_handling", "performance"]
    )
    parser.add_argument(
        "--output-dir",
        default="tests/reports/journeys",
        help="Output directory for reports"
    )
    parser.add_argument(
        "--real-credentials",
        action="store_true",
        help="Use real credentials from googleads.yaml"
    )
    
    args = parser.parse_args()
    
    # Set environment variable for real credentials
    if args.real_credentials:
        os.environ["USE_REAL_CREDENTIALS"] = "true"
    
    # Run tests
    runner = JourneyTestRunner(output_dir=args.output_dir)
    runner.run_all_journeys(categories=args.categories)


if __name__ == "__main__":
    main()