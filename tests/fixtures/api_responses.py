"""
Mock API response fixtures for testing.

Provides realistic API response data for both SOAP and REST API testing.
"""

from datetime import datetime, date
from typing import Dict, List, Any


class MockSOAPResponses:
    """Mock SOAP API response data."""
    
    @staticmethod
    def get_network_info() -> Dict[str, Any]:
        """Mock getCurrentNetwork response."""
        return {
            'id': '123456789',
            'networkCode': '123456789',
            'displayName': 'Test Network',
            'timeZone': 'America/New_York',
            'currencyCode': 'USD',
            'effectiveRootAdUnitId': '987654321',
            'isTest': True,
            'propertyCode': 'TEST_PROP',
            'enabledApiVersions': ['v202311'],
            'childNetworks': []
        }
    
    @staticmethod
    def get_report_job_complete() -> Dict[str, Any]:
        """Mock completed report job."""
        return {
            'id': 12345,
            'reportQuery': {
                'dimensions': ['DATE', 'AD_UNIT_NAME'],
                'metrics': ['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 'TOTAL_LINE_ITEM_LEVEL_CLICKS'],
                'dateRangeType': 'CUSTOM_DATE',
                'startDate': {'year': 2024, 'month': 1, 'day': 1},
                'endDate': {'year': 2024, 'month': 1, 'day': 31}
            },
            'reportJobStatus': 'COMPLETED'
        }
    
    @staticmethod
    def get_report_job_running() -> Dict[str, Any]:
        """Mock running report job."""
        job = MockSOAPResponses.get_report_job_complete()
        job['reportJobStatus'] = 'RUNNING'
        return job
    
    @staticmethod
    def get_report_job_failed() -> Dict[str, Any]:
        """Mock failed report job."""
        job = MockSOAPResponses.get_report_job_complete()
        job['reportJobStatus'] = 'FAILED'
        return job
    
    @staticmethod
    def get_report_download_url() -> str:
        """Mock report download URL."""
        return "https://storage.googleapis.com/test-bucket/report-123.csv.gz"
    
    @staticmethod
    def get_report_csv_data() -> str:
        """Mock CSV report data."""
        return """DATE,AD_UNIT_NAME,TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS,TOTAL_LINE_ITEM_LEVEL_CLICKS
2024-01-01,Mobile Banner,1000,50
2024-01-01,Desktop Banner,2000,100
2024-01-02,Mobile Banner,1500,75
2024-01-02,Desktop Banner,2500,125
"""
    
    @staticmethod
    def get_ad_units() -> List[Dict[str, Any]]:
        """Mock ad units response."""
        return [
            {
                'id': '1001',
                'name': 'Mobile Banner',
                'parentId': '1000',
                'status': 'ACTIVE',
                'adUnitCode': 'mobile_banner_300x250',
                'sizes': [{'width': 300, 'height': 250}]
            },
            {
                'id': '1002', 
                'name': 'Desktop Banner',
                'parentId': '1000',
                'status': 'ACTIVE',
                'adUnitCode': 'desktop_banner_728x90',
                'sizes': [{'width': 728, 'height': 90}]
            }
        ]
    
    @staticmethod
    def get_line_items() -> List[Dict[str, Any]]:
        """Mock line items response."""
        return [
            {
                'id': '2001',
                'name': 'Test Campaign Line Item',
                'orderId': '3001',
                'status': 'DELIVERING',
                'lineItemType': 'STANDARD',
                'startDateTime': {'date': {'year': 2024, 'month': 1, 'day': 1}},
                'endDateTime': {'date': {'year': 2024, 'month': 12, 'day': 31}},
                'costType': 'CPM',
                'costPerUnit': {'microAmount': 2000000}  # $2.00 CPM
            }
        ]


class MockRESTResponses:
    """Mock REST API v1 response data."""
    
    @staticmethod
    def get_network_info() -> Dict[str, Any]:
        """Mock network info from REST API."""
        return {
            'name': 'networks/123456789',
            'networkCode': '123456789',
            'displayName': 'Test Network',
            'timeZone': 'America/New_York',
            'currencyCode': 'USD',
            'effectiveRootAdUnitId': '987654321',
            'isTest': True
        }
    
    @staticmethod
    def get_create_report_response() -> Dict[str, Any]:
        """Mock create report response."""
        return {
            'name': 'networks/123456789/reports/test-report-123',
            'displayName': 'Test Delivery Report',
            'reportDefinition': {
                'dimensions': ['DATE', 'AD_UNIT_NAME'],
                'metrics': ['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 'TOTAL_LINE_ITEM_LEVEL_CLICKS'],
                'dateRange': {
                    'startDate': '2024-01-01',
                    'endDate': '2024-01-31'
                },
                'reportType': 'HISTORICAL'
            },
            'createTime': '2024-01-01T10:00:00Z',
            'updateTime': '2024-01-01T10:00:00Z'
        }
    
    @staticmethod
    def get_run_report_operation() -> Dict[str, Any]:
        """Mock run report operation response."""
        return {
            'name': 'operations/test-operation-123',
            'done': False,
            'metadata': {
                '@type': 'type.googleapis.com/google.ads.admanager.v1.RunReportOperationMetadata',
                'reportName': 'networks/123456789/reports/test-report-123',
                'progressPercent': 0
            }
        }
    
    @staticmethod
    def get_operation_in_progress() -> Dict[str, Any]:
        """Mock operation in progress."""
        op = MockRESTResponses.get_run_report_operation()
        op['metadata']['progressPercent'] = 50
        return op
    
    @staticmethod
    def get_operation_complete() -> Dict[str, Any]:
        """Mock completed operation."""
        return {
            'name': 'operations/test-operation-123',
            'done': True,
            'metadata': {
                '@type': 'type.googleapis.com/google.ads.admanager.v1.RunReportOperationMetadata',
                'reportName': 'networks/123456789/reports/test-report-123',
                'progressPercent': 100
            },
            'response': {
                '@type': 'type.googleapis.com/google.ads.admanager.v1.RunReportResponse',
                'reportResult': {
                    'name': 'networks/123456789/reports/test-report-123/results/result-123'
                }
            }
        }
    
    @staticmethod
    def get_operation_failed() -> Dict[str, Any]:
        """Mock failed operation."""
        return {
            'name': 'operations/test-operation-123',
            'done': True,
            'error': {
                'code': 3,
                'message': 'Report generation failed: Invalid date range',
                'details': []
            }
        }
    
    @staticmethod
    def get_fetch_results_response() -> Dict[str, Any]:
        """Mock fetch results response."""
        return {
            'rows': [
                {
                    'dimensionValues': ['2024-01-01', 'Mobile Banner'],
                    'metricValueGroups': [{'primaryValues': ['1000', '50']}]
                },
                {
                    'dimensionValues': ['2024-01-01', 'Desktop Banner'],
                    'metricValueGroups': [{'primaryValues': ['2000', '100']}]
                },
                {
                    'dimensionValues': ['2024-01-02', 'Mobile Banner'],
                    'metricValueGroups': [{'primaryValues': ['1500', '75']}]
                },
                {
                    'dimensionValues': ['2024-01-02', 'Desktop Banner'],
                    'metricValueGroups': [{'primaryValues': ['2500', '125']}]
                }
            ],
            'nextPageToken': '',
            'metadata': {
                'generatedAt': '2024-01-01T10:00:00Z',
                'totalRows': 4
            }
        }
    
    @staticmethod
    def get_paginated_results_page1() -> Dict[str, Any]:
        """Mock first page of paginated results."""
        return {
            'rows': [
                {
                    'dimensionValues': ['2024-01-01', 'Mobile Banner'],
                    'metricValueGroups': [{'primaryValues': ['1000', '50']}]
                },
                {
                    'dimensionValues': ['2024-01-01', 'Desktop Banner'],
                    'metricValueGroups': [{'primaryValues': ['2000', '100']}]
                }
            ],
            'nextPageToken': 'next_page_token_123',
            'metadata': {
                'generatedAt': '2024-01-01T10:00:00Z',
                'totalRows': 4
            }
        }
    
    @staticmethod
    def get_paginated_results_page2() -> Dict[str, Any]:
        """Mock second page of paginated results."""
        return {
            'rows': [
                {
                    'dimensionValues': ['2024-01-02', 'Mobile Banner'],
                    'metricValueGroups': [{'primaryValues': ['1500', '75']}]
                },
                {
                    'dimensionValues': ['2024-01-02', 'Desktop Banner'],
                    'metricValueGroups': [{'primaryValues': ['2500', '125']}]
                }
            ],
            'nextPageToken': '',
            'metadata': {
                'generatedAt': '2024-01-01T10:00:00Z',
                'totalRows': 4
            }
        }
    
    @staticmethod
    def get_list_reports_response() -> Dict[str, Any]:
        """Mock list reports response."""
        return {
            'reports': [
                {
                    'name': 'networks/123456789/reports/report-1',
                    'displayName': 'Daily Delivery Report',
                    'reportDefinition': {
                        'dimensions': ['DATE', 'AD_UNIT_NAME'],
                        'metrics': ['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS'],
                        'reportType': 'HISTORICAL'
                    },
                    'createTime': '2024-01-01T09:00:00Z'
                },
                {
                    'name': 'networks/123456789/reports/report-2',
                    'displayName': 'Weekly Performance Report',
                    'reportDefinition': {
                        'dimensions': ['DATE', 'ADVERTISER_NAME'],
                        'metrics': ['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 'TOTAL_LINE_ITEM_LEVEL_CLICKS'],
                        'reportType': 'HISTORICAL'
                    },
                    'createTime': '2024-01-01T08:00:00Z'
                }
            ],
            'nextPageToken': ''
        }
    
    @staticmethod
    def get_error_response(error_code: int = 400, message: str = "Bad Request") -> Dict[str, Any]:
        """Mock error response."""
        return {
            'error': {
                'code': error_code,
                'message': message,
                'status': 'INVALID_ARGUMENT' if error_code == 400 else 'INTERNAL',
                'details': [
                    {
                        '@type': 'type.googleapis.com/google.rpc.ErrorInfo',
                        'reason': 'INVALID_PARAMETER',
                        'domain': 'admanager.googleapis.com'
                    }
                ]
            }
        }


class MockReportData:
    """Mock report data generators."""
    
    @staticmethod
    def generate_delivery_report_data(num_rows: int = 10) -> List[Dict[str, Any]]:
        """Generate mock delivery report data."""
        rows = []
        ad_units = ['Mobile Banner', 'Desktop Banner', 'Tablet Banner', 'Video Ad']
        
        for i in range(num_rows):
            day = (i % 31) + 1
            ad_unit = ad_units[i % len(ad_units)]
            impressions = 1000 + (i * 100)
            clicks = impressions // 20  # 5% CTR
            
            rows.append({
                'dimensionValues': [f'2024-01-{day:02d}', ad_unit],
                'metricValueGroups': [{'primaryValues': [str(impressions), str(clicks)]}]
            })
        
        return rows
    
    @staticmethod
    def generate_inventory_report_data(num_rows: int = 10) -> List[Dict[str, Any]]:
        """Generate mock inventory report data."""
        rows = []
        ad_units = ['Banner Top', 'Banner Bottom', 'Sidebar', 'Interstitial']
        
        for i in range(num_rows):
            day = (i % 31) + 1
            ad_unit = ad_units[i % len(ad_units)]
            requests = 10000 + (i * 500)
            matched = int(requests * 0.8)  # 80% match rate
            impressions = int(matched * 0.9)  # 90% fill rate
            
            rows.append({
                'dimensionValues': [f'2024-01-{day:02d}', ad_unit],
                'metricValueGroups': [{'primaryValues': [str(requests), str(matched), str(impressions)]}]
            })
        
        return rows
    
    @staticmethod
    def generate_sales_report_data(num_rows: int = 10) -> List[Dict[str, Any]]:
        """Generate mock sales report data."""
        rows = []
        advertisers = ['Advertiser A', 'Advertiser B', 'Advertiser C']
        orders = ['Order 1', 'Order 2', 'Order 3', 'Order 4']
        
        for i in range(num_rows):
            day = (i % 31) + 1
            advertiser = advertisers[i % len(advertisers)]
            order = orders[i % len(orders)]
            impressions = 5000 + (i * 200)
            revenue = impressions * 2.5 / 1000  # $2.50 CPM
            
            rows.append({
                'dimensionValues': [f'2024-01-{day:02d}', advertiser, order],
                'metricValueGroups': [{'primaryValues': [str(impressions), f'{revenue:.2f}']}]
            })
        
        return rows
    
    @staticmethod
    def create_report_result(report_type: str = 'delivery', num_rows: int = 10):
        """Create a complete ReportResult object."""
        from src.sdk.reports import ReportResult
        
        if report_type == 'delivery':
            rows = MockReportData.generate_delivery_report_data(num_rows)
            dimensions = ['DATE', 'AD_UNIT_NAME']
            metrics = ['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 'TOTAL_LINE_ITEM_LEVEL_CLICKS']
        elif report_type == 'inventory':
            rows = MockReportData.generate_inventory_report_data(num_rows)
            dimensions = ['DATE', 'AD_UNIT_NAME']
            metrics = ['AD_REQUESTS', 'MATCHED_REQUESTS', 'TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS']
        elif report_type == 'sales':
            rows = MockReportData.generate_sales_report_data(num_rows)
            dimensions = ['DATE', 'ADVERTISER_NAME', 'ORDER_NAME']
            metrics = ['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 'TOTAL_LINE_ITEM_LEVEL_REVENUE']
        else:
            raise ValueError(f"Unknown report type: {report_type}")
        
        metadata = {
            'generated_at': datetime.now().isoformat(),
            'report_type': report_type,
            'total_rows': len(rows)
        }
        
        return ReportResult(rows, dimensions, metrics, metadata)


class MockCredentials:
    """Mock OAuth2 credentials."""
    
    def __init__(self, expired: bool = False):
        self.expired = expired
        self.expiry = datetime.now() if expired else datetime.now().replace(year=2025)
        self.refresh_token = 'test_refresh_token'
        self.token = 'test_access_token'
        self.scopes = [
            'https://www.googleapis.com/auth/dfp',
            'https://www.googleapis.com/auth/admanager'
        ]
        self._refresh_called = False
    
    def refresh(self, request):
        """Mock refresh method."""
        self._refresh_called = True
        self.expired = False
        self.token = 'new_access_token'
        self.expiry = datetime.now().replace(year=2025)
    
    def apply(self, headers):
        """Mock apply method."""
        headers['Authorization'] = f'Bearer {self.token}'