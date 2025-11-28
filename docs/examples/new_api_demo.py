#!/usr/bin/env python3
"""
GAM API - New Clean Interface Demo

This example demonstrates the new clean, user-friendly API that was
implemented as part of Option 2 from the AA-487 repository restructuring.

Key features:
- Simple imports: from gam_api import GAMClient
- Intuitive method names: client.delivery_report()
- Helper classes: DateRange, ReportBuilder
- Fluent API design for building custom reports
"""

import sys
import os

# This demo shows both the new API and backward compatibility
def main():
    print("🚀 GAM API - New Clean Interface Demo")
    print("=====================================\n")
    
    # 1. Simple Import Structure
    print("1. 📦 Simple Import Structure")
    print("   from gam_api import GAMClient, DateRange, ReportBuilder")
    
    try:
        from gam_api import GAMClient, DateRange, ReportBuilder
        print("   ✅ Clean imports successful!\n")
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        print("   💡 Make sure to run: pip install -e .\n")
        return
    
    # 2. Easy Client Creation
    print("2. 🔧 Easy Client Creation")
    print("   client = GAMClient()  # Auto-loads config")
    
    # Mock config for demo (replace with real config in production)
    mock_config = {
        'auth': {
            'network_code': '123456789',
            'client_id': 'your-client-id.apps.googleusercontent.com',
            'client_secret': 'your-client-secret',
            'refresh_token': 'your-refresh-token'
        }
    }
    
    try:
        client = GAMClient(config=mock_config)
        print("   ✅ Client created successfully!\n")
    except Exception as e:
        print(f"   ⚠️  Client creation failed (expected with mock config): {e}")
        print("   💡 In production, use: client = GAMClient() with real config\n")
        # Continue with demo even if client creation fails
        client = None
    
    # 3. DateRange Helpers
    print("3. 📅 DateRange Helpers")
    print("   DateRange.last_week(), DateRange.last_month(), DateRange.last_n_days(14)")
    
    last_week = DateRange.last_week()
    last_month = DateRange.last_month()
    last_14_days = DateRange.last_n_days(14)
    custom_range = DateRange("2024-01-01", "2024-01-31")
    
    print(f"   ✅ Last week: {last_week.start_date} to {last_week.end_date}")
    print(f"   ✅ Last month: {last_month.start_date} to {last_month.end_date}")
    print(f"   ✅ Custom range: {custom_range.start_date} to {custom_range.end_date}\n")
    
    # 4. Quick Reports (if client available)
    print("4. 📊 Quick Report Methods")
    if client:
        print("   # These would work with real credentials:")
        print("   delivery = client.delivery_report(DateRange.last_week())")
        print("   inventory = client.inventory_report(DateRange.last_month())")
        print("   sales = client.sales_report(DateRange.last_n_days(30))")
    else:
        print("   💡 Quick report examples (need real config):")
        print("   client.delivery_report(DateRange.last_week())    # Impressions, clicks, CTR")
        print("   client.inventory_report(DateRange.last_month())  # Ad requests, fill rate")
        print("   client.sales_report(DateRange.last_n_days(30))   # Revenue, eCPM")
    print()
    
    # 5. Report Builder
    print("5. 🏗️  ReportBuilder - Fluent API")
    print("   Building a custom report with fluent interface:")
    
    report_definition = (
        ReportBuilder()
        .add_dimension("DATE")
        .add_dimension("AD_UNIT_NAME")
        .add_dimension("COUNTRY_NAME")
        .add_metric("IMPRESSIONS")
        .add_metric("CLICKS")
        .add_metric("CTR")
        .add_metric("REVENUE")
        .set_date_range(DateRange.last_n_days(7))
        .add_filter("AD_UNIT_NAME", "CONTAINS", "Mobile")
        .add_filter("COUNTRY_NAME", "EQUALS", "United States")
        .build()
    )
    
    print("   ✅ Report definition created:")
    print(f"      Dimensions: {report_definition['dimensions']}")
    print(f"      Metrics: {report_definition['metrics']}")
    print(f"      Date range: {report_definition['date_range']}")
    print(f"      Filters: {len(report_definition['filters'])} filters\n")
    
    # 6. Error Handling
    print("6. 🚨 Error Handling")
    print("   from gam_api import APIError, AuthenticationError, ReportGenerationError")
    
    try:
        from gam_api import APIError, AuthenticationError, ReportGenerationError
        print("   ✅ Exception classes imported")
        print("   💡 Use try/except blocks for proper error handling\n")
    except ImportError as e:
        print(f"   ❌ Exception import failed: {e}\n")
    
    # 7. Backward Compatibility
    print("7. 🔄 Backward Compatibility")
    print("   Legacy imports still work (with deprecation warnings):")
    
    try:
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # This should issue a deprecation warning
            from src.core.unified import GAMUnifiedClient
            
            if w:
                print("   ✅ Legacy import works with deprecation warning")
                for warning in w:
                    if "deprecated" in str(warning.message).lower():
                        print(f"   ⚠️  Warning: {warning.message}")
            else:
                print("   ✅ Legacy import works (warning system may vary)")
    except Exception as e:
        print(f"   ❌ Legacy import test failed: {e}")
    
    print()
    
    # 8. Integration Example
    print("8. 🔌 Integration Example")
    print("   How other applications can integrate:")
    print("""
   # In another application's requirements.txt:
   gam-api>=1.0.0
   
   # In application code:
   from gam_api import GAMClient, DateRange
   
   def get_weekly_metrics():
       client = GAMClient()  # Loads config automatically
       return client.delivery_report(DateRange.last_week())
   
   def get_custom_analysis():
       client = GAMClient()
       return client.create_report(
           ReportBuilder()
           .add_dimension("DATE")
           .add_metric("REVENUE")
           .set_date_range(DateRange.last_month())
           .build()
       )
""")
    
    # 9. Benefits Summary
    print("9. ✨ Benefits of New Structure")
    benefits = [
        "Clean imports: `from gam_api import GAMClient`",
        "Intuitive method names: `client.delivery_report()`",
        "Helper classes: `DateRange.last_week()`",
        "Fluent API: `ReportBuilder().add_dimension().build()`", 
        "Type hints and IDE support",
        "Backward compatibility maintained",
        "Easy integration for other applications",
        "< 1 hour setup time for new projects"
    ]
    
    for i, benefit in enumerate(benefits, 1):
        print(f"   {i}. ✅ {benefit}")
    
    print("\n🎉 Demo Complete!")
    print("The new gam_api package provides the clean, simple interface")
    print("that was envisioned in AA-487, making GAM integration easy!")

if __name__ == "__main__":
    main()