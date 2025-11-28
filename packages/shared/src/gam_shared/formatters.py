"""
Output formatters for Google Ad Manager API data.
"""

import json
import csv
import io
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date

# Define local classes for shared package
class ExportFormat:
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"
    XML = "xml"

class ReportResult:
    def __init__(self, data=None):
        self.data = data or []
        self.total_rows = len(self.data)
        
class Report:
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name


class ReportFormatter:
    """Base class for report formatters."""
    
    def format(self, result: ReportResult) -> Any:
        """Format report result."""
        raise NotImplementedError


class JSONFormatter(ReportFormatter):
    """Format report data as JSON."""
    
    def __init__(self, pretty: bool = True, include_metadata: bool = True):
        """
        Initialize JSON formatter.
        
        Args:
            pretty: Whether to pretty-print JSON
            include_metadata: Whether to include report metadata
        """
        self.pretty = pretty
        self.include_metadata = include_metadata
    
    def format(self, result: ReportResult) -> str:
        """
        Format report result as JSON string.
        
        Args:
            result: Report result to format
            
        Returns:
            JSON string
        """
        data = {
            "reportId": result.report_id,
            "totalRows": result.total_rows,
            "executionTime": result.execution_time,
            "dimensions": result.dimension_headers,
            "metrics": result.metric_headers,
            "data": []
        }
        
        # Convert rows to structured format
        for row in result.rows:
            formatted_row = self._format_row(row, result.dimension_headers, result.metric_headers)
            data["data"].append(formatted_row)
        
        if self.pretty:
            return json.dumps(data, indent=2, default=self._json_serializer)
        else:
            return json.dumps(data, default=self._json_serializer)
    
    def _format_row(self, row: Dict[str, Any], dimension_headers: List[str], metric_headers: List[str]) -> Dict[str, Any]:
        """Format a single row."""
        formatted = {}
        
        # Extract dimensions
        if 'dimensionValues' in row:
            for i, dim_value in enumerate(row['dimensionValues']):
                header = dimension_headers[i] if i < len(dimension_headers) else f"dimension_{i}"
                formatted[header] = self._extract_value(dim_value)
        
        # Extract metrics
        if 'metricValueGroups' in row and row['metricValueGroups']:
            first_group = row['metricValueGroups'][0]
            if 'primaryValues' in first_group:
                for i, metric_value in enumerate(first_group['primaryValues']):
                    header = metric_headers[i] if i < len(metric_headers) else f"metric_{i}"
                    formatted[header] = self._extract_value(metric_value)
        
        return formatted
    
    def _extract_value(self, value_obj: Dict[str, Any]) -> Any:
        """Extract actual value from API format."""
        if 'stringValue' in value_obj:
            return value_obj['stringValue']
        elif 'intValue' in value_obj:
            return int(value_obj['intValue'])
        elif 'doubleValue' in value_obj:
            return float(value_obj['doubleValue'])
        elif 'booleanValue' in value_obj:
            return value_obj['booleanValue']
        elif 'stringListValue' in value_obj and 'values' in value_obj['stringListValue']:
            return value_obj['stringListValue']['values']
        else:
            return None
    
    def _json_serializer(self, obj):
        """Handle special types for JSON serialization."""
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        else:
            return str(obj)


class CSVFormatter(ReportFormatter):
    """Format report data as CSV."""
    
    def __init__(self, delimiter: str = ',', include_headers: bool = True):
        """
        Initialize CSV formatter.
        
        Args:
            delimiter: Field delimiter
            include_headers: Whether to include header row
        """
        self.delimiter = delimiter
        self.include_headers = include_headers
    
    def format(self, result: ReportResult) -> str:
        """
        Format report result as CSV string.
        
        Args:
            result: Report result to format
            
        Returns:
            CSV string
        """
        output = io.StringIO()
        writer = csv.writer(output, delimiter=self.delimiter)
        
        # Write headers
        if self.include_headers:
            headers = result.dimension_headers + result.metric_headers
            writer.writerow(headers)
        
        # Write data rows
        for row in result.rows:
            csv_row = self._format_row(row, result.dimension_headers, result.metric_headers)
            writer.writerow(csv_row)
        
        return output.getvalue()
    
    def format_to_file(self, result: ReportResult, filename: str):
        """
        Format report result directly to CSV file.
        
        Args:
            result: Report result to format
            filename: Output filename
        """
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=self.delimiter)
            
            # Write headers
            if self.include_headers:
                headers = result.dimension_headers + result.metric_headers
                writer.writerow(headers)
            
            # Write data rows
            for row in result.rows:
                csv_row = self._format_row(row, result.dimension_headers, result.metric_headers)
                writer.writerow(csv_row)
    
    def _format_row(self, row: Dict[str, Any], dimension_headers: List[str], metric_headers: List[str]) -> List[Any]:
        """Format a single row for CSV."""
        values = []
        
        # Extract dimension values
        if 'dimensionValues' in row:
            for dim_value in row['dimensionValues']:
                values.append(self._extract_value(dim_value))
        
        # Extract metric values
        if 'metricValueGroups' in row and row['metricValueGroups']:
            first_group = row['metricValueGroups'][0]
            if 'primaryValues' in first_group:
                for metric_value in first_group['primaryValues']:
                    values.append(self._extract_value(metric_value))
        
        return values
    
    def _extract_value(self, value_obj: Dict[str, Any]) -> Any:
        """Extract actual value from API format."""
        if 'stringValue' in value_obj:
            return value_obj['stringValue']
        elif 'intValue' in value_obj:
            return value_obj['intValue']
        elif 'doubleValue' in value_obj:
            return value_obj['doubleValue']
        elif 'booleanValue' in value_obj:
            return value_obj['booleanValue']
        elif 'stringListValue' in value_obj and 'values' in value_obj['stringListValue']:
            return ', '.join(value_obj['stringListValue']['values'])
        else:
            return ''


