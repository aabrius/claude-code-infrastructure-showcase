"""
REST adapter implementation for Google Ad Manager API.

This module provides a REST API adapter that implements the APIAdapter interface
with advanced features like streaming, caching, retry logic, and circuit breaker patterns.
"""

import logging
import time
import threading
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import asyncio
import aiohttp
from google.auth.transport.requests import AuthorizedSession

from ..base import APIAdapter
from ...models import (
    Report, ReportDefinition, ReportStatus, ReportType,
    DateRange, Dimension, Metric
)
from ...exceptions import (
    APIError, InvalidRequestError, QuotaExceededError,
    ReportError, ReportTimeoutError, ValidationError,
    AuthenticationError
)
from ...auth import AuthManager, get_auth_manager

logger = logging.getLogger(__name__)

# GAM REST API v1 base URL
API_BASE_URL = "https://admanager.googleapis.com/v1"


# ============================================================================
# Enums and Constants
# ============================================================================

class Visibility:
    """Report visibility options."""
    UNSPECIFIED = "VISIBILITY_UNSPECIFIED"
    HIDDEN = "HIDDEN"
    DRAFT = "DRAFT"
    SAVED = "SAVED"


class Recurrence:
    """Schedule recurrence options."""
    UNSPECIFIED = "RECURRENCE_UNSPECIFIED"
    ONE_TIME = "ONE_TIME"
    REPEATING = "REPEATING"


class Frequency:
    """Schedule frequency options (for REPEATING recurrence)."""
    UNSPECIFIED = "FREQUENCY_UNSPECIFIED"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


class DayOfWeek:
    """Days of the week for weekly scheduling."""
    UNSPECIFIED = "DAY_OF_WEEK_UNSPECIFIED"
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


class TimeZoneSource:
    """Time zone source options."""
    UNSPECIFIED = "TIME_ZONE_SOURCE_UNSPECIFIED"
    NETWORK = "NETWORK"
    CUSTOM = "CUSTOM"


class ReportType:
    """Report type options."""
    UNSPECIFIED = "REPORT_TYPE_UNSPECIFIED"
    HISTORICAL = "HISTORICAL"
    REACH = "REACH"
    AD_SPEED = "AD_SPEED"


class TimePeriodColumn:
    """Time period column options for comparison."""
    UNSPECIFIED = "TIME_PERIOD_COLUMN_UNSPECIFIED"
    DATE = "TIME_PERIOD_COLUMN_DATE"
    WEEK = "TIME_PERIOD_COLUMN_WEEK"
    MONTH = "TIME_PERIOD_COLUMN_MONTH"


# ============================================================================
# Builder Classes
# ============================================================================

class ScheduleOptionsBuilder:
    """Builder for ScheduleOptions configuration."""

    def __init__(self):
        self._options = {}

    def one_time(self, start_time: str) -> 'ScheduleOptionsBuilder':
        """Configure one-time execution."""
        self._options['recurrence'] = Recurrence.ONE_TIME
        self._options['startTime'] = start_time
        return self

    def repeating(self, start_time: str, frequency: str) -> 'ScheduleOptionsBuilder':
        """Configure repeating execution."""
        self._options['recurrence'] = Recurrence.REPEATING
        self._options['startTime'] = start_time
        self._options['frequency'] = frequency
        return self

    def daily(self, start_time: str) -> 'ScheduleOptionsBuilder':
        """Configure daily execution."""
        return self.repeating(start_time, Frequency.DAILY)

    def weekly(self, start_time: str, day_of_week: str) -> 'ScheduleOptionsBuilder':
        """Configure weekly execution on specified day."""
        self.repeating(start_time, Frequency.WEEKLY)
        self._options['dayOfWeek'] = day_of_week
        return self

    def monthly(self, start_time: str, day_of_month: int) -> 'ScheduleOptionsBuilder':
        """Configure monthly execution on specified day (1-31)."""
        if not 1 <= day_of_month <= 31:
            raise ValueError("day_of_month must be between 1 and 31")
        self.repeating(start_time, Frequency.MONTHLY)
        self._options['dayOfMonth'] = day_of_month
        return self

    def end_time(self, end_time: str) -> 'ScheduleOptionsBuilder':
        """Set schedule end time (RFC3339 format)."""
        self._options['endTime'] = end_time
        return self

    def build(self) -> Dict[str, Any]:
        """Build the schedule options dictionary."""
        return self._options.copy()


class SortBuilder:
    """Builder for report sort configuration."""

    def __init__(self):
        self._sorts = []

    def by_dimension(self, dimension: str, descending: bool = False) -> 'SortBuilder':
        """Add sort by dimension."""
        self._sorts.append({
            'field': {'dimension': dimension},
            'descending': descending
        })
        return self

    def by_metric(self, metric: str, descending: bool = False) -> 'SortBuilder':
        """Add sort by metric."""
        self._sorts.append({
            'field': {'metric': metric},
            'descending': descending
        })
        return self

    def build(self) -> List[Dict[str, Any]]:
        """Build the sort configuration list."""
        return self._sorts.copy()


class ReportDefinitionBuilder:
    """Builder for comprehensive report definitions."""

    def __init__(self):
        self._definition = {
            'reportType': ReportType.HISTORICAL
        }
        self._report = {}

    def display_name(self, name: str) -> 'ReportDefinitionBuilder':
        """Set report display name."""
        self._report['displayName'] = name
        return self

    def visibility(self, visibility: str) -> 'ReportDefinitionBuilder':
        """Set report visibility (HIDDEN, DRAFT, SAVED)."""
        self._report['visibility'] = visibility
        return self

    def locale(self, locale: str) -> 'ReportDefinitionBuilder':
        """Set report locale (e.g., 'en-US')."""
        self._report['locale'] = locale
        return self

    def report_type(self, report_type: str) -> 'ReportDefinitionBuilder':
        """Set report type (HISTORICAL, REACH, AD_SPEED)."""
        self._definition['reportType'] = report_type
        return self

    def dimensions(self, dimensions: List[str]) -> 'ReportDefinitionBuilder':
        """Set report dimensions."""
        self._definition['dimensions'] = dimensions
        return self

    def metrics(self, metrics: List[str]) -> 'ReportDefinitionBuilder':
        """Set report metrics."""
        self._definition['metrics'] = metrics
        return self

    def date_range_fixed(self, start_date: Dict, end_date: Dict) -> 'ReportDefinitionBuilder':
        """Set fixed date range."""
        self._definition['dateRange'] = {
            'fixed': {
                'startDate': start_date,
                'endDate': end_date
            }
        }
        return self

    def date_range_relative(self, preset: str) -> 'ReportDefinitionBuilder':
        """Set relative date range (e.g., 'LAST_7_DAYS')."""
        self._definition['dateRange'] = {
            'relative': {'relativePreset': preset}
        }
        return self

    def compare_date_range_fixed(self, start_date: Dict, end_date: Dict) -> 'ReportDefinitionBuilder':
        """Set comparison date range (fixed)."""
        self._definition['compareDateRange'] = {
            'fixed': {
                'startDate': start_date,
                'endDate': end_date
            }
        }
        return self

    def compare_date_range_relative(self, preset: str) -> 'ReportDefinitionBuilder':
        """Set comparison date range (relative)."""
        self._definition['compareDateRange'] = {
            'relative': {'relativePreset': preset}
        }
        return self

    def time_zone(self, time_zone: str, source: str = None) -> 'ReportDefinitionBuilder':
        """Set time zone (IANA identifier)."""
        self._definition['timeZone'] = time_zone
        if source:
            self._definition['timeZoneSource'] = source
        return self

    def currency_code(self, currency: str) -> 'ReportDefinitionBuilder':
        """Set currency code (ISO 4217)."""
        self._definition['currencyCode'] = currency
        return self

    def time_period_column(self, column: str) -> 'ReportDefinitionBuilder':
        """Set time period column for comparison."""
        self._definition['timePeriodColumn'] = column
        return self

    def custom_dimension_keys(self, key_ids: List[str]) -> 'ReportDefinitionBuilder':
        """Set custom targeting key IDs for KEY_VALUES dimension."""
        self._definition['customDimensionKeyIds'] = key_ids
        return self

    def line_item_custom_fields(self, field_ids: List[str]) -> 'ReportDefinitionBuilder':
        """Set custom field IDs for line items."""
        self._definition['lineItemCustomFieldIds'] = field_ids
        return self

    def order_custom_fields(self, field_ids: List[str]) -> 'ReportDefinitionBuilder':
        """Set custom field IDs for orders."""
        self._definition['orderCustomFieldIds'] = field_ids
        return self

    def creative_custom_fields(self, field_ids: List[str]) -> 'ReportDefinitionBuilder':
        """Set custom field IDs for creatives."""
        self._definition['creativeCustomFieldIds'] = field_ids
        return self

    def sorts(self, sorts: List[Dict]) -> 'ReportDefinitionBuilder':
        """Set sort configuration."""
        self._definition['sorts'] = sorts
        return self

    def add_filter_string(self, values: List[str], match_type: str = 'EXACT') -> 'ReportDefinitionBuilder':
        """Add string filter."""
        if 'filters' not in self._definition:
            self._definition['filters'] = []
        self._definition['filters'].append({
            'stringValue': {
                'values': values,
                'matchType': match_type
            }
        })
        return self

    def add_filter_int(self, values: List[str], operation: str = 'EQUALS') -> 'ReportDefinitionBuilder':
        """Add integer filter."""
        if 'filters' not in self._definition:
            self._definition['filters'] = []
        self._definition['filters'].append({
            'intValue': {
                'values': values,
                'operation': operation
            }
        })
        return self

    def schedule(self, schedule_options: Dict) -> 'ReportDefinitionBuilder':
        """Set schedule options."""
        self._report['scheduleOptions'] = schedule_options
        return self

    def build(self) -> Dict[str, Any]:
        """Build the complete report request."""
        result = self._report.copy()
        result['reportDefinition'] = self._definition.copy()
        return result


