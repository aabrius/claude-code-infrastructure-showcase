"""
Example usage of the SOAP adapter.

This file demonstrates how to use the SOAPAdapter for various
Google Ad Manager operations.
"""

from src.core.adapters.soap import SOAPAdapter
from src.core.config import get_config


def main():
    """Demonstrate SOAP adapter usage."""
    
    # Load configuration
    config = get_config()
    
    # Convert config to dict format expected by adapter
    adapter_config = {
        'network_code': config.auth.network_code,
        'client_id': config.auth.client_id,
        'client_secret': config.auth.client_secret,
        'refresh_token': config.auth.refresh_token,
        'application_name': 'GAM SOAP Adapter Example'
    }
    
    # Create SOAP adapter
    adapter = SOAPAdapter(adapter_config)
    
    # Test connection
    if adapter.test_connection():
        print("✅ Successfully connected to GAM API")
        
        # Get network info
        network_info = adapter.get_network_info()
        print(f"Network: {network_info['display_name']} ({network_info['network_code']})")
    
    # Get available dimensions and metrics
    dimensions = adapter.get_dimensions()
    metrics = adapter.get_metrics()
    print(f"Available dimensions: {len(dimensions)}")
    print(f"Available metrics: {len(metrics)}")
    
    # Create a report
    report_definition = {
        'dimensions': ['DATE', 'AD_UNIT_NAME'],
        'metrics': ['AD_SERVER_IMPRESSIONS', 'AD_SERVER_CLICKS'],
        'startDate': '2024-01-01',
        'endDate': '2024-01-31',
        'adUnitView': 'HIERARCHICAL'
    }
    
    try:
        report = adapter.create_report(report_definition)
        print(f"Created report with ID: {report['id']}")
        
        # Check report status
        status = adapter.get_report_status(report['id'])
        print(f"Report status: {status}")
        
        # If completed, download results
        if status == 'COMPLETED':
            csv_data = adapter.download_report(report['id'], format='CSV')
            print(f"Downloaded report data ({len(csv_data)} bytes)")
    
    except Exception as e:
        print(f"Error creating report: {e}")
    
    # Get line items example
    try:
        line_items = adapter.get_line_items(status='READY')
        print(f"Found {len(line_items)} active line items")
        
        for item in line_items[:5]:  # Show first 5
            print(f"  - {item['name']} (ID: {item['id']})")
    
    except Exception as e:
        print(f"Error getting line items: {e}")
    
    # Get ad units example
    try:
        ad_units = adapter.get_inventory('AD_UNITS')
        print(f"Found {len(ad_units)} ad units")
        
        for unit in ad_units[:5]:  # Show first 5
            print(f"  - {unit['name']} ({unit['ad_unit_code']})")
    
    except Exception as e:
        print(f"Error getting ad units: {e}")


if __name__ == '__main__':
    main()