class ExcelFormatter(ReportFormatter):
    """Format report data as Excel file."""
    
    def __init__(self, sheet_name: str = "Report Data"):
        """
        Initialize Excel formatter.
        
        Args:
            sheet_name: Name for the worksheet
        """
        self.sheet_name = sheet_name
    
    def format_to_file(self, result: ReportResult, filename: str):
        """
        Format report result to Excel file.
        
        Args:
            result: Report result to format
            filename: Output filename
        """
        try:
            import pandas as pd
            
            # Convert to DataFrame
            df = result.to_dataframe()
            
            # Write to Excel
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=self.sheet_name, index=False)
                
                # Auto-adjust column widths
                worksheet = writer.sheets[self.sheet_name]
                for column in df:
                    column_length = max(df[column].astype(str).map(len).max(), len(column))
                    col_idx = df.columns.get_loc(column)
                    worksheet.column_dimensions[chr(65 + col_idx)].width = min(column_length + 2, 50)
                    
        except ImportError:
            raise ImportError("pandas and openpyxl are required for Excel export")


class SummaryFormatter(ReportFormatter):
    """Format report data as human-readable summary."""
    
    def format(self, result: ReportResult) -> str:
        """
        Format report result as summary text.
        
        Args:
            result: Report result to format
            
        Returns:
            Summary text
        """
        lines = [
            f"Report Summary",
            f"=" * 50,
            f"Report ID: {result.report_id}",
            f"Total Rows: {result.total_rows:,}",
        ]
        
        if result.execution_time:
            lines.append(f"Execution Time: {result.execution_time:.2f} seconds")
        
        lines.extend([
            "",
            f"Dimensions ({len(result.dimension_headers)}): {', '.join(result.dimension_headers)}",
            f"Metrics ({len(result.metric_headers)}): {', '.join(result.metric_headers)}",
            ""
        ])
        
        # Show sample data
        if result.rows:
            lines.append("Sample Data (first 5 rows):")
            lines.append("-" * 50)
            
            # Convert first 5 rows to readable format
            json_formatter = JSONFormatter(pretty=True, include_metadata=False)
            for i, row in enumerate(result.rows[:5], 1):
                formatted_row = json_formatter._format_row(row, result.dimension_headers, result.metric_headers)
                lines.append(f"\nRow {i}:")
                for key, value in formatted_row.items():
                    lines.append(f"  {key}: {value}")
        
        return "\n".join(lines)


# Factory function
def get_formatter(format_type: Union[str, ExportFormat], **kwargs) -> ReportFormatter:
    """
    Get formatter instance for specified format.
    
    Args:
        format_type: Export format type
        **kwargs: Additional arguments for formatter
        
    Returns:
        Formatter instance
        
    Raises:
        ValueError: If format type is not supported
    """
    if isinstance(format_type, str):
        format_type = format_type.upper()
    
    formatters = {
        ExportFormat.JSON: JSONFormatter,
        ExportFormat.CSV: CSVFormatter,
        ExportFormat.EXCEL: ExcelFormatter,
        "JSON": JSONFormatter,
        "CSV": CSVFormatter,
        "EXCEL": ExcelFormatter,
        "XLSX": ExcelFormatter,
        "TSV": lambda **kw: CSVFormatter(delimiter='\t', **kw),
        "SUMMARY": SummaryFormatter
    }
    
    formatter_class = formatters.get(format_type)
    if not formatter_class:
        raise ValueError(f"Unsupported format type: {format_type}")
    
    return formatter_class(**kwargs)


# Convenience functions

def format_report(result: ReportResult, format_type: Union[str, ExportFormat] = "JSON", **kwargs) -> str:
    """
    Format report result to string.
    
    Args:
        result: Report result to format
        format_type: Output format
        **kwargs: Additional formatter arguments
        
    Returns:
        Formatted string
    """
    formatter = get_formatter(format_type, **kwargs)
    return formatter.format(result)


# Compatibility functions for fastmcp_server
def format_as_json(data):
    """Format data as JSON for compatibility."""
    import json
    return json.dumps(data, indent=2)

def format_as_csv(data):
    """Format data as CSV for compatibility."""
    if not data:
        return ""
    
    import csv, io
    output = io.StringIO()
    if isinstance(data, list) and data:
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    return output.getvalue()

# Alias for DataFormatter
DataFormatter = ReportFormatter

def save_report(result: ReportResult, filename: str, format_type: Optional[Union[str, ExportFormat]] = None, **kwargs):
    """
    Save report result to file.
    
    Args:
        result: Report result to save
        filename: Output filename
        format_type: Output format (auto-detected from extension if not provided)
        **kwargs: Additional formatter arguments
    """
    # Auto-detect format from filename if not provided
    if format_type is None:
        if filename.endswith('.json'):
            format_type = "JSON"
        elif filename.endswith('.csv'):
            format_type = "CSV"
        elif filename.endswith('.tsv'):
            format_type = "TSV"
        elif filename.endswith(('.xlsx', '.xls')):
            format_type = "EXCEL"
        else:
            format_type = "JSON"  # Default
    
    formatter = get_formatter(format_type, **kwargs)
    
    # Use specialized file methods if available
    if hasattr(formatter, 'format_to_file'):
        formatter.format_to_file(result, filename)
    else:
        # Write formatted string
        content = formatter.format(result)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)