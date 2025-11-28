#!/usr/bin/env python3
"""
Coverage reporting and validation script.

Runs comprehensive test suite with coverage analysis and generates
detailed reports for code coverage validation.
"""

import os
import sys
import subprocess
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse


class CoverageReporter:
    """Generate and analyze test coverage reports."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.coverage_dir = self.project_root / "htmlcov"
        self.reports_dir = self.project_root / "coverage_reports"
        self.reports_dir.mkdir(exist_ok=True)
    
    def run_tests_with_coverage(self, test_types: List[str] = None, fail_under: int = 90) -> bool:
        """Run tests with coverage collection."""
        print("🧪 Running tests with coverage collection...")
        
        # Build pytest command
        cmd = [
            sys.executable, "-m", "pytest",
            "--cov=src",
            "--cov-report=html:htmlcov",
            "--cov-report=xml:coverage.xml",
            "--cov-report=json:coverage.json",
            "--cov-report=term-missing",
            f"--cov-fail-under={fail_under}",
            "-v"
        ]
        
        # Add test type filters
        if test_types:
            for test_type in test_types:
                cmd.extend(["-m", test_type])
        
        # Add test directories
        cmd.extend([
            "tests/unit",
            "tests/integration"
        ])
        
        # Include performance tests if requested
        if not test_types or "performance" in test_types:
            cmd.append("tests/performance")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False
            )
            
            print(f"✅ Tests completed with exit code: {result.returncode}")
            
            if result.stdout:
                print("\n📊 Test Output:")
                print(result.stdout)
            
            if result.stderr:
                print("\n⚠️ Test Warnings/Errors:")
                print(result.stderr)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return False
    
    def analyze_coverage_data(self) -> Dict:
        """Analyze coverage data from JSON report."""
        coverage_file = self.project_root / "coverage.json"
        
        if not coverage_file.exists():
            print("❌ Coverage JSON file not found")
            return {}
        
        try:
            with open(coverage_file, 'r') as f:
                coverage_data = json.load(f)
            
            analysis = {
                'overall_coverage': coverage_data.get('totals', {}).get('percent_covered', 0),
                'files_coverage': {},
                'summary': {
                    'total_statements': coverage_data.get('totals', {}).get('num_statements', 0),
                    'covered_statements': coverage_data.get('totals', {}).get('covered_lines', 0),
                    'missing_statements': coverage_data.get('totals', {}).get('missing_lines', 0),
                    'excluded_statements': coverage_data.get('totals', {}).get('excluded_lines', 0)
                }
            }
            
            # Analyze per-file coverage
            for file_path, file_data in coverage_data.get('files', {}).items():
                if file_path.startswith('src/'):
                    relative_path = file_path[4:]  # Remove 'src/' prefix
                    coverage_percent = file_data.get('summary', {}).get('percent_covered', 0)
                    
                    analysis['files_coverage'][relative_path] = {
                        'coverage_percent': coverage_percent,
                        'statements': file_data.get('summary', {}).get('num_statements', 0),
                        'covered': file_data.get('summary', {}).get('covered_lines', 0),
                        'missing': file_data.get('summary', {}).get('missing_lines', 0),
                        'missing_line_numbers': file_data.get('missing_lines', [])
                    }
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error analyzing coverage data: {e}")
            return {}
    
    def generate_coverage_report(self, analysis: Dict) -> str:
        """Generate detailed coverage report."""
        report_lines = [
            "# Test Coverage Report",
            f"Generated on: {__import__('datetime').datetime.now().isoformat()}",
            "",
            "## Overall Coverage Summary",
            f"- **Total Coverage:** {analysis['overall_coverage']:.1f}%",
            f"- **Total Statements:** {analysis['summary']['total_statements']:,}",
            f"- **Covered Statements:** {analysis['summary']['covered_statements']:,}",
            f"- **Missing Statements:** {analysis['summary']['missing_statements']:,}",
            "",
            "## Coverage by Module",
            ""
        ]
        
        # Group files by module
        modules = {}
        for file_path, file_data in analysis['files_coverage'].items():
            if '/' in file_path:
                module = file_path.split('/')[0]
            else:
                module = 'root'
            
            if module not in modules:
                modules[module] = []
            modules[module].append((file_path, file_data))
        
        # Sort modules and generate report
        for module_name in sorted(modules.keys()):
            files = modules[module_name]
            
            # Calculate module average
            total_statements = sum(f[1]['statements'] for f in files)
            covered_statements = sum(f[1]['covered'] for f in files)
            module_coverage = (covered_statements / total_statements * 100) if total_statements > 0 else 0
            
            report_lines.extend([
                f"### {module_name.title()} Module ({module_coverage:.1f}%)",
                ""
            ])
            
            # Sort files by coverage (lowest first)
            files.sort(key=lambda x: x[1]['coverage_percent'])
            
            for file_path, file_data in files:
                coverage_icon = self._get_coverage_icon(file_data['coverage_percent'])
                report_lines.append(
                    f"- {coverage_icon} **{file_path}**: {file_data['coverage_percent']:.1f}% "
                    f"({file_data['covered']}/{file_data['statements']} statements)"
                )
                
                # Show missing lines for low coverage files
                if file_data['coverage_percent'] < 80 and file_data['missing_line_numbers']:
                    missing_lines = file_data['missing_line_numbers'][:10]  # Show first 10
                    if len(file_data['missing_line_numbers']) > 10:
                        missing_lines.append('...')
                    report_lines.append(f"  - Missing lines: {', '.join(map(str, missing_lines))}")
            
            report_lines.append("")
        
        # Add recommendations
        report_lines.extend([
            "## Recommendations",
            ""
        ])
        
        low_coverage_files = [
            (path, data) for path, data in analysis['files_coverage'].items()
            if data['coverage_percent'] < 80
        ]
        
        if low_coverage_files:
            report_lines.extend([
                "### Files needing attention (< 80% coverage):",
                ""
            ])
            
            for file_path, file_data in sorted(low_coverage_files, key=lambda x: x[1]['coverage_percent']):
                report_lines.append(
                    f"1. **{file_path}** ({file_data['coverage_percent']:.1f}%): "
                    f"Add {file_data['statements'] - file_data['covered']} more test cases"
                )
        else:
            report_lines.append("✅ All files have good coverage (≥ 80%)")
        
        return '\n'.join(report_lines)
    
    def _get_coverage_icon(self, coverage_percent: float) -> str:
        """Get appropriate icon for coverage percentage."""
        if coverage_percent >= 95:
            return "🟢"
        elif coverage_percent >= 80:
            return "🟡"
        elif coverage_percent >= 60:
            return "🟠"
        else:
            return "🔴"
    
    def save_reports(self, analysis: Dict, report_text: str):
        """Save coverage reports in multiple formats."""
        # Save markdown report
        report_file = self.reports_dir / "coverage_report.md"
        with open(report_file, 'w') as f:
            f.write(report_text)
        print(f"📄 Coverage report saved: {report_file}")
        
        # Save JSON analysis
        json_file = self.reports_dir / "coverage_analysis.json"
        with open(json_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"📄 Coverage analysis saved: {json_file}")
        
        # Save CSV summary
        csv_file = self.reports_dir / "coverage_summary.csv"
        self._save_csv_summary(analysis, csv_file)
        print(f"📄 Coverage CSV saved: {csv_file}")
    
    def _save_csv_summary(self, analysis: Dict, csv_file: Path):
        """Save coverage summary as CSV."""
        import csv
        
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['File', 'Coverage %', 'Statements', 'Covered', 'Missing'])
            
            for file_path, file_data in sorted(analysis['files_coverage'].items()):
                writer.writerow([
                    file_path,
                    f"{file_data['coverage_percent']:.1f}",
                    file_data['statements'],
                    file_data['covered'],
                    file_data['statements'] - file_data['covered']
                ])
    
    def validate_coverage_threshold(self, analysis: Dict, threshold: float = 90.0) -> bool:
        """Validate that coverage meets threshold."""
        overall_coverage = analysis.get('overall_coverage', 0)
        
        print(f"\n📊 Coverage Validation:")
        print(f"- Required: {threshold:.1f}%")
        print(f"- Actual: {overall_coverage:.1f}%")
        
        if overall_coverage >= threshold:
            print("✅ Coverage threshold met!")
            return True
        else:
            print(f"❌ Coverage below threshold by {threshold - overall_coverage:.1f}%")
            return False
    
    def open_html_report(self):
        """Open HTML coverage report in browser."""
        html_file = self.coverage_dir / "index.html"
        
        if html_file.exists():
            import webbrowser
            webbrowser.open(f"file://{html_file.absolute()}")
            print(f"🌐 Opened HTML report: {html_file}")
        else:
            print("❌ HTML coverage report not found")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run test coverage analysis")
    parser.add_argument(
        "--test-types",
        nargs="+",
        choices=["unit", "integration", "performance", "sdk"],
        help="Types of tests to run"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=90.0,
        help="Coverage threshold percentage (default: 90.0)"
    )
    parser.add_argument(
        "--open-html",
        action="store_true",
        help="Open HTML coverage report in browser"
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root directory (default: current directory)"
    )
    
    args = parser.parse_args()
    
    # Initialize reporter
    reporter = CoverageReporter(args.project_root)
    
    print("🚀 Starting coverage analysis...")
    print(f"📂 Project root: {reporter.project_root.absolute()}")
    print(f"📊 Coverage threshold: {args.threshold}%")
    
    if args.test_types:
        print(f"🧪 Test types: {', '.join(args.test_types)}")
    
    # Run tests with coverage
    success = reporter.run_tests_with_coverage(args.test_types, int(args.threshold))
    
    if not success:
        print("❌ Tests failed or coverage threshold not met")
        sys.exit(1)
    
    # Analyze coverage data
    print("\n📈 Analyzing coverage data...")
    analysis = reporter.analyze_coverage_data()
    
    if not analysis:
        print("❌ Failed to analyze coverage data")
        sys.exit(1)
    
    # Generate report
    print("📝 Generating coverage report...")
    report_text = reporter.generate_coverage_report(analysis)
    
    # Save reports
    reporter.save_reports(analysis, report_text)
    
    # Validate threshold
    threshold_met = reporter.validate_coverage_threshold(analysis, args.threshold)
    
    # Open HTML report if requested
    if args.open_html:
        reporter.open_html_report()
    
    print(f"\n📁 Reports saved in: {reporter.reports_dir}")
    print(f"🌐 HTML report: {reporter.coverage_dir / 'index.html'}")
    
    if threshold_met:
        print("🎉 Coverage analysis completed successfully!")
        sys.exit(0)
    else:
        print("📊 Coverage analysis completed with warnings")
        sys.exit(1)


if __name__ == "__main__":
    main()