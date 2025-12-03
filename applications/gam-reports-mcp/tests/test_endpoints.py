# tests/test_endpoints.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from endpoints.create import create_report
from endpoints.run import run_report
from endpoints.get import get_report
from endpoints.list import list_reports
from endpoints.update import update_report
from endpoints.delete import delete_report
from endpoints.fetch import fetch_rows
from endpoints.operations import get_operation, wait_for_operation
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
        metrics=["IMPRESSIONS"],
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
        metrics=["IMPRESSIONS"],
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


@pytest.mark.asyncio
async def test_run_report_returns_operation_name(mock_client):
    mock_client.post.return_value = {
        "name": "networks/123/operations/reports/runs/789",
        "done": False,
    }

    result = await run_report(mock_client, "123", "456")

    assert result == "networks/123/operations/reports/runs/789"
    mock_client.post.assert_called_with("/networks/123/reports/456:run", json=None)


@pytest.mark.asyncio
async def test_get_report_success(mock_client):
    mock_client.get.return_value = {
        "name": "networks/123/reports/456",
        "displayName": "My Report",
        "state": "COMPLETED",
    }

    result = await get_report(mock_client, "123", "456")

    assert result.report_id == "456"
    assert result.display_name == "My Report"
    mock_client.get.assert_called_with("/networks/123/reports/456")


@pytest.mark.asyncio
async def test_list_reports_success(mock_client):
    mock_client.get.return_value = {
        "reports": [{"name": "networks/123/reports/1"}],
        "nextPageToken": "token123",
    }

    result = await list_reports(mock_client, "123", page_size=50)

    assert "reports" in result
    mock_client.get.assert_called_with("/networks/123/reports?pageSize=50")


@pytest.mark.asyncio
async def test_list_reports_with_page_token(mock_client):
    mock_client.get.return_value = {"reports": []}

    await list_reports(mock_client, "123", page_size=100, page_token="token123")

    mock_client.get.assert_called_with(
        "/networks/123/reports?pageSize=100&pageToken=token123"
    )


@pytest.mark.asyncio
async def test_update_report_success(mock_client):
    mock_client.patch.return_value = {
        "name": "networks/123/reports/456",
        "displayName": "Updated Report",
        "state": "COMPLETED",
    }

    updates = {"displayName": "Updated Report"}
    result = await update_report(mock_client, "123", "456", updates)

    assert result.display_name == "Updated Report"
    mock_client.patch.assert_called_with(
        "/networks/123/reports/456", json=updates
    )


@pytest.mark.asyncio
async def test_delete_report_success(mock_client):
    mock_client.delete.return_value = None

    result = await delete_report(mock_client, "123", "456")

    assert result is None
    mock_client.delete.assert_called_with("/networks/123/reports/456")


@pytest.mark.asyncio
async def test_fetch_rows_success(mock_client):
    mock_client.post.return_value = {
        "rows": [{"date": "2024-01-01", "impressions": 1000}],
        "nextPageToken": "page2",
        "totalRowCount": 100,
    }

    result = await fetch_rows(mock_client, "123", "456", page_size=10)

    assert len(result.rows) == 1
    assert result.next_page_token == "page2"
    assert result.total_row_count == 100
    mock_client.post.assert_called_with(
        "/networks/123/reports/456/results:fetchRows",
        json={"pageSize": 10},
    )


@pytest.mark.asyncio
async def test_fetch_rows_with_page_token(mock_client):
    mock_client.post.return_value = {"rows": [], "totalRowCount": 0}

    await fetch_rows(mock_client, "123", "456", page_size=10, page_token="token123")

    mock_client.post.assert_called_with(
        "/networks/123/reports/456/results:fetchRows",
        json={"pageSize": 10, "pageToken": "token123"},
    )


@pytest.mark.asyncio
async def test_get_operation_success(mock_client):
    operation_name = "networks/123/operations/reports/runs/789"
    mock_client.get.return_value = {
        "name": operation_name,
        "done": True,
    }

    result = await get_operation(mock_client, operation_name)

    assert result["done"] is True
    mock_client.get.assert_called_with(f"/{operation_name}")


@pytest.mark.asyncio
async def test_wait_for_operation_completes_immediately(mock_client):
    operation_name = "networks/123/operations/reports/runs/789"
    mock_client.get.return_value = {
        "name": operation_name,
        "done": True,
    }

    result = await wait_for_operation(
        mock_client, operation_name, timeout=10, poll_interval=1
    )

    assert result["done"] is True


@pytest.mark.asyncio
async def test_wait_for_operation_polls_until_complete(mock_client):
    operation_name = "networks/123/operations/reports/runs/789"
    # First call returns not done, second call returns done
    mock_client.get.side_effect = [
        {"name": operation_name, "done": False},
        {"name": operation_name, "done": True},
    ]

    result = await wait_for_operation(
        mock_client, operation_name, timeout=10, poll_interval=1
    )

    assert result["done"] is True
    assert mock_client.get.call_count == 2


@pytest.mark.asyncio
async def test_wait_for_operation_timeout(mock_client):
    operation_name = "networks/123/operations/reports/runs/789"
    mock_client.get.return_value = {"name": operation_name, "done": False}

    with pytest.raises(TimeoutError, match="timed out after 5s"):
        await wait_for_operation(
            mock_client, operation_name, timeout=5, poll_interval=1
        )
