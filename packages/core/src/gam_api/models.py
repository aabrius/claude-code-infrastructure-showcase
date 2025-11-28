"""
Data models for Google Ad Manager API.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from enum import Enum


class ReportType(str, Enum):
    """Report type enumeration."""
    DELIVERY = "delivery"
    INVENTORY = "inventory"
    SALES = "sales" 
    REACH = "reach"
    PROGRAMMATIC = "programmatic"


class DateRangeType(str, Enum):
    """Date range type enumeration."""
    LAST_WEEK = "LAST_WEEK"
    LAST_MONTH = "LAST_MONTH"
    CUSTOM = "CUSTOM"
    LAST_N_DAYS = "LAST_N_DAYS"


class DateRange:
    """Date range model."""
    
    def __init__(self, start_date: str = None, end_date: str = None, date_range_type: DateRangeType = None):
        self.start_date = start_date
        self.end_date = end_date
        self.date_range_type = date_range_type
    
    @classmethod
    def last_n_days(cls, days: int) -> 'DateRange':
        """Create a date range for the last N days."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        return cls(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            date_range_type=DateRangeType.LAST_N_DAYS
        )


class ReportDefinition:
    """Report definition model."""
    
    def __init__(self, name: str, dimensions: List[str] = None, metrics: List[str] = None,
                 date_range: DateRange = None, **kwargs):
        self.name = name
        self.dimensions = dimensions or []
        self.metrics = metrics or []
        self.date_range = date_range
        self.filters = kwargs.get('filters', [])


class ReportStatus(str, Enum):
    """Report status enumeration."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Report:
    """Report model."""
    
    def __init__(self, id: str, name: str, status: ReportStatus = ReportStatus.PENDING, **kwargs):
        self.id = id
        self.name = name
        self.status = status
        self.data = kwargs.get('data', [])
        self.created_at = kwargs.get('created_at')
        self.completed_at = kwargs.get('completed_at')


class ReportResult:
    """Report result model."""
    
    def __init__(self, data: List[Dict] = None, **kwargs):
        self.data = data or []
        self.total_rows = kwargs.get('total_rows', len(self.data))
        self.headers = kwargs.get('headers', [])
        

class ExportFormat(str, Enum):
    """Export format enumeration."""
    JSON = "json"
    CSV = "csv"
    XLSX = "xlsx"


class Dimension:
    """Dimension model."""
    DATE = "DATE"
    AD_UNIT_NAME = "AD_UNIT_NAME"
    ADVERTISER_NAME = "ADVERTISER_NAME"


class Metric:
    """Metric model."""
    IMPRESSIONS = "IMPRESSIONS"
    CLICKS = "CLICKS"
    CTR = "CTR"


class QuickReportConfig:
    """Quick report configuration model."""
    
    def __init__(self, report_type: str, dimensions: List[str] = None, metrics: List[str] = None, **kwargs):
        self.report_type = report_type
        self.dimensions = dimensions or []
        self.metrics = metrics or []
        self.description = kwargs.get('description', '')