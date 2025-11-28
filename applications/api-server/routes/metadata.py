"""
Metadata API endpoints for dimensions, metrics, and combinations.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional

from models import (
    DimensionsMetricsResponse,
    CommonCombinationsResponse, CommonCombination,
    SuccessResponse, ReportTypeEnum
)
from gam_shared.validators import VALID_DIMENSIONS, VALID_METRICS, REACH_ONLY_METRICS
from gam_shared.logger import get_structured_logger

logger = get_structured_logger('api_metadata')
router = APIRouter()


@router.get("/dimensions-metrics", response_model=DimensionsMetricsResponse)
async def get_dimensions_metrics(
    report_type: ReportTypeEnum = Query(default=ReportTypeEnum.HISTORICAL),
    category: str = Query(default="both", regex="^(dimensions|metrics|both)$")
):
    """
    Get available dimensions and metrics for report creation.
    
    Args:
        report_type: Type of report (HISTORICAL, REACH, AD_SPEED)
        category: What to return (dimensions, metrics, both)
    
    Returns:
        Available dimensions and/or metrics based on report type
    """
    try:
        logger.log_function_call("get_dimensions_metrics", kwargs={
            "report_type": report_type.value,
            "category": category
        })
        
        response_data = {
            "report_type": report_type.value
        }
        
        if category in ["dimensions", "both"]:
            # Convert set to sorted list for JSON serialization
            response_data["dimensions"] = sorted(list(VALID_DIMENSIONS))
        
        if category in ["metrics", "both"]:
            if report_type == ReportTypeEnum.REACH:
                # Include reach-specific metrics
                metrics = REACH_ONLY_METRICS.union({
                    "TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS", 
                    "TOTAL_LINE_ITEM_LEVEL_CLICKS"
                })
            else:
                # Exclude reach-only metrics for other report types
                metrics = VALID_METRICS - REACH_ONLY_METRICS
            
            response_data["metrics"] = sorted(list(metrics))
        
        response = DimensionsMetricsResponse(**response_data)
        
        logger.logger.info(f"Retrieved {category} for {report_type.value} reports")
        return response
        
    except Exception as e:
        logger.logger.error(f"Error getting dimensions/metrics: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/combinations", response_model=CommonCombinationsResponse)
async def get_common_combinations():
    """
    Get common dimension-metric combinations for different use cases.
    
    Returns predefined combinations that work well together for various
    reporting scenarios.
    """
    try:
        logger.log_function_call("get_common_combinations")
        
        combinations = [
            CommonCombination(
                name="Basic Delivery",
                description="Basic delivery metrics by date and ad unit",
                dimensions=["DATE", "AD_UNIT_NAME"],
                metrics=["TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS", "TOTAL_LINE_ITEM_LEVEL_CLICKS"],
                use_case="Daily performance tracking"
            ),
            CommonCombination(
                name="Advertiser Performance",
                description="Performance metrics grouped by advertiser",
                dimensions=["DATE", "ADVERTISER_NAME", "ORDER_NAME"],
                metrics=["TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS", "TOTAL_LINE_ITEM_LEVEL_CLICKS", "TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE"],
                use_case="Advertiser revenue analysis"
            ),
            CommonCombination(
                name="Inventory Analysis",
                description="Ad unit inventory performance",
                dimensions=["DATE", "AD_UNIT_NAME"],
                metrics=["TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS", "UNFILLED_IMPRESSIONS", "AD_REQUESTS"],
                use_case="Inventory optimization"
            ),
            CommonCombination(
                name="Geographic Performance",
                description="Performance by geographic location",
                dimensions=["DATE", "COUNTRY_NAME", "REGION_NAME"],
                metrics=["TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS", "TOTAL_LINE_ITEM_LEVEL_CLICKS"],
                use_case="Geographic targeting analysis"
            ),
            CommonCombination(
                name="Device Analysis",
                description="Performance across different device types",
                dimensions=["DATE", "DEVICE_CATEGORY_NAME", "MOBILE_DEVICE_NAME"],
                metrics=["TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS", "TOTAL_LINE_ITEM_LEVEL_CLICKS"],
                use_case="Device targeting optimization"
            ),
            CommonCombination(
                name="Creative Performance",
                description="Creative and line item performance",
                dimensions=["DATE", "LINE_ITEM_NAME", "CREATIVE_NAME"],
                metrics=["TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS", "TOTAL_LINE_ITEM_LEVEL_CLICKS", "TOTAL_LINE_ITEM_LEVEL_CTR"],
                use_case="Creative optimization"
            ),
            CommonCombination(
                name="Revenue Analysis",
                description="Detailed revenue breakdown",
                dimensions=["DATE", "ADVERTISER_NAME", "LINE_ITEM_TYPE"],
                metrics=["TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS", "TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE", "TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM"],
                use_case="Revenue optimization"
            ),
            CommonCombination(
                name="Programmatic Overview",
                description="Programmatic channel performance",
                dimensions=["DATE", "DEMAND_CHANNEL_NAME"],
                metrics=["TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS", "TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE"],
                use_case="Programmatic revenue analysis"
            )
        ]
        
        response = CommonCombinationsResponse(
            message="Common combinations retrieved successfully",
            data={},
            combinations=combinations
        )
        
        logger.logger.info(f"Retrieved {len(combinations)} common combinations")
        return response
        
    except Exception as e:
        logger.logger.error(f"Error getting common combinations: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/report-types", response_model=SuccessResponse)
async def get_report_types():
    """
    Get available report types and their descriptions.
    """
    try:
        report_types = {
            "HISTORICAL": {
                "name": "Historical",
                "description": "Standard historical reports with delivery and performance metrics",
                "supported_metrics": "Most standard metrics"
            },
            "REACH": {
                "name": "Reach",
                "description": "Audience reach and frequency reports",
                "supported_metrics": "Reach-specific metrics like unique reach and frequency"
            },
            "AD_SPEED": {
                "name": "Ad Speed",
                "description": "Ad loading speed and performance reports",
                "supported_metrics": "Speed and latency metrics"
            }
        }
        
        response = SuccessResponse(
            message="Report types retrieved successfully",
            data={"report_types": report_types}
        )
        
        return response
        
    except Exception as e:
        logger.logger.error(f"Error getting report types: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")