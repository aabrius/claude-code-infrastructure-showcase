"""
MCP tools for metadata operations (dimensions, metrics, etc.).
"""

import json
from typing import Dict, Any

from gam_shared.validators import VALID_DIMENSIONS, VALID_METRICS, REACH_ONLY_METRICS


async def handle_get_dimensions_metrics(args: Dict[str, Any]) -> str:
    """
    Get available dimensions and metrics for report creation.
    
    Args:
        args: Dictionary containing:
            - report_type: Type of report (optional)
            - category: What to return - dimensions, metrics, or both (optional)
    
    Returns:
        JSON string with dimensions and metrics
    """
    report_type = args.get("report_type", "HISTORICAL")
    category = args.get("category", "both")
    
    result = {
        "success": True,
        "report_type": report_type
    }
    
    if category in ["dimensions", "both"]:
        # Convert set to sorted list for JSON serialization
        dimensions_list = sorted(list(VALID_DIMENSIONS))
        
        # Categorize dimensions for better understanding
        categorized_dimensions = _categorize_dimensions(dimensions_list)
        
        result["dimensions"] = {
            "total_count": len(dimensions_list),
            "all_dimensions": dimensions_list,
            "by_category": categorized_dimensions
        }
    
    if category in ["metrics", "both"]:
        if report_type == "REACH":
            # Include reach-specific metrics
            metrics = REACH_ONLY_METRICS.union(
                {"TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS", "TOTAL_LINE_ITEM_LEVEL_CLICKS"}
            )
        else:
            # Exclude reach-only metrics for other report types
            metrics = VALID_METRICS - REACH_ONLY_METRICS
        
        metrics_list = sorted(list(metrics))
        
        # Categorize metrics for better understanding
        categorized_metrics = _categorize_metrics(metrics_list)
        
        result["metrics"] = {
            "total_count": len(metrics_list),
            "all_metrics": metrics_list,
            "by_category": categorized_metrics
        }
    
    # Add usage tips
    result["usage_tips"] = {
        "dimensions": "Dimensions define how data is grouped (e.g., by date, ad unit, advertiser)",
        "metrics": "Metrics are the values you want to measure (e.g., impressions, clicks, revenue)",
        "combinations": "Some dimension-metric combinations may not be available for all report types",
        "reach_reports": "REACH reports require specific dimensions and have unique metrics"
    }
    
    return json.dumps(result, indent=2)


def _categorize_dimensions(dimensions: list) -> Dict[str, list]:
    """Categorize dimensions by type for better understanding."""
    categories = {
        "time": [],
        "inventory": [],
        "order_line_item": [],
        "advertiser": [],
        "geographic": [],
        "device_browser": [],
        "creative": [],
        "programmatic": [],
        "other": []
    }
    
    for dim in dimensions:
        if any(x in dim for x in ["DATE", "WEEK", "MONTH", "YEAR"]):
            categories["time"].append(dim)
        elif any(x in dim for x in ["AD_UNIT", "PLACEMENT"]):
            categories["inventory"].append(dim)
        elif any(x in dim for x in ["ORDER", "LINE_ITEM"]):
            categories["order_line_item"].append(dim)
        elif "ADVERTISER" in dim:
            categories["advertiser"].append(dim)
        elif any(x in dim for x in ["COUNTRY", "REGION", "CITY", "METRO", "POSTAL"]):
            categories["geographic"].append(dim)
        elif any(x in dim for x in ["DEVICE", "BROWSER", "OPERATING_SYSTEM"]):
            categories["device_browser"].append(dim)
        elif "CREATIVE" in dim:
            categories["creative"].append(dim)
        elif "PROGRAMMATIC" in dim:
            categories["programmatic"].append(dim)
        else:
            categories["other"].append(dim)
    
    # Remove empty categories
    return {k: v for k, v in categories.items() if v}


