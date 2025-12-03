"""GAM Report API enums - complete mapping of all enum types."""

from enum import Enum


class Visibility(str, Enum):
    """Report visibility setting."""

    VISIBILITY_UNSPECIFIED = "VISIBILITY_UNSPECIFIED"
    HIDDEN = "HIDDEN"
    DRAFT = "DRAFT"
    SAVED = "SAVED"


class ReportType(str, Enum):
    """Report classification types."""

    REPORT_TYPE_UNSPECIFIED = "REPORT_TYPE_UNSPECIFIED"
    HISTORICAL = "HISTORICAL"
    REACH = "REACH"
    AD_SPEED = "AD_SPEED"
    PRIVACY_AND_MESSAGING = "PRIVACY_AND_MESSAGING"


class RelativeDateRange(str, Enum):
    """Dynamic date range periods."""

    RELATIVE_DATE_RANGE_UNSPECIFIED = "RELATIVE_DATE_RANGE_UNSPECIFIED"
    TODAY = "TODAY"
    YESTERDAY = "YESTERDAY"
    THIS_WEEK = "THIS_WEEK"
    THIS_WEEK_TO_DATE = "THIS_WEEK_TO_DATE"
    THIS_MONTH = "THIS_MONTH"
    THIS_MONTH_TO_DATE = "THIS_MONTH_TO_DATE"
    THIS_QUARTER = "THIS_QUARTER"
    THIS_QUARTER_TO_DATE = "THIS_QUARTER_TO_DATE"
    THIS_YEAR = "THIS_YEAR"
    THIS_YEAR_TO_DATE = "THIS_YEAR_TO_DATE"
    PREVIOUS_DAY = "PREVIOUS_DAY"
    PREVIOUS_WEEK = "PREVIOUS_WEEK"
    PREVIOUS_MONTH = "PREVIOUS_MONTH"
    PREVIOUS_QUARTER = "PREVIOUS_QUARTER"
    PREVIOUS_YEAR = "PREVIOUS_YEAR"
    LAST_7_DAYS = "LAST_7_DAYS"
    LAST_30_DAYS = "LAST_30_DAYS"
    LAST_60_DAYS = "LAST_60_DAYS"
    LAST_90_DAYS = "LAST_90_DAYS"
    LAST_180_DAYS = "LAST_180_DAYS"
    LAST_360_DAYS = "LAST_360_DAYS"
    LAST_365_DAYS = "LAST_365_DAYS"
    ALL_TIME = "ALL_TIME"


class Operation(str, Enum):
    """Filter comparison operators - matches GAM REST API v1."""

    # Core operations (official API)
    IN = "IN"  # Default - matches value(s) in list
    NOT_IN = "NOT_IN"  # Does not match value(s)
    CONTAINS = "CONTAINS"  # String contains substring
    NOT_CONTAINS = "NOT_CONTAINS"  # String does not contain
    LESS_THAN = "LESS_THAN"  # Numeric less than
    LESS_THAN_EQUALS = "LESS_THAN_EQUALS"  # Numeric less than or equal
    GREATER_THAN = "GREATER_THAN"  # Numeric greater than
    GREATER_THAN_EQUALS = "GREATER_THAN_EQUALS"  # Numeric greater than or equal
    BETWEEN = "BETWEEN"  # Value in range (requires 2 values)
    MATCHES = "MATCHES"  # Regex pattern match
    NOT_MATCHES = "NOT_MATCHES"  # Regex pattern does not match

    # Aliases for convenience (map to IN/NOT_IN with single value)
    @classmethod
    def equals_op(cls) -> "Operation":
        """Use IN with single value for equality check."""
        return cls.IN

    @classmethod
    def not_equals_op(cls) -> "Operation":
        """Use NOT_IN with single value for inequality check."""
        return cls.NOT_IN


class TimePeriodColumn(str, Enum):
    """Time period grouping for comparison columns."""

    TIME_PERIOD_COLUMN_UNSPECIFIED = "TIME_PERIOD_COLUMN_UNSPECIFIED"
    DAYS = "DAYS"
    WEEKS = "WEEKS"
    MONTHS = "MONTHS"
    QUARTERS = "QUARTERS"


class TimeZoneSource(str, Enum):
    """Source of timezone for report."""

    TIME_ZONE_SOURCE_UNSPECIFIED = "TIME_ZONE_SOURCE_UNSPECIFIED"
    PUBLISHER = "PUBLISHER"
    PROVIDED = "PROVIDED"


class DayOfWeek(str, Enum):
    """Days of the week for scheduling."""

    DAY_OF_WEEK_UNSPECIFIED = "DAY_OF_WEEK_UNSPECIFIED"
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


class Frequency(str, Enum):
    """Schedule frequency options."""

    FREQUENCY_UNSPECIFIED = "FREQUENCY_UNSPECIFIED"
    ONCE = "ONCE"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    TWICE_MONTHLY = "TWICE_MONTHLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    YEARLY = "YEARLY"


class DeliveryCondition(str, Enum):
    """Conditions for report delivery."""

    DELIVERY_CONDITION_UNSPECIFIED = "DELIVERY_CONDITION_UNSPECIFIED"
    REPORT_RUN_COMPLETED = "REPORT_RUN_COMPLETED"
    REPORT_HAS_DATA = "REPORT_HAS_DATA"


class MetricValueType(str, Enum):
    """Metric data type classifications."""

    METRIC_VALUE_TYPE_UNSPECIFIED = "METRIC_VALUE_TYPE_UNSPECIFIED"
    ACTIVE_VIEW = "ACTIVE_VIEW"
    ADSENSE = "ADSENSE"
    AD_EXCHANGE = "AD_EXCHANGE"
    AD_SERVER = "AD_SERVER"
    ADS_TRAFFIC_NAVIGATOR = "ADS_TRAFFIC_NAVIGATOR"
    REVENUE = "REVENUE"
    IMPRESSIONS = "IMPRESSIONS"
    CLICKS = "CLICKS"
    VIDEO = "VIDEO"
    RICH_MEDIA = "RICH_MEDIA"
    REACH = "REACH"
    AD_SPEED = "AD_SPEED"
    PROGRAMMATIC = "PROGRAMMATIC"


class ComparisonType(str, Enum):
    """Comparison types for reports."""

    COMPARISON_TYPE_UNSPECIFIED = "COMPARISON_TYPE_UNSPECIFIED"
    ABSOLUTE_VALUE = "ABSOLUTE_VALUE"
    PREVIOUS_PERIOD = "PREVIOUS_PERIOD"
    PREVIOUS_YEAR = "PREVIOUS_YEAR"


class ReportState(str, Enum):
    """State of a report run."""

    STATE_UNSPECIFIED = "STATE_UNSPECIFIED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
