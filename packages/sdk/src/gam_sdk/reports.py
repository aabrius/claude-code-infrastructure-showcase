"""
Fluent report builder and result handling for the GAM SDK.

Provides chainable methods for building and executing reports
with intelligent defaults and comprehensive export options.
"""

import json
import csv
import io
import logging
from typing import Optional, List, Dict, Any, Union, Callable
from datetime import datetime, date, timedelta
from pathlib import Path

import pandas as pd

from gam_api.config import Config
from gam_api.auth import AuthManager
from gam_api.models import ReportDefinition, DateRange, DateRangeType, ReportType
from gam_api.reports import ReportGenerator, generate_quick_report, QUICK_REPORTS
from gam_api.exceptions import ReportGenerationError
from .exceptions import ReportError, ValidationError, SDKError

logger = logging.getLogger(__name__)


class ReportResult:
    """
    Container for report results with export and manipulation methods.
    
    Provides fluent interface for working with report data including
    export to various formats, data transformation, and analysis.
    """
    
    def __init__(self, 
                 rows: List[Dict[str, Any]], 
                 dimension_headers: List[str],
                 metric_headers: List[str],
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize report result.
        
        Args:
            rows: List of data rows
            dimension_headers: Dimension column names
            metric_headers: Metric column names
            metadata: Optional report metadata
        """
        self.rows = rows
        self.dimension_headers = dimension_headers
        self.metric_headers = metric_headers
        self.metadata = metadata or {}
        self._dataframe = None
    
    @property
    def headers(self) -> List[str]:
        """Get all column headers (dimensions + metrics)."""
        return self.dimension_headers + self.metric_headers
    
    @property
    def row_count(self) -> int:
        """Get number of data rows."""
        return len(self.rows)
    
    @property
    def column_count(self) -> int:
        """Get number of columns."""
        return len(self.headers)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary format.
        
        Returns:
            Dictionary with headers and data
        """
        return {
            'headers': self.headers,
            'dimension_headers': self.dimension_headers,
            'metric_headers': self.metric_headers,
            'rows': self.rows,
            'metadata': self.metadata,
            'summary': {
                'row_count': self.row_count,
                'column_count': self.column_count
            }
        }
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert to pandas DataFrame.
        
        Returns:
            Pandas DataFrame with report data
        """
        if self._dataframe is None:
            # Convert rows to flat format for DataFrame
            flat_rows = []
            for row in self.rows:
                flat_row = {}
                
                # Add dimension values
                for i, header in enumerate(self.dimension_headers):
                    if i < len(row.get('dimensionValues', [])):
                        flat_row[header] = row['dimensionValues'][i]
                    else:
                        flat_row[header] = None
                
                # Add metric values
                if 'metricValueGroups' in row and row['metricValueGroups']:
                    primary_values = row['metricValueGroups'][0].get('primaryValues', [])
                    for i, header in enumerate(self.metric_headers):
                        if i < len(primary_values):
                            # Try to convert to numeric if possible
                            value = primary_values[i]
                            try:
                                if '.' in str(value):
                                    flat_row[header] = float(value)
                                else:
                                    flat_row[header] = int(value)
                            except (ValueError, TypeError):
                                flat_row[header] = value
                        else:
                            flat_row[header] = None
                
                flat_rows.append(flat_row)
            
            self._dataframe = pd.DataFrame(flat_rows)
        
        return self._dataframe
    
    def to_csv(self, file_path: Union[str, Path]) -> 'ReportResult':
        """
        Export to CSV file.
        
        Args:
            file_path: Path to save CSV file
            
        Returns:
            Self for chaining
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        df = self.to_dataframe()
        df.to_csv(file_path, index=False)
        
        logger.info(f"Report exported to CSV: {file_path}")
        return self
    
    def to_json(self, file_path: Union[str, Path], format: str = 'records') -> 'ReportResult':
        """
        Export to JSON file.
        
        Args:
            file_path: Path to save JSON file
            format: JSON format ('records', 'values', 'index', 'table')
            
        Returns:
            Self for chaining
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == 'records':
            # Export as list of records
            data = self.to_dataframe().to_dict('records')
        elif format == 'table':
            # Export as table format with metadata
            data = self.to_dict()
        else:
            # Use pandas built-in formats
            data = self.to_dataframe().to_dict(format)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Report exported to JSON: {file_path}")
        return self
    
    def to_excel(self, file_path: Union[str, Path], sheet_name: str = 'Report') -> 'ReportResult':
        """
        Export to Excel file.
        
        Args:
            file_path: Path to save Excel file
            sheet_name: Excel sheet name
            
        Returns:
            Self for chaining
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        df = self.to_dataframe()
        df.to_excel(file_path, sheet_name=sheet_name, index=False)
        
        logger.info(f"Report exported to Excel: {file_path}")
        return self
    
    def filter(self, condition: Callable[[Dict[str, Any]], bool]) -> 'ReportResult':
        """
        Filter rows based on condition.
        
        Args:
            condition: Function that returns True for rows to keep
            
        Returns:
            New ReportResult with filtered data
        """
        df = self.to_dataframe()
        filtered_df = df[df.apply(condition, axis=1)]
        
        # Convert back to original format
        filtered_rows = []
        for _, row in filtered_df.iterrows():
            row_dict = {
                'dimensionValues': [row[h] for h in self.dimension_headers],
                'metricValueGroups': [{
                    'primaryValues': [row[h] for h in self.metric_headers]
                }]
            }
            filtered_rows.append(row_dict)
        
        return ReportResult(
            rows=filtered_rows,
            dimension_headers=self.dimension_headers,
            metric_headers=self.metric_headers,
            metadata=self.metadata
        )
    
    def sort(self, by: Union[str, List[str]], ascending: bool = True) -> 'ReportResult':
        """
        Sort results by column(s).
        
        Args:
            by: Column name or list of column names to sort by
            ascending: Sort order
            
        Returns:
            New ReportResult with sorted data
        """
        df = self.to_dataframe()
        sorted_df = df.sort_values(by=by, ascending=ascending)
        
        # Convert back to original format
        sorted_rows = []
        for _, row in sorted_df.iterrows():
            row_dict = {
                'dimensionValues': [row[h] for h in self.dimension_headers],
                'metricValueGroups': [{
                    'primaryValues': [row[h] for h in self.metric_headers]
                }]
            }
            sorted_rows.append(row_dict)
        
        return ReportResult(
            rows=sorted_rows,
            dimension_headers=self.dimension_headers,
            metric_headers=self.metric_headers,
            metadata=self.metadata
        )
    
    def head(self, n: int = 5) -> 'ReportResult':
        """
        Get first n rows.
        
        Args:
            n: Number of rows to return
            
        Returns:
            New ReportResult with first n rows
        """
        return ReportResult(
            rows=self.rows[:n],
            dimension_headers=self.dimension_headers,
            metric_headers=self.metric_headers,
            metadata=self.metadata
        )
    
    def tail(self, n: int = 5) -> 'ReportResult':
        """
        Get last n rows.
        
        Args:
            n: Number of rows to return
            
        Returns:
            New ReportResult with last n rows
        """
        return ReportResult(
            rows=self.rows[-n:] if n < len(self.rows) else self.rows,
            dimension_headers=self.dimension_headers,
            metric_headers=self.metric_headers,
            metadata=self.metadata
        )
    
    def summary(self) -> Dict[str, Any]:
        """
        Get summary statistics for numeric columns.
        
        Returns:
            Dictionary with summary statistics
        """
        df = self.to_dataframe()
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if not numeric_cols:
            return {'message': 'No numeric columns found'}
        
        summary_stats = df[numeric_cols].describe().to_dict()
        
        return {
            'row_count': self.row_count,
            'column_count': self.column_count,
            'numeric_columns': numeric_cols,
            'statistics': summary_stats
        }
    
    def __len__(self) -> int:
        """Get number of rows."""
        return self.row_count
    
    def __iter__(self):
        """Iterate over rows."""
        return iter(self.rows)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"ReportResult(rows={self.row_count}, cols={self.column_count})"


class ReportBuilder:
    """
    Fluent builder for GAM reports with method chaining.
    
    Provides intuitive interface for building complex reports
    with intelligent defaults and validation.
    """
    
    def __init__(self, config: Config, auth_manager: AuthManager):
        """
        Initialize report builder.
        
        Args:
            config: GAM configuration
            auth_manager: Authentication manager
        """
        self._config = config
        self._auth_manager = auth_manager
        self._generator = ReportGenerator()

        # Report configuration
        self._report_type = ReportType.DELIVERY  # Default report type
        self._dimensions = []
        self._metrics = []
        self._date_range = None
        self._filters = []
        self._report_name = None
        self._quick_report_type = None
    
    def quick(self, report_type: str) -> 'ReportBuilder':
        """
        Use predefined quick report configuration.
        
        Args:
            report_type: Type of quick report (delivery, inventory, sales, etc.)
            
        Returns:
            Self for chaining
            
        Raises:
            ValidationError: If report type is invalid
        """
        if report_type not in QUICK_REPORTS:
            available = ', '.join(QUICK_REPORTS.keys())
            raise ValidationError(
                f"Invalid quick report type '{report_type}'. Available: {available}",
                field_name='report_type',
                field_value=report_type
            )
        
        self._quick_report_type = report_type
        return self
    
    def delivery(self) -> 'ReportBuilder':
        """Configure for delivery performance report."""
        return self.quick('delivery')
    
    def inventory(self) -> 'ReportBuilder':
        """Configure for inventory analysis report."""
        return self.quick('inventory')
    
    def sales(self) -> 'ReportBuilder':
        """Configure for sales and revenue report."""
        return self.quick('sales')
    
    def reach(self) -> 'ReportBuilder':
        """Configure for audience reach report."""
        return self.quick('reach')
    
    def programmatic(self) -> 'ReportBuilder':
        """Configure for programmatic advertising report."""
        return self.quick('programmatic')
    
    def dimensions(self, *dimension_names: str) -> 'ReportBuilder':
        """
        Add dimensions to the report.
        
        Args:
            *dimension_names: Dimension names to include
            
        Returns:
            Self for chaining
        """
        self._dimensions.extend(dimension_names)
        return self
    
    def metrics(self, *metric_names: str) -> 'ReportBuilder':
        """
        Add metrics to the report.
        
        Args:
            *metric_names: Metric names to include
            
        Returns:
            Self for chaining
        """
        self._metrics.extend(metric_names)
        return self
    
    def date_range(self, start_date: date, end_date: date) -> 'ReportBuilder':
        """
        Set custom date range.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            Self for chaining
        """
        self._date_range = DateRange(
            start_date=start_date,
            end_date=end_date,
            date_range_type=DateRangeType.CUSTOM
        )
        return self
    
    def days_back(self, days: int) -> 'ReportBuilder':
        """
        Set date range to last N days.
        
        Args:
            days: Number of days back from today
            
        Returns:
            Self for chaining
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        return self.date_range(start_date, end_date)
    
    def last_7_days(self) -> 'ReportBuilder':
        """Set date range to last 7 days."""
        return self.days_back(7)
    
    def last_30_days(self) -> 'ReportBuilder':
        """Set date range to last 30 days."""
        return self.days_back(30)
    
    def last_90_days(self) -> 'ReportBuilder':
        """Set date range to last 90 days."""
        return self.days_back(90)
    
    def this_month(self) -> 'ReportBuilder':
        """Set date range to current month."""
        today = date.today()
        start_date = today.replace(day=1)
        return self.date_range(start_date, today)
    
    def last_month(self) -> 'ReportBuilder':
        """Set date range to previous month."""
        today = date.today()
        first_this_month = today.replace(day=1)
        last_month_end = first_this_month - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        return self.date_range(last_month_start, last_month_end)
    
    def name(self, report_name: str) -> 'ReportBuilder':
        """
        Set report name.
        
        Args:
            report_name: Name for the report
            
        Returns:
            Self for chaining
        """
        self._report_name = report_name
        return self
    
    def filter(self, dimension: str, operator: str, values: List[str]) -> 'ReportBuilder':
        """
        Add filter to the report.
        
        Args:
            dimension: Dimension to filter on
            operator: Filter operator (EQUALS, CONTAINS, etc.)
            values: Values to filter by
            
        Returns:
            Self for chaining
        """
        self._filters.append({
            'dimension': dimension,
            'operator': operator,
            'values': values
        })
        return self
    
    def execute(self) -> ReportResult:
        """
        Execute the report and return results.
        
        Returns:
            ReportResult with the generated data
            
        Raises:
            ReportError: If report generation fails
            ValidationError: If report configuration is invalid
        """
        try:
            # Use quick report if specified
            if self._quick_report_type:
                days_back = 30  # Default
                if self._date_range:
                    days_back = (self._date_range.end_date - self._date_range.start_date).days
                
                result = generate_quick_report(self._quick_report_type, days_back)
                
                return ReportResult(
                    rows=result.rows,
                    dimension_headers=result.dimension_headers,
                    metric_headers=result.metric_headers,
                    metadata={
                        'report_type': 'quick',
                        'quick_type': self._quick_report_type,
                        'days_back': days_back,
                        'generated_at': datetime.now().isoformat()
                    }
                )
            
            # Build custom report
            if not self._dimensions:
                raise ValidationError("At least one dimension is required")
            
            if not self._metrics:
                raise ValidationError("At least one metric is required")
            
            if not self._date_range:
                # Default to last 30 days
                self._date_range = DateRange(
                    start_date=date.today() - timedelta(days=30),
                    end_date=date.today(),
                    date_range_type=DateRangeType.CUSTOM
                )

            # Generate report name if not provided
            if not self._report_name:
                self._report_name = f"Custom Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            # Create report definition
            report_def = ReportDefinition(
                name=self._report_name,
                dimensions=self._dimensions,
                metrics=self._metrics
            )
            
            # Execute report
            report = self._generator.create_report(report_def, self._report_name)
            completed_report = self._generator.run_report(report)
            result = self._generator.fetch_results(completed_report)
            
            return ReportResult(
                rows=result.rows,
                dimension_headers=self._dimensions,
                metric_headers=self._metrics,
                metadata={
                    'report_type': 'custom',
                    'report_name': self._report_name,
                    'date_range': {
                        'start': self._date_range.start_date.isoformat(),
                        'end': self._date_range.end_date.isoformat()
                    },
                    'dimensions': self._dimensions,
                    'metrics': self._metrics,
                    'filters': self._filters,
                    'generated_at': datetime.now().isoformat()
                }
            )
            
        except ValidationError:
            raise  # Re-raise validation errors without wrapping
        except ReportGenerationError as e:
            raise ReportError(f"Report generation failed: {e}") from e
        except Exception as e:
            raise ReportError(f"Unexpected error during report execution: {e}") from e
    
    def preview(self, limit: int = 5) -> ReportResult:
        """
        Execute report and return preview with limited rows.
        
        Args:
            limit: Number of rows to return
            
        Returns:
            ReportResult with limited data
        """
        result = self.execute()
        return result.head(limit)
    
    def __repr__(self) -> str:
        """String representation of the builder."""
        parts = []
        if self._quick_report_type:
            parts.append(f"quick={self._quick_report_type}")
        if self._dimensions:
            parts.append(f"dims={len(self._dimensions)}")
        if self._metrics:
            parts.append(f"metrics={len(self._metrics)}")
        if self._date_range:
            days = (self._date_range.end_date - self._date_range.start_date).days
            parts.append(f"days={days}")
        
        config_str = ", ".join(parts) if parts else "empty"
        return f"ReportBuilder({config_str})"