def _categorize_metrics(metrics: list) -> Dict[str, list]:
    """Categorize metrics by type for better understanding."""
    categories = {
        "impressions": [],
        "clicks": [],
        "ctr": [],
        "revenue": [],
        "cpm_ecpm": [],
        "requests_fill": [],
        "programmatic": [],
        "reach": [],
        "other": []
    }
    
    for metric in metrics:
        if "IMPRESSION" in metric:
            categories["impressions"].append(metric)
        elif "CLICK" in metric and "CTR" not in metric:
            categories["clicks"].append(metric)
        elif "CTR" in metric:
            categories["ctr"].append(metric)
        elif any(x in metric for x in ["REVENUE", "CPM", "CPC"]):
            categories["revenue"].append(metric)
        elif any(x in metric for x in ["ECPM", "CPM"]):
            categories["cpm_ecpm"].append(metric)
        elif any(x in metric for x in ["REQUEST", "FILL", "MATCH"]):
            categories["requests_fill"].append(metric)
        elif "PROGRAMMATIC" in metric:
            categories["programmatic"].append(metric)
        elif any(x in metric for x in ["REACH", "FREQUENCY", "UNIQUE"]):
            categories["reach"].append(metric)
        else:
            categories["other"].append(metric)
    
    # Remove empty categories
    return {k: v for k, v in categories.items() if v}


async def handle_get_common_combinations(args: Dict[str, Any]) -> str:
    """
    Get common dimension-metric combinations for different use cases.
    
    Args:
        args: Dictionary containing request parameters
    
    Returns:
        JSON string with common combinations
    """
    combinations = {
        "delivery_analysis": {
            "description": "Analyze delivery performance by ad unit and time",
            "dimensions": ["DATE", "AD_UNIT_NAME", "LINE_ITEM_NAME"],
            "metrics": [
                "TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS",
                "TOTAL_LINE_ITEM_LEVEL_CLICKS",
                "TOTAL_LINE_ITEM_LEVEL_CTR",
                "TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE"
            ]
        },
        "inventory_analysis": {
            "description": "Analyze ad unit performance and fill rates",
            "dimensions": ["DATE", "AD_UNIT_NAME"],
            "metrics": [
                "TOTAL_AD_REQUESTS",
                "TOTAL_CODE_SERVED_COUNT",
                "TOTAL_FILL_RATE",
                "TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS"
            ]
        },
        "revenue_analysis": {
            "description": "Analyze revenue by advertiser and order",
            "dimensions": ["DATE", "ADVERTISER_NAME", "ORDER_NAME"],
            "metrics": [
                "TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS",
                "TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE",
                "TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM"
            ]
        },
        "geographic_analysis": {
            "description": "Analyze performance by geography",
            "dimensions": ["DATE", "COUNTRY_NAME", "REGION_NAME"],
            "metrics": [
                "TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS",
                "TOTAL_LINE_ITEM_LEVEL_CLICKS",
                "TOTAL_LINE_ITEM_LEVEL_CTR"
            ]
        },
        "device_analysis": {
            "description": "Analyze performance by device and browser",
            "dimensions": ["DATE", "DEVICE_CATEGORY_NAME", "BROWSER_NAME"],
            "metrics": [
                "TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS",
                "TOTAL_LINE_ITEM_LEVEL_CLICKS",
                "TOTAL_LINE_ITEM_LEVEL_CTR"
            ]
        },
        "programmatic_analysis": {
            "description": "Analyze programmatic performance",
            "dimensions": ["DATE", "PROGRAMMATIC_CHANNEL_NAME"],
            "metrics": [
                "TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS",
                "TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE",
                "PROGRAMMATIC_MATCH_RATE"
            ]
        }
    }
    
    response = {
        "success": True,
        "common_combinations": combinations,
        "usage": "Use these combinations as starting points for your custom reports",
        "note": "You can modify dimensions and metrics based on your specific needs"
    }
    
    return json.dumps(response, indent=2)