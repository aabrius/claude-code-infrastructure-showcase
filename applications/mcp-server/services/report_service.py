"""
Report service - business logic for report generation.

This service is independent of MCP and can be tested without FastMCP.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import time
import logging

logger = logging.getLogger(__name__)

# Server start time for uptime calculation
_server_start_time = time.time()

# Operation metrics tracking
_operation_metrics: Dict[str, Dict[str, Any]] = {}


class ReportService:
    """
    Business logic for GAM report generation.

    Separates business logic from MCP tool definitions for testability.
    """

    VALID_REPORT_TYPES = {"delivery", "inventory", "sales", "reach", "programmatic"}

    def __init__(self, client=None, cache=None, mock_mode: bool = False):
        """
        Initialize report service.

        Args:
            client: GAMClient instance for API calls (optional if mock_mode=True)
            cache: Optional cache manager for result caching
            mock_mode: If True, allow None client for testing metadata tools

        Raises:
            ValueError: If client is None and mock_mode is False
        """
        self.mock_mode = mock_mode
        if client is None and not mock_mode:
            raise ValueError(
                "Client cannot be None. Please provide a valid GAMClient instance. "
                "You can create one using: client = GAMClient.from_config(config). "
                "For testing, use mock_mode=True to enable metadata-only tools."
            )
        self.client = client
        self.cache = cache

    async def quick_report(
        self,
        report_type: str,
        days_back: int = 30,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        Generate a quick report with predefined configuration.

        Args:
            report_type: Type of report (delivery, inventory, sales, reach, programmatic)
            days_back: Number of days to look back (ignored if start_date/end_date provided)
            start_date: Explicit start date (YYYY-MM-DD)
            end_date: Explicit end date (YYYY-MM-DD)
            format: Output format (json, csv, summary)

        Returns:
            Dict with report results

        Raises:
            ValueError: If report_type is invalid or client unavailable
        """
        if self.mock_mode or self.client is None:
            return {
                "success": False,
                "error": "GAM client not available",
                "message": "Server running in mock mode. Configure GAM credentials for full functionality.",
                "available_in_mock": ["get_quick_report_types", "get_common_combinations", "get_dimensions_metrics"],
            }

        if report_type not in self.VALID_REPORT_TYPES:
            raise ValueError(f"Unknown report type: {report_type}. Valid types: {self.VALID_REPORT_TYPES}")

        # Build cache key
        if start_date and end_date:
            cache_key = f"quick_report:{report_type}:{start_date}:{end_date}:{format}"
        else:
            cache_key = f"quick_report:{report_type}:{days_back}:{format}"

        # Check cache first
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                logger.info(f"Cache hit for {cache_key}")
                return cached

        # Generate report using predefined configurations
        from datetime import datetime as dt, timedelta

        # Use explicit dates if provided, otherwise use days_back
        if start_date and end_date:
            start = dt.strptime(start_date, "%Y-%m-%d").date()
            end = dt.strptime(end_date, "%Y-%m-%d").date()
        else:
            end = dt.now().date() - timedelta(days=1)  # Yesterday
            start = end - timedelta(days=days_back)

        # Predefined report configurations (matches get_quick_report_types_enhanced)
        REPORT_CONFIGS = {
            "delivery": {
                "dimensions": ["DATE", "AD_UNIT_NAME", "ADVERTISER_NAME", "ORDER_NAME", "LINE_ITEM_NAME"],
                "metrics": ["AD_SERVER_IMPRESSIONS", "AD_SERVER_CLICKS", "AD_SERVER_CTR", "AD_SERVER_CPM_AND_CPC_REVENUE"],
                "report_type": "HISTORICAL",
            },
            "inventory": {
                "dimensions": ["DATE", "AD_UNIT_NAME", "AD_UNIT_ID"],
                "metrics": ["TOTAL_AD_REQUESTS", "TOTAL_RESPONSES_SERVED", "TOTAL_FILL_RATE", "TOTAL_INVENTORY_LEVEL_UNFILLED_IMPRESSIONS"],
                "report_type": "HISTORICAL",
            },
            "sales": {
                "dimensions": ["DATE", "ADVERTISER_NAME", "ORDER_NAME", "SALESPERSON_NAME"],
                "metrics": ["AD_SERVER_CPM_AND_CPC_REVENUE", "AD_SERVER_IMPRESSIONS", "AD_SERVER_WITHOUT_CPD_AVERAGE_ECPM"],
                "report_type": "HISTORICAL",
            },
            "reach": {
                "dimensions": ["DATE", "COUNTRY_NAME", "DEVICE_CATEGORY_NAME"],
                "metrics": ["UNIQUE_REACH", "UNIQUE_REACH_FREQUENCY", "UNIQUE_REACH_IMPRESSIONS"],
                "report_type": "REACH",
            },
            "programmatic": {
                "dimensions": ["DATE", "DEMAND_CHANNEL_NAME", "BUYER_NETWORK_NAME"],
                "metrics": ["AD_EXCHANGE_LINE_ITEM_LEVEL_IMPRESSIONS", "AD_EXCHANGE_LINE_ITEM_LEVEL_REVENUE", "AD_EXCHANGE_LINE_ITEM_LEVEL_AVERAGE_ECPM"],
                "report_type": "HISTORICAL",
            },
        }

        config = REPORT_CONFIGS[report_type]

        # Build report definition for REST API
        report_definition = {
            "displayName": f"Quick {report_type.title()} Report - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "reportDefinition": {
                "dimensions": config["dimensions"],
                "metrics": config["metrics"],
                "dateRange": {
                    "fixed": {
                        "startDate": {"year": start.year, "month": start.month, "day": start.day},
                        "endDate": {"year": end.year, "month": end.month, "day": end.day},
                    }
                },
                "reportType": config["report_type"],
            },
        }

        try:
            # Create the report using unified client
            result = await self.client._unified_client.create_report(report_definition)

            # Build response
            response = {
                "success": True,
                "report_type": report_type,
                "days_back": days_back,
                "report_id": result.get("reportId") or result.get("name", "").split("/")[-1],
                "report_name": result.get("name"),
                "dimensions": config["dimensions"],
                "metrics": config["metrics"],
                "date_range": {"start": start.isoformat(), "end": end.isoformat()},
                "generated_at": datetime.now().isoformat(),
                "message": "Report created. Use run_report to execute and get results.",
            }

            # Cache successful result
            if self.cache:
                self.cache.set(cache_key, response, ttl=1800)

            return response

        except Exception as e:
            logger.exception("Quick report creation failed")
            return {
                "success": False,
                "error": "Quick report creation failed",
                "message": str(e),
            }

    def list_reports(self, limit: int = 20) -> Dict[str, Any]:
        """
        List available reports.

        Args:
            limit: Maximum reports to return

        Returns:
            Dict with report list
        """
        if self.mock_mode or self.client is None:
            return {
                "success": False,
                "error": "GAM client not available",
                "message": "Server running in mock mode. Configure GAM credentials for full functionality.",
            }

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
            Dict with available fields using DimensionsMetricsResponse model
        """
        from gam_shared.dimensions_metrics import (
            ALL_DIMENSIONS, ALL_METRICS, REACH_METRICS,
            get_metrics_for_report_type, ReportType,
            DimensionsMetricsResponse,
        )

        # Convert string to ReportType enum if needed
        try:
            rt = ReportType(report_type.upper()) if isinstance(report_type, str) else report_type
        except ValueError:
            rt = ReportType.HISTORICAL

        dimensions = None
        metrics = None

        if category in ["dimensions", "both"]:
            dimensions = sorted(list(ALL_DIMENSIONS))

        if category in ["metrics", "both"]:
            valid_metrics = get_metrics_for_report_type(rt)
            metrics = sorted(list(valid_metrics))

        response = DimensionsMetricsResponse(
            success=True,
            report_type=report_type,
            dimensions=dimensions,
            metrics=metrics,
            dimension_count=len(dimensions) if dimensions else None,
            metric_count=len(metrics) if metrics else None,
        )

        return response.model_dump(exclude_none=True)

    def get_common_combinations(self) -> Dict[str, Any]:
        """
        Get common dimension-metric combinations.

        Returns:
            Dict with common combinations using Pydantic models
        """
        from gam_shared.dimensions_metrics import get_common_combinations as get_combinations

        # Get predefined combinations from the centralized module
        combinations = get_combinations()

        # Convert to dict format for JSON response
        combinations_dict = {}
        for combo in combinations:
            combinations_dict[combo.name] = {
                "description": combo.description,
                "dimensions": combo.dimensions,
                "metrics": combo.metrics,
                "report_type": combo.report_type.value,
            }

        return {
            "success": True,
            "combinations": combinations_dict,
            "total_combinations": len(combinations_dict),
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

    async def create_report(
        self,
        name: str,
        dimensions: list,
        metrics: list,
        start_date: str,
        end_date: str,
        report_type: str = "HISTORICAL",
        run_immediately: bool = True,
    ) -> Dict[str, Any]:
        """
        Create a custom report with specified dimensions and metrics.

        Args:
            name: Report name
            dimensions: List of dimension names
            metrics: List of metric names
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            report_type: Report type (HISTORICAL, REACH, AD_SPEED)
            run_immediately: Whether to run the report immediately

        Returns:
            Dict with report results or creation status
        """
        if self.mock_mode or self.client is None:
            return {
                "success": False,
                "error": "GAM client not available",
                "message": "Server running in mock mode. Configure GAM credentials for full functionality.",
            }

        # Note: Skip client-side validation - REST API v1 uses different metric names than SOAP
        # Let the REST API validate dimensions/metrics directly
        validated_dims = [d.upper() for d in dimensions]
        validated_metrics = [m.upper() for m in metrics]

        # Parse dates
        from datetime import datetime as dt

        try:
            start = dt.strptime(start_date, "%Y-%m-%d").date()
            end = dt.strptime(end_date, "%Y-%m-%d").date()
        except ValueError as e:
            return {
                "success": False,
                "error": "Invalid date format",
                "message": f"Use YYYY-MM-DD format. Error: {e}",
            }

        # Create report definition
        from gam_api.models import ReportDefinition, DateRange, DateRangeType

        date_range = DateRange(
            start_date=start,
            end_date=end,
            date_range_type=DateRangeType.CUSTOM,
        )

        report_def = ReportDefinition(
            name=name,
            dimensions=validated_dims,
            metrics=validated_metrics,
            date_range=date_range,
            report_type=report_type,  # Use string directly (HISTORICAL, REACH, AD_SPEED)
        )

        # Create report using the unified client
        try:
            # Build report definition for REST API
            # Per GAM API v1 spec, dateRange uses fixed/relative wrapper
            report_definition = {
                "displayName": name,
                "reportDefinition": {
                    "dimensions": validated_dims,
                    "metrics": validated_metrics,
                    "dateRange": {
                        "fixed": {
                            "startDate": {"year": start.year, "month": start.month, "day": start.day},
                            "endDate": {"year": end.year, "month": end.month, "day": end.day},
                        }
                    },
                    "reportType": report_type,
                },
            }

            # Use the unified client's async method to create the report
            result = await self.client._unified_client.create_report(report_definition)

            response = {
                "success": True,
                "action": "created",
                "report_id": result.get("reportId") or result.get("name", "").split("/")[-1],
                "name": name,
                "dimensions": validated_dims,
                "metrics": validated_metrics,
                "date_range": {"start": start_date, "end": end_date},
                "report_type": report_type,
                "created_at": datetime.now().isoformat(),
                "raw_response": result,
            }

            return response

        except Exception as e:
            logger.exception("Report creation failed")
            return {
                "success": False,
                "error": "Report creation failed",
                "message": str(e),
            }

    async def run_report(
        self,
        report_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute an existing saved report.

        Args:
            report_id: ID of the saved report to run
            start_date: Optional date override (YYYY-MM-DD)
            end_date: Optional date override (YYYY-MM-DD)

        Returns:
            Dict with execution status and results
        """
        if self.mock_mode or self.client is None:
            return {
                "success": False,
                "error": "GAM client not available",
                "message": "Server running in mock mode. Configure GAM credentials for full functionality.",
            }

        start_time = time.time()

        try:
            # Build date override if provided
            date_override = None
            if start_date and end_date:
                from datetime import datetime as dt
                start = dt.strptime(start_date, "%Y-%m-%d").date()
                end = dt.strptime(end_date, "%Y-%m-%d").date()
                date_override = {
                    "fixed": {
                        "startDate": {"year": start.year, "month": start.month, "day": start.day},
                        "endDate": {"year": end.year, "month": end.month, "day": end.day},
                    }
                }

            # Run the report
            result = await self.client._unified_client.run_report(report_id, date_override=date_override)

            execution_time = time.time() - start_time

            return {
                "success": True,
                "report_id": report_id,
                "status": result.get("state", "COMPLETED"),
                "total_rows": result.get("rowCount", 0),
                "execution_time": round(execution_time, 2),
                "data_preview": result.get("rows", [])[:10] if result.get("rows") else None,
            }

        except Exception as e:
            logger.exception(f"Run report failed for {report_id}")
            return {
                "success": False,
                "report_id": report_id,
                "error": "Report execution failed",
                "message": str(e),
            }

    def get_report_types(self) -> Dict[str, Any]:
        """
        Get available report types and their descriptions.

        Returns:
            Dict with report type details for HISTORICAL, REACH, AD_SPEED
        """
        report_types = {
            "HISTORICAL": {
                "name": "Historical",
                "description": "Standard historical reports with delivery and performance metrics. Most common report type.",
                "supported_metrics": "Most standard metrics including impressions, clicks, CTR, revenue, fill rate",
                "use_cases": [
                    "Campaign performance tracking",
                    "Revenue analysis",
                    "Inventory reporting",
                    "Advertiser reports"
                ]
            },
            "REACH": {
                "name": "Reach",
                "description": "Audience reach and frequency reports. Measures unique users reached.",
                "supported_metrics": "UNIQUE_REACH, UNIQUE_REACH_FREQUENCY, UNIQUE_REACH_IMPRESSIONS",
                "use_cases": [
                    "Audience measurement",
                    "Frequency cap analysis",
                    "Campaign reach optimization",
                    "Geographic reach analysis"
                ]
            },
            "AD_SPEED": {
                "name": "Ad Speed",
                "description": "Ad loading speed and performance reports. Measures creative load times.",
                "supported_metrics": "Load time percentiles (0-500ms, 500ms-1s, 1-2s, 2-4s, 4-8s, >8s)",
                "use_cases": [
                    "Creative performance optimization",
                    "Load time monitoring",
                    "User experience analysis"
                ]
            }
        }

        return {
            "success": True,
            "report_types": report_types,
            "total_types": len(report_types),
        }

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get server performance statistics.

        Returns:
            Dict with server stats, operation metrics, cache stats
        """
        uptime_seconds = time.time() - _server_start_time
        uptime_hours = uptime_seconds / 3600
        uptime_days = uptime_seconds / 86400

        if uptime_days >= 1:
            uptime_human = f"{uptime_days:.1f} days"
        elif uptime_hours >= 1:
            uptime_human = f"{uptime_hours:.1f} hours"
        else:
            uptime_human = f"{uptime_seconds:.0f} seconds"

        # Get cache stats if available
        cache_stats = None
        if self.cache:
            try:
                stats = self.cache.get_stats()
                cache_stats = {
                    "hits": stats.get("hits", 0),
                    "misses": stats.get("misses", 0),
                    "hit_rate": stats.get("hit_rate", 0.0),
                    "total_size_mb": stats.get("size_mb", 0.0),
                }
            except Exception:
                cache_stats = {"error": "Unable to retrieve cache stats"}

        return {
            "success": True,
            "server_stats": {
                "uptime_seconds": round(uptime_seconds),
                "uptime_human": uptime_human,
                "start_time": datetime.fromtimestamp(_server_start_time).isoformat(),
            },
            "operation_performance": _operation_metrics,
            "cache_stats": cache_stats,
            "circuit_breaker_state": "CLOSED",  # TODO: Implement actual circuit breaker tracking
        }

    def list_reports_enhanced(
        self,
        limit: int = 20,
        page: int = 1,
        search: Optional[str] = None,
        report_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List available reports with enhanced filtering and pagination.

        Args:
            limit: Maximum reports per page
            page: Page number (1-indexed)
            search: Filter reports by name (case-insensitive)
            report_type: Filter by report type

        Returns:
            Dict with paginated report list
        """
        if self.mock_mode or self.client is None:
            return {
                "success": False,
                "error": "GAM client not available",
                "message": "Server running in mock mode. Configure GAM credentials for full functionality.",
            }

        # Get more reports for filtering/pagination
        fetch_limit = limit * page * 2  # Fetch extra to handle filtering
        reports = self.client.list_reports(limit=fetch_limit)

        # Apply filters
        filtered = []
        for report in reports:
            name = report.get("displayName", "")
            rtype = report.get("reportType", "")

            # Apply search filter
            if search and search.lower() not in name.lower():
                continue

            # Apply report type filter
            if report_type and report_type.upper() != rtype.upper():
                continue

            filtered.append({
                "id": report.get("reportId"),
                "name": name,
                "report_type": rtype,
                "created": report.get("createTime"),
                "updated": report.get("updateTime"),
            })

        # Apply pagination
        total_reports = len(filtered)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        page_reports = filtered[start_idx:end_idx]

        total_pages = (total_reports + limit - 1) // limit if total_reports > 0 else 1

        return {
            "success": True,
            "total_reports": total_reports,
            "reports": page_reports,
            "page": page,
            "page_size": limit,
            "total_pages": total_pages,
        }

    def get_quick_report_types_enhanced(self) -> Dict[str, Any]:
        """
        Get available quick report types with dimensions and metrics.

        Returns:
            Dict with report type details including dimensions and metrics
        """
        types = {
            "delivery": {
                "name": "Delivery Report",
                "description": "Track impressions, clicks, CTR, and revenue by ad unit and advertiser",
                "dimensions": ["DATE", "AD_UNIT_NAME", "ADVERTISER_NAME", "ORDER_NAME", "LINE_ITEM_NAME"],
                "metrics": ["AD_SERVER_IMPRESSIONS", "AD_SERVER_CLICKS", "AD_SERVER_CTR", "AD_SERVER_CPM_AND_CPC_REVENUE"],
            },
            "inventory": {
                "name": "Inventory Report",
                "description": "Monitor ad inventory utilization and fill rates",
                "dimensions": ["DATE", "AD_UNIT_NAME", "AD_UNIT_ID"],
                "metrics": ["TOTAL_AD_REQUESTS", "TOTAL_RESPONSES_SERVED", "TOTAL_FILL_RATE", "TOTAL_INVENTORY_LEVEL_UNFILLED_IMPRESSIONS"],
            },
            "sales": {
                "name": "Sales Report",
                "description": "Analyze revenue by advertiser, order, and salesperson",
                "dimensions": ["DATE", "ADVERTISER_NAME", "ORDER_NAME", "SALESPERSON_NAME"],
                "metrics": ["AD_SERVER_CPM_AND_CPC_REVENUE", "AD_SERVER_IMPRESSIONS", "AD_SERVER_WITHOUT_CPD_AVERAGE_ECPM"],
            },
            "reach": {
                "name": "Reach Report",
                "description": "Measure unique audience reach and frequency (requires REACH report type)",
                "dimensions": ["DATE", "COUNTRY_NAME", "DEVICE_CATEGORY_NAME"],
                "metrics": ["UNIQUE_REACH", "UNIQUE_REACH_FREQUENCY", "UNIQUE_REACH_IMPRESSIONS"],
            },
            "programmatic": {
                "name": "Programmatic Report",
                "description": "Track programmatic/exchange revenue and performance",
                "dimensions": ["DATE", "DEMAND_CHANNEL_NAME", "BUYER_NETWORK_NAME"],
                "metrics": ["AD_EXCHANGE_LINE_ITEM_LEVEL_IMPRESSIONS", "AD_EXCHANGE_LINE_ITEM_LEVEL_REVENUE", "AD_EXCHANGE_LINE_ITEM_LEVEL_AVERAGE_ECPM"],
            },
        }

        return {
            "success": True,
            "quick_report_types": types,
        }

    def get_dimensions_metrics_enhanced(
        self,
        report_type: str = "HISTORICAL",
        category: str = "both"
    ) -> Dict[str, Any]:
        """
        Get available dimensions and metrics with detailed info.

        Args:
            report_type: Report type to get fields for
            category: What to return (dimensions, metrics, both)

        Returns:
            Dict with detailed dimension/metric information
        """
        from gam_shared.dimensions_metrics import (
            ALL_DIMENSIONS, get_metrics_for_report_type, ReportType,
        )

        # Dimension metadata
        DIMENSION_INFO = {
            "DATE": {"name": "Date", "description": "Report date (YYYY-MM-DD)", "category": "time"},
            "HOUR": {"name": "Hour", "description": "Hour of day (0-23)", "category": "time"},
            "WEEK": {"name": "Week", "description": "Week number", "category": "time"},
            "MONTH": {"name": "Month", "description": "Month (YYYY-MM)", "category": "time"},
            "AD_UNIT_ID": {"name": "Ad Unit ID", "description": "Ad unit unique identifier", "category": "inventory"},
            "AD_UNIT_NAME": {"name": "Ad Unit", "description": "Ad unit name", "category": "inventory"},
            "ADVERTISER_ID": {"name": "Advertiser ID", "description": "Advertiser unique identifier", "category": "advertiser"},
            "ADVERTISER_NAME": {"name": "Advertiser", "description": "Advertiser name", "category": "advertiser"},
            "ORDER_ID": {"name": "Order ID", "description": "Order unique identifier", "category": "order"},
            "ORDER_NAME": {"name": "Order", "description": "Order name", "category": "order"},
            "LINE_ITEM_ID": {"name": "Line Item ID", "description": "Line item unique identifier", "category": "line_item"},
            "LINE_ITEM_NAME": {"name": "Line Item", "description": "Line item name", "category": "line_item"},
            "CREATIVE_ID": {"name": "Creative ID", "description": "Creative unique identifier", "category": "creative"},
            "CREATIVE_NAME": {"name": "Creative", "description": "Creative name", "category": "creative"},
            "COUNTRY_NAME": {"name": "Country", "description": "Country name", "category": "geography"},
            "REGION_NAME": {"name": "Region", "description": "Region/state name", "category": "geography"},
            "CITY_NAME": {"name": "City", "description": "City name", "category": "geography"},
            "DEVICE_CATEGORY_NAME": {"name": "Device Category", "description": "Device type (Desktop, Mobile, Tablet)", "category": "device"},
            "BROWSER_NAME": {"name": "Browser", "description": "Browser name", "category": "device"},
            "OS_NAME": {"name": "Operating System", "description": "OS name", "category": "device"},
            "DEMAND_CHANNEL_NAME": {"name": "Demand Channel", "description": "Demand source channel", "category": "programmatic"},
            "BUYER_NETWORK_NAME": {"name": "Buyer Network", "description": "Programmatic buyer network", "category": "programmatic"},
            "SALESPERSON_NAME": {"name": "Salesperson", "description": "Salesperson name", "category": "sales"},
        }

        # Metric metadata
        METRIC_INFO = {
            "AD_SERVER_IMPRESSIONS": {"name": "Impressions", "description": "Ad server impressions", "type": "integer"},
            "AD_SERVER_CLICKS": {"name": "Clicks", "description": "Ad server clicks", "type": "integer"},
            "AD_SERVER_CTR": {"name": "CTR", "description": "Click-through rate", "type": "percentage"},
            "AD_SERVER_CPM_AND_CPC_REVENUE": {"name": "Revenue", "description": "CPM and CPC revenue", "type": "currency"},
            "AD_SERVER_WITHOUT_CPD_AVERAGE_ECPM": {"name": "eCPM", "description": "Average eCPM (without CPD)", "type": "currency"},
            "TOTAL_AD_REQUESTS": {"name": "Ad Requests", "description": "Total ad requests", "type": "integer"},
            "TOTAL_RESPONSES_SERVED": {"name": "Responses Served", "description": "Total responses served", "type": "integer"},
            "TOTAL_FILL_RATE": {"name": "Fill Rate", "description": "Fill rate percentage", "type": "percentage"},
            "TOTAL_INVENTORY_LEVEL_UNFILLED_IMPRESSIONS": {"name": "Unfilled", "description": "Unfilled impressions", "type": "integer"},
            "UNIQUE_REACH": {"name": "Unique Reach", "description": "Unique users reached", "type": "integer"},
            "UNIQUE_REACH_FREQUENCY": {"name": "Frequency", "description": "Average frequency per user", "type": "decimal"},
            "UNIQUE_REACH_IMPRESSIONS": {"name": "Reach Impressions", "description": "Impressions for reach calculation", "type": "integer"},
            "AD_EXCHANGE_LINE_ITEM_LEVEL_IMPRESSIONS": {"name": "Exchange Impressions", "description": "Ad Exchange impressions", "type": "integer"},
            "AD_EXCHANGE_LINE_ITEM_LEVEL_REVENUE": {"name": "Exchange Revenue", "description": "Ad Exchange revenue", "type": "currency"},
            "AD_EXCHANGE_LINE_ITEM_LEVEL_AVERAGE_ECPM": {"name": "Exchange eCPM", "description": "Ad Exchange average eCPM", "type": "currency"},
        }

        # Convert string to ReportType enum
        try:
            rt = ReportType(report_type.upper()) if isinstance(report_type, str) else report_type
        except ValueError:
            rt = ReportType.HISTORICAL

        dimensions = None
        metrics = None

        if category in ["dimensions", "both"]:
            dimensions = []
            for dim in sorted(ALL_DIMENSIONS):
                info = DIMENSION_INFO.get(dim, {
                    "name": dim.replace("_", " ").title(),
                    "description": f"{dim} dimension",
                    "category": "other"
                })
                dimensions.append({
                    "id": dim,
                    "name": info["name"],
                    "description": info["description"],
                    "category": info["category"],
                })

        if category in ["metrics", "both"]:
            valid_metrics = get_metrics_for_report_type(rt)
            metrics = []
            for metric in sorted(valid_metrics):
                info = METRIC_INFO.get(metric, {
                    "name": metric.replace("_", " ").title(),
                    "description": f"{metric} metric",
                    "type": "number"
                })
                metrics.append({
                    "id": metric,
                    "name": info["name"],
                    "description": info["description"],
                    "type": info["type"],
                })

        return {
            "success": True,
            "report_type": report_type,
            "dimensions": dimensions,
            "metrics": metrics,
            "dimension_count": len(dimensions) if dimensions else None,
            "metric_count": len(metrics) if metrics else None,
        }


    async def get_report(self, report_id: str) -> Dict[str, Any]:
        """
        Get details of a specific report by ID.

        Args:
            report_id: ID of the report to retrieve

        Returns:
            Dict with report details
        """
        if self.mock_mode or self.client is None:
            return {
                "success": False,
                "error": "GAM client not available",
                "message": "Server running in mock mode. Configure GAM credentials for full functionality.",
            }

        try:
            result = await self.client._unified_client.get_report(report_id)

            # Extract report definition
            report_def = result.get("reportDefinition", {})

            return {
                "success": True,
                "report_id": report_id,
                "name": result.get("displayName"),
                "report_type": report_def.get("reportType", "HISTORICAL"),
                "dimensions": report_def.get("dimensions", []),
                "metrics": report_def.get("metrics", []),
                "date_range": report_def.get("dateRange"),
                "filters": report_def.get("filters", []),
                "labels": result.get("labels", []),
                "schedule": result.get("scheduleOptions"),
                "created_at": result.get("createTime"),
                "updated_at": result.get("updateTime"),
                "last_run_at": result.get("lastRunTime"),
            }
        except Exception as e:
            logger.exception(f"Get report failed for {report_id}")
            return {
                "success": False,
                "report_id": report_id,
                "error": "Failed to get report",
                "message": str(e),
            }

    async def update_report(
        self,
        report_id: str,
        name: Optional[str] = None,
        dimensions: Optional[List[str]] = None,
        metrics: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update an existing report.

        Args:
            report_id: ID of the report to update
            name: New display name (optional)
            dimensions: New dimensions list (optional)
            metrics: New metrics list (optional)
            start_date: New start date (optional, YYYY-MM-DD)
            end_date: New end date (optional, YYYY-MM-DD)

        Returns:
            Dict with update result
        """
        if self.mock_mode or self.client is None:
            return {
                "success": False,
                "error": "GAM client not available",
                "message": "Server running in mock mode. Configure GAM credentials for full functionality.",
            }

        try:
            # Build update mask and body
            update_fields = []
            update_body = {}

            if name:
                update_body["displayName"] = name
                update_fields.append("displayName")

            # Build report definition updates
            report_def_updates = {}

            if dimensions:
                report_def_updates["dimensions"] = [d.upper() for d in dimensions]
                update_fields.append("dimensions")

            if metrics:
                report_def_updates["metrics"] = [m.upper() for m in metrics]
                update_fields.append("metrics")

            if start_date and end_date:
                from datetime import datetime as dt
                start = dt.strptime(start_date, "%Y-%m-%d").date()
                end = dt.strptime(end_date, "%Y-%m-%d").date()
                report_def_updates["dateRange"] = {
                    "fixed": {
                        "startDate": {"year": start.year, "month": start.month, "day": start.day},
                        "endDate": {"year": end.year, "month": end.month, "day": end.day},
                    }
                }
                update_fields.append("dateRange")

            if report_def_updates:
                update_body["reportDefinition"] = report_def_updates

            if not update_fields:
                return {
                    "success": False,
                    "report_id": report_id,
                    "error": "No fields to update",
                    "message": "Provide at least one field to update (name, dimensions, metrics, or date range)",
                }

            # Call API to update
            result = await self.client._unified_client.update_report(report_id, update_body)

            return {
                "success": True,
                "report_id": report_id,
                "updated_fields": update_fields,
                "name": result.get("displayName"),
                "dimensions": result.get("reportDefinition", {}).get("dimensions"),
                "metrics": result.get("reportDefinition", {}).get("metrics"),
                "message": f"Successfully updated {len(update_fields)} field(s)",
            }
        except Exception as e:
            logger.exception(f"Update report failed for {report_id}")
            return {
                "success": False,
                "report_id": report_id,
                "error": "Failed to update report",
                "message": str(e),
            }

    async def delete_report(self, report_id: str) -> Dict[str, Any]:
        """
        Delete a report.

        Args:
            report_id: ID of the report to delete

        Returns:
            Dict with deletion result
        """
        if self.mock_mode or self.client is None:
            return {
                "success": False,
                "error": "GAM client not available",
                "message": "Server running in mock mode. Configure GAM credentials for full functionality.",
            }

        try:
            await self.client._unified_client.delete_report(report_id)

            return {
                "success": True,
                "report_id": report_id,
                "deleted": True,
                "message": f"Report {report_id} deleted successfully",
            }
        except Exception as e:
            logger.exception(f"Delete report failed for {report_id}")
            return {
                "success": False,
                "report_id": report_id,
                "deleted": False,
                "error": "Failed to delete report",
                "message": str(e),
            }

    async def add_report_label(
        self,
        report_id: str,
        labels: List[str],
    ) -> Dict[str, Any]:
        """
        Add labels to a report.

        Args:
            report_id: ID of the report
            labels: Labels to add

        Returns:
            Dict with label operation result
        """
        if self.mock_mode or self.client is None:
            return {
                "success": False,
                "error": "GAM client not available",
                "message": "Server running in mock mode. Configure GAM credentials for full functionality.",
            }

        try:
            # First get current labels
            current_report = await self.client._unified_client.get_report(report_id)
            current_labels = set(current_report.get("labels", []))

            # Determine which labels to add
            new_labels = set(labels)
            already_present = current_labels & new_labels
            to_add = new_labels - current_labels

            # Update with combined labels
            all_labels = list(current_labels | new_labels)

            if to_add:
                update_body = {"labels": all_labels}
                await self.client._unified_client.update_report(report_id, update_body)

            return {
                "success": True,
                "report_id": report_id,
                "labels": all_labels,
                "added": list(to_add),
                "already_present": list(already_present),
                "message": f"Added {len(to_add)} label(s)" if to_add else "All labels already present",
            }
        except Exception as e:
            logger.exception(f"Add label failed for {report_id}")
            return {
                "success": False,
                "report_id": report_id,
                "error": "Failed to add labels",
                "message": str(e),
            }


def track_operation(operation_name: str, duration_ms: float, error: bool = False):
    """Track operation metrics for performance stats."""
    global _operation_metrics

    if operation_name not in _operation_metrics:
        _operation_metrics[operation_name] = {
            "count": 0,
            "errors": 0,
            "total_time_ms": 0.0,
            "times": [],
        }

    metrics = _operation_metrics[operation_name]
    metrics["count"] += 1
    if error:
        metrics["errors"] += 1
    metrics["total_time_ms"] += duration_ms
    metrics["times"].append(duration_ms)

    # Keep only last 100 times for percentile calculation
    if len(metrics["times"]) > 100:
        metrics["times"] = metrics["times"][-100:]

    # Calculate avg and percentiles
    times = sorted(metrics["times"])
    metrics["avg_time_ms"] = round(metrics["total_time_ms"] / metrics["count"], 2)
    if len(times) > 0:
        metrics["p50_ms"] = round(times[len(times) // 2], 2)
        metrics["p95_ms"] = round(times[int(len(times) * 0.95)], 2) if len(times) > 1 else metrics["p50_ms"]
        metrics["p99_ms"] = round(times[int(len(times) * 0.99)], 2) if len(times) > 1 else metrics["p50_ms"]
