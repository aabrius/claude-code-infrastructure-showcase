#!/usr/bin/env python3
"""
Example usage of Google Ad Manager API Python SDK.

This example demonstrates how to use the modular Python SDK for
Google Ad Manager operations, suitable for Python applications and scripts.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import List

# Import the SDK modules from new packages
try:
    from gam_api.auth import get_auth_manager
    from gam_api.client import get_gam_client
    from gam_api.reports import ReportGenerator, list_quick_report_types
    from gam_api.models import (
        DateRange, DateRangeType, ReportDefinition, ReportType, ReportStatus
    )
    from gam_shared.logger import get_structured_logger
    from gam_shared.formatters import get_formatter
    from gam_shared.cache import get_cache
except ImportError:
    # Fallback to legacy imports
    from src.core.auth import get_auth_manager
    from src.core.client import get_gam_client
    from src.core.reports import ReportGenerator, list_quick_report_types
    from src.core.models import (
        DateRange, DateRangeType, ReportDefinition, ReportType, ReportStatus
    )
    from src.utils.logger import get_structured_logger
    from src.utils.formatters import get_formatter
    from src.utils.cache import get_cache


def example_basic_setup():
    """Example: Basic SDK setup and authentication."""
    print("\n=== Basic SDK Setup ===")
    
    try:
        # Initialize authentication
        print("1. Setting up authentication...")
        auth_manager = get_auth_manager()
        
        # Validate configuration
        auth_manager.validate_config()
        print("✓ Configuration valid")
        
        # Get credentials
        credentials, network_code = auth_manager.get_credentials_and_network()
        print(f"✓ Authenticated for network: {network_code}")
        
        # Initialize client
        print("\n2. Initializing GAM client...")
        client = get_gam_client()
        
        # Test connection
        client.test_connection()
        print("✓ Connection test successful")
        
        return client
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return None


def example_quick_reports(client):
    """Example: Generate quick reports using the SDK."""
    print("\n=== Quick Reports Example ===")
    
    try:
        # Get available report types
        print("1. Available quick report types:")
        report_types = list_quick_report_types()
        for report_type, info in report_types.items():
            print(f"   - {report_type}: {info['description']}")
        
        # Initialize report generator
        generator = ReportGenerator()
        
        # Generate delivery report
        print("\n2. Generating delivery report...")
        result = generator.generate_quick_report("delivery", days_back=7)
        
        print(f"✓ Report completed:")
        print(f"   - Total rows: {result.total_rows}")
        print(f"   - Execution time: {result.execution_time:.2f}s")
        print(f"   - Dimensions: {result.dimension_headers}")
        print(f"   - Metrics: {result.metric_headers}")
        
        # Show sample data
        if result.rows:
            print("\n   Sample data (first 3 rows):")
            formatter = get_formatter("summary")
            sample_data = result.rows[:3]
            print(f"   {formatter.format_sample(sample_data)}")
        
        return result
        
    except Exception as e:
        print(f"❌ Quick report failed: {e}")
        return None


def example_custom_reports(client):
    """Example: Create custom reports using the SDK."""
    print("\n=== Custom Reports Example ===")
    
    try:
        # Create custom date range
        start_date = datetime.now().date() - timedelta(days=14)
        end_date = datetime.now().date() - timedelta(days=1)
        
        date_range = DateRange(
            range_type=DateRangeType.CUSTOM,
            start_date=start_date,
            end_date=end_date
        )
        
        # Define custom report
        definition = ReportDefinition(
            report_type=ReportType.HISTORICAL,
            dimensions=["DATE", "AD_UNIT_NAME", "DEVICE_CATEGORY_NAME"],
            metrics=[
                "TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS",
                "TOTAL_LINE_ITEM_LEVEL_CLICKS",
                "TOTAL_LINE_ITEM_LEVEL_CTR",
                "TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE"
            ],
            date_range=date_range
        )
        
        print("1. Creating custom report...")
        print(f"   - Dimensions: {definition.dimensions}")
        print(f"   - Metrics: {definition.metrics}")
        print(f"   - Date range: {start_date} to {end_date}")
        
        # Create and run report
        generator = ReportGenerator()
        report = generator.create_report(definition, "SDK Custom Report")
        
        print(f"✓ Report created: {report.id}")
        
        # Run the report
        print("\n2. Running report...")
        report = generator.run_report(report, timeout=300)
        
        if report.status == ReportStatus.COMPLETED:
            print("✓ Report completed successfully")
            
            # Fetch results
            result = generator.fetch_results(report, max_pages=3)
            print(f"   - Total rows: {result.total_rows}")
            print(f"   - Pages fetched: 3 (limited for example)")
            
            return result
        else:
            print(f"❌ Report failed with status: {report.status}")
            return None
        
    except Exception as e:
        print(f"❌ Custom report failed: {e}")
        return None


def example_data_export(report_result):
    """Example: Export report data in different formats."""
    print("\n=== Data Export Example ===")
    
    if not report_result:
        print("❌ No report result to export")
        return
    
    try:
        # Export as JSON
        print("1. Exporting as JSON...")
        json_formatter = get_formatter("json")
        json_data = json_formatter.format(report_result)
        
        with open("reports/example_report.json", "w") as f:
            f.write(json_data)
        print("✓ JSON export saved to reports/example_report.json")
        
        # Export as CSV
        print("\n2. Exporting as CSV...")
        csv_formatter = get_formatter("csv")
        csv_data = csv_formatter.format(report_result)
        
        with open("reports/example_report.csv", "w") as f:
            f.write(csv_data)
        print("✓ CSV export saved to reports/example_report.csv")
        
        # Export as Excel (if openpyxl is available)
        try:
            print("\n3. Exporting as Excel...")
            excel_formatter = get_formatter("excel")
            excel_formatter.save_to_file(report_result, "reports/example_report.xlsx")
            print("✓ Excel export saved to reports/example_report.xlsx")
        except ImportError:
            print("⚠️  Excel export requires openpyxl package")
        
    except Exception as e:
        print(f"❌ Data export failed: {e}")


def example_caching():
    """Example: Using the caching system."""
    print("\n=== Caching Example ===")
    
    try:
        # Get cache instance
        cache = get_cache()
        
        # Store some data
        print("1. Storing data in cache...")
        sample_data = {
            "report_type": "delivery",
            "total_rows": 1500,
            "generated_at": datetime.now().isoformat()
        }
        
        cache.set("example_report_summary", sample_data, ttl=3600)
        print("✓ Data stored in cache")
        
        # Retrieve data
        print("\n2. Retrieving data from cache...")
        cached_data = cache.get("example_report_summary")
        
        if cached_data:
            print("✓ Cache hit:")
            print(f"   {json.dumps(cached_data, indent=2)}")
        else:
            print("❌ Cache miss")
        
        # Check cache stats
        print("\n3. Cache statistics:")
        stats = cache.get_stats()
        print(f"   - Hits: {stats.get('hits', 0)}")
        print(f"   - Misses: {stats.get('misses', 0)}")
        print(f"   - Size: {stats.get('size', 0)} items")
        
    except Exception as e:
        print(f"❌ Caching example failed: {e}")


def example_logging():
    """Example: Using structured logging."""
    print("\n=== Logging Example ===")
    
    try:
        # Get structured logger
        logger = get_structured_logger("sdk_example")
        
        # Log different types of events
        print("1. Logging various events...")
        
        # API request log
        logger.log_api_request(
            method="POST",
            url="/api/v1/reports",
            status_code=200,
            response_time=1.5
        )
        
        # Report lifecycle log
        logger.log_report_lifecycle(
            event="created",
            report_id="example_123",
            report_type="delivery",
            dimensions=["DATE", "AD_UNIT_NAME"]
        )
        
        # Authentication log
        logger.log_auth_event(
            event="token_refresh",
            success=True
        )
        
        # Cache event log
        logger.log_cache_event(
            event="get",
            key="report_metadata",
            hit=True
        )
        
        print("✓ Events logged (check logs/gam_api.log)")
        
    except Exception as e:
        print(f"❌ Logging example failed: {e}")


def example_error_handling():
    """Example: Error handling patterns."""
    print("\n=== Error Handling Example ===")
    
    try:
        generator = ReportGenerator()
        
        # Example 1: Invalid report type
        print("1. Testing invalid report type...")
        try:
            generator.generate_quick_report("invalid_type")
        except ValueError as e:
            print(f"✓ Caught expected error: {e}")
        
        # Example 2: Invalid dimensions
        print("\n2. Testing invalid dimensions...")
        try:
            try:
                from gam_shared.validators import validate_dimensions_list
            except ImportError:
                from src.utils.validators import validate_dimensions_list
            validate_dimensions_list(["INVALID_DIMENSION"])
        except Exception as e:
            print(f"✓ Caught validation error: {e}")
        
        # Example 3: Network error simulation
        print("\n3. Error recovery patterns demonstrated")
        print("   - Automatic retries for transient failures")
        print("   - Graceful degradation when API is unavailable")
        print("   - Detailed error messages for debugging")
        
    except Exception as e:
        print(f"❌ Error handling example failed: {e}")


def example_advanced_usage():
    """Example: Advanced SDK usage patterns."""
    print("\n=== Advanced Usage Patterns ===")
    
    print("1. Batch Processing:")
    print("   - Generate multiple reports concurrently")
    print("   - Use asyncio for parallel operations")
    print("   - Implement progress tracking")
    
    print("\n2. Streaming Large Reports:")
    print("   - Process reports page by page")
    print("   - Avoid memory issues with large datasets")
    print("   - Real-time data processing")
    
    print("\n3. Custom Metric Calculations:")
    print("   - Post-process report data")
    print("   - Calculate derived metrics")
    print("   - Aggregate data across time periods")
    
    print("\n4. Integration Patterns:")
    print("   - Database storage of report data")
    print("   - ETL pipeline integration")
    print("   - Real-time dashboard updates")


async def example_async_operations():
    """Example: Asynchronous operations (future enhancement)."""
    print("\n=== Async Operations (Future) ===")
    
    print("Planned async features:")
    print("1. Concurrent report generation")
    print("2. Non-blocking API calls")
    print("3. Real-time progress updates")
    print("4. Streaming data processing")
    
    # Placeholder for future async implementation
    await asyncio.sleep(0.1)


def main():
    """Run all SDK examples."""
    print("Google Ad Manager API - Python SDK Usage Examples")
    print("=" * 55)
    
    print("📚 This example demonstrates the Python SDK for GAM API")
    print("   The SDK provides a clean, Pythonic interface for:")
    print("   - Authentication management")
    print("   - Report generation and management")
    print("   - Data export and formatting")
    print("   - Caching and performance optimization")
    print("   - Structured logging and observability")
    
    # Setup
    client = example_basic_setup()
    if not client:
        print("\n❌ Cannot continue without valid setup")
        return
    
    # Core functionality
    quick_result = example_quick_reports(client)
    custom_result = example_custom_reports(client)
    
    # Choose result for export example
    export_result = custom_result or quick_result
    if export_result:
        example_data_export(export_result)
    
    # Utility examples
    example_caching()
    example_logging()
    example_error_handling()
    example_advanced_usage()
    
    print("\n=== SDK Benefits ===")
    print("✓ Type safety with dataclasses and enums")
    print("✓ Automatic error handling and retries")
    print("✓ Built-in caching for performance")
    print("✓ Structured logging for observability")
    print("✓ Multiple output formats (JSON, CSV, Excel)")
    print("✓ Easy integration with Python applications")
    
    print("\n=== Getting Started ===")
    print("1. Configure authentication in config/agent_config.yaml")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Import SDK modules in your Python code")
    print("4. Use ReportGenerator for report operations")
    print("5. Leverage utilities for caching, logging, formatting")


if __name__ == "__main__":
    # Run sync examples
    main()
    
    # Run async examples
    asyncio.run(example_async_operations())