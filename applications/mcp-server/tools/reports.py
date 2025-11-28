"""
MCP tools for report operations.
"""

import json
from typing import Dict, Any
from datetime import datetime, timedelta

from gam_api.reports import ReportGenerator, list_quick_report_types
from gam_api.models import DateRange, DateRangeType, ReportDefinition, ReportType
from gam_api.exceptions import ValidationError
from gam_shared.validators import validate_dimensions_list, validate_metrics_list
from gam_shared.formatters import get_formatter


async def handle_quick_report(args: Dict[str, Any]) -> str:
    """
    Generate a quick report with predefined configuration.
    
    Args:
        args: Dictionary containing:
            - report_type: Type of quick report
            - days_back: Number of days to look back (optional)
            - format: Output format (optional)
    
    Returns:
        JSON string with report results
    """
    report_type = args["report_type"]
    days_back = args.get("days_back", 30)
    format_type = args.get("format", "json")
    
    # Generate report
    generator = ReportGenerator()
    result = generator.generate_quick_report(report_type, days_back)
    
    # Format output
    formatter = get_formatter(format_type)
    
    if format_type == "summary":
        return formatter.format(result)
    elif format_type == "csv":
        return formatter.format(result)
    else:  # json
        response = {
            "success": True,
            "report_type": report_type,
            "days_back": days_back,
            "total_rows": result.total_rows,
            "dimensions": result.dimension_headers,
            "metrics": result.metric_headers,
            "execution_time": result.execution_time
        }
        
        # Include actual data
        if result.rows:
            # Convert first few rows to structured format for preview
            formatted_data = []
            for row in result.rows[:10]:  # Limit to first 10 rows for MCP
                formatted_row = {}
                
                # Extract dimensions
                if 'dimensionValues' in row:
                    for i, dim_value in enumerate(row['dimensionValues']):
                        header = result.dimension_headers[i] if i < len(result.dimension_headers) else f"dim_{i}"
                        formatted_row[header] = _extract_value(dim_value)
                
                # Extract metrics
                if 'metricValueGroups' in row and row['metricValueGroups']:
                    first_group = row['metricValueGroups'][0]
                    if 'primaryValues' in first_group:
                        for i, metric_value in enumerate(first_group['primaryValues']):
                            header = result.metric_headers[i] if i < len(result.metric_headers) else f"metric_{i}"
                            formatted_row[header] = _extract_value(metric_value)
                
                formatted_data.append(formatted_row)
            
            response["data_preview"] = formatted_data
            response["note"] = f"Showing first 10 rows of {result.total_rows} total rows"
        
        return json.dumps(response, indent=2)


