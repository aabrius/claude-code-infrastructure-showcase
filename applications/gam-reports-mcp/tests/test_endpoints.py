# tests/test_endpoints.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from endpoints.create import create_report
from models.reports import CreateReportRequest


@pytest.fixture
def mock_client():
    client = AsyncMock()
    client.post.return_value = {
        "name": "networks/123/reports/456",
        "displayName": "Test Report",
        "state": "COMPLETED",
    }
    return client


@pytest.mark.asyncio
async def test_create_report_success(mock_client):
    request = CreateReportRequest(
        display_name="Test Report",
        dimensions=["DATE"],
        metrics=["TOTAL_IMPRESSIONS"],
        start_date="2024-01-01",
        end_date="2024-01-31",
    )

    result = await create_report(mock_client, "123", request)

    assert result.report_id == "456"
    assert result.name == "networks/123/reports/456"


@pytest.mark.asyncio
async def test_create_report_validates_dimensions(mock_client):
    request = CreateReportRequest(
        dimensions=["INVALID_DIMENSION"],
        metrics=["TOTAL_IMPRESSIONS"],
        start_date="2024-01-01",
        end_date="2024-01-31",
    )

    with pytest.raises(ValueError, match="not in curated allowlist"):
        await create_report(mock_client, "123", request)


@pytest.mark.asyncio
async def test_create_report_validates_metrics(mock_client):
    request = CreateReportRequest(
        dimensions=["DATE"],
        metrics=["INVALID_METRIC"],
        start_date="2024-01-01",
        end_date="2024-01-31",
    )

    with pytest.raises(ValueError, match="not in curated allowlist"):
        await create_report(mock_client, "123", request)
