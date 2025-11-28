#!/usr/bin/env python3
"""
Example usage of Google Ad Manager API via REST API endpoints.

This example demonstrates how to interact with the GAM API using HTTP requests,
which is useful for web applications and external integrations.
"""

import asyncio
import json
import httpx
from typing import Dict, Any, Optional


class GAMAPIClient:
    """Client for interacting with GAM REST API."""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL of the GAM API service
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.client = httpx.AsyncClient()
    
    @property
    def headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request to API."""
        url = f"{self.base_url}/api/v1{endpoint}"
        response = await self.client.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request to API."""
        url = f"{self.base_url}/api/v1{endpoint}"
        response = await self.client.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


async def example_health_check():
    """Example: Check API health and status."""
    print("\n=== Health Check Example ===")
    
    client = GAMAPIClient()
    
    try:
        # Check health
        print("1. Checking API health...")
        health = await client.get("/health")
        print(f"Health status: {health}")
        
        # Check detailed status
        print("\n2. Checking detailed status...")
        status = await client.get("/status")
        print(f"Status: {json.dumps(status, indent=2)}")
        
    except httpx.HTTPError as e:
        print(f"Health check failed: {e}")
    finally:
        await client.close()


async def example_quick_reports_api():
    """Example: Generate quick reports via REST API."""
    print("\n=== Quick Reports via REST API ===")
    
    client = GAMAPIClient(api_key="your-api-key-here")
    
    try:
        # Generate delivery report
        print("1. Generating delivery report...")
        report_request = {
            "report_type": "delivery",
            "days_back": 7,
            "format": "json"
        }
        
        response = await client.post("/reports/quick", report_request)
        print(f"Delivery report: {json.dumps(response, indent=2)}")
        
        # Generate inventory report with CSV format
        print("\n2. Generating inventory report (CSV)...")
        report_request = {
            "report_type": "inventory",
            "days_back": 30,
            "format": "csv"
        }
        
        response = await client.post("/reports/quick", report_request)
        print(f"Inventory report: {response}")
        
    except httpx.HTTPError as e:
        print(f"Quick reports failed: {e}")
    finally:
        await client.close()


async def example_custom_reports_api():
    """Example: Create custom reports via REST API."""
    print("\n=== Custom Reports via REST API ===")
    
    client = GAMAPIClient(api_key="your-api-key-here")
    
    try:
        # Create custom report
        print("1. Creating custom performance report...")
        report_request = {
            "name": "API Custom Performance Report",
            "dimensions": ["DATE", "AD_UNIT_NAME", "ADVERTISER_NAME"],
            "metrics": [
                "TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS",
                "TOTAL_LINE_ITEM_LEVEL_CLICKS",
                "TOTAL_LINE_ITEM_LEVEL_CTR",
                "TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE"
            ],
            "report_type": "HISTORICAL",
            "days_back": 14,
            "run_immediately": True,
            "format": "json"
        }
        
        response = await client.post("/reports/custom", report_request)
        print(f"Custom report created: {json.dumps(response, indent=2)}")
        
        # Get report by ID (if it was created)
        if response.get("success") and "report_id" in response:
            report_id = response["report_id"]
            print(f"\n2. Getting report details for ID: {report_id}")
            
            report_details = await client.get(f"/reports/{report_id}")
            print(f"Report details: {json.dumps(report_details, indent=2)}")
        
    except httpx.HTTPError as e:
        print(f"Custom reports failed: {e}")
    finally:
        await client.close()


async def example_metadata_api():
    """Example: Get metadata via REST API."""
    print("\n=== Metadata via REST API ===")
    
    client = GAMAPIClient()
    
    try:
        # Get dimensions and metrics
        print("1. Getting dimensions and metrics...")
        metadata = await client.get("/metadata/dimensions-metrics", {
            "report_type": "HISTORICAL",
            "category": "both"
        })
        print(f"Metadata available: {len(metadata.get('dimensions', []))} dimensions, "
              f"{len(metadata.get('metrics', []))} metrics")
        
        # Get common combinations
        print("\n2. Getting common combinations...")
        combinations = await client.get("/metadata/combinations")
        
        if "common_combinations" in combinations:
            print("Available analysis types:")
            for analysis_type, config in combinations["common_combinations"].items():
                print(f"  - {analysis_type}: {config['description']}")
        
    except httpx.HTTPError as e:
        print(f"Metadata requests failed: {e}")
    finally:
        await client.close()


