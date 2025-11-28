#!/usr/bin/env python3
"""
GAM SDK Quick Start Examples

This script demonstrates the basic usage of the Google Ad Manager SDK
with fluent API design patterns for common operations.
"""

from pathlib import Path
import sys
from datetime import date, timedelta

# Add SDK to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sdk import GAMClient
from sdk.exceptions import SDKError, ReportError, AuthError, ConfigError


def example_basic_client_setup():
    """Example: Basic client initialization."""
    print("=" * 60)
    print("EXAMPLE 1: Basic Client Setup")
    print("=" * 60)
    
    try:
        # Basic initialization (uses default config)
        client = GAMClient()
        print(f"✅ Client initialized: {client}")
        
        # Test connection
        status = client.test_connection()
        print(f"✅ Connection status: {status['overall_status']}")
        print(f"   Network: {status['network_code']}")
        
        return client
        
    except ConfigError as e:
        print(f"❌ Configuration error: {e}")
        print("   Make sure googleads.yaml is configured properly")
        return None
    except AuthError as e:
        print(f"❌ Authentication error: {e}")
        print("   Run: python generate_new_token.py")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def example_quick_reports(client):
    """Example: Generate quick reports with predefined settings."""
    if not client:
        return
        
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Quick Reports")
    print("=" * 60)
    
    try:
        # Generate delivery report for last 7 days
        print("Generating delivery report for last 7 days...")
        report = client.quick_report('delivery', days_back=7)
        
        print(f"✅ Report generated: {len(report)} rows")
        print(f"   Columns: {', '.join(report.headers[:5])}...")
        
        # Show preview
        preview = report.head(3)
        print(f"   Preview: {len(preview)} rows")
        
        # Export to CSV
        output_path = Path("relatorios/delivery_7days.csv")
        output_path.parent.mkdir(exist_ok=True)
        report.to_csv(output_path)
        print(f"✅ Exported to: {output_path}")
        
    except ReportError as e:
        print(f"❌ Report generation failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def example_fluent_reports(client):
    """Example: Fluent report building with method chaining."""
    if not client:
        return
        
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Fluent Report Building")
    print("=" * 60)
    
    try:
        # Build custom report with fluent interface
        print("Building custom report with fluent API...")
        
        report = (client
            .reports()
            .delivery()
            .last_30_days()
            .dimensions('DATE', 'AD_UNIT_NAME', 'LINE_ITEM_NAME')
            .metrics('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 'TOTAL_LINE_ITEM_LEVEL_CLICKS')
            .execute())
        
        print(f"✅ Custom report generated: {len(report)} rows")
        
        # Data manipulation examples
        print("\nData manipulation examples:")
        
        # Filter high-impression data
        high_impressions = report.filter(
            lambda row: row.get('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 0) > 1000
        )
        print(f"   High impressions (>1000): {len(high_impressions)} rows")
        
        # Sort by impressions
        sorted_report = report.sort('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', ascending=False)
        print(f"   Sorted by impressions: {len(sorted_report)} rows")
        
        # Get summary statistics
        summary = report.summary()
        print(f"   Summary stats: {summary.get('row_count', 0)} rows analyzed")
        
        # Export to multiple formats
        base_path = Path("relatorios/custom_report")
        base_path.parent.mkdir(exist_ok=True)
        
        report.to_csv(f"{base_path}.csv")
        report.to_json(f"{base_path}.json")
        report.to_excel(f"{base_path}.xlsx")
        
        print(f"✅ Exported to CSV, JSON, and Excel formats")
        
    except ReportError as e:
        print(f"❌ Report generation failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def example_configuration_management(client):
    """Example: Configuration management with fluent interface."""
    if not client:
        return
        
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Configuration Management")
    print("=" * 60)
    
    try:
        # Get current configuration
        config = client.config()
        
        network_code = config.get('gam.network_code')
        print(f"Current network code: {network_code}")
        
        # Show current config (with secrets hidden)
        current_config = config.show(hide_secrets=True)
        print(f"Configuration sections: {list(current_config.keys())}")
        
        # Validate configuration
        print("Validating configuration...")
        config.validate()
        
        validation_results = config.get_validation_results()
        if validation_results:
            for key, result in validation_results.items():
                print(f"   {key}: {result}")
        
        print("✅ Configuration validation passed")
        
        # Test connection using config
        print("Testing API connection...")
        config.test_connection()
        print("✅ API connection test passed")
        
    except ConfigError as e:
        print(f"❌ Configuration error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def example_authentication_management(client):
    """Example: Authentication management and status checking."""
    if not client:
        return
        
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Authentication Management")
    print("=" * 60)
    
    try:
        # Check authentication status
        auth = client.auth()
        
        print("Checking authentication status...")
        auth.check_status()
        
        status = auth.get_status()
        if status:
            print(f"   Authenticated: {status['authenticated']}")
            print(f"   Credentials present: {status['credentials_present']}")
            print(f"   Last check: {status['last_check']}")
            
            if status['errors']:
                print(f"   Errors: {', '.join(status['errors'])}")
        
        # Refresh credentials if needed
        print("Refreshing credentials if needed...")
        auth.refresh_if_needed()
        print("✅ Credential refresh completed")
        
        # Test API connections
        print("Testing API connections...")
        auth.test_connection()
        print("✅ API connection test passed")
        
        # Get network information
        print("Getting network information...")
        network_info = auth.get_network_info()
        print(f"   Network: {network_info.get('displayName', 'Unknown')}")
        print(f"   Code: {network_info.get('networkCode', 'Unknown')}")
        print(f"   Timezone: {network_info.get('timeZone', 'Unknown')}")
        print(f"   Currency: {network_info.get('currencyCode', 'Unknown')}")
        
        # Validate OAuth scopes
        print("Validating OAuth scopes...")
        auth.validate_scopes()
        print("✅ OAuth scope validation passed")
        
    except AuthError as e:
        print(f"❌ Authentication error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def example_advanced_date_ranges(client):
    """Example: Advanced date range configurations."""
    if not client:
        return
        
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Advanced Date Ranges")
    print("=" * 60)
    
    try:
        reports = client.reports()
        
        # Last 7 days
        print("Report for last 7 days...")
        report_7d = (reports
            .inventory()
            .last_7_days()
            .execute())
        print(f"✅ Last 7 days: {len(report_7d)} rows")
        
        # Last 30 days
        print("Report for last 30 days...")
        report_30d = (reports
            .inventory()
            .last_30_days()
            .execute())
        print(f"✅ Last 30 days: {len(report_30d)} rows")
        
        # Current month
        print("Report for current month...")
        report_month = (reports
            .inventory()
            .this_month()
            .execute())
        print(f"✅ This month: {len(report_month)} rows")
        
        # Last month
        print("Report for last month...")
        report_last_month = (reports
            .inventory()
            .last_month()
            .execute())
        print(f"✅ Last month: {len(report_last_month)} rows")
        
        # Custom date range
        print("Report for custom date range...")
        start_date = date.today() - timedelta(days=14)
        end_date = date.today() - timedelta(days=7)
        
        report_custom = (reports
            .sales()
            .date_range(start_date, end_date)
            .execute())
        print(f"✅ Custom range ({start_date} to {end_date}): {len(report_custom)} rows")
        
    except ReportError as e:
        print(f"❌ Report generation failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def example_data_analysis_workflow(client):
    """Example: Complete data analysis workflow."""
    if not client:
        return
        
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Data Analysis Workflow")
    print("=" * 60)
    
    try:
        # Generate comprehensive report
        print("Generating comprehensive performance report...")
        
        report = (client
            .reports()
            .delivery()
            .last_30_days()
            .dimensions('DATE', 'AD_UNIT_NAME', 'ADVERTISER_NAME')
            .metrics(
                'TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS',
                'TOTAL_LINE_ITEM_LEVEL_CLICKS',
                'TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE'
            )
            .execute())
        
        print(f"✅ Generated report: {len(report)} rows")
        
        # Convert to DataFrame for analysis
        df = report.to_dataframe()
        print(f"   DataFrame shape: {df.shape}")
        print(f"   Columns: {list(df.columns)}")
        
        # Perform analysis
        print("\nPerforming data analysis:")
        
        # Top performing ad units
        if 'TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS' in df.columns:
            top_units = df.nlargest(5, 'TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS')
            print(f"   Top 5 ad units by impressions:")
            for _, row in top_units.iterrows():
                unit_name = row.get('AD_UNIT_NAME', 'Unknown')[:30]
                impressions = row.get('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 0)
                print(f"     - {unit_name}: {impressions:,.0f} impressions")
        
        # Summary statistics
        summary = report.summary()
        print(f"\n   Summary statistics:")
        print(f"     Total rows: {summary['row_count']}")
        print(f"     Total columns: {summary['column_count']}")
        
        if 'statistics' in summary:
            for col, stats in summary['statistics'].items():
                mean_val = stats.get('mean', 0)
                print(f"     {col} average: {mean_val:,.2f}")
        
        # Export analysis results
        output_dir = Path("relatorios/analysis")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Export full report
        report.to_excel(output_dir / "full_report.xlsx")
        
        # Export top performers
        top_performers = report.sort('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', ascending=False).head(20)
        top_performers.to_csv(output_dir / "top_performers.csv")
        
        # Export summary
        with open(output_dir / "summary.json", 'w') as f:
            import json
            json.dump(summary, f, indent=2, default=str)
        
        print(f"✅ Analysis complete - results saved to {output_dir}")
        
    except ReportError as e:
        print(f"❌ Analysis failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def main():
    """Run all SDK examples."""
    print("Google Ad Manager SDK - Examples")
    print("=" * 60)
    print("This script demonstrates the fluent API design of the GAM SDK.")
    print("Make sure you have configured authentication before running.")
    print()
    
    # Initialize client
    client = example_basic_client_setup()
    
    if client:
        # Run examples
        example_quick_reports(client)
        example_fluent_reports(client)
        example_configuration_management(client)
        example_authentication_management(client)
        example_advanced_date_ranges(client)
        example_data_analysis_workflow(client)
        
        print("\n" + "=" * 60)
        print("🎉 ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("Check the 'relatorios/' directory for generated reports.")
        print("See the SDK documentation for more advanced usage patterns.")
    else:
        print("\n" + "=" * 60)
        print("❌ SETUP REQUIRED")
        print("=" * 60)
        print("Please configure authentication before running examples:")
        print("1. Set up googleads.yaml with your GAM credentials")
        print("2. Run: python generate_new_token.py")
        print("3. Run this script again")


if __name__ == "__main__":
    main()