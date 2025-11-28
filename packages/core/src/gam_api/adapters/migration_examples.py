"""
Migration examples for transitioning to the adapter pattern.

This file shows before/after examples of how to migrate existing
SOAP client code to use the new adapter pattern.
"""

# ============================================================================
# EXAMPLE 1: Report Generation
# ============================================================================

def old_report_generation():
    """Old way using direct SOAP client."""
    from src.core.auth import get_auth_manager
    
    # Get SOAP client
    auth_manager = get_auth_manager()
    soap_client = auth_manager.get_soap_client()
    report_service = soap_client.GetService('ReportService')
    
    # Create report job
    report_job = {
        'reportQuery': {
            'dimensions': ['DATE', 'AD_UNIT_NAME'],
            'adUnitView': 'HIERARCHICAL',
            'columns': ['AD_SERVER_IMPRESSIONS', 'AD_SERVER_CLICKS'],
            'dateRangeType': 'CUSTOM_DATE',
            'startDate': {'year': 2024, 'month': 1, 'day': 1},
            'endDate': {'year': 2024, 'month': 1, 'day': 31}
        }
    }
    
    # Run report
    report_job_response = report_service.runReportJob(report_job)
    report_id = report_job_response['id']
    
    # Check status
    report_job = report_service.getReportJob(report_id)
    status = report_job['reportJobStatus']
    
    # Download if ready
    if status == 'COMPLETED':
        report_downloader = report_service.getReportDownloader(report_id, 'CSV_DUMP')
        csv_data = report_downloader.DownloadReportToString()
        return csv_data


def new_report_generation():
    """New way using adapter pattern."""
    from src.core.adapters.soap import SOAPAdapter
    from src.core.config import get_config
    
    # Get configuration
    config = get_config()
    adapter_config = {
        'network_code': config.auth.network_code,
        'client_id': config.auth.client_id,
        'client_secret': config.auth.client_secret,
        'refresh_token': config.auth.refresh_token
    }
    
    # Create adapter
    adapter = SOAPAdapter(adapter_config)
    
    # Create report with simple definition
    report_definition = {
        'dimensions': ['DATE', 'AD_UNIT_NAME'],
        'metrics': ['AD_SERVER_IMPRESSIONS', 'AD_SERVER_CLICKS'],
        'startDate': '2024-01-01',
        'endDate': '2024-01-31'
    }
    
    # Run report
    report = adapter.create_report(report_definition)
    
    # Check status
    status = adapter.get_report_status(report['id'])
    
    # Download if ready
    if status == 'COMPLETED':
        csv_data = adapter.download_report(report['id'])
        return csv_data


# ============================================================================
# EXAMPLE 2: Line Item Management
# ============================================================================

def old_line_item_management():
    """Old way of managing line items."""
    from src.core.auth import get_auth_manager
    from googleads import ad_manager
    
    # Get SOAP client
    auth_manager = get_auth_manager()
    soap_client = auth_manager.get_soap_client()
    line_item_service = soap_client.GetService('LineItemService')
    
    # Get line items with complex statement
    statement_builder = ad_manager.StatementBuilder()
    statement_builder.Where('orderId = :orderId').WithBindVariable('orderId', 12345)
    statement_builder.Where('status = :status').WithBindVariable('status', 'READY')
    statement_builder.OrderBy('id', ascending=False).Limit(500)
    
    line_items = []
    while True:
        response = line_item_service.getLineItemsByStatement(statement_builder.ToStatement())
        
        if 'results' in response and len(response['results']):
            line_items.extend(response['results'])
            statement_builder.offset += len(response['results'])
        else:
            break
    
    return line_items


def new_line_item_management():
    """New way using adapter pattern."""
    from src.core.adapters.soap import SOAPAdapter
    from src.core.config import get_config
    
    # Create adapter
    config = get_config()
    adapter_config = {
        'network_code': config.auth.network_code,
        'client_id': config.auth.client_id,
        'client_secret': config.auth.client_secret,
        'refresh_token': config.auth.refresh_token
    }
    adapter = SOAPAdapter(adapter_config)
    
    # Get line items with simple filters
    line_items = adapter.get_line_items(
        order_id=12345,
        status='READY'
    )
    
    return line_items


# ============================================================================
# EXAMPLE 3: Error Handling
# ============================================================================

def old_error_handling():
    """Old way of handling SOAP errors."""
    from src.core.auth import get_auth_manager
    
    auth_manager = get_auth_manager()
    soap_client = auth_manager.get_soap_client()
    
    try:
        network_service = soap_client.GetService('NetworkService')
        network = network_service.getCurrentNetwork()
        return network
    except Exception as e:
        error_str = str(e)
        if 'Authentication' in error_str:
            print("Authentication failed")
        elif 'QuotaExceeded' in error_str:
            print("Quota exceeded")
        else:
            print(f"Unknown error: {error_str}")
        raise


def new_error_handling():
    """New way with typed exceptions."""
    from src.core.adapters.soap import SOAPAdapter
    from src.core.exceptions import AuthError, QuotaExceededError, APIError
    from src.core.config import get_config
    
    # Create adapter
    config = get_config()
    adapter_config = {
        'network_code': config.auth.network_code,
        'client_id': config.auth.client_id,
        'client_secret': config.auth.client_secret,
        'refresh_token': config.auth.refresh_token
    }
    adapter = SOAPAdapter(adapter_config)
    
    try:
        network_info = adapter.get_network_info()
        return network_info
    except AuthError:
        print("Authentication failed - check credentials")
        raise
    except QuotaExceededError as e:
        print(f"Quota exceeded - retry after some time")
        raise
    except APIError as e:
        print(f"API error: {e}")
        raise