# ============================================================================
# Response Parsers
# ============================================================================

class MetricValueParser:
    """Parser for metric values from fetchRows response."""

    @staticmethod
    def parse_value(value_obj: Dict) -> Any:
        """Parse a single metric value object."""
        if 'integerValue' in value_obj:
            return int(value_obj['integerValue'])
        elif 'decimalValue' in value_obj:
            return float(value_obj['decimalValue'])
        elif 'micros' in value_obj:
            # Convert micros to standard currency (divide by 1,000,000)
            return float(value_obj['micros']) / 1_000_000
        elif 'stringValue' in value_obj:
            return value_obj['stringValue']
        elif 'boolValue' in value_obj:
            return value_obj['boolValue']
        elif 'percentageChange' in value_obj:
            return {'type': 'percentage_change', 'value': float(value_obj['percentageChange'])}
        elif 'absoluteChange' in value_obj:
            return {'type': 'absolute_change', 'value': float(value_obj['absoluteChange'])}
        return value_obj

    @staticmethod
    def parse_metric_value_group(group: Dict) -> Dict[str, Any]:
        """
        Parse a MetricValueGroup object.

        Returns dict with:
        - primary: Primary date range values
        - comparison: Comparison date range values (if compareDateRange specified)
        - primary_change: Change from baseline for primary values
        - comparison_change: Change from baseline for comparison values
        - flags: Flag metric values
        """
        result = {}

        if 'primaryValues' in group:
            result['primary'] = {
                k: MetricValueParser.parse_value(v)
                for k, v in group['primaryValues'].items()
            }

        if 'comparisonValues' in group:
            result['comparison'] = {
                k: MetricValueParser.parse_value(v)
                for k, v in group['comparisonValues'].items()
            }

        if 'compareToBaselinePrimaryValues' in group:
            result['primary_change'] = {
                k: MetricValueParser.parse_value(v)
                for k, v in group['compareToBaselinePrimaryValues'].items()
            }

        if 'compareToBaselineComparisonValues' in group:
            result['comparison_change'] = {
                k: MetricValueParser.parse_value(v)
                for k, v in group['compareToBaselineComparisonValues'].items()
            }

        if 'flagValues' in group:
            result['flags'] = {
                k: MetricValueParser.parse_value(v)
                for k, v in group['flagValues'].items()
            }

        return result

    @staticmethod
    def parse_row(row: Dict) -> Dict[str, Any]:
        """
        Parse a complete report row.

        Returns dict with:
        - dimensions: Dimension values
        - metrics: List of parsed MetricValueGroups
        """
        result = {'dimensions': {}, 'metrics': []}

        # Parse dimension values
        if 'dimensionValues' in row:
            for dim_name, dim_value in row['dimensionValues'].items():
                result['dimensions'][dim_name] = MetricValueParser.parse_value(dim_value)

        # Parse metric value groups
        if 'metricValueGroups' in row:
            for group in row['metricValueGroups']:
                result['metrics'].append(
                    MetricValueParser.parse_metric_value_group(group)
                )

        return result


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""
    pass


class CircuitBreaker:
    """Thread-safe circuit breaker implementation for resilience."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._lock = threading.RLock()  # Re-entrant lock for thread safety
        self._failure_count = 0
        self._last_failure_time = None
        self._state = 'closed'  # closed, open, half_open
    
    @property
    def state(self) -> str:
        """Get current circuit breaker state (thread-safe)."""
        with self._lock:
            return self._state
    
    @property 
    def failure_count(self) -> int:
        """Get current failure count (thread-safe)."""
        with self._lock:
            return self._failure_count
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection (thread-safe)."""
        with self._lock:
            current_time = time.time()
            
            if self._state == 'open':
                if self._last_failure_time and (current_time - self._last_failure_time > self.recovery_timeout):
                    self._state = 'half_open'
                    logger.debug("Circuit breaker transitioning to half-open state")
                else:
                    raise CircuitBreakerError(
                        f"Circuit breaker is open. Retry after {self.recovery_timeout - (current_time - (self._last_failure_time or 0)):.1f}s"
                    )
        
        try:
            result = func(*args, **kwargs)
            
            # Success - reset failure count if we were in half-open state
            with self._lock:
                if self._state == 'half_open':
                    self._state = 'closed'
                    self._failure_count = 0
                    logger.info("Circuit breaker closed after successful recovery")
                    
            return result
            
        except Exception as e:
            with self._lock:
                self._failure_count += 1
                self._last_failure_time = current_time
                
                if self._failure_count >= self.failure_threshold:
                    if self._state != 'open':
                        self._state = 'open'
                        logger.warning(f"Circuit breaker opened after {self._failure_count} failures")
            
            raise e
    
    def reset(self):
        """Reset circuit breaker to closed state (thread-safe)."""
        with self._lock:
            self._state = 'closed'
            self._failure_count = 0
            self._last_failure_time = None
            logger.info("Circuit breaker reset to closed state")


