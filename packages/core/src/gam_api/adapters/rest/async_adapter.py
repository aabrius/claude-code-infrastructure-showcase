"""
Async REST adapter implementation for Google Ad Manager API.

Provides async/await support for long-running operations and concurrent processing.
"""

import logging
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

from .rest_adapter import RESTAdapter, CircuitBreaker, CircuitBreakerError
from ...exceptions import (
    APIError, InvalidRequestError, QuotaExceededError,
    ReportError, ReportTimeoutError, AuthenticationError
)

logger = logging.getLogger(__name__)

# GAM REST API v1 base URL
API_BASE_URL = "https://admanager.googleapis.com/v1"


class AsyncRESTAdapter(RESTAdapter):
    """
    Async REST adapter for Google Ad Manager API.
    
    Extends RESTAdapter with async/await support for:
    - Concurrent report processing
    - Long-running operations with async monitoring
    - Connection pooling with aiohttp
    - Async batch operations
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize async REST adapter."""
        super().__init__(config)
        self._async_session: Optional[aiohttp.ClientSession] = None
        self._connector: Optional[aiohttp.TCPConnector] = None
        logger.info("AsyncRESTAdapter initialized")
    
    async def get_async_session(self) -> aiohttp.ClientSession:
        """
        Get or create async session with connection pooling.
        
        Returns:
            Configured aiohttp ClientSession
        """
        if self._async_session is None or self._async_session.closed:
            # Configure connector with connection pooling
            if self._connector is None or self._connector.closed:
                self._connector = aiohttp.TCPConnector(
                    limit=100,  # Total connection pool size
                    limit_per_host=10,  # Per-host connection limit
                    enable_cleanup_closed=True,
                    use_dns_cache=True,
                    keepalive_timeout=30
                )
            
            # Get OAuth2 token for authentication
            credentials = self.auth_manager.get_oauth2_credentials()
            token = credentials.token
            
            # Create session with auth headers
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'User-Agent': 'GAM-REST-Adapter/1.0'
            }
            
            timeout = aiohttp.ClientTimeout(total=300, connect=30)  # 5 min total, 30s connect
            
            self._async_session = aiohttp.ClientSession(
                connector=self._connector,
                headers=headers,
                timeout=timeout
            )
            
            logger.debug("Created new async session with connection pooling")
        
        return self._async_session
    
    async def _handle_async_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """
        Handle async response with error mapping.
        
        Args:
            response: aiohttp ClientResponse
            
        Returns:
            Parsed JSON response
        """
        try:
            if response.status == 200:
                return await response.json()
            
            # Try to get error details
            error_text = await response.text()
            error_data = {}
            try:
                import json
                error_data = json.loads(error_text)
            except:
                pass
            
            error_message = error_data.get('error', {}).get('message', error_text)
            error_code = error_data.get('error', {}).get('status', '')
            
            # Map status codes to exceptions (same as sync version)
            if response.status == 400:
                raise InvalidRequestError(error_message, response.status, error_code)
            elif response.status == 401:
                raise AuthenticationError("Authentication failed", response.status, error_code)
            elif response.status == 404:
                raise InvalidRequestError(f"Resource not found: {error_message}", response.status, error_code)
            elif response.status == 429:
                retry_after = response.headers.get('Retry-After', '60')
                raise QuotaExceededError(
                    f"Quota exceeded. Retry after {retry_after}s",
                    response.status, error_code, retry_after=int(retry_after)
                )
            elif response.status >= 500:
                raise APIError(f"Server error: {error_message}", response.status, error_code)
            else:
                raise APIError(f"Request failed: {error_message}", response.status, error_code)
                
        except aiohttp.ClientError as e:
            raise APIError(f"HTTP client error: {str(e)}")
    
    async def _async_retry_with_backoff(
        self, 
        coro_func,
        max_retries: int = 3,
        base_delay: float = 1.0
    ):
        """
        Execute async function with exponential backoff retry.
        
        Args:
            coro_func: Async function to execute
            max_retries: Maximum retry attempts
            base_delay: Base delay for exponential backoff
            
        Returns:
            Function result
        """
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return await coro_func()
            except (QuotaExceededError, APIError) as e:
                last_exception = e
                if attempt == max_retries:
                    break
                
                # Calculate delay
                delay = base_delay * (2 ** attempt)
                if isinstance(e, QuotaExceededError) and hasattr(e, 'retry_after'):
                    delay = max(delay, e.retry_after)
                
                logger.warning(f"Async API call failed (attempt {attempt + 1}), "
                             f"retrying in {delay}s: {str(e)}")
                await asyncio.sleep(delay)
        
        raise last_exception
    
    async def async_create_report(self, report_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Async create report.
        
        Args:
            report_definition: Report configuration
            
        Returns:
            Report creation result
        """
        async def _create():
            session = await self.get_async_session()
            url = f"{API_BASE_URL}/networks/{self.network_code}/reports"
            
            async with session.post(url, json=report_definition) as response:
                return await self._handle_async_response(response)
        
        result = await self._async_retry_with_backoff(_create)
        logger.info(f"Async created report: {result.get('reportId')}")
        return result
    
    async def async_get_report_status(self, report_id: str) -> str:
        """
        Async get report status.
        
        Args:
            report_id: Report ID or resource name
            
        Returns:
            Status string
        """
        async def _get_status():
            session = await self.get_async_session()
            
            if report_id.startswith('networks/'):
                url = f"{API_BASE_URL}/{report_id}"
            else:
                url = f"{API_BASE_URL}/networks/{self.network_code}/reports/{report_id}"
            
            async with session.get(url) as response:
                data = await self._handle_async_response(response)
                return data.get('status', 'UNKNOWN')
        
        return await self._async_retry_with_backoff(_get_status)
    
    async def async_run_report(self, report_name: str) -> str:
        """
        Async run report.
        
        Args:
            report_name: Report resource name
            
        Returns:
            Operation ID
        """
        async def _run_report():
            session = await self.get_async_session()
            url = f"{API_BASE_URL}/{report_name}:run"
            
            async with session.post(url) as response:
                data = await self._handle_async_response(response)
                return data.get('name')
        
        operation_id = await self._async_retry_with_backoff(_run_report)
        logger.info(f"Async started report: {operation_id}")
        return operation_id
    
    async def async_create_and_run_report(self, report_definition: Dict[str, Any]) -> str:
        """
        Async create and run report.
        
        Args:
            report_definition: Report configuration
            
        Returns:
            Operation ID
        """
        # Create report
        report = await self.async_create_report(report_definition)
        report_name = report.get('name')
        
        if not report_name:
            raise ReportError("Failed to get report resource name")
        
        # Run report
        operation_id = await self.async_run_report(report_name)
        return operation_id
    
    async def async_wait_for_report(
        self,
        report_id: str,
        timeout: int = 300,
        poll_interval: int = 10
    ) -> str:
        """
        Async wait for report completion.
        
        Args:
            report_id: Report ID to wait for
            timeout: Maximum wait time in seconds
            poll_interval: Polling interval in seconds
            
        Returns:
            Final report status
        """
        start_time = asyncio.get_event_loop().time()
        
        while True:
            current_time = asyncio.get_event_loop().time()
            if current_time - start_time > timeout:
                raise ReportTimeoutError(f"Report {report_id} timeout after {timeout}s")
            
            status = await self.async_get_report_status(report_id)
            
            if status in ['COMPLETED', 'FAILED']:
                return status
            
            logger.debug(f"Async waiting for report {report_id}, status: {status}")
            await asyncio.sleep(poll_interval)
    
    async def async_download_report(self, report_id: str, format: str = 'CSV') -> str:
        """
        Async download report with streaming.
        
        Args:
            report_id: Report ID or resource name
            format: Output format
            
        Returns:
            Report data
        """
        # Check if ready
        status = await self.async_get_report_status(report_id)
        if status != 'COMPLETED':
            if status == 'FAILED':
                raise ReportError(f"Report {report_id} failed")
            else:
                raise ReportTimeoutError(f"Report {report_id} not ready (status: {status})")
        
        async def _download():
            session = await self.get_async_session()
            
            if report_id.startswith('networks/'):
                base_url = f"{API_BASE_URL}/{report_id}"
            else:
                base_url = f"{API_BASE_URL}/networks/{self.network_code}/reports/{report_id}"
            
            url = f"{base_url}:fetchRows"
            all_data = []
            page_token = None
            
            while True:
                params = {'pageSize': 1000}
                if page_token:
                    params['pageToken'] = page_token
                
                async with session.get(url, params=params) as response:
                    data = await self._handle_async_response(response)
                
                rows = data.get('rows', [])
                all_data.extend(rows)
                
                page_token = data.get('nextPageToken')
                if not page_token:
                    break
            
            # Format data
            if format.upper() == 'JSON':
                import json
                return json.dumps(all_data, indent=2)
            elif format.upper() in ['CSV', 'TSV']:
                delimiter = ',' if format.upper() == 'CSV' else '\t'
                
                if not all_data:
                    return ""
                
                headers = list(all_data[0].keys()) if all_data else []
                csv_lines = [delimiter.join(headers)]
                
                for row in all_data:
                    values = [str(row.get(header, '')) for header in headers]
                    csv_lines.append(delimiter.join(values))
                
                return '\n'.join(csv_lines)
            else:
                raise ValidationError(f"Unsupported format: {format}")
        
        return await self._async_retry_with_backoff(_download)
    
    async def async_batch_create_reports(
        self,
        report_definitions: List[Dict[str, Any]],
        concurrency_limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Create multiple reports concurrently.
        
        Args:
            report_definitions: List of report configurations
            concurrency_limit: Maximum concurrent operations
            
        Returns:
            List of creation results
        """
        semaphore = asyncio.Semaphore(concurrency_limit)
        
        async def create_with_semaphore(report_def):
            async with semaphore:
                try:
                    return await self.async_create_report(report_def)
                except Exception as e:
                    logger.error(f"Failed to create report {report_def.get('displayName')}: {e}")
                    return {"error": str(e), "report_def": report_def}
        
        tasks = [create_with_semaphore(rd) for rd in report_definitions]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [r if not isinstance(r, Exception) else {"error": str(r)} for r in results]
    
    async def async_batch_process_reports(
        self,
        report_definitions: List[Dict[str, Any]],
        concurrency_limit: int = 3,
        timeout: int = 300
    ) -> List[Dict[str, Any]]:
        """
        End-to-end async batch processing: create, run, wait, download.
        
        Args:
            report_definitions: List of report configurations
            concurrency_limit: Maximum concurrent operations
            timeout: Timeout per report
            
        Returns:
            List of complete results
        """
        semaphore = asyncio.Semaphore(concurrency_limit)
        
        async def process_single_report(report_def):
            async with semaphore:
                try:
                    # Create and run
                    operation_id = await self.async_create_and_run_report(report_def)
                    
                    # Wait for completion
                    final_status = await self.async_wait_for_report(operation_id, timeout)
                    
                    if final_status == 'FAILED':
                        return {
                            "status": "failed",
                            "report_name": report_def.get('displayName'),
                            "operation_id": operation_id,
                            "error": "Report generation failed"
                        }
                    
                    # Download results
                    data = await self.async_download_report(operation_id, 'JSON')
                    
                    return {
                        "status": "completed",
                        "report_name": report_def.get('displayName'),
                        "operation_id": operation_id,
                        "data": data
                    }
                    
                except Exception as e:
                    logger.error(f"Async batch processing failed for {report_def.get('displayName')}: {e}")
                    return {
                        "status": "failed",
                        "report_name": report_def.get('displayName'),
                        "error": str(e)
                    }
        
        tasks = [process_single_report(rd) for rd in report_definitions]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [r if not isinstance(r, Exception) else {"error": str(r)} for r in results]
    
    async def close(self):
        """Close async session and connector."""
        try:
            if self._async_session and not self._async_session.closed:
                await self._async_session.close()
            if self._connector and not self._connector.closed:
                await self._connector.close()
            logger.debug("Closed async session and connector")
        except Exception as e:
            logger.warning(f"Error during async cleanup: {e}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    def __del__(self):
        """
        Safe cleanup on deletion.
        
        Note: We cannot use asyncio.create_task() in __del__ as it may be called
        during interpreter shutdown when the event loop is not available.
        We log a warning if resources weren't properly cleaned up.
        """
        if hasattr(self, '_async_session') and self._async_session and not self._async_session.closed:
            logger.warning(
                "AsyncRESTAdapter was not properly closed. Use 'async with adapter:' or call 'await adapter.close()' explicitly."
            )
        if hasattr(self, '_connector') and self._connector and not self._connector.closed:
            logger.warning(
                "AsyncRESTAdapter connector was not properly closed. Use proper cleanup to avoid resource leaks."
            )