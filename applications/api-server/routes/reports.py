"""
Report-related API endpoints.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import List, Optional, Union
import json
from datetime import datetime, timedelta

# Import from the new clean package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from gam_api import GAMClient, DateRange, ReportBuilder
from gam_api import APIError, ReportGenerationError

from models import (
    QuickReportRequest, QuickReportResponse,
    CustomReportRequest, CustomReportResponse,
    ReportListResponse, ReportInfo,
    ErrorResponse, SuccessResponse
)

# Updated imports for new package structure
from gam_shared.validators import validate_dimensions_list, validate_metrics_list
from gam_shared.formatters import get_formatter
from gam_shared.logger import get_structured_logger

logger = get_structured_logger('api_reports')
router = APIRouter()


@router.post("/quick", response_model=QuickReportResponse)
async def generate_quick_report(request: QuickReportRequest):
    """
    Generate a quick report with predefined configurations.
    
    Quick reports include:
    - delivery: Impressions, clicks, CTR metrics
    - inventory: Ad unit performance analysis
    - sales: Revenue and monetization metrics
    - reach: Audience reach and frequency
    - programmatic: Programmatic advertising metrics
    """
    try:
        logger.log_function_call("generate_quick_report", kwargs=request.dict())
        
        # Generate report
        generator = ReportGenerator()
        result = generator.generate_quick_report(
            report_type=request.report_type.value,
            days_back=request.days_back
        )
        
        # Format output
        formatter = get_formatter(request.format.value)
        
        if request.format.value == "summary":
            formatted_data = formatter.format(result)
        elif request.format.value == "csv":
            formatted_data = formatter.format(result)
        else:  # json
            formatted_data = formatter.format(result)
        
        response = QuickReportResponse(
            report_type=request.report_type.value,
            days_back=request.days_back,
            total_rows=result.total_rows,
            dimensions=result.dimension_headers,
            metrics=result.metric_headers,
            data=formatted_data,
            execution_time=result.execution_time
        )
        
        logger.logger.info(f"Quick report generated successfully: {request.report_type.value}")
        return response
        
    except ValidationError as e:
        logger.logger.warning(f"Validation error in quick report: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except GAMError as e:
        logger.logger.error(f"GAM error in quick report: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.logger.error(f"Unexpected error in quick report: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/custom", response_model=CustomReportResponse)
async def create_custom_report(request: CustomReportRequest):
    """
    Create a custom report with specified dimensions and metrics.
    
    Allows full customization of:
    - Dimensions (e.g., DATE, AD_UNIT_NAME, LINE_ITEM_NAME)
    - Metrics (e.g., TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS, TOTAL_LINE_ITEM_LEVEL_CLICKS)
    - Report type (HISTORICAL, REACH, AD_SPEED)
    - Date range
    """
    try:
        logger.log_function_call("create_custom_report", kwargs=request.dict())
        
        # Validate inputs
        try:
            dimensions = validate_dimensions_list(request.dimensions)
            metrics = validate_metrics_list(request.metrics)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=f"Validation error: {e}")
        
        # Create date range
        if request.days_back == 7:
            date_range = DateRange(range_type=DateRangeType.LAST_7_DAYS)
        elif request.days_back == 30:
            date_range = DateRange(range_type=DateRangeType.LAST_30_DAYS)
        else:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=request.days_back)
            date_range = DateRange(
                range_type=DateRangeType.CUSTOM,
                start_date=start_date,
                end_date=end_date
            )
        
        # Create report definition
        definition = ReportDefinition(
            report_type=ReportType(request.report_type.value),
            dimensions=dimensions,
            metrics=metrics,
            date_range=date_range
        )
        
        # Create report
        generator = ReportGenerator()
        report = generator.create_report(definition, request.name)
        
        response_data = {
            "action": "created",
            "report_id": report.id,
            "name": report.name,
            "status": report.status.value,
            "created_at": report.created_at
        }
        
        # Run immediately if requested
        if request.run_immediately:
            try:
                report = generator.run_report(report)
                result = generator.fetch_results(report)
                
                response_data.update({
                    "action": "created_and_executed",
                    "status": report.status.value,
                    "total_rows": result.total_rows,
                    "execution_time": result.execution_time
                })
                
                # Include data if requested
                if request.format.value != "summary":
                    formatter = get_formatter(request.format.value)
                    response_data["data"] = formatter.format(result)
                
            except Exception as e:
                logger.logger.error(f"Report execution failed: {e}")
                response_data.update({
                    "action": "created_but_execution_failed",
                    "execution_error": str(e)
                })
        
        response = CustomReportResponse(**response_data)
        logger.logger.info(f"Custom report created: {request.name}")
        return response
        
    except ValidationError as e:
        logger.logger.warning(f"Validation error in custom report: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except GAMError as e:
        logger.logger.error(f"GAM error in custom report: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.logger.error(f"Unexpected error in custom report: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("", response_model=ReportListResponse)
async def list_reports(
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of reports to return"),
    page: int = Query(default=1, ge=1, description="Page number for pagination")
):
    """
    List available reports in the Ad Manager network.
    
    Returns paginated list of reports with basic information.
    """
    try:
        logger.log_function_call("list_reports", kwargs={"limit": limit, "page": page})
        
        generator = ReportGenerator()
        reports = generator.list_reports(limit * page)  # Get enough for pagination
        
        # Calculate pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        page_reports = reports[start_idx:end_idx]
        
        # Simplify report data for display
        simplified_reports = []
        for report in page_reports:
            simplified = ReportInfo(
                id=report.get("reportId", ""),
                name=report.get("displayName", ""),
                status="unknown",  # Status not available in list
                created_at=report.get("createTime"),
                updated_at=report.get("updateTime")
            )
            simplified_reports.append(simplified)
        
        total_pages = (len(reports) + limit - 1) // limit
        
        response = ReportListResponse(
            total_reports=len(reports),
            reports=simplified_reports,
            page=page,
            page_size=limit,
            total_pages=total_pages
        )
        
        logger.logger.info(f"Listed {len(simplified_reports)} reports (page {page}/{total_pages})")
        return response
        
    except GAMError as e:
        logger.logger.error(f"GAM error in list reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.logger.error(f"Unexpected error in list reports: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/quick-types", response_model=SuccessResponse)
async def get_quick_report_types():
    """
    Get available quick report types and their descriptions.
    """
    try:
        types = list_quick_report_types()
        
        response = SuccessResponse(
            message="Quick report types retrieved successfully",
            data={"quick_report_types": types}
        )
        
        return response
        
    except Exception as e:
        logger.logger.error(f"Error getting quick report types: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/{report_id}")
async def get_report(report_id: str):
    """
    Get details of a specific report by ID.
    
    Note: This endpoint is planned but not yet implemented.
    """
    raise HTTPException(
        status_code=501,
        detail="Getting report by ID is not yet implemented. Use list_reports or create new reports."
    )


@router.put("/{report_id}")
async def update_report(report_id: str):
    """
    Update an existing report.
    
    Note: This endpoint is planned but not yet implemented.
    """
    raise HTTPException(
        status_code=501,
        detail="Updating reports is not yet implemented. Create new reports instead."
    )


@router.delete("/{report_id}")
async def delete_report(report_id: str):
    """
    Delete a report.
    
    Note: This endpoint is planned but not yet implemented.
    """
    raise HTTPException(
        status_code=501,
        detail="Deleting reports is not yet implemented."
    )