async def handle_create_report(args: Dict[str, Any]) -> str:
    """
    Create a custom report with specified dimensions and metrics.
    
    Args:
        args: Dictionary containing report parameters
    
    Returns:
        JSON string with creation results
    """
    name = args["name"]
    dimensions = args["dimensions"]
    metrics = args["metrics"]
    report_type = ReportType(args.get("report_type", "HISTORICAL"))
    days_back = args.get("days_back", 30)
    run_immediately = args.get("run_immediately", True)
    format_type = args.get("format", "json")
    
    # Validate inputs
    try:
        dimensions = validate_dimensions_list(dimensions)
        metrics = validate_metrics_list(metrics)
    except ValidationError as e:
        raise ValueError(f"Validation error: {e}")
    
    # Create date range
    if days_back == 7:
        date_range = DateRange(range_type=DateRangeType.LAST_7_DAYS)
    elif days_back == 30:
        date_range = DateRange(range_type=DateRangeType.LAST_30_DAYS)
    else:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)
        date_range = DateRange(
            range_type=DateRangeType.CUSTOM,
            start_date=start_date,
            end_date=end_date
        )
    
    # Create report definition
    definition = ReportDefinition(
        report_type=report_type,
        dimensions=dimensions,
        metrics=metrics,
        date_range=date_range
    )
    
    # Create report
    generator = ReportGenerator()
    report = generator.create_report(definition, name)
    
    response = {
        "success": True,
        "action": "created",
        "report_id": report.id,
        "name": report.name,
        "status": report.status.value,
        "created_at": report.created_at.isoformat() if report.created_at else None,
        "dimensions": dimensions,
        "metrics": metrics,
        "date_range": {
            "type": date_range.range_type.value,
            "days_back": days_back
        }
    }
    
    # Run immediately if requested
    if run_immediately:
        try:
            report = generator.run_report(report, timeout=300)  # 5 minute timeout for MCP
            result = generator.fetch_results(report, max_pages=5)  # Limit pages for MCP
            
            response.update({
                "action": "created_and_executed",
                "status": report.status.value,
                "total_rows": result.total_rows,
                "execution_time": result.execution_time
            })
            
            # Include data preview
            if result.rows and format_type != "summary":
                formatted_data = []
                for row in result.rows[:5]:  # First 5 rows for MCP
                    formatted_row = {}
                    
                    # Extract dimensions
                    if 'dimensionValues' in row:
                        for i, dim_value in enumerate(row['dimensionValues']):
                            header = result.dimension_headers[i] if i < len(result.dimension_headers) else f"dim_{i}"
                            formatted_row[header] = _extract_value(dim_value)
                    
                    # Extract metrics
                    if 'metricValueGroups' in row and row['metricValueGroups']:
                        first_group = row['metricValueGroups'][0]
                        if 'primaryValues' in first_group:
                            for i, metric_value in enumerate(first_group['primaryValues']):
                                header = result.metric_headers[i] if i < len(result.metric_headers) else f"metric_{i}"
                                formatted_row[header] = _extract_value(metric_value)
                    
                    formatted_data.append(formatted_row)
                
                response["data_preview"] = formatted_data
                response["note"] = f"Showing first 5 rows of {result.total_rows} total rows"
            
        except Exception as e:
            response.update({
                "action": "created_but_execution_failed",
                "execution_error": str(e),
                "note": "Report was created but execution failed. You can try running it later."
            })
    
    return json.dumps(response, indent=2)


async def handle_list_reports(args: Dict[str, Any]) -> str:
    """
    List available reports in the Ad Manager network.
    
    Args:
        args: Dictionary containing list parameters
    
    Returns:
        JSON string with report list
    """
    limit = args.get("limit", 20)
    
    generator = ReportGenerator()
    reports = generator.list_reports(limit)
    
    # Simplify report data for display
    simplified_reports = []
    for report in reports:
        simplified = {
            "id": report.get("reportId"),
            "name": report.get("displayName"),
            "created": report.get("createTime"),
            "updated": report.get("updateTime"),
            "resource_name": report.get("name")
        }
        simplified_reports.append(simplified)
    
    response = {
        "success": True,
        "total_reports": len(simplified_reports),
        "reports": simplified_reports,
        "note": f"Showing up to {limit} reports. Use limit parameter to see more."
    }
    
    return json.dumps(response, indent=2)


async def handle_get_quick_report_types(args: Dict[str, Any]) -> str:
    """
    Get available quick report types and their descriptions.
    
    Args:
        args: Dictionary (unused)
    
    Returns:
        JSON string with report types
    """
    types = list_quick_report_types()
    
    response = {
        "success": True,
        "quick_report_types": types,
        "usage": "Use these report types with the gam_quick_report tool"
    }
    
    return json.dumps(response, indent=2)


def _extract_value(value_obj: Dict[str, Any]) -> Any:
    """Extract actual value from API response format."""
    if 'stringValue' in value_obj:
        return value_obj['stringValue']
    elif 'intValue' in value_obj:
        return int(value_obj['intValue'])
    elif 'doubleValue' in value_obj:
        return float(value_obj['doubleValue'])
    elif 'booleanValue' in value_obj:
        return value_obj['booleanValue']
    elif 'stringListValue' in value_obj and 'values' in value_obj['stringListValue']:
        return ', '.join(value_obj['stringListValue']['values'])
    else:
        return None