class RESTAdapter(APIAdapter):
    """
    REST API adapter for Google Ad Manager.
    
    Provides REST API v1 implementation with advanced features:
    - Automatic pagination handling
    - Response streaming for large datasets
    - Intelligent caching of metadata
    - Circuit breaker pattern for resilience
    - Exponential backoff retry logic
    - Rate limiting awareness
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize REST adapter.
        
        Args:
            config: Configuration dictionary containing authentication and API settings.
        """
        super().__init__(config)
        self.auth_manager = get_auth_manager()
        self._session: Optional[AuthorizedSession] = None
        self._async_session: Optional[aiohttp.ClientSession] = None
        
        # Circuit breaker for resilience
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)
        
        # Cache for metadata (dimensions, metrics)
        self._metadata_cache: Dict[str, Any] = {}
        self._cache_expiry = timedelta(hours=1)
        self._cache_timestamps: Dict[str, datetime] = {}
        
        logger.info("RESTAdapter initialized")
    
    @property
    def session(self) -> AuthorizedSession:
        """Get or create authorized session."""
        if self._session is None:
            credentials = self.auth_manager.get_oauth2_credentials()
            self._session = AuthorizedSession(credentials)
            logger.debug("Created new authorized session")
        return self._session
    
    @property
    def network_code(self) -> str:
        """Get network code from auth manager."""
        return self.auth_manager.network_code
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid."""
        if cache_key not in self._cache_timestamps:
            return False
        return datetime.now() - self._cache_timestamps[cache_key] < self._cache_expiry
    
    def _cache_set(self, cache_key: str, value: Any) -> None:
        """Set cache entry with timestamp."""
        self._metadata_cache[cache_key] = value
        self._cache_timestamps[cache_key] = datetime.now()
    
    def _cache_get(self, cache_key: str) -> Optional[Any]:
        """Get cache entry if valid."""
        if self._is_cache_valid(cache_key):
            return self._metadata_cache.get(cache_key)
        return None
    
    def _sanitize_error_message(self, message: str) -> str:
        """
        Sanitize error message to prevent credential exposure.
        
        Args:
            message: Raw error message
            
        Returns:
            Sanitized error message
        """
        import re
        
        # Remove potential OAuth tokens
        message = re.sub(r'Bearer\s+[A-Za-z0-9\-_.~+/]+=*', 'Bearer [REDACTED]', message)
        
        # Remove potential API keys
        message = re.sub(r'key=[A-Za-z0-9\-_]{20,}', 'key=[REDACTED]', message)
        
        # Remove potential client secrets
        message = re.sub(r'client_secret=[A-Za-z0-9\-_]{20,}', 'client_secret=[REDACTED]', message)
        
        # Remove potential refresh tokens  
        message = re.sub(r'refresh_token=[A-Za-z0-9\-_.~+/]+=*', 'refresh_token=[REDACTED]', message)
        
        return message
    
    def _validate_report_id(self, report_id: str) -> str:
        """
        Validate and sanitize report ID to prevent injection attacks.
        
        Args:
            report_id: Report ID to validate
            
        Returns:
            Validated report ID
            
        Raises:
            ValidationError: If report ID is invalid
        """
        if not report_id:
            raise ValidationError("Report ID cannot be empty")
        
        # Allow alphanumeric, hyphens, underscores, slashes for resource names
        import re
        if not re.match(r'^[a-zA-Z0-9\-_/]+$', report_id):
            raise ValidationError(f"Invalid report ID format: {report_id}")
        
        # Check for path traversal attempts
        if '..' in report_id or report_id.startswith('/') and not report_id.startswith('networks/'):
            raise ValidationError(f"Invalid report ID: {report_id}")
        
        return report_id
    
    def _handle_rest_response(self, response) -> Dict[str, Any]:
        """
        Handle REST API response with comprehensive error mapping and credential protection.
        
        Args:
            response: requests Response object
            
        Returns:
            Parsed JSON response
            
        Raises:
            Various APIError subclasses based on response
        """
        try:
            response.raise_for_status()
            return response.json()
        except Exception as e:
            error_data = {}
            try:
                error_data = response.json()
            except:
                pass
            
            status_code = response.status_code
            raw_error_message = error_data.get('error', {}).get('message', str(e))
            error_code = error_data.get('error', {}).get('status', '')
            
            # Sanitize error message to prevent credential exposure
            error_message = self._sanitize_error_message(raw_error_message)
            
            # Map HTTP status codes to specific exceptions
            if status_code == 400:
                raise InvalidRequestError(error_message, status_code, error_code)
            elif status_code == 401:
                raise AuthenticationError("Authentication failed. Please check credentials.", status_code, error_code)
            elif status_code == 404:
                raise InvalidRequestError(f"Resource not found: {error_message}", status_code, error_code)
            elif status_code == 429:
                retry_after = response.headers.get('Retry-After', '60')
                raise QuotaExceededError(
                    f"API quota exceeded. Retry after {retry_after} seconds.", 
                    status_code, error_code, retry_after=int(retry_after)
                )
            elif status_code >= 500:
                raise APIError(f"Server error: {error_message}", status_code, error_code)
            else:
                raise APIError(f"API request failed: {error_message}", status_code, error_code)
    
    def _retry_with_backoff(self, func, max_retries: int = 3, base_delay: float = 1.0):
        """
        Execute function with exponential backoff retry logic.
        
        Args:
            func: Function to execute
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds for exponential backoff
            
        Returns:
            Function result
            
        Raises:
            Last exception if all retries fail
        """
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return self.circuit_breaker.call(func)
            except (QuotaExceededError, APIError) as e:
                last_exception = e
                if attempt == max_retries:
                    break
                
                # Calculate delay with exponential backoff
                delay = base_delay * (2 ** attempt)
                
                # For quota exceeded, respect the Retry-After header
                if isinstance(e, QuotaExceededError) and hasattr(e, 'retry_after'):
                    delay = max(delay, e.retry_after)
                
                logger.warning(f"API call failed (attempt {attempt + 1}/{max_retries + 1}), "
                             f"retrying in {delay} seconds: {str(e)}")
                time.sleep(delay)
            except CircuitBreakerError as e:
                logger.error(f"Circuit breaker is open: {str(e)}")
                raise e
        
        raise last_exception
    
    # Report Operations Implementation
    
    def get_reports(self, **filters) -> List[Dict[str, Any]]:
        """
        Get list of reports with optional filtering and automatic pagination.
        
        Args:
            **filters: Optional filters (page_size, page_token, status)
            
        Returns:
            List of report dictionaries
        """
        def _get_reports_page():
            url = f"{API_BASE_URL}/networks/{self.network_code}/reports"
            params = {}
            
            # Handle pagination
            if 'page_size' in filters:
                params['pageSize'] = filters['page_size']
            if 'page_token' in filters:
                params['pageToken'] = filters['page_token']
                
            response = self.session.get(url, params=params)
            return self._handle_rest_response(response)
        
        result = self._retry_with_backoff(_get_reports_page)
        
        # Auto-paginate if no specific page_token provided
        if 'page_token' not in filters:
            reports = result.get('reports', [])
            next_page_token = result.get('nextPageToken')
            
            while next_page_token and len(reports) < 1000:  # Safety limit
                filters['page_token'] = next_page_token
                next_result = self._retry_with_backoff(_get_reports_page)
                reports.extend(next_result.get('reports', []))
                next_page_token = next_result.get('nextPageToken')
            
            return reports
        
        return result.get('reports', [])
    
    def create_report(self, report_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new report job with validation.
        
        Args:
            report_definition: Report configuration including dimensions, metrics, filters
            
        Returns:
            Report job information including ID
        """
        def _create_report():
            url = f"{API_BASE_URL}/networks/{self.network_code}/reports"
            
            # Validate required fields
            if 'displayName' not in report_definition:
                raise ValidationError("Report definition must include 'displayName'")
            if 'reportDefinition' not in report_definition:
                raise ValidationError("Report definition must include 'reportDefinition'")
            
            response = self.session.post(url, json=report_definition)
            return self._handle_rest_response(response)
        
        result = self._retry_with_backoff(_create_report)
        logger.info(f"Created report: {result.get('reportId')} - {result.get('displayName')}")
        return result

    def run_report(self, report_name: str) -> Dict[str, Any]:
        """
        Run an existing report asynchronously.

        This method triggers the execution of a previously created report.
        Returns an Operation object that can be polled using check_operation_status().

        Args:
            report_name: Report resource name (e.g., 'networks/{networkCode}/reports/{reportId}')
                        or just the report ID

        Returns:
            Operation object with 'name' field for tracking progress

        Example:
            >>> operation = adapter.run_report('networks/12345/reports/67890')
            >>> while True:
            ...     status = adapter.check_operation_status(operation['name'])
            ...     if status.get('done'):
            ...         break
            ...     time.sleep(5)
        """
        # Handle both report ID and full resource name
        if not report_name.startswith('networks/'):
            report_name = f"networks/{self.network_code}/reports/{report_name}"

        # Validate report name
        validated_name = self._validate_report_id(report_name)

        def _run_report():
            url = f"{API_BASE_URL}/{validated_name}:run"
            response = self.session.post(url)
            return self._handle_rest_response(response)

        result = self._retry_with_backoff(_run_report)
        logger.info(f"Started report execution: {result.get('name')}")
        return result

    def update_report(self, report_id: str, update_body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing report.

        Args:
            report_id: Report ID or full resource name
            update_body: Fields to update (displayName, reportDefinition, etc.)

        Returns:
            Updated report data

        Example:
            >>> adapter.update_report('12345', {'displayName': 'New Name'})
        """
        # Handle both report ID and full resource name
        if not report_id.startswith('networks/'):
            report_id = f"networks/{self.network_code}/reports/{report_id}"

        # Validate report ID
        validated_id = self._validate_report_id(report_id)

        def _update_report():
            url = f"{API_BASE_URL}/{validated_id}"
            response = self.session.patch(url, json=update_body)
            return self._handle_rest_response(response)

        result = self._retry_with_backoff(_update_report)
        logger.info(f"Updated report: {validated_id}")
        return result

    def delete_report(self, report_id: str) -> bool:
        """
        Delete a report.

        Args:
            report_id: Report ID or full resource name

        Returns:
            True if deletion was successful
        """
        # Handle both report ID and full resource name
        if not report_id.startswith('networks/'):
            report_id = f"networks/{self.network_code}/reports/{report_id}"

        # Validate report ID
        validated_id = self._validate_report_id(report_id)

        def _delete_report():
            url = f"{API_BASE_URL}/{validated_id}"
            response = self.session.delete(url)
            self._handle_rest_response(response)
            return True

        result = self._retry_with_backoff(_delete_report)
        logger.info(f"Deleted report: {validated_id}")
        return result

    def get_report(self, report_id: str) -> Dict[str, Any]:
        """
        Get a specific report by ID.

        Args:
            report_id: Report ID or full resource name

        Returns:
            Report data
        """
        # Handle both report ID and full resource name
        if not report_id.startswith('networks/'):
            report_id = f"networks/{self.network_code}/reports/{report_id}"

        # Validate report ID
        validated_id = self._validate_report_id(report_id)

        def _get_report():
            url = f"{API_BASE_URL}/{validated_id}"
            response = self.session.get(url)
            return self._handle_rest_response(response)

        return self._retry_with_backoff(_get_report)

    def get_report_status(self, report_id: str) -> str:
        """
        Get current status of a report job.
        
        Args:
            report_id: Report job ID or resource name
            
        Returns:
            Status string ('COMPLETED', 'IN_PROGRESS', 'FAILED', etc.)
        """
        # Validate and sanitize report ID
        validated_report_id = self._validate_report_id(report_id)
        
        def _get_status():
            # Handle both report ID and full resource name
            if validated_report_id.startswith('networks/'):
                url = f"{API_BASE_URL}/{validated_report_id}"
            else:
                url = f"{API_BASE_URL}/networks/{self.network_code}/reports/{validated_report_id}"
            
            response = self.session.get(url)
            data = self._handle_rest_response(response)
            return data.get('status', 'UNKNOWN')
        
        return self._retry_with_backoff(_get_status)
    
    def download_report(self, report_id: str, format: str = 'CSV', max_memory_mb: int = 100) -> Union[str, bytes]:
        """
        Download report results with streaming support for large datasets.
        
        Args:
            report_id: Report job ID or resource name
            format: Output format (CSV, TSV, JSON)
            max_memory_mb: Maximum memory usage in MB before switching to file streaming
            
        Returns:
            Report data as string or bytes
        """
        # Validate inputs
        validated_report_id = self._validate_report_id(report_id)
        
        if format.upper() not in ['CSV', 'TSV', 'JSON']:
            raise ValidationError(f"Unsupported format: {format}. Supported formats: CSV, TSV, JSON")
        
        if max_memory_mb <= 0 or max_memory_mb > 1000:
            raise ValidationError(f"Invalid memory limit: {max_memory_mb}MB. Must be between 1-1000MB")
        
        # First check if report is ready
        status = self.get_report_status(validated_report_id)
        if status != 'COMPLETED':
            if status == 'FAILED':
                raise ReportError(f"Report {validated_report_id} failed to generate")
            else:
                raise ReportTimeoutError(f"Report {validated_report_id} is not ready (status: {status})")
        
        def _download_report():
            # Handle both report ID and full resource name  
            if validated_report_id.startswith('networks/'):
                base_url = f"{API_BASE_URL}/{validated_report_id}"
            else:
                base_url = f"{API_BASE_URL}/networks/{self.network_code}/reports/{validated_report_id}"
            
            url = f"{base_url}:fetchRows"
            
            # Use streaming approach for memory efficiency
            return self._stream_download_data(url, format, max_memory_mb)
        
        return self._retry_with_backoff(_download_report)
    
    def _stream_download_data(self, url: str, format: str, max_memory_mb: int) -> str:
        """
        Stream download data with memory management.
        
        Args:
            url: API endpoint URL
            format: Output format
            max_memory_mb: Memory limit before switching to temp file
            
        Returns:
            Report data as string
        """
        import tempfile
        import os
        import sys
        
        data_chunks = []
        current_memory_mb = 0
        temp_file = None
        temp_file_path = None
        page_token = None
        headers = None
        first_page = True
        
        try:
            while True:
                params = {'pageSize': 1000}
                if page_token:
                    params['pageToken'] = page_token
                
                response = self.session.get(url, params=params)
                data = self._handle_rest_response(response)
                
                rows = data.get('rows', [])
                if not rows:
                    break
                
                # Extract headers from first page
                if first_page and rows:
                    headers = list(rows[0].keys())
                    first_page = False
                
                # Estimate memory usage (rough calculation)
                chunk_size_mb = sys.getsizeof(rows) / (1024 * 1024)
                current_memory_mb += chunk_size_mb
                
                # If exceeding memory limit, switch to temp file
                if current_memory_mb > max_memory_mb and temp_file is None:
                    logger.info(f"Switching to file streaming due to memory limit ({max_memory_mb}MB)")
                    temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=f'.{format.lower()}')
                    temp_file_path = temp_file.name
                    
                    # Write existing data to file first
                    if data_chunks:
                        self._write_chunks_to_file(temp_file, data_chunks, headers, format, is_first=True)
                        data_chunks.clear()  # Free memory
                    
                    # Write current chunk
                    self._write_chunks_to_file(temp_file, [rows], headers, format, is_first=len(data_chunks) == 0)
                else:
                    if temp_file:
                        # Continue writing to file
                        self._write_chunks_to_file(temp_file, [rows], headers, format, is_first=False)
                    else:
                        # Keep in memory
                        data_chunks.append(rows)
                
                page_token = data.get('nextPageToken')
                if not page_token:
                    break
            
            # Return results based on storage method
            if temp_file:
                temp_file.close()
                # Read file contents and cleanup
                try:
                    with open(temp_file_path, 'r') as f:
                        result = f.read()
                    return result
                finally:
                    os.unlink(temp_file_path)
            else:
                # Format in-memory data
                return self._format_data_chunks(data_chunks, headers, format)
                
        except Exception as e:
            # Cleanup temp file on error
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
            raise e
    
    def _write_chunks_to_file(self, file, chunks: List[List[Dict]], headers: List[str], format: str, is_first: bool):
        """Write data chunks to temporary file."""
        if format.upper() == 'JSON':
            import json
            if is_first:
                file.write('[\n')
            
            for chunk in chunks:
                for i, row in enumerate(chunk):
                    if not is_first or i > 0:
                        file.write(',\n')
                    file.write(json.dumps(row, indent=2))
        else:
            delimiter = ',' if format.upper() == 'CSV' else '\t'
            
            # Write headers only once
            if is_first and headers:
                file.write(delimiter.join(headers) + '\n')
            
            # Write data rows
            for chunk in chunks:
                for row in chunk:
                    values = [str(row.get(header, '')) for header in headers]
                    file.write(delimiter.join(values) + '\n')
    
    def _format_data_chunks(self, chunks: List[List[Dict]], headers: List[str], format: str) -> str:
        """Format in-memory data chunks."""
        if not chunks:
            return ""
        
        # Flatten chunks
        all_data = []
        for chunk in chunks:
            all_data.extend(chunk)
        
        if format.upper() == 'JSON':
            import json
            return json.dumps(all_data, indent=2)
        else:
            delimiter = ',' if format.upper() == 'CSV' else '\t'
            
            if not headers:
                return ""
            
            lines = [delimiter.join(headers)]
            for row in all_data:
                values = [str(row.get(header, '')) for header in headers]
                lines.append(delimiter.join(values))
            
            return '\n'.join(lines)
    
    # Line Item Operations (REST API v1 Limitations)
    
    def manage_line_items(self, operation: str, line_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Manage line items - NOT SUPPORTED in GAM REST API v1.
        
        GAM REST API v1 is primarily focused on reporting and does not support
        line item management operations (create, update, delete).
        
        Args:
            operation: Operation type ('CREATE', 'UPDATE', 'DELETE')
            line_items: List of line item configurations
            
        Raises:
            NotImplementedError: Always raised as operation is not supported
            
        Note:
            For line item operations, use the SOAP adapter which provides full
            line item management capabilities via the GAM SOAP API.
        """
        logger.warning(f"Line item operation '{operation}' not supported in REST API v1")
        raise NotImplementedError(
            f"Line item management (operation: {operation}) is not supported in GAM REST API v1.\n"
            "Available alternatives:\n"
            "1. Use SOAPAdapter for full line item management\n"
            "2. Use UnifiedAdapter which will automatically route to SOAP for line items\n"
            "3. Wait for future GAM REST API versions that may support line items"
        )
    
    def get_line_items(self, **filters) -> List[Dict[str, Any]]:
        """
        Get line items - NOT SUPPORTED in GAM REST API v1.
        
        GAM REST API v1 focuses on reporting and does not provide endpoints
        for querying line items directly.
        
        Args:
            **filters: Filter criteria (not used due to lack of support)
            
        Raises:
            NotImplementedError: Always raised as operation is not supported
            
        Note:
            For line item queries, use the SOAP adapter which provides full
            access to line item data via the GAM SOAP API.
        """
        logger.warning("Line item queries not supported in REST API v1")
        raise NotImplementedError(
            "Line item queries are not supported in GAM REST API v1.\n"
            "Available alternatives:\n"
            "1. Use SOAPAdapter.get_line_items() for direct line item access\n"
            "2. Use UnifiedAdapter which will route to SOAP automatically\n"
            "3. Generate reports with LINE_ITEM_* dimensions to get line item data"
        )
    
    # Inventory Operations (REST API v1 Limitations)
    
    def get_inventory(self, inventory_type: str, **filters) -> List[Dict[str, Any]]:
        """
        Get inventory items - NOT SUPPORTED in GAM REST API v1.
        
        GAM REST API v1 does not provide inventory management endpoints
        for ad units, placements, or other inventory items.
        
        Args:
            inventory_type: Type of inventory ('AD_UNITS', 'PLACEMENTS')
            **filters: Filter criteria (not used due to lack of support)
            
        Raises:
            NotImplementedError: Always raised as operation is not supported
            
        Note:
            For inventory operations, use the SOAP adapter which provides
            full inventory access via the GAM SOAP API.
        """
        logger.warning(f"Inventory operations for '{inventory_type}' not supported in REST API v1")
        raise NotImplementedError(
            f"Inventory operations (type: {inventory_type}) are not supported in GAM REST API v1.\n"
            "Available alternatives:\n"
            "1. Use SOAPAdapter.get_inventory() for direct inventory access\n"  
            "2. Use UnifiedAdapter which will route to SOAP automatically\n"
            "3. Generate reports with AD_UNIT_* dimensions to get inventory data"
        )
    
    def create_ad_unit(self, ad_unit_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create ad unit - NOT SUPPORTED in GAM REST API v1.
        
        GAM REST API v1 does not support creating or modifying ad units
        or other inventory items.
        
        Args:
            ad_unit_config: Ad unit configuration (not used due to lack of support)
            
        Raises:
            NotImplementedError: Always raised as operation is not supported
            
        Note:
            For ad unit creation, use the SOAP adapter which provides
            full inventory management via the GAM SOAP API.
        """
        logger.warning("Ad unit creation not supported in REST API v1")
        raise NotImplementedError(
            "Ad unit creation is not supported in GAM REST API v1.\n"
            "Available alternatives:\n"
            "1. Use SOAPAdapter.create_ad_unit() for ad unit creation\n"
            "2. Use UnifiedAdapter which will route to SOAP automatically\n"
            "3. Use GAM UI or SOAP API for inventory management"
        )
    
    # Metadata Operations with Intelligent Caching
    
    def get_dimensions(self) -> List[str]:
        """
        Get available report dimensions with caching.

        Note: GAM REST API v1 does not provide explicit metadata endpoints for dimensions.
        This method returns a comprehensive list of all supported dimensions based on
        Google Ad Manager API v202511 documentation.

        Returns:
            List of dimension names (200+ dimensions)
        """
        cache_key = 'dimensions'
        cached = self._cache_get(cache_key)
        if cached:
            return cached

        # Comprehensive list based on GAM API v202511 documentation
        # Reference: docs/api/GAM_API_V1_COMPLETE_REFERENCE.md
        dimensions = [
            # Time Dimensions
            'DATE', 'HOUR', 'DAY_OF_WEEK', 'WEEK', 'MONTH', 'YEAR',

            # Advertiser Dimensions
            'ADVERTISER_ID', 'ADVERTISER_NAME', 'ADVERTISER_DOMAIN_NAME',
            'ADVERTISER_EXTERNAL_ID', 'ADVERTISER_LABELS', 'ADVERTISER_LABEL_IDS',
            'ADVERTISER_PRIMARY_CONTACT', 'ADVERTISER_STATUS', 'ADVERTISER_STATUS_NAME',
            'ADVERTISER_TYPE', 'ADVERTISER_TYPE_NAME', 'ADVERTISER_VERTICAL',
            'ADVERTISER_CREDIT_STATUS', 'ADVERTISER_CREDIT_STATUS_NAME',

            # Ad Unit Dimensions (with hierarchy levels 1-16)
            'AD_UNIT_ID', 'AD_UNIT_NAME', 'AD_UNIT_CODE',
            'AD_UNIT_ID_ALL_LEVEL', 'AD_UNIT_NAME_ALL_LEVEL',
            'AD_UNIT_ID_TOP_LEVEL', 'AD_UNIT_NAME_TOP_LEVEL',
            'AD_UNIT_STATUS', 'AD_UNIT_STATUS_NAME',
            'AD_UNIT_REWARD_AMOUNT', 'AD_UNIT_REWARD_TYPE',
            # Levels 1-16
            'AD_UNIT_ID_LEVEL_1', 'AD_UNIT_NAME_LEVEL_1', 'AD_UNIT_CODE_LEVEL_1',
            'AD_UNIT_ID_LEVEL_2', 'AD_UNIT_NAME_LEVEL_2', 'AD_UNIT_CODE_LEVEL_2',
            'AD_UNIT_ID_LEVEL_3', 'AD_UNIT_NAME_LEVEL_3', 'AD_UNIT_CODE_LEVEL_3',
            'AD_UNIT_ID_LEVEL_4', 'AD_UNIT_NAME_LEVEL_4', 'AD_UNIT_CODE_LEVEL_4',
            'AD_UNIT_ID_LEVEL_5', 'AD_UNIT_NAME_LEVEL_5', 'AD_UNIT_CODE_LEVEL_5',

            # Line Item Dimensions
            'LINE_ITEM_ID', 'LINE_ITEM_NAME', 'LINE_ITEM_EXTERNAL_ID',
            'LINE_ITEM_AGENCY', 'LINE_ITEM_ARCHIVED', 'LINE_ITEM_LABELS',
            'LINE_ITEM_LABEL_IDS', 'LINE_ITEM_COST_TYPE', 'LINE_ITEM_COST_TYPE_NAME',
            'LINE_ITEM_COST_PER_UNIT', 'LINE_ITEM_CURRENCY_CODE',
            'LINE_ITEM_START_DATE', 'LINE_ITEM_END_DATE', 'LINE_ITEM_END_DATE_TIME',
            'LINE_ITEM_DELIVERY_RATE_TYPE', 'LINE_ITEM_DELIVERY_RATE_TYPE_NAME',
            'LINE_ITEM_DELIVERY_INDICATOR', 'LINE_ITEM_COMPUTED_STATUS',
            'LINE_ITEM_COMPUTED_STATUS_NAME', 'LINE_ITEM_OPTIMIZABLE',
            'LINE_ITEM_PRIORITY', 'LINE_ITEM_CONTRACTED_QUANTITY',
            'LINE_ITEM_LIFETIME_IMPRESSIONS', 'LINE_ITEM_LIFETIME_CLICKS',
            'LINE_ITEM_LIFETIME_VIEWABLE_IMPRESSIONS', 'LINE_ITEM_FREQUENCY_CAP',
            'LINE_ITEM_EXTERNAL_DEAL_ID', 'LINE_ITEM_MAKEGOOD', 'LINE_ITEM_PO_NUMBER',
            'LINE_ITEM_PRIMARY_GOAL_TYPE', 'LINE_ITEM_PRIMARY_GOAL_TYPE_NAME',
            'LINE_ITEM_PRIMARY_GOAL_UNIT_TYPE', 'LINE_ITEM_PRIMARY_GOAL_UNIT_TYPE_NAME',
            'LINE_ITEM_RESERVATION_STATUS', 'LINE_ITEM_RESERVATION_STATUS_NAME',
            'LINE_ITEM_CREATIVE_ROTATION_TYPE', 'LINE_ITEM_CREATIVE_ROTATION_TYPE_NAME',
            'LINE_ITEM_CREATIVE_START_DATE', 'LINE_ITEM_CREATIVE_END_DATE',
            'LINE_ITEM_ENVIRONMENT_TYPE', 'LINE_ITEM_ENVIRONMENT_TYPE_NAME',
            'LINE_ITEM_COMPANION_DELIVERY_OPTION', 'LINE_ITEM_COMPANION_DELIVERY_OPTION_NAME',
            'LINE_ITEM_LAST_MODIFIED_BY_APP', 'LINE_ITEM_NON_CPD_BOOKED_REVENUE',
            'LINE_ITEM_DISCOUNT_ABSOLUTE', 'LINE_ITEM_DISCOUNT_PERCENTAGE',
            'LINE_ITEM_PRIMARY_GOAL_UNITS_ABSOLUTE', 'LINE_ITEM_PRIMARY_GOAL_UNITS_PERCENTAGE',

            # Order Dimensions
            'ORDER_ID', 'ORDER_NAME', 'ORDER_DELIVERY_STATUS',
            'ORDER_START_DATE_TIME', 'ORDER_END_DATE_TIME', 'ORDER_EXTERNAL_ID',
            'ORDER_PO_NUMBER', 'ORDER_IS_PROGRAMMATIC', 'ORDER_AGENCY', 'ORDER_AGENCY_ID',
            'ORDER_LABELS', 'ORDER_LABEL_IDS', 'ORDER_TRAFFICKER', 'ORDER_TRAFFICKER_ID',
            'ORDER_SECONDARY_TRAFFICKERS', 'ORDER_SALESPERSON', 'ORDER_SECONDARY_SALESPEOPLE',
            'ORDER_LIFETIME_IMPRESSIONS', 'ORDER_LIFETIME_CLICKS',

            # Creative Dimensions
            'CREATIVE_ID', 'CREATIVE_NAME', 'CREATIVE_TYPE', 'CREATIVE_TYPE_NAME',
            'CREATIVE_BILLING_TYPE', 'CREATIVE_BILLING_TYPE_NAME',
            'CREATIVE_CLICK_THROUGH_URL', 'CREATIVE_THIRD_PARTY_VENDOR',
            'CREATIVE_TECHNOLOGY', 'CREATIVE_TECHNOLOGY_NAME',
            'CREATIVE_POLICIES_FILTERING', 'CREATIVE_POLICIES_FILTERING_NAME',
            'CREATIVE_SET_ROLE_TYPE', 'CREATIVE_SET_ROLE_TYPE_NAME',
            'CREATIVE_VIDEO_REDIRECT_THIRD_PARTY', 'CREATIVE_SIZE',

            # Geographic Dimensions
            'COUNTRY_ID', 'COUNTRY_NAME', 'COUNTRY_CODE',
            'CONTINENT', 'CONTINENT_NAME',
            'CITY_ID', 'CITY_NAME',
            'REGION_CODE', 'REGION_NAME', 'METRO_CODE', 'METRO_NAME',

            # Device Dimensions
            'DEVICE', 'DEVICE_NAME', 'DEVICE_CATEGORY', 'DEVICE_CATEGORY_NAME',
            'DEVICE_MANUFACTURER_ID', 'DEVICE_MANUFACTURER_NAME',
            'DEVICE_MODEL_ID', 'DEVICE_MODEL_NAME',

            # Browser Dimensions
            'BROWSER_ID', 'BROWSER_NAME', 'BROWSER_CATEGORY', 'BROWSER_CATEGORY_NAME',

            # Carrier Dimensions
            'CARRIER_ID', 'CARRIER_NAME',

            # Audience & User Dimensions
            'AGE_BRACKET', 'AGE_BRACKET_NAME', 'GENDER', 'GENDER_NAME',
            'INTEREST', 'AUDIENCE_SEGMENT_ID_TARGETED', 'AUDIENCE_SEGMENT_TARGETED',

            # Deal Dimensions
            'DEAL_ID', 'DEAL_NAME', 'DEAL_BUYER_ID', 'DEAL_BUYER_NAME',
            'EXCHANGE_BIDDING_DEAL_ID', 'EXCHANGE_BIDDING_DEAL_TYPE',
            'EXCHANGE_BIDDING_DEAL_TYPE_NAME',
            'AUCTION_PACKAGE_DEAL', 'AUCTION_PACKAGE_DEAL_ID',

            # Demand & Channel Dimensions
            'DEMAND_CHANNEL', 'DEMAND_CHANNEL_NAME',
            'DEMAND_SOURCE', 'DEMAND_SOURCE_NAME',
            'DEMAND_SUBCHANNEL', 'DEMAND_SUBCHANNEL_NAME', 'CHANNEL',

            # Bidding Dimensions
            'BIDDER_ENCRYPTED_ID', 'BIDDER_NAME', 'BID_RANGE',
            'BID_REJECTION_REASON', 'BID_REJECTION_REASON_NAME',
            'HEADER_BIDDER_INTEGRATION_TYPE', 'HEADER_BIDDER_INTEGRATION_TYPE_NAME',
            'BUYER_NETWORK_ID', 'BUYER_NETWORK_NAME',

            # Inventory Dimensions
            'INVENTORY_TYPE', 'INVENTORY_TYPE_NAME',
            'INVENTORY_FORMAT', 'INVENTORY_FORMAT_NAME',
            'AD_LOCATION', 'AD_LOCATION_NAME',
            'PLACEMENT_ID', 'PLACEMENT_NAME',

            # Content Dimensions
            'CONTENT_ID', 'CONTENT_NAME', 'CONTENT_CMS_NAME', 'CONTENT_CMS_VIDEO_ID',
            'CONTENT_MAPPING_PRESENCE', 'CONTENT_MAPPING_PRESENCE_NAME',

            # Ad Type Dimensions
            'AD_TYPE', 'AD_TYPE_NAME', 'AD_EXPERIENCES_TYPE', 'AD_EXPERIENCES_TYPE_NAME',

            # Programmatic Dimensions
            'ADX_PRODUCT', 'ADX_PRODUCT_NAME', 'BRANDING_TYPE', 'BRANDING_TYPE_NAME',
            'DYNAMIC_ALLOCATION_TYPE', 'DYNAMIC_ALLOCATION_TYPE_NAME',
            'IS_ADX_DIRECT', 'IS_FIRST_LOOK_DEAL',

            # Yield & Exchange Dimensions
            'EXCHANGE_THIRD_PARTY_COMPANY_ID', 'EXCHANGE_THIRD_PARTY_COMPANY_NAME',
            'HBT_YIELD_PARTNER_ID', 'HBT_YIELD_PARTNER_NAME',
            'CURATOR_ID', 'CURATOR_NAME', 'IS_CURATION_TARGETED',
            'YIELD_GROUP_ID', 'YIELD_GROUP_NAME',
            'YIELD_PARTNER_ID', 'YIELD_PARTNER_NAME',

            # Custom Targeting Dimensions
            'KEY_VALUES_ID', 'KEY_VALUES_NAME', 'CUSTOM_SPOT_ID', 'CUSTOM_SPOT_NAME',
            'CUSTOM_CRITERIA', 'CUSTOM_TARGETING_VALUE_ID', 'CUSTOM_TARGETING_VALUE_NAME',

            # Active View Dimensions
            'ACTIVE_VIEW_MEASUREMENT_SOURCE', 'ACTIVE_VIEW_MEASUREMENT_SOURCE_NAME',

            # Ad Technology Provider Dimensions
            'AD_TECHNOLOGY_PROVIDER_ID', 'AD_TECHNOLOGY_PROVIDER_NAME',
            'AD_TECHNOLOGY_PROVIDER_DOMAIN',

            # Child Network Dimensions (MCM)
            'CHILD_NETWORK_CODE', 'CHILD_NETWORK_ID', 'CHILD_PARTNER_NAME',

            # Privacy & Consent Dimensions
            'APP_TRACKING_TRANSPARENCY_CONSENT_STATUS',
            'APP_TRACKING_TRANSPARENCY_CONSENT_STATUS_NAME',
            'FIRST_PARTY_ID_STATUS', 'FIRST_PARTY_ID_STATUS_NAME',

            # Agency Dimensions
            'AGENCY_LEVEL_1_ID', 'AGENCY_LEVEL_1_NAME',
            'AGENCY_LEVEL_2_ID', 'AGENCY_LEVEL_2_NAME',
            'AGENCY_LEVEL_3_ID', 'AGENCY_LEVEL_3_NAME',

            # Classified Dimensions
            'CLASSIFIED_ADVERTISER_ID', 'CLASSIFIED_ADVERTISER_NAME',
            'CLASSIFIED_BRAND_ID', 'CLASSIFIED_BRAND_NAME',

            # Video Dimensions
            'VIDEO_POSITION', 'VIDEO_FALLBACK_POSITION',

            # Miscellaneous Dimensions
            'APP_VERSION', 'AUTO_REFRESHED_TRAFFIC', 'AUTO_REFRESHED_TRAFFIC_NAME',
            'DSP_SEAT_ID', 'IMPRESSION_COUNTING_METHOD', 'IMPRESSION_COUNTING_METHOD_NAME',
            'INTERACTION_TYPE', 'INTERACTION_TYPE_NAME',
            'GOOGLE_ANALYTICS_STREAM_ID', 'GOOGLE_ANALYTICS_STREAM_NAME',
            'FIRST_LOOK_PRICING_RULE_ID', 'FIRST_LOOK_PRICING_RULE_NAME',
            'OS_ID', 'OS_NAME', 'OS_VERSION',
            'SALESPERSON_ID', 'SALESPERSON_NAME',
        ]

        self._cache_set(cache_key, dimensions)
        logger.info(f"Loaded {len(dimensions)} GAM dimensions")
        return dimensions
    
    def get_metrics(self) -> List[str]:
        """
        Get available report metrics with caching.

        Note: GAM REST API v1 does not provide explicit metadata endpoints for metrics.
        This method returns a comprehensive list of all supported metrics based on
        Google Ad Manager API v202511 documentation.

        Returns:
            List of metric names (150+ metrics)
        """
        cache_key = 'metrics'
        cached = self._cache_get(cache_key)
        if cached:
            return cached

        # Comprehensive list based on GAM API v202511 documentation
        # Reference: docs/api/GAM_API_V1_COMPLETE_REFERENCE.md
        metrics = [
            # Core Ad Server Metrics
            'AD_SERVER_IMPRESSIONS', 'AD_SERVER_BEGIN_TO_RENDER_IMPRESSIONS',
            'AD_SERVER_TARGETED_IMPRESSIONS', 'AD_SERVER_CLICKS',
            'AD_SERVER_TARGETED_CLICKS', 'AD_SERVER_UNFILTERED_IMPRESSIONS',
            'AD_SERVER_UNFILTERED_CLICKS', 'AD_SERVER_CTR',

            # Revenue Metrics
            'AD_SERVER_CPM_AND_CPC_REVENUE', 'AD_SERVER_CPM_AND_CPC_REVENUE_GROSS',
            'AD_SERVER_CPD_REVENUE', 'AD_SERVER_ALL_REVENUE',
            'AD_SERVER_ALL_REVENUE_GROSS', 'AD_SERVER_WITHOUT_CPD_AVERAGE_ECPM',
            'AD_SERVER_WITH_CPD_AVERAGE_ECPM',

            # Line Item Level Allocation
            'AD_SERVER_LINE_ITEM_LEVEL_PERCENT_IMPRESSIONS',
            'AD_SERVER_LINE_ITEM_LEVEL_PERCENT_CLICKS',
            'AD_SERVER_LINE_ITEM_LEVEL_WITHOUT_CPD_PERCENT_REVENUE',
            'AD_SERVER_LINE_ITEM_LEVEL_WITH_CPD_PERCENT_REVENUE',

            # Total/Aggregated Metrics
            'TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 'TOTAL_LINE_ITEM_LEVEL_TARGETED_IMPRESSIONS',
            'TOTAL_LINE_ITEM_LEVEL_CLICKS', 'TOTAL_LINE_ITEM_LEVEL_TARGETED_CLICKS',
            'TOTAL_LINE_ITEM_LEVEL_CTR', 'TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE',
            'TOTAL_LINE_ITEM_LEVEL_ALL_REVENUE',
            'TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM',
            'TOTAL_LINE_ITEM_LEVEL_WITH_CPD_AVERAGE_ECPM',
            'TOTAL_CODE_SERVED_COUNT', 'TOTAL_AD_REQUESTS',
            'TOTAL_RESPONSES_SERVED', 'TOTAL_UNMATCHED_AD_REQUESTS',
            'TOTAL_FILL_RATE', 'TOTAL_INVENTORY_LEVEL_UNFILLED_IMPRESSIONS',

            # AdSense Metrics
            'ADSENSE_LINE_ITEM_LEVEL_IMPRESSIONS', 'ADSENSE_LINE_ITEM_LEVEL_CLICKS',
            'ADSENSE_LINE_ITEM_LEVEL_CTR', 'ADSENSE_LINE_ITEM_LEVEL_REVENUE',
            'ADSENSE_LINE_ITEM_LEVEL_AVERAGE_ECPM',
            'ADSENSE_LINE_ITEM_LEVEL_PERCENT_IMPRESSIONS',
            'ADSENSE_LINE_ITEM_LEVEL_PERCENT_CLICKS',
            'ADSENSE_LINE_ITEM_LEVEL_WITHOUT_CPD_PERCENT_REVENUE',
            'ADSENSE_LINE_ITEM_LEVEL_WITH_CPD_PERCENT_REVENUE',
            'ADSENSE_RESPONSES_SERVED',

            # Ad Exchange Metrics
            'AD_EXCHANGE_LINE_ITEM_LEVEL_IMPRESSIONS',
            'AD_EXCHANGE_LINE_ITEM_LEVEL_CLICKS',
            'AD_EXCHANGE_LINE_ITEM_LEVEL_CTR',
            'AD_EXCHANGE_LINE_ITEM_LEVEL_REVENUE',
            'AD_EXCHANGE_LINE_ITEM_LEVEL_AVERAGE_ECPM',
            'AD_EXCHANGE_LINE_ITEM_LEVEL_PERCENT_IMPRESSIONS',
            'AD_EXCHANGE_LINE_ITEM_LEVEL_PERCENT_CLICKS',
            'AD_EXCHANGE_LINE_ITEM_LEVEL_WITHOUT_CPD_PERCENT_REVENUE',
            'AD_EXCHANGE_LINE_ITEM_LEVEL_WITH_CPD_PERCENT_REVENUE',
            'AD_EXCHANGE_TOTAL_REQUESTS', 'AD_EXCHANGE_MATCH_RATE',
            'AD_EXCHANGE_COST_PER_CLICK', 'AD_EXCHANGE_TOTAL_REQUEST_CTR',
            'AD_EXCHANGE_MATCHED_REQUEST_CTR', 'AD_EXCHANGE_TOTAL_REQUEST_ECPM',
            'AD_EXCHANGE_MATCHED_REQUEST_ECPM', 'AD_EXCHANGE_LIFT_EARNINGS',
            'AD_EXCHANGE_RESPONSES_SERVED',

            # Bidding & Yield Metrics
            'BID_COUNT', 'BID_AVERAGE_CPM',
            'YIELD_GROUP_CALLOUTS', 'YIELD_GROUP_SUCCESSFUL_RESPONSES',
            'YIELD_GROUP_BIDS', 'YIELD_GROUP_BIDS_IN_AUCTION',
            'YIELD_GROUP_AUCTIONS_WON', 'YIELD_GROUP_IMPRESSIONS',
            'YIELD_GROUP_ESTIMATED_REVENUE', 'YIELD_GROUP_ESTIMATED_CPM',
            'YIELD_GROUP_MEDIATION_FILL_RATE', 'YIELD_GROUP_MEDIATION_PASSBACKS',
            'YIELD_GROUP_MEDIATION_THIRD_PARTY_ECPM',
            'YIELD_GROUP_MEDIATION_CHAINS_SERVED', 'MEDIATION_THIRD_PARTY_ECPM',

            # Programmatic Deals Metrics
            'DEALS_BID_REQUESTS', 'DEALS_BIDS', 'DEALS_BID_RATE',
            'DEALS_WINNING_BIDS', 'DEALS_WIN_RATE',
            'PROGRAMMATIC_RESPONSES_SERVED', 'PROGRAMMATIC_MATCH_RATE',
            'TOTAL_PROGRAMMATIC_ELIGIBLE_AD_REQUESTS',

            # Active View Metrics
            'TOTAL_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS',
            'TOTAL_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS',
            'TOTAL_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS_RATE',
            'TOTAL_ACTIVE_VIEW_ELIGIBLE_IMPRESSIONS',
            'TOTAL_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS_RATE',
            'TOTAL_ACTIVE_VIEW_AVERAGE_VIEWABLE_TIME',
            'TOTAL_ACTIVE_VIEW_REVENUE',
            'ACTIVE_VIEW_PERCENT_AUDIBLE_START_IMPRESSIONS',
            'ACTIVE_VIEW_PERCENT_EVER_AUDIBLE_IMPRESSIONS',
            'AD_SERVER_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS',
            'AD_SERVER_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS',
            'AD_SERVER_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS_RATE',
            'AD_SERVER_ACTIVE_VIEW_ELIGIBLE_IMPRESSIONS',
            'AD_SERVER_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS_RATE',
            'AD_SERVER_ACTIVE_VIEW_REVENUE',
            'AD_SERVER_ACTIVE_VIEW_AVERAGE_VIEWABLE_TIME',

            # Video Viewership Metrics
            'VIDEO_VIEWERSHIP_START', 'VIDEO_VIEWERSHIP_FIRST_QUARTILE',
            'VIDEO_VIEWERSHIP_MIDPOINT', 'VIDEO_VIEWERSHIP_THIRD_QUARTILE',
            'VIDEO_VIEWERSHIP_COMPLETE', 'VIDEO_VIEWERSHIP_AVERAGE_VIEW_RATE',
            'VIDEO_VIEWERSHIP_AVERAGE_VIEW_TIME', 'VIDEO_VIEWERSHIP_COMPLETION_RATE',
            'VIDEO_VIEWERSHIP_TOTAL_ERROR_COUNT', 'VIDEO_VIEWERSHIP_VIDEO_LENGTH',
            'VIDEO_VIEWERSHIP_SKIP_BUTTON_SHOWN', 'VIDEO_VIEWERSHIP_ENGAGED_VIEW',
            'VIDEO_VIEWERSHIP_VIEW_THROUGH_RATE', 'VIDEO_VIEWERSHIP_AUTO_PLAYS',
            'VIDEO_VIEWERSHIP_CLICK_TO_PLAYS', 'VIDEO_VIEWERSHIP_TOTAL_ERROR_RATE',

            # Video Interaction Metrics
            'VIDEO_INTERACTION_PAUSE', 'VIDEO_INTERACTION_RESUME',
            'VIDEO_INTERACTION_REWIND', 'VIDEO_INTERACTION_MUTE',
            'VIDEO_INTERACTION_UNMUTE', 'VIDEO_INTERACTION_COLLAPSE',
            'VIDEO_INTERACTION_EXPAND', 'VIDEO_INTERACTION_FULL_SCREEN',
            'VIDEO_INTERACTION_AVERAGE_INTERACTION_RATE',
            'VIDEO_INTERACTION_VIDEO_SKIPS',

            # Video Opportunity Metrics
            'TOTAL_VIDEO_OPPORTUNITIES', 'TOTAL_VIDEO_CAPPED_OPPORTUNITIES',
            'TOTAL_VIDEO_MATCHED_OPPORTUNITIES', 'TOTAL_VIDEO_MATCHED_DURATION',
            'TOTAL_VIDEO_DURATION', 'TOTAL_VIDEO_BREAK_START',
            'TOTAL_VIDEO_BREAK_END',

            # Rich Media Metrics
            'RICH_MEDIA_BACKUP_IMAGES', 'RICH_MEDIA_DISPLAY_TIME',
            'RICH_MEDIA_AVERAGE_DISPLAY_TIME', 'RICH_MEDIA_EXPANSIONS',
            'RICH_MEDIA_EXPANDING_TIME', 'RICH_MEDIA_INTERACTION_TIME',
            'RICH_MEDIA_INTERACTION_COUNT', 'RICH_MEDIA_INTERACTION_RATE',
            'RICH_MEDIA_AVERAGE_INTERACTION_TIME', 'RICH_MEDIA_INTERACTION_IMPRESSIONS',
            'RICH_MEDIA_MANUAL_CLOSES', 'RICH_MEDIA_FULL_SCREEN_IMPRESSIONS',
            'RICH_MEDIA_VIDEO_INTERACTIONS', 'RICH_MEDIA_VIDEO_INTERACTION_RATE',
            'RICH_MEDIA_VIDEO_MUTES', 'RICH_MEDIA_VIDEO_PAUSES',
            'RICH_MEDIA_VIDEO_PLAYES', 'RICH_MEDIA_VIDEO_MIDPOINTS',
            'RICH_MEDIA_VIDEO_COMPLETES', 'RICH_MEDIA_VIDEO_REPLAYS',
            'RICH_MEDIA_VIDEO_STOPS', 'RICH_MEDIA_VIDEO_UNMUTES',
            'RICH_MEDIA_VIDEO_VIEW_TIME', 'RICH_MEDIA_VIDEO_VIEW_RATE',
            'RICH_MEDIA_CUSTOM_EVENT_TIME', 'RICH_MEDIA_CUSTOM_EVENT_COUNT',

            # Unique Reach Metrics
            'UNIQUE_REACH_FREQUENCY', 'UNIQUE_REACH_IMPRESSIONS', 'UNIQUE_REACH',

            # SDK Mediation Metrics
            'SDK_MEDIATION_CREATIVE_IMPRESSIONS', 'SDK_MEDIATION_CREATIVE_CLICKS',

            # Forecasting Metrics
            'SELL_THROUGH_FORECASTED_IMPRESSIONS', 'SELL_THROUGH_AVAILABLE_IMPRESSIONS',
            'SELL_THROUGH_RESERVED_IMPRESSIONS', 'SELL_THROUGH_SELL_THROUGH_RATE',

            # Ad Speed Metrics
            'CREATIVE_LOAD_TIME_0_500_MS_PERCENT',
            'CREATIVE_LOAD_TIME_500_1000_MS_PERCENT',
            'CREATIVE_LOAD_TIME_1_2_S_PERCENT',
            'CREATIVE_LOAD_TIME_2_4_S_PERCENT',
            'CREATIVE_LOAD_TIME_4_8_S_PERCENT',
            'CREATIVE_LOAD_TIME_GREATER_THAN_8_S_PERCENT',
            'UNVIEWED_REASON_SLOT_NEVER_ENTERED_VIEWPORT_PERCENT',
            'UNVIEWED_REASON_USER_SCROLLED_BEFORE_AD_FILLED_PERCENT',
            'UNVIEWED_REASON_USER_SCROLLED_BEFORE_AD_LOADED_PERCENT',
            'UNVIEWED_REASON_USER_SCROLLED_BEFORE_1_S_PERCENT',
            'UNVIEWED_REASON_OTHER_PERCENT',

            # Invoicing Metrics
            'INVOICED_IMPRESSIONS', 'INVOICED_UNFILLED_IMPRESSIONS',

            # Partner Management Metrics
            'PARTNER_MANAGEMENT_HOST_IMPRESSIONS', 'PARTNER_MANAGEMENT_HOST_CLICKS',
            'PARTNER_MANAGEMENT_HOST_CTR', 'PARTNER_MANAGEMENT_UNFILLED_IMPRESSIONS',
            'PARTNER_MANAGEMENT_PARTNER_IMPRESSIONS', 'PARTNER_MANAGEMENT_PARTNER_CLICKS',
            'PARTNER_MANAGEMENT_PARTNER_CTR', 'PARTNER_MANAGEMENT_GROSS_REVENUE',

            # Ad Connector Metrics
            'DP_IMPRESSIONS', 'DP_CLICKS', 'DP_QUERIES', 'DP_MATCHED_QUERIES',
            'DP_COST', 'DP_ECPM', 'DP_ACTIVE_VIEW_ELIGIBLE_IMPRESSIONS',
            'DP_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS', 'DP_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS',
            'DP_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS_RATE',
            'DP_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS_RATE',

            # Demand Source Response Metrics
            'AD_SERVER_RESPONSES_SERVED', 'ADSENSE_RESPONSES_SERVED',
            'AD_EXCHANGE_RESPONSES_SERVED', 'PROGRAMMATIC_RESPONSES_SERVED',

            # Dynamic Allocation Metrics
            'DYNAMIC_ALLOCATION_OPPORTUNITY_IMPRESSIONS_COMPETING_TOTAL',
            'DYNAMIC_ALLOCATION_OPPORTUNITY_UNFILLED_IMPRESSIONS_COMPETING',
            'DYNAMIC_ALLOCATION_OPPORTUNITY_ELIGIBLE_IMPRESSIONS_TOTAL',
            'DYNAMIC_ALLOCATION_OPPORTUNITY_IMPRESSIONS_NOT_COMPETING_TOTAL',
            'DYNAMIC_ALLOCATION_OPPORTUNITY_IMPRESSIONS_NOT_COMPETING_PERCENT_TOTAL',
            'DYNAMIC_ALLOCATION_OPPORTUNITY_SATURATION_RATE_TOTAL',
            'DYNAMIC_ALLOCATION_OPPORTUNITY_MATCH_RATE_TOTAL',

            # Basic/Legacy Metrics (for backwards compatibility)
            'IMPRESSIONS', 'CLICKS', 'CTR', 'REVENUE', 'ECPM', 'CPC',
            'AD_REQUESTS', 'MATCHED_REQUESTS', 'FILL_RATE',
            'UNFILLED_IMPRESSIONS', 'INVENTORY_LEVEL_IMPRESSIONS',
        ]

        self._cache_set(cache_key, metrics)
        logger.info(f"Loaded {len(metrics)} GAM metrics")
        return metrics
    
    # Utility Operations
    
    def test_connection(self) -> bool:
        """
        Test API connectivity and authentication.
        
        Returns:
            True if connection successful
        """
        try:
            # Test with a simple API call
            url = f"{API_BASE_URL}/networks/{self.network_code}"
            response = self.session.get(url)
            self._handle_rest_response(response)
            logger.info("REST API connection test successful")
            return True
        except Exception as e:
            logger.error(f"REST API connection test failed: {e}")
            return False
    
    def get_network_info(self) -> Dict[str, Any]:
        """
        Get network information.
        
        Returns:
            Network details including code, name, timezone
        """
        def _get_network_info():
            url = f"{API_BASE_URL}/networks/{self.network_code}"
            response = self.session.get(url)
            return self._handle_rest_response(response)
        
        result = self._retry_with_backoff(_get_network_info)
        
        return {
            'id': result.get('networkId'),
            'networkCode': result.get('networkCode'),
            'displayName': result.get('displayName', ''),
            'timeZone': result.get('timeZone', ''),
            'currencyCode': result.get('currencyCode', '')
        }
    
    # Advanced Methods
    
    def create_and_run_report(self, report_definition: Dict[str, Any]) -> str:
        """
        Create and immediately run a report (optimized workflow).
        
        Args:
            report_definition: Report configuration
            
        Returns:
            Operation ID for tracking progress
        """
        # Create report
        report = self.create_report(report_definition)
        report_name = report.get('name')
        
        if not report_name:
            raise ReportError("Failed to get report resource name")
        
        # Run report
        def _run_report():
            url = f"{API_BASE_URL}/{report_name}:run"
            response = self.session.post(url)
            return self._handle_rest_response(response)
        
        operation = self._retry_with_backoff(_run_report)
        operation_id = operation.get('name')
        
        logger.info(f"Started report execution: {operation_id}")
        return operation_id
    
    def check_operation_status(self, operation_id: str) -> Dict[str, Any]:
        """
        Check status of a long-running operation.
        
        Args:
            operation_id: Operation ID to check
            
        Returns:
            Operation status data
        """
        def _check_status():
            url = f"{API_BASE_URL}/{operation_id}"
            response = self.session.get(url)
            return self._handle_rest_response(response)
        
        return self._retry_with_backoff(_check_status)
    
    def wait_for_report(self, report_id: str, timeout: int = 300, poll_interval: int = 10) -> str:
        """
        Wait for report to complete with timeout.
        
        Args:
            report_id: Report ID to wait for
            timeout: Maximum wait time in seconds
            poll_interval: Polling interval in seconds
            
        Returns:
            Final report status
            
        Raises:
            ReportTimeoutError: If report doesn't complete within timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_report_status(report_id)
            
            if status in ['COMPLETED', 'FAILED']:
                return status
            
            logger.debug(f"Report {report_id} status: {status}, waiting...")
            time.sleep(poll_interval)
        
        raise ReportTimeoutError(f"Report {report_id} did not complete within {timeout} seconds")
    
    # =========================================================================
    # Custom Targeting Values Operations
    # =========================================================================

    def get_custom_targeting_values(
        self,
        key_id: str,
        page_size: int = 50,
        page_token: str = None,
        filter: str = None,
        order_by: str = None
    ) -> Dict[str, Any]:
        """
        List custom targeting values for a given key.

        Args:
            key_id: Custom targeting key ID or full resource name
                   (e.g., '123456' or 'networks/{networkCode}/customTargetingKeys/123456')
            page_size: Maximum results to return (default: 50, max: 1000)
            page_token: Page token from previous call
            filter: AIP-160 filter expression
            order_by: Sort order

        Returns:
            Dict with customTargetingValues list, nextPageToken, and totalSize
        """
        # Handle both key ID and full resource name
        if not key_id.startswith('networks/'):
            key_resource = f"networks/{self.network_code}/customTargetingKeys/{key_id}"
        else:
            key_resource = key_id

        def _get_values():
            url = f"{API_BASE_URL}/{key_resource}/customTargetingValues"
            params = {'pageSize': min(page_size, 1000)}

            if page_token:
                params['pageToken'] = page_token
            if filter:
                params['filter'] = filter
            if order_by:
                params['orderBy'] = order_by

            response = self.session.get(url, params=params)
            return self._handle_rest_response(response)

        result = self._retry_with_backoff(_get_values)
        logger.info(f"Retrieved {len(result.get('customTargetingValues', []))} custom targeting values")
        return result

    def get_custom_targeting_value(self, key_id: str, value_id: str) -> Dict[str, Any]:
        """
        Get a single custom targeting value.

        Args:
            key_id: Custom targeting key ID
            value_id: Custom targeting value ID

        Returns:
            Custom targeting value resource
        """
        # Build full resource name
        if not key_id.startswith('networks/'):
            resource_name = f"networks/{self.network_code}/customTargetingKeys/{key_id}/customTargetingValues/{value_id}"
        else:
            resource_name = f"{key_id}/customTargetingValues/{value_id}"

        def _get_value():
            url = f"{API_BASE_URL}/{resource_name}"
            response = self.session.get(url)
            return self._handle_rest_response(response)

        return self._retry_with_backoff(_get_value)

    def list_all_custom_targeting_values(self, key_id: str, **filters) -> List[Dict[str, Any]]:
        """
        List all custom targeting values with automatic pagination.

        Args:
            key_id: Custom targeting key ID
            **filters: Additional filters (filter, order_by)

        Returns:
            List of all custom targeting values for the key
        """
        all_values = []
        page_token = None

        while True:
            result = self.get_custom_targeting_values(
                key_id=key_id,
                page_size=1000,
                page_token=page_token,
                filter=filters.get('filter'),
                order_by=filters.get('order_by')
            )

            values = result.get('customTargetingValues', [])
            all_values.extend(values)

            page_token = result.get('nextPageToken')
            if not page_token or len(all_values) >= 10000:  # Safety limit
                break

        logger.info(f"Retrieved total of {len(all_values)} custom targeting values for key {key_id}")
        return all_values

    # =========================================================================
    # Enhanced Report Fetching with Parsing
    # =========================================================================

    def fetch_report_rows(
        self,
        report_result_name: str,
        page_size: int = 1000,
        page_token: str = None,
        parse_values: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch report result rows with optional value parsing.

        Args:
            report_result_name: Report result resource name
                               (e.g., 'networks/{networkCode}/reports/{reportId}/results/{resultId}')
            page_size: Maximum rows to return (default: 1000, max: 10000)
            page_token: Page token from previous call
            parse_values: If True, parse MetricValueGroups into Python types

        Returns:
            Dict with:
            - rows: List of parsed (if parse_values=True) or raw rows
            - nextPageToken: Token for next page
            - totalRowCount: Total rows available
            - runTime: When the report was run
            - dateRanges: Date ranges used in the report
        """
        def _fetch_rows():
            url = f"{API_BASE_URL}/{report_result_name}:fetchRows"
            params = {'pageSize': min(page_size, 10000)}

            if page_token:
                params['pageToken'] = page_token

            response = self.session.get(url, params=params)
            return self._handle_rest_response(response)

        result = self._retry_with_backoff(_fetch_rows)

        # Parse values if requested
        if parse_values and 'rows' in result:
            result['rows'] = [
                MetricValueParser.parse_row(row)
                for row in result['rows']
            ]

        return result

    def fetch_all_report_rows(
        self,
        report_result_name: str,
        parse_values: bool = True,
        max_rows: int = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch all report rows with automatic pagination.

        Args:
            report_result_name: Report result resource name
            parse_values: If True, parse MetricValueGroups into Python types
            max_rows: Maximum rows to fetch (None for all)

        Returns:
            List of all report rows (parsed if parse_values=True)
        """
        all_rows = []
        page_token = None

        while True:
            result = self.fetch_report_rows(
                report_result_name=report_result_name,
                page_size=10000,
                page_token=page_token,
                parse_values=parse_values
            )

            rows = result.get('rows', [])
            all_rows.extend(rows)

            # Check max_rows limit
            if max_rows and len(all_rows) >= max_rows:
                all_rows = all_rows[:max_rows]
                break

            page_token = result.get('nextPageToken')
            if not page_token:
                break

        logger.info(f"Fetched total of {len(all_rows)} report rows")
        return all_rows

    def run_and_fetch_report(
        self,
        report_definition: Dict[str, Any],
        timeout: int = 300,
        poll_interval: int = 10,
        parse_values: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Complete workflow: create report, run it, wait for completion, and fetch all rows.

        Args:
            report_definition: Complete report request (use ReportDefinitionBuilder)
            timeout: Maximum wait time in seconds
            poll_interval: Polling interval in seconds
            parse_values: If True, parse metric values

        Returns:
            List of all report rows

        Example:
            >>> builder = ReportDefinitionBuilder()
            >>> report_def = (builder
            ...     .display_name("My Report")
            ...     .dimensions(['DATE', 'AD_UNIT_NAME'])
            ...     .metrics(['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS'])
            ...     .date_range_relative('LAST_7_DAYS')
            ...     .build())
            >>> rows = adapter.run_and_fetch_report(report_def)
        """
        # Create report
        report = self.create_report(report_definition)
        report_name = report.get('name')

        if not report_name:
            raise ReportError("Failed to get report resource name")

        # Run report
        operation = self.run_report(report_name)
        operation_name = operation.get('name')

        if not operation_name:
            raise ReportError("Failed to get operation name")

        # Poll until complete
        start_time = time.time()
        report_result_name = None

        while time.time() - start_time < timeout:
            status = self.check_operation_status(operation_name)

            if status.get('done'):
                if 'error' in status:
                    error_msg = status['error'].get('message', 'Unknown error')
                    raise ReportError(f"Report execution failed: {error_msg}")

                # Extract result name
                response = status.get('response', {})
                report_result_name = response.get('reportResult')
                break

            logger.debug(f"Report operation {operation_name} in progress...")
            time.sleep(poll_interval)

        if not report_result_name:
            raise ReportTimeoutError(f"Report did not complete within {timeout} seconds")

        # Fetch all rows
        return self.fetch_all_report_rows(
            report_result_name=report_result_name,
            parse_values=parse_values
        )

    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, '_session') and self._session:
            self._session.close()
        if hasattr(self, '_async_session') and self._async_session:
            asyncio.create_task(self._async_session.close())