async def example_report_management_api():
    """Example: Manage reports via REST API."""
    print("\n=== Report Management via REST API ===")
    
    client = GAMAPIClient(api_key="your-api-key-here")
    
    try:
        # List reports
        print("1. Listing reports...")
        reports = await client.get("/reports", {"limit": 10})
        
        print(f"Found {reports.get('total_reports', 0)} reports:")
        for report in reports.get("reports", [])[:5]:
            print(f"  - {report.get('name')} (ID: {report.get('id')})")
        
        # Get specific report (if any exist)
        if reports.get("reports"):
            first_report = reports["reports"][0]
            report_id = first_report.get("id")
            
            if report_id:
                print(f"\n2. Getting details for report {report_id}...")
                report_details = await client.get(f"/reports/{report_id}")
                print(f"Report details: {json.dumps(report_details, indent=2)}")
        
    except httpx.HTTPError as e:
        print(f"Report management failed: {e}")
    finally:
        await client.close()


def example_curl_commands():
    """Example: Show equivalent curl commands."""
    print("\n=== Equivalent cURL Commands ===")
    
    base_url = "http://localhost:8000/api/v1"
    api_key = "your-api-key-here"
    
    print("1. Health check:")
    print(f"curl {base_url}/health")
    
    print("\n2. Quick report:")
    print(f"curl -X POST {base_url}/reports/quick \\")
    print(f"  -H \"Content-Type: application/json\" \\")
    print(f"  -H \"X-API-Key: {api_key}\" \\")
    print("  -d '{")
    print('    "report_type": "delivery",')
    print('    "days_back": 7,')
    print('    "format": "json"')
    print("  }'")
    
    print("\n3. Get dimensions and metrics:")
    print(f"curl \"{base_url}/metadata/dimensions-metrics?report_type=HISTORICAL&category=both\"")
    
    print("\n4. List reports:")
    print(f"curl -H \"X-API-Key: {api_key}\" \"{base_url}/reports?limit=10\"")


def example_javascript_fetch():
    """Example: Show JavaScript fetch usage."""
    print("\n=== JavaScript Fetch Example ===")
    
    js_code = '''
// Quick report generation
async function generateQuickReport(reportType, daysBack = 30) {
    const response = await fetch('http://localhost:8000/api/v1/reports/quick', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-API-Key': 'your-api-key-here'
        },
        body: JSON.stringify({
            report_type: reportType,
            days_back: daysBack,
            format: 'json'
        })
    });
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
}

// Get available dimensions and metrics
async function getMetadata(reportType = 'HISTORICAL') {
    const url = new URL('http://localhost:8000/api/v1/metadata/dimensions-metrics');
    url.searchParams.append('report_type', reportType);
    url.searchParams.append('category', 'both');
    
    const response = await fetch(url);
    return await response.json();
}

// Usage examples
try {
    const deliveryReport = await generateQuickReport('delivery', 7);
    console.log('Delivery report:', deliveryReport);
    
    const metadata = await getMetadata();
    console.log('Available dimensions:', metadata.dimensions.length);
} catch (error) {
    console.error('API error:', error);
}
'''
    
    print(js_code)


async def main():
    """Run all API examples."""
    print("Google Ad Manager API - REST API Usage Examples")
    print("=" * 55)
    
    print("⚠️  These examples require:")
    print("1. Running GAM API server (python -m src.api.server)")
    print("2. Valid API configuration")
    print("3. Network access to Google Ad Manager API")
    
    # Always show these (don't require running server)
    example_curl_commands()
    example_javascript_fetch()
    
    # Uncomment these to test with actual running server
    # await example_health_check()
    # await example_quick_reports_api()
    # await example_custom_reports_api()
    # await example_metadata_api()
    # await example_report_management_api()
    
    print("\n=== Integration Patterns ===")
    print("1. Web Dashboard:")
    print("   - Use JavaScript fetch to call API endpoints")
    print("   - Display reports in tables/charts")
    print("   - Real-time status updates")
    
    print("\n2. Mobile App:")
    print("   - HTTP client for API calls")
    print("   - Offline caching of report data")
    print("   - Push notifications for report completion")
    
    print("\n3. ETL Pipeline:")
    print("   - Scheduled API calls for data extraction")
    print("   - Batch processing of large datasets")
    print("   - Integration with data warehouses")
    
    print("\n4. Monitoring System:")
    print("   - Health check endpoints")
    print("   - Performance metrics collection")
    print("   - Alert generation based on thresholds")


if __name__ == "__main__":
    asyncio.run(main())