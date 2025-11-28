#!/usr/bin/env python3
"""
GAM SDK Advanced Usage Examples

This script demonstrates advanced features and patterns of the
Google Ad Manager SDK including error handling, context managers,
custom configurations, and complex report scenarios.
"""

from pathlib import Path
import sys
from datetime import date, timedelta
import json
import logging

# Add SDK to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sdk import GAMClient, SDKError
from sdk.exceptions import ReportError, AuthError, ConfigError, ValidationError, NetworkError


def setup_logging():
    """Configure logging for examples."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('sdk_examples.log'),
            logging.StreamHandler()
        ]
    )


def example_context_manager():
    """Example: Using GAMClient as a context manager."""
    print("=" * 60)
    print("ADVANCED EXAMPLE 1: Context Manager Usage")
    print("=" * 60)
    
    try:
        # Use client as context manager for automatic resource cleanup
        with GAMClient(auto_authenticate=True) as client:
            print(f"✅ Client initialized in context: {client}")
            
            # Generate report within context
            report = (client
                .reports()
                .delivery()
                .last_7_days()
                .execute())
            
            print(f"✅ Report generated: {len(report)} rows")
            
            # Export with automatic cleanup
            output_path = Path("relatorios/context_example.csv")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            report.to_csv(output_path)
            
            print(f"✅ Report exported: {output_path}")
        
        print("✅ Context manager cleanup completed")
        
    except Exception as e:
        print(f"❌ Context manager example failed: {e}")


def example_comprehensive_error_handling():
    """Example: Comprehensive error handling patterns."""
    print("\n" + "=" * 60)
    print("ADVANCED EXAMPLE 2: Error Handling Patterns")
    print("=" * 60)
    
    try:
        client = GAMClient()
        
        # Example 1: Report validation errors
        print("Testing validation error handling...")
        try:
            # This should fail - no dimensions specified
            report = (client
                .reports()
                .metrics('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS')
                .execute())
        except ValidationError as e:
            print(f"✅ Caught validation error as expected: {e}")
            print(f"   Field: {getattr(e, 'field_name', 'unknown')}")
            print(f"   Value: {getattr(e, 'field_value', 'unknown')}")
        
        # Example 2: Invalid report type
        print("Testing invalid report type...")
        try:
            report = (client
                .reports()
                .quick('invalid_report_type')
                .execute())
        except ValidationError as e:
            print(f"✅ Caught invalid report type: {e}")
        
        # Example 3: Network error simulation
        print("Testing network error handling...")
        try:
            # Test connection to detect any network issues
            status = client.test_connection()
            if status['overall_status'] == 'unhealthy':
                print(f"⚠️  Network connectivity issues detected")
                print(f"   SOAP API: {status['soap_api']['status']}")
                print(f"   REST API: {status['rest_api']['status']}")
            else:
                print(f"✅ Network connection healthy")
        except NetworkError as e:
            print(f"✅ Caught network error: {e}")
            print(f"   Status code: {getattr(e, 'status_code', 'unknown')}")
        
        # Example 4: Authentication error handling
        print("Testing authentication status...")
        try:
            auth = client.auth()
            auth.check_status()
            
            if not auth.is_authenticated():
                print("⚠️  Authentication required")
                print("   Run: python generate_new_token.py")
            else:
                print("✅ Authentication verified")
                
                # Test scope validation
                auth.validate_scopes()
                print("✅ OAuth scopes validated")
                
        except AuthError as e:
            print(f"✅ Caught authentication error: {e}")
            print(f"   Auth step: {getattr(e, 'auth_step', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Error handling example failed: {e}")


def example_custom_configuration():
    """Example: Custom configuration scenarios."""
    print("\n" + "=" * 60)
    print("ADVANCED EXAMPLE 3: Custom Configuration")
    print("=" * 60)
    
    try:
        # Example 1: Configuration inspection
        client = GAMClient()
        config = client.config()
        
        print("Current configuration overview:")
        current_config = config.show(hide_secrets=True)
        
        for section, values in current_config.items():
            print(f"  [{section}]")
            if isinstance(values, dict):
                for key, value in values.items():
                    print(f"    {key}: {value}")
            else:
                print(f"    {values}")
        
        # Example 2: Configuration validation with detailed results
        print("\nDetailed configuration validation:")
        config.validate()
        
        validation_results = config.get_validation_results()
        if validation_results:
            for field, result in validation_results.items():
                status = "✅" if result.startswith("✅") else "❌" if result.startswith("❌") else "⚠️"
                print(f"  {status} {field}: {result}")
        
        # Example 3: Pending changes management
        print("\nConfiguration change management:")
        
        # Make some test changes (without saving)
        config.set('test.example_setting', 'test_value')
        config.set('test.another_setting', 42)
        
        if config.has_pending_changes():
            changes = config.get_pending_changes()
            print(f"  Pending changes: {len(changes)}")
            for key, value in changes.items():
                print(f"    {key} = {value}")
            
            # Discard changes
            config.discard_changes()
            print("  ✅ Changes discarded")
        
        # Example 4: Environment-specific settings
        print("\nEnvironment detection:")
        network_code = config.get('gam.network_code')
        if network_code:
            # Simple heuristic to detect test vs production
            is_test_env = len(str(network_code)) < 10
            env_type = "TEST" if is_test_env else "PRODUCTION"
            print(f"  Environment: {env_type}")
            print(f"  Network Code: {network_code}")
        
    except Exception as e:
        print(f"❌ Configuration example failed: {e}")


def example_complex_report_scenarios():
    """Example: Complex report building scenarios."""
    print("\n" + "=" * 60)
    print("ADVANCED EXAMPLE 4: Complex Report Scenarios")
    print("=" * 60)
    
    try:
        client = GAMClient()
        
        # Scenario 1: Multi-timeframe comparison
        print("Scenario 1: Multi-timeframe comparison report...")
        
        # Current month
        current_month = (client
            .reports()
            .sales()
            .this_month()
            .name("Sales - Current Month")
            .execute())
        
        # Previous month
        previous_month = (client
            .reports()
            .sales()
            .last_month()
            .name("Sales - Previous Month")
            .execute())
        
        print(f"  Current month: {len(current_month)} rows")
        print(f"  Previous month: {len(previous_month)} rows")
        
        # Scenario 2: Multi-dimension analysis
        print("\nScenario 2: Multi-dimension performance analysis...")
        
        detailed_report = (client
            .reports()
            .delivery()
            .last_30_days()
            .dimensions(
                'DATE',
                'AD_UNIT_NAME', 
                'ADVERTISER_NAME',
                'LINE_ITEM_NAME',
                'CREATIVE_NAME'
            )
            .metrics(
                'TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS',
                'TOTAL_LINE_ITEM_LEVEL_CLICKS',
                'TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE'
            )
            .execute())
        
        print(f"  Detailed report: {len(detailed_report)} rows")
        print(f"  Dimensions: {len(detailed_report.dimension_headers)}")
        print(f"  Metrics: {len(detailed_report.metric_headers)}")
        
        # Scenario 3: Data transformation pipeline
        print("\nScenario 3: Data transformation pipeline...")
        
        # Get base data
        base_report = (client
            .reports()
            .inventory()
            .last_7_days()
            .execute())
        
        # Transform: Filter high-performing ad units
        high_performers = base_report.filter(
            lambda row: row.get('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 0) > 10000
        )
        
        # Transform: Sort by performance
        sorted_performers = high_performers.sort(
            'TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 
            ascending=False
        )
        
        # Transform: Get top 10
        top_10 = sorted_performers.head(10)
        
        print(f"  Base data: {len(base_report)} rows")
        print(f"  High performers: {len(high_performers)} rows")
        print(f"  Top 10: {len(top_10)} rows")
        
        # Scenario 4: Multi-format export pipeline
        print("\nScenario 4: Multi-format export pipeline...")
        
        output_dir = Path("relatorios/advanced_scenarios")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Export comparison data
        current_month.to_csv(output_dir / "current_month.csv")
        previous_month.to_csv(output_dir / "previous_month.csv")
        
        # Export detailed analysis
        detailed_report.to_excel(output_dir / "detailed_analysis.xlsx")
        detailed_report.to_json(output_dir / "detailed_analysis.json", format='table')
        
        # Export top performers
        top_10.to_csv(output_dir / "top_performers.csv")
        
        # Create summary report
        summary_data = {
            'analysis_date': date.today().isoformat(),
            'reports_generated': 4,
            'total_rows_analyzed': (
                len(current_month) + 
                len(previous_month) + 
                len(detailed_report) + 
                len(base_report)
            ),
            'timeframes': {
                'current_month_rows': len(current_month),
                'previous_month_rows': len(previous_month),
                'last_30_days_detailed': len(detailed_report),
                'last_7_days_inventory': len(base_report)
            },
            'top_performers_identified': len(top_10)
        }
        
        with open(output_dir / "analysis_summary.json", 'w') as f:
            json.dump(summary_data, f, indent=2)
        
        print(f"  ✅ All reports exported to {output_dir}")
        print(f"  ✅ Summary: {summary_data['total_rows_analyzed']} total rows analyzed")
        
    except Exception as e:
        print(f"❌ Complex scenarios example failed: {e}")


def example_performance_optimization():
    """Example: Performance optimization techniques."""
    print("\n" + "=" * 60)
    print("ADVANCED EXAMPLE 5: Performance Optimization")
    print("=" * 60)
    
    try:
        import time
        
        client = GAMClient()
        
        # Technique 1: Report preview for quick validation
        print("Technique 1: Using report preview...")
        
        start_time = time.time()
        preview = (client
            .reports()
            .delivery()
            .last_30_days()
            .preview(limit=5))  # Only get 5 rows for quick validation
        
        preview_time = time.time() - start_time
        print(f"  ✅ Preview generated in {preview_time:.2f}s: {len(preview)} rows")
        
        # Technique 2: Efficient date range selection
        print("\nTechnique 2: Efficient date range selection...")
        
        # Smaller date range for faster processing
        start_time = time.time()
        small_range = (client
            .reports()
            .inventory()
            .last_7_days()  # Smaller range = faster processing
            .execute())
        
        small_range_time = time.time() - start_time
        print(f"  ✅ 7-day report in {small_range_time:.2f}s: {len(small_range)} rows")
        
        # Technique 3: Selective dimension/metric usage
        print("\nTechnique 3: Selective dimension/metric usage...")
        
        start_time = time.time()
        focused_report = (client
            .reports()
            .last_7_days()
            .dimensions('DATE', 'AD_UNIT_NAME')  # Only essential dimensions
            .metrics('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS')  # Only essential metrics
            .execute())
        
        focused_time = time.time() - start_time
        print(f"  ✅ Focused report in {focused_time:.2f}s: {len(focused_report)} rows")
        
        # Technique 4: Efficient data filtering
        print("\nTechnique 4: Efficient data filtering...")
        
        # Filter early in the pipeline
        start_time = time.time()
        
        base_data = (client
            .reports()
            .delivery()
            .last_7_days()
            .execute())
        
        # Efficient filtering with early exit
        filtered_data = base_data.filter(
            lambda row: (
                row.get('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 0) > 1000 and
                row.get('TOTAL_LINE_ITEM_LEVEL_CLICKS', 0) > 10
            )
        )
        
        filter_time = time.time() - start_time
        print(f"  ✅ Filtered {len(base_data)} → {len(filtered_data)} rows in {filter_time:.2f}s")
        
        # Technique 5: Batch export optimization
        print("\nTechnique 5: Batch export optimization...")
        
        output_dir = Path("relatorios/performance_test")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        start_time = time.time()
        
        # Export to most efficient format first (CSV)
        focused_report.to_csv(output_dir / "efficient_export.csv")
        
        export_time = time.time() - start_time
        print(f"  ✅ CSV export in {export_time:.2f}s")
        
        # Performance summary
        print(f"\nPerformance Summary:")
        print(f"  Preview (5 rows): {preview_time:.2f}s")
        print(f"  Small range (7 days): {small_range_time:.2f}s")
        print(f"  Focused report: {focused_time:.2f}s")
        print(f"  Data filtering: {filter_time:.2f}s")
        print(f"  CSV export: {export_time:.2f}s")
        
    except Exception as e:
        print(f"❌ Performance optimization example failed: {e}")


def example_production_ready_patterns():
    """Example: Production-ready usage patterns."""
    print("\n" + "=" * 60)
    print("ADVANCED EXAMPLE 6: Production-Ready Patterns")
    print("=" * 60)
    
    try:
        # Pattern 1: Robust initialization with retries
        print("Pattern 1: Robust client initialization...")
        
        max_retries = 3
        client = None
        
        for attempt in range(max_retries):
            try:
                client = GAMClient(auto_authenticate=True)
                print(f"  ✅ Client initialized on attempt {attempt + 1}")
                break
            except (AuthError, ConfigError) as e:
                print(f"  ⚠️  Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
        
        if not client:
            raise Exception("Failed to initialize client after retries")
        
        # Pattern 2: Health check before operations
        print("\nPattern 2: Pre-operation health checks...")
        
        health_status = client.test_connection()
        if health_status['overall_status'] != 'healthy':
            print(f"  ⚠️  System health check failed: {health_status['overall_status']}")
            print("  Proceeding with limited functionality...")
        else:
            print(f"  ✅ System health check passed")
        
        # Pattern 3: Graceful error handling with fallbacks
        print("\nPattern 3: Graceful error handling...")
        
        try:
            # Try preferred report type
            report = (client
                .reports()
                .delivery()
                .last_30_days()
                .execute())
            print(f"  ✅ Primary report generated: {len(report)} rows")
            
        except ReportError as e:
            print(f"  ⚠️  Primary report failed: {e}")
            print("  Falling back to simpler report...")
            
            # Fallback to simpler report
            try:
                report = (client
                    .reports()
                    .delivery()
                    .last_7_days()
                    .execute())
                print(f"  ✅ Fallback report generated: {len(report)} rows")
            except Exception as fallback_error:
                print(f"  ❌ Fallback also failed: {fallback_error}")
                report = None
        
        # Pattern 4: Comprehensive logging and monitoring
        print("\nPattern 4: Comprehensive logging...")
        
        logger = logging.getLogger('gam_sdk_production')
        
        if report:
            logger.info(f"Report generated successfully: {len(report)} rows")
            logger.info(f"Report columns: {', '.join(report.headers)}")
            
            # Log performance metrics
            row_count = len(report)
            if row_count > 10000:
                logger.warning(f"Large dataset detected: {row_count} rows")
            elif row_count == 0:
                logger.warning("Empty dataset returned")
            else:
                logger.info(f"Normal dataset size: {row_count} rows")
        
        # Pattern 5: Secure output handling
        print("\nPattern 5: Secure output handling...")
        
        if report:
            output_dir = Path("relatorios/production")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Set secure file permissions
            import stat
            
            # Export with timestamp for uniqueness
            timestamp = date.today().strftime("%Y%m%d")
            output_file = output_dir / f"production_report_{timestamp}.csv"
            
            report.to_csv(output_file)
            
            # Set restrictive permissions (owner read/write only)
            output_file.chmod(stat.S_IRUSR | stat.S_IWUSR)
            
            print(f"  ✅ Secure report exported: {output_file}")
            print(f"  ✅ File permissions: {oct(output_file.stat().st_mode)[-3:]}")
        
        # Pattern 6: Cleanup and resource management
        print("\nPattern 6: Resource cleanup...")
        
        # Clear any cached data
        if hasattr(client, '_clear_cache'):
            client._clear_cache()
        
        # Log final status
        logger.info("Production workflow completed successfully")
        print("  ✅ Production workflow completed")
        
    except Exception as e:
        logger = logging.getLogger('gam_sdk_production')
        logger.error(f"Production workflow failed: {e}")
        print(f"❌ Production pattern example failed: {e}")


def main():
    """Run all advanced SDK examples."""
    print("Google Ad Manager SDK - Advanced Examples")
    print("=" * 60)
    print("This script demonstrates advanced usage patterns, error handling,")
    print("and production-ready techniques for the GAM SDK.")
    print()
    
    # Setup logging
    setup_logging()
    
    try:
        # Run advanced examples
        example_context_manager()
        example_comprehensive_error_handling()
        example_custom_configuration()
        example_complex_report_scenarios()
        example_performance_optimization()
        example_production_ready_patterns()
        
        print("\n" + "=" * 60)
        print("🚀 ALL ADVANCED EXAMPLES COMPLETED!")
        print("=" * 60)
        print("Check the logs and output directories for detailed results.")
        print("These patterns are ready for production deployment.")
        
    except Exception as e:
        print(f"\n❌ Advanced examples failed: {e}")
        print("Check the logs for detailed error information.")


if __name__ == "__main__":
    main()