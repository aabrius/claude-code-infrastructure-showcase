"""
Mock data generators for testing.
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any


class MockDataGenerator:
    """Generate mock data for testing."""
    
    @staticmethod
    def generate_date_range(days_back: int = 30) -> List[str]:
        """Generate a list of dates."""
        end_date = datetime.now()
        dates = []
        for i in range(days_back):
            date = end_date - timedelta(days=i)
            dates.append(date.strftime('%Y-%m-%d'))
        return sorted(dates)
    
    @staticmethod
    def generate_ad_units(count: int = 5) -> List[str]:
        """Generate mock ad unit names."""
        ad_unit_types = ['Banner', 'Sidebar', 'Leaderboard', 'Rectangle', 'Skyscraper']
        positions = ['Homepage', 'Article', 'Category', 'Search', 'Mobile']
        
        ad_units = []
        for i in range(count):
            unit_type = random.choice(ad_unit_types)
            position = random.choice(positions)
            ad_units.append(f"{position}_{unit_type}_{i+1}")
        
        return ad_units
    
    @staticmethod
    def generate_advertisers(count: int = 10) -> List[str]:
        """Generate mock advertiser names."""
        companies = [
            'Acme Corp', 'Global Tech', 'Media Solutions', 'Digital Ads Inc',
            'Marketing Pro', 'Brand Central', 'Ad Network Plus', 'Creative Agency',
            'Performance Media', 'Growth Partners'
        ]
        return companies[:count]
    
    @staticmethod
    def generate_delivery_report_data(days: int = 7, ad_units: int = 3) -> List[List[str]]:
        """Generate mock delivery report data."""
        dates = MockDataGenerator.generate_date_range(days)
        units = MockDataGenerator.generate_ad_units(ad_units)
        
        data = []
        for date in dates:
            for unit in units:
                impressions = random.randint(1000, 50000)
                clicks = int(impressions * random.uniform(0.001, 0.05))
                ctr = round((clicks / impressions) * 100, 2)
                cpm = round(random.uniform(0.5, 10.0), 2)
                revenue = round((impressions / 1000) * cpm, 2)
                
                data.append([
                    date,
                    unit,
                    str(impressions),
                    str(clicks),
                    f"{ctr}%",
                    f"${cpm}",
                    f"${revenue}"
                ])
        
        return data
    
    @staticmethod
    def generate_inventory_report_data(days: int = 7, ad_units: int = 3) -> List[List[str]]:
        """Generate mock inventory report data."""
        dates = MockDataGenerator.generate_date_range(days)
        units = MockDataGenerator.generate_ad_units(ad_units)
        
        data = []
        for date in dates:
            for unit in units:
                ad_requests = random.randint(2000, 60000)
                matched_requests = int(ad_requests * random.uniform(0.7, 0.95))
                fill_rate = round((matched_requests / ad_requests) * 100, 2)
                impressions = int(matched_requests * random.uniform(0.8, 0.98))
                
                data.append([
                    date,
                    unit,
                    str(ad_requests),
                    str(matched_requests),
                    f"{fill_rate}%",
                    str(impressions)
                ])
        
        return data
    
    @staticmethod
    def generate_sales_report_data(days: int = 7, advertisers: int = 5) -> List[List[str]]:
        """Generate mock sales report data."""
        dates = MockDataGenerator.generate_date_range(days)
        advertiser_list = MockDataGenerator.generate_advertisers(advertisers)
        
        data = []
        for date in dates:
            for advertiser in advertiser_list:
                impressions = random.randint(5000, 100000)
                revenue = round(random.uniform(50, 5000), 2)
                ecpm = round((revenue / impressions) * 1000, 2)
                clicks = int(impressions * random.uniform(0.001, 0.03))
                
                data.append([
                    date,
                    advertiser,
                    f"Order_{random.randint(1000, 9999)}",
                    str(impressions),
                    str(clicks),
                    f"${revenue}",
                    f"${ecpm}"
                ])
        
        return data
    
    @staticmethod
    def generate_reach_report_data(days: int = 7) -> List[List[str]]:
        """Generate mock reach report data."""
        dates = MockDataGenerator.generate_date_range(days)
        countries = ['US', 'GB', 'CA', 'AU', 'DE']
        devices = ['Desktop', 'Mobile', 'Tablet']
        
        data = []
        for date in dates:
            for country in countries:
                for device in devices:
                    unique_reach = random.randint(1000, 50000)
                    impressions = int(unique_reach * random.uniform(1.2, 5.0))
                    frequency = round(impressions / unique_reach, 2)
                    
                    data.append([
                        date,
                        country,
                        device,
                        str(unique_reach),
                        str(impressions),
                        f"{frequency}"
                    ])
        
        return data
    
    @staticmethod
    def generate_programmatic_report_data(days: int = 7) -> List[List[str]]:
        """Generate mock programmatic report data."""
        dates = MockDataGenerator.generate_date_range(days)
        channels = ['Ad Exchange', 'Open Bidding', 'Private Marketplace', 'Programmatic Guaranteed']
        
        data = []
        for date in dates:
            for channel in channels:
                impressions = random.randint(10000, 200000)
                revenue = round(random.uniform(100, 10000), 2)
                ecpm = round((revenue / impressions) * 1000, 2)
                fill_rate = round(random.uniform(60, 95), 2)
                
                data.append([
                    date,
                    channel,
                    str(impressions),
                    f"${revenue}",
                    f"${ecpm}",
                    f"{fill_rate}%"
                ])
        
        return data
    
    @staticmethod
    def generate_report_metadata(report_type: str = 'delivery') -> Dict[str, Any]:
        """Generate mock report metadata."""
        metadata_map = {
            'delivery': {
                'dimension_headers': ['DATE', 'AD_UNIT_NAME'],
                'metric_headers': ['IMPRESSIONS', 'CLICKS', 'CTR', 'CPM', 'REVENUE'],
                'report_name': 'Delivery Performance Report'
            },
            'inventory': {
                'dimension_headers': ['DATE', 'AD_UNIT_NAME'],
                'metric_headers': ['AD_REQUESTS', 'MATCHED_REQUESTS', 'FILL_RATE', 'IMPRESSIONS'],
                'report_name': 'Inventory Analysis Report'
            },
            'sales': {
                'dimension_headers': ['DATE', 'ADVERTISER_NAME', 'ORDER_NAME'],
                'metric_headers': ['IMPRESSIONS', 'CLICKS', 'REVENUE', 'ECPM'],
                'report_name': 'Sales Performance Report'
            },
            'reach': {
                'dimension_headers': ['DATE', 'COUNTRY_NAME', 'DEVICE_CATEGORY_NAME'],
                'metric_headers': ['UNIQUE_REACH', 'IMPRESSIONS', 'FREQUENCY'],
                'report_name': 'Audience Reach Report'
            },
            'programmatic': {
                'dimension_headers': ['DATE', 'DEMAND_CHANNEL_NAME'],
                'metric_headers': ['IMPRESSIONS', 'REVENUE', 'ECPM', 'FILL_RATE'],
                'report_name': 'Programmatic Performance Report'
            }
        }
        
        metadata = metadata_map.get(report_type, metadata_map['delivery'])
        metadata.update({
            'report_id': f"report_{report_type}_{random.randint(1000, 9999)}",
            'created_at': datetime.now().isoformat(),
            'status': 'COMPLETED',
            'execution_time': round(random.uniform(1.0, 5.0), 2)
        })
        
        return metadata
    
    @staticmethod
    def generate_complete_report(report_type: str = 'delivery', days: int = 7) -> Dict[str, Any]:
        """Generate a complete mock report with data and metadata."""
        # Generate data based on report type
        data_generators = {
            'delivery': lambda: MockDataGenerator.generate_delivery_report_data(days),
            'inventory': lambda: MockDataGenerator.generate_inventory_report_data(days),
            'sales': lambda: MockDataGenerator.generate_sales_report_data(days),
            'reach': lambda: MockDataGenerator.generate_reach_report_data(days),
            'programmatic': lambda: MockDataGenerator.generate_programmatic_report_data(days)
        }
        
        data = data_generators.get(report_type, data_generators['delivery'])()
        metadata = MockDataGenerator.generate_report_metadata(report_type)
        
        return {
            'data': data,
            'dimension_headers': metadata['dimension_headers'],
            'metric_headers': metadata['metric_headers'],
            'total_rows': len(data),
            'report_id': metadata['report_id'],
            'report_name': metadata['report_name'],
            'created_at': metadata['created_at'],
            'status': metadata['status'],
            'execution_time': metadata['execution_time']
        }
    
    @staticmethod
    def generate_api_error_response(error_type: str = 'quota') -> Dict[str, Any]:
        """Generate mock API error responses."""
        error_types = {
            'quota': {
                'code': 'QUOTA_EXCEEDED',
                'message': 'Daily API quota exceeded',
                'details': {
                    'quota_limit': 10000,
                    'quota_used': 10001,
                    'reset_time': (datetime.now() + timedelta(hours=6)).isoformat()
                }
            },
            'auth': {
                'code': 'AUTHENTICATION_ERROR',
                'message': 'Invalid or expired credentials',
                'details': {
                    'token_expired': True,
                    'required_scopes': ['https://www.googleapis.com/auth/dfp']
                }
            },
            'validation': {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid request parameters',
                'details': {
                    'field': 'dimensions',
                    'error': 'Invalid dimension: INVALID_DIMENSION',
                    'valid_values': ['DATE', 'AD_UNIT_NAME', 'ADVERTISER_NAME']
                }
            },
            'rate_limit': {
                'code': 'RATE_LIMIT_ERROR',
                'message': 'Too many requests',
                'details': {
                    'retry_after': 60,
                    'rate_limit': '100 requests per minute'
                }
            }
        }
        
        return error_types.get(error_type, error_types['quota'])


class MockResponseGenerator:
    """Generate mock API responses."""
    
    @staticmethod
    def create_report_response(report_id: str = None) -> Dict[str, Any]:
        """Create a mock report creation response."""
        if not report_id:
            report_id = f"report_{random.randint(10000, 99999)}"
        
        return {
            'id': report_id,
            'reportJob': {
                'id': report_id,
                'reportQuery': {
                    'dimensions': ['DATE', 'AD_UNIT_NAME'],
                    'columns': ['IMPRESSIONS', 'CLICKS'],
                    'dateRangeType': 'LAST_WEEK'
                }
            },
            'status': 'IN_PROGRESS',
            'createdDateTime': datetime.now().isoformat()
        }
    
    @staticmethod
    def report_status_response(report_id: str, status: str = 'COMPLETED') -> Dict[str, Any]:
        """Create a mock report status response."""
        statuses = {
            'IN_PROGRESS': {
                'percentComplete': random.randint(10, 90),
                'estimatedCompletionTime': (datetime.now() + timedelta(minutes=5)).isoformat()
            },
            'COMPLETED': {
                'percentComplete': 100,
                'completionTime': datetime.now().isoformat(),
                'downloadUrl': f"https://storage.googleapis.com/reports/{report_id}.csv"
            },
            'FAILED': {
                'percentComplete': 0,
                'error': 'Report generation failed',
                'errorDetails': 'Insufficient data for the requested date range'
            }
        }
        
        response = {
            'id': report_id,
            'status': status
        }
        response.update(statuses.get(status, {}))
        
        return response
    
    @staticmethod
    def list_reports_response(count: int = 10) -> Dict[str, Any]:
        """Create a mock list reports response."""
        reports = []
        
        for i in range(count):
            report_type = random.choice(['delivery', 'inventory', 'sales'])
            reports.append({
                'id': f"report_{random.randint(10000, 99999)}",
                'displayName': f"{report_type.capitalize()} Report {i+1}",
                'reportType': report_type,
                'createdDateTime': (datetime.now() - timedelta(days=i)).isoformat(),
                'lastModifiedDateTime': (datetime.now() - timedelta(hours=i*2)).isoformat(),
                'status': random.choice(['COMPLETED', 'IN_PROGRESS', 'SCHEDULED'])
            })
        
        return {
            'totalResultSetSize': count,
            'results': reports
        }
    
    @staticmethod
    def network_info_response(network_code: str = '123456789') -> Dict[str, Any]:
        """Create a mock network info response."""
        return {
            'id': network_code,
            'networkCode': network_code,
            'displayName': 'Test Ad Network',
            'timeZone': 'America/New_York',
            'currencyCode': 'USD',
            'effectiveRootAdUnitId': '987654321',
            'effectiveRootAdUnitName': 'Root Ad Unit',
            'isTest': True,
            'childPublishers': []
        }


class MockFixtures:
    """Common test fixtures."""
    
    @staticmethod
    def oauth_credentials():
        """Mock OAuth2 credentials."""
        return {
            'client_id': 'test-client-id.apps.googleusercontent.com',
            'client_secret': 'test-client-secret',
            'refresh_token': 'test-refresh-token',
            'access_token': 'test-access-token',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'scopes': [
                'https://www.googleapis.com/auth/dfp',
                'https://www.googleapis.com/auth/admanager'
            ]
        }
    
    @staticmethod
    def config_data():
        """Mock configuration data."""
        return {
            'ad_manager': {
                'network_code': '123456789',
                'application_name': 'GAM-API-Test',
                'client_id': 'test-client-id.apps.googleusercontent.com',
                'client_secret': 'test-client-secret',
                'refresh_token': 'test-refresh-token'
            },
            'api': {
                'prefer_rest': True,
                'timeout': 120,
                'max_retries': 3
            },
            'cache': {
                'enabled': True,
                'directory': '/tmp/gam-api-test-cache',
                'ttl': 3600
            },
            'logging': {
                'level': 'DEBUG',
                'directory': '/tmp/gam-api-test-logs',
                'file': 'test.log'
            }
        }