# ============================================================================
# EXAMPLE 4: Working with Ad Units
# ============================================================================

def old_ad_unit_operations():
    """Old way of working with ad units."""
    from src.core.auth import get_auth_manager
    from googleads import ad_manager
    
    auth_manager = get_auth_manager()
    soap_client = auth_manager.get_soap_client()
    inventory_service = soap_client.GetService('InventoryService')
    
    # Get ad units
    statement_builder = ad_manager.StatementBuilder()
    statement_builder.Where('parentId IS NULL')
    statement_builder.OrderBy('id', ascending=True).Limit(500)
    
    ad_units = []
    while True:
        response = inventory_service.getAdUnitsByStatement(statement_builder.ToStatement())
        
        if 'results' in response and len(response['results']):
            ad_units.extend(response['results'])
            statement_builder.offset += len(response['results'])
        else:
            break
    
    # Create ad unit
    new_ad_unit = {
        'name': 'Test Ad Unit',
        'adUnitCode': 'TEST_AD_UNIT',
        'parentId': None,
        'description': 'Test ad unit',
        'targetWindow': 'BLANK',
        'adUnitSizes': [{
            'size': {
                'width': 300,
                'height': 250
            },
            'environmentType': 'BROWSER'
        }]
    }
    
    created_units = inventory_service.createAdUnits([new_ad_unit])
    return created_units[0]


def new_ad_unit_operations():
    """New way using adapter pattern."""
    from src.core.adapters.soap import SOAPAdapter
    from src.core.config import get_config
    
    # Create adapter
    config = get_config()
    adapter_config = {
        'network_code': config.auth.network_code,
        'client_id': config.auth.client_id,
        'client_secret': config.auth.client_secret,
        'refresh_token': config.auth.refresh_token
    }
    adapter = SOAPAdapter(adapter_config)
    
    # Get ad units - much simpler!
    ad_units = adapter.get_inventory('AD_UNITS', parent_id=None)
    
    # Create ad unit with same config
    new_ad_unit = {
        'name': 'Test Ad Unit',
        'adUnitCode': 'TEST_AD_UNIT',
        'parentId': None,
        'description': 'Test ad unit',
        'targetWindow': 'BLANK',
        'adUnitSizes': [{
            'size': {
                'width': 300,
                'height': 250
            },
            'environmentType': 'BROWSER'
        }]
    }
    
    created_unit = adapter.create_ad_unit(new_ad_unit)
    return created_unit


# ============================================================================
# EXAMPLE 5: Batch Operations
# ============================================================================

def old_batch_operations():
    """Old way of handling batch operations."""
    from src.core.auth import get_auth_manager
    
    auth_manager = get_auth_manager()
    soap_client = auth_manager.get_soap_client()
    line_item_service = soap_client.GetService('LineItemService')
    
    # Update multiple line items
    line_items_to_update = []
    for line_item_id in [123, 456, 789]:
        line_item = line_item_service.getLineItem(line_item_id)
        line_item['priority'] = 8
        line_items_to_update.append(line_item)
    
    updated_items = line_item_service.updateLineItems(line_items_to_update)
    return updated_items


def new_batch_operations():
    """New way using adapter pattern."""
    from src.core.adapters.soap import SOAPAdapter
    from src.core.config import get_config
    
    # Create adapter
    config = get_config()
    adapter_config = {
        'network_code': config.auth.network_code,
        'client_id': config.auth.client_id,
        'client_secret': config.auth.client_secret,
        'refresh_token': config.auth.refresh_token
    }
    adapter = SOAPAdapter(adapter_config)
    
    # Update multiple line items
    line_items_to_update = []
    for line_item_id in ['123', '456', '789']:
        line_items_to_update.append({
            'id': line_item_id,
            'priority': 8
        })
    
    updated_items = adapter.manage_line_items('UPDATE', line_items_to_update)
    return updated_items


# ============================================================================
# Migration Checklist
# ============================================================================

"""
Migration Checklist:

1. Update imports:
   - Remove: from googleads import ad_manager
   - Add: from src.core.adapters.soap import SOAPAdapter

2. Replace authentication:
   - Remove: auth_manager.get_soap_client()
   - Add: SOAPAdapter(config)

3. Simplify service access:
   - Remove: soap_client.GetService('ServiceName')
   - Use: adapter methods directly

4. Update date formats:
   - Remove: {'year': 2024, 'month': 1, 'day': 1}
   - Use: '2024-01-01'

5. Handle IDs as strings:
   - Convert: report_id = 12345
   - To: report_id = '12345'

6. Update error handling:
   - Remove: generic Exception catching
   - Use: specific exception types (AuthError, APIError, etc.)

7. Simplify filtering:
   - Remove: complex StatementBuilder logic
   - Use: simple keyword arguments

8. Test thoroughly:
   - Verify all operations work as expected
   - Check error handling scenarios
   - Validate data format conversions
"""