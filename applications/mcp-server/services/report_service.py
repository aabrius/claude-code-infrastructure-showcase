"""
Report service - business logic for report generation.

This service is independent of MCP and can be tested without FastMCP.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ReportService:
    """
    Business logic for GAM report generation.

    Separates business logic from MCP tool definitions for testability.
    """

    VALID_REPORT_TYPES = {"delivery", "inventory", "sales", "reach", "programmatic"}

    def __init__(self, client, cache=None):
        """
        Initialize report service.

        Args:
            client: GAMClient instance for API calls
            cache: Optional cache manager for result caching
        """
        self.client = client
        self.cache = cache

    def quick_report(
        self,
        report_type: str,
        days_back: int = 30,
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        Generate a quick report with predefined configuration.

        Args:
            report_type: Type of report (delivery, inventory, sales, reach, programmatic)
            days_back: Number of days to look back
            format: Output format (json, csv, summary)

        Returns:
            Dict with report results

        Raises:
            ValueError: If report_type is invalid
        """
        if report_type not in self.VALID_REPORT_TYPES:
            raise ValueError(f"Unknown report type: {report_type}. Valid types: {self.VALID_REPORT_TYPES}")

        # Check cache first
        cache_key = f"quick_report:{report_type}:{days_back}:{format}"
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                logger.info(f"Cache hit for {cache_key}")
                return cached

        # Generate report using client
        from gam_api import DateRange
        date_range = DateRange.last_n_days(days_back)

        # Call appropriate report method
        report_methods = {
            "delivery": self.client.delivery_report,
            "inventory": self.client.inventory_report,
            "sales": self.client.sales_report,
            "reach": self.client.reach_report,
            "programmatic": self.client.programmatic_report,
        }

        result = report_methods[report_type](date_range)

        # Build response
        response = {
            "success": True,
            "report_type": report_type,
            "days_back": days_back,
            "total_rows": result.total_rows,
            "dimensions": result.dimension_headers,
            "metrics": result.metric_headers,
            "generated_at": datetime.now().isoformat(),
        }

        # Cache successful result
        if self.cache:
            self.cache.set(cache_key, response, ttl=1800)

        return response

    def list_reports(self, limit: int = 20) -> Dict[str, Any]:
        """
        List available reports.

        Args:
            limit: Maximum reports to return

        Returns:
            Dict with report list
        """
        reports = self.client.list_reports(limit=limit)

        simplified = []
        for report in reports:
            simplified.append({
                "id": report.get("reportId"),
                "name": report.get("displayName"),
                "created": report.get("createTime"),
                "updated": report.get("updateTime"),
            })

        return {
            "success": True,
            "total_reports": len(simplified),
            "reports": simplified,
        }

    def get_dimensions_metrics(
        self,
        report_type: str = "HISTORICAL",
        category: str = "both"
    ) -> Dict[str, Any]:
        """
        Get available dimensions and metrics.

        Args:
            report_type: Report type to get fields for
            category: What to return (dimensions, metrics, both)

        Returns:
            Dict with available fields
        """
        from gam_shared.validators import VALID_DIMENSIONS, VALID_METRICS, REACH_ONLY_METRICS

        result = {
            "success": True,
            "report_type": report_type,
        }

        if category in ["dimensions", "both"]:
            result["dimensions"] = sorted(list(VALID_DIMENSIONS))

        if category in ["metrics", "both"]:
            if report_type == "REACH":
                metrics = REACH_ONLY_METRICS.union(
                    {"TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS", "TOTAL_LINE_ITEM_LEVEL_CLICKS"}
                )
            else:
                metrics = VALID_METRICS - REACH_ONLY_METRICS
            result["metrics"] = sorted(list(metrics))

        return result

    def get_common_combinations(self) -> Dict[str, Any]:
        """
        Get common dimension-metric combinations.

        Returns:
            Dict with common combinations
        """
        combinations = {
            "delivery_analysis": {
                "description": "Analyze delivery performance by ad unit and time",
                "dimensions": ["DATE", "AD_UNIT_NAME", "LINE_ITEM_NAME"],
                "metrics": [
                    "TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS",
                    "TOTAL_LINE_ITEM_LEVEL_CLICKS",
                    "TOTAL_LINE_ITEM_LEVEL_CTR",
                ],
            },
            "inventory_analysis": {
                "description": "Analyze ad unit performance and fill rates",
                "dimensions": ["DATE", "AD_UNIT_NAME"],
                "metrics": [
                    "TOTAL_AD_REQUESTS",
                    "TOTAL_CODE_SERVED_COUNT",
                    "TOTAL_FILL_RATE",
                ],
            },
            "revenue_analysis": {
                "description": "Analyze revenue by advertiser and order",
                "dimensions": ["DATE", "ADVERTISER_NAME", "ORDER_NAME"],
                "metrics": [
                    "TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS",
                    "TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE",
                ],
            },
        }

        return {
            "success": True,
            "combinations": combinations,
        }

    def get_quick_report_types(self) -> Dict[str, Any]:
        """
        Get available quick report types.

        Returns:
            Dict with report type details
        """
        types = {
            "delivery": {
                "name": "Delivery Report",
                "description": "Impressions, clicks, CTR, revenue",
            },
            "inventory": {
                "name": "Inventory Report",
                "description": "Ad requests, fill rate, matched requests",
            },
            "sales": {
                "name": "Sales Report",
                "description": "Revenue, eCPM by advertiser/order",
            },
            "reach": {
                "name": "Reach Report",
                "description": "Unique reach, frequency by country/device",
            },
            "programmatic": {
                "name": "Programmatic Report",
                "description": "Programmatic channel performance",
            },
        }

        return {
            "success": True,
            "quick_report_types": types,
        }
