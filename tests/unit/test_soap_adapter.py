"""
Unit tests for SOAP adapter implementation.

Tests the SOAPAdapter class functionality including authentication,
service creation, and API operations.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from gam_api.adapters.soap.soap_adapter import SOAPAdapter
from gam_api.exceptions import (
    AuthenticationError, APIError, InvalidRequestError, 
    QuotaExceededError, NotFoundError, ReportNotReadyError,
    ConfigurationError
)


class TestSOAPAdapter(unittest.TestCase):
    """Test cases for SOAPAdapter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'network_code': '123456789',
            'client_id': 'test-client-id',
            'client_secret': 'test-client-secret',
            'refresh_token': 'test-refresh-token',
            'application_name': 'Test App'
        }
    
    @patch('src.core.adapters.soap.soap_adapter.ad_manager')
    def test_init_success(self, mock_ad_manager):
        """Test successful adapter initialization."""
        # Mock the SOAP client
        mock_client = Mock()
        mock_ad_manager.AdManagerClient.LoadFromStorage.return_value = mock_client
        
        # Create adapter
        adapter = SOAPAdapter(self.config)
        
        # Verify initialization
        self.assertIsNotNone(adapter._soap_client)
        self.assertEqual(adapter._network_code, '123456789')
        mock_ad_manager.AdManagerClient.LoadFromStorage.assert_called_once()
    
    def test_init_missing_config(self):
        """Test initialization with missing configuration."""
        # Remove required field
        del self.config['network_code']
        
        # Should raise ConfigurationError
        with self.assertRaises(ConfigurationError) as context:
            SOAPAdapter(self.config)
        
        self.assertIn('Missing required config fields', str(context.exception))
    
    @patch('src.core.adapters.soap.soap_adapter.ad_manager')
    def test_get_service(self, mock_ad_manager):
        """Test service creation and caching."""
        # Mock SOAP client
        mock_client = Mock()
        mock_service = Mock()
        mock_client.GetService.return_value = mock_service
        mock_ad_manager.AdManagerClient.LoadFromStorage.return_value = mock_client
        
        # Create adapter
        adapter = SOAPAdapter(self.config)
        
        # Get service twice
        service1 = adapter._get_service('ReportService')
        service2 = adapter._get_service('ReportService')
        
        # Should be the same cached instance
        self.assertEqual(service1, service2)
        # Should only create service once
        mock_client.GetService.assert_called_once_with('ReportService')
    
    @patch('src.core.adapters.soap.soap_adapter.ad_manager')
    def test_handle_soap_error_auth(self, mock_ad_manager):
        """Test error handling for authentication errors."""
        adapter = SOAPAdapter(self.config)
        
        # Test authentication error
        error = Exception("Authentication failed")
        with self.assertRaises(AuthenticationError):
            adapter._handle_soap_error(error)
    
    @patch('src.core.adapters.soap.soap_adapter.ad_manager')
    def test_handle_soap_error_quota(self, mock_ad_manager):
        """Test error handling for quota errors."""
        adapter = SOAPAdapter(self.config)
        
        # Test quota error
        error = Exception("QuotaExceeded: Daily limit reached")
        with self.assertRaises(QuotaExceededError):
            adapter._handle_soap_error(error)
    
    @patch('src.core.adapters.soap.soap_adapter.ad_manager')
    def test_create_report(self, mock_ad_manager):
        """Test report creation."""
        # Mock setup
        mock_client = Mock()
        mock_service = Mock()
        mock_client.GetService.return_value = mock_service
        mock_ad_manager.AdManagerClient.LoadFromStorage.return_value = mock_client
        
        # Mock report response
        mock_report_job = {
            'id': 12345,
            'reportJobStatus': 'IN_PROGRESS',
            'reportQuery': {}
        }
        mock_service.runReportJob.return_value = mock_report_job
        
        # Create adapter and run report
        adapter = SOAPAdapter(self.config)
        report_def = {
            'dimensions': ['DATE', 'AD_UNIT_NAME'],
            'metrics': ['IMPRESSIONS', 'CLICKS'],
            'startDate': '2024-01-01',
            'endDate': '2024-01-31'
        }
        
        result = adapter.create_report(report_def)
        
        # Verify result
        self.assertEqual(result['id'], '12345')
        self.assertEqual(result['status'], 'IN_PROGRESS')
        mock_service.runReportJob.assert_called_once()
    
    @patch('src.core.adapters.soap.soap_adapter.ad_manager')
    def test_get_report_status(self, mock_ad_manager):
        """Test getting report status."""
        # Mock setup
        mock_client = Mock()
        mock_service = Mock()
        mock_client.GetService.return_value = mock_service
        mock_ad_manager.AdManagerClient.LoadFromStorage.return_value = mock_client
        
        # Mock report job
        mock_service.getReportJob.return_value = {
            'id': 12345,
            'reportJobStatus': 'COMPLETED'
        }
        
        # Get status
        adapter = SOAPAdapter(self.config)
        status = adapter.get_report_status('12345')
        
        self.assertEqual(status, 'COMPLETED')
        mock_service.getReportJob.assert_called_once_with(12345)
    
    @patch('src.core.adapters.soap.soap_adapter.ad_manager')
    def test_download_report_not_ready(self, mock_ad_manager):
        """Test downloading report that's not ready."""
        # Mock setup
        mock_client = Mock()
        mock_service = Mock()
        mock_client.GetService.return_value = mock_service
        mock_ad_manager.AdManagerClient.LoadFromStorage.return_value = mock_client
        
        # Mock incomplete report
        mock_service.getReportJob.return_value = {
            'id': 12345,
            'reportJobStatus': 'IN_PROGRESS'
        }
        
        # Should raise ReportNotReadyError
        adapter = SOAPAdapter(self.config)
        with self.assertRaises(ReportNotReadyError):
            adapter.download_report('12345')
    
    @patch('src.core.adapters.soap.soap_adapter.ad_manager')
    def test_test_connection_success(self, mock_ad_manager):
        """Test successful connection test."""
        # Mock setup
        mock_client = Mock()
        mock_service = Mock()
        mock_client.GetService.return_value = mock_service
        mock_ad_manager.AdManagerClient.LoadFromStorage.return_value = mock_client
        
        # Mock network response
        mock_service.getCurrentNetwork.return_value = {
            'id': 123,
            'networkCode': '123456789',
            'displayName': 'Test Network'
        }
        
        # Test connection
        adapter = SOAPAdapter(self.config)
        result = adapter.test_connection()
        
        self.assertTrue(result)
        mock_service.getCurrentNetwork.assert_called_once()
    
    @patch('src.core.adapters.soap.soap_adapter.ad_manager')
    def test_get_dimensions(self, mock_ad_manager):
        """Test getting available dimensions."""
        adapter = SOAPAdapter(self.config)
        dimensions = adapter.get_dimensions()
        
        # Should return predefined list
        self.assertIn('DATE', dimensions)
        self.assertIn('AD_UNIT_NAME', dimensions)
        self.assertIn('ADVERTISER_NAME', dimensions)
        self.assertTrue(len(dimensions) > 10)
    
    @patch('src.core.adapters.soap.soap_adapter.ad_manager')
    def test_get_metrics(self, mock_ad_manager):
        """Test getting available metrics."""
        adapter = SOAPAdapter(self.config)
        metrics = adapter.get_metrics()
        
        # Should return predefined list
        self.assertIn('AD_SERVER_IMPRESSIONS', metrics)
        self.assertIn('AD_SERVER_CLICKS', metrics)
        self.assertIn('TOTAL_REVENUE', metrics)
        self.assertIn('AD_SERVER_REVENUE', metrics)
        self.assertTrue(len(metrics) > 10)
    
    @patch('src.core.adapters.soap.soap_adapter.ad_manager')
    def test_format_date(self, mock_ad_manager):
        """Test date formatting for SOAP."""
        adapter = SOAPAdapter(self.config)
        
        # Test valid date
        date_obj = adapter._format_date('2024-01-15')
        self.assertEqual(date_obj['year'], 2024)
        self.assertEqual(date_obj['month'], 1)
        self.assertEqual(date_obj['day'], 15)
        
        # Test None
        self.assertIsNone(adapter._format_date(None))
    
    @patch('src.core.adapters.soap.soap_adapter.ad_manager')
    def test_datetime_to_string(self, mock_ad_manager):
        """Test datetime conversion from SOAP format."""
        adapter = SOAPAdapter(self.config)
        
        # Test valid datetime
        datetime_obj = {
            'date': {
                'year': 2024,
                'month': 1,
                'day': 15
            }
        }
        date_str = adapter._datetime_to_string(datetime_obj)
        self.assertEqual(date_str, '2024-01-15')
        
        # Test None
        self.assertIsNone(adapter._datetime_to_string(None))


if __name__ == '__main__':
    unittest.main()