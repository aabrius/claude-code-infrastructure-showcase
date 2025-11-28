"""
Fallback Management for Unified GAM Client

This module implements intelligent fallback logic with retry mechanisms,
error aggregation, and context preservation between API attempts.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Tuple, Union
from functools import wraps

from ..exceptions import (
    APIError, AuthenticationError, QuotaExceededError, 
    InvalidRequestError
)
from .strategy import APIType, OperationType


logger = logging.getLogger(__name__)


class RetryStrategy(Enum):
    """Retry strategy types"""
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    FIBONACCI = "fibonacci"
    CUSTOM = "custom"


class FallbackReason(Enum):
    """Reasons for fallback activation"""
    PRIMARY_API_ERROR = "primary_api_error"
    AUTHENTICATION_FAILURE = "authentication_failure"
    QUOTA_EXCEEDED = "quota_exceeded"
    NETWORK_ERROR = "network_error"
    TIMEOUT = "timeout"
    INVALID_REQUEST = "invalid_request"
    PERFORMANCE_THRESHOLD = "performance_threshold"
    CIRCUIT_BREAKER = "circuit_breaker"


@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    max_retries: int = 3
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_multiplier: float = 2.0
    jitter: bool = True
    retry_on: List[type] = field(default_factory=lambda: [
        QuotaExceededError, APIError
    ])
    no_retry_on: List[type] = field(default_factory=lambda: [
        AuthenticationError, InvalidRequestError
    ])


@dataclass
class FallbackAttempt:
    """Record of a fallback attempt"""
    api: APIType
    operation: OperationType
    attempt_number: int
    start_time: float
    end_time: Optional[float] = None
    success: bool = False
    error: Optional[Exception] = None
    response_time: Optional[float] = None
    reason: Optional[FallbackReason] = None


@dataclass
class FallbackContext:
    """Context maintained across fallback attempts"""
    operation: OperationType
    original_params: Dict[str, Any]
    primary_api: APIType
    fallback_api: Optional[APIType]
    attempts: List[FallbackAttempt] = field(default_factory=list)
    total_start_time: float = field(default_factory=time.time)
    aggregate_errors: List[Exception] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class CircuitBreaker:
    """Circuit breaker for API failure protection"""
    
    def __init__(
        self, 
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = 'HALF_OPEN'
                logger.info("Circuit breaker moving to HALF_OPEN state")
            else:
                raise APIError("Circuit breaker is OPEN - too many failures")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        if self.state == 'HALF_OPEN':
            self.state = 'CLOSED'
            logger.info("Circuit breaker CLOSED after successful recovery")
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            logger.warning(
                f"Circuit breaker OPEN after {self.failure_count} failures"
            )


class FallbackManager:
    """
    Manages fallback logic with intelligent retry mechanisms,
    error aggregation, and performance tracking.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize fallback manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        
        # Default retry configurations per operation type
        self.retry_configs = self._build_retry_configs()
        
        # Circuit breakers per API
        self.circuit_breakers: Dict[APIType, CircuitBreaker] = {
            api: CircuitBreaker(
                failure_threshold=self.config.get('circuit_breaker_threshold', 5),
                recovery_timeout=self.config.get('circuit_breaker_timeout', 60.0)
            )
            for api in APIType
        }
        
        # Performance tracking
        self.fallback_stats = {
            'total_fallbacks': 0,
            'successful_fallbacks': 0,
            'failed_fallbacks': 0,
            'fallback_reasons': {},
            'avg_fallback_time': 0.0
        }
        
        logger.info("FallbackManager initialized")
    
    async def execute_with_fallback(
        self,
        primary_api: APIType,
        fallback_api: Optional[APIType],
        operation: OperationType,
        primary_func: Callable,
        fallback_func: Optional[Callable],
        params: Dict[str, Any],
        **kwargs
    ) -> Any:
        """
        Execute operation with intelligent fallback logic.
        
        Args:
            primary_api: Primary API to try first
            fallback_api: Fallback API if primary fails
            operation: Operation type being performed
            primary_func: Function to call for primary API
            fallback_func: Function to call for fallback API
            params: Parameters for the operation
            **kwargs: Additional parameters
            
        Returns:
            Result from successful API call
            
        Raises:
            AggregateError: If all attempts fail
        """
        context = FallbackContext(
            operation=operation,
            original_params=params.copy(),
            primary_api=primary_api,
            fallback_api=fallback_api
        )
        
        retry_config = self.retry_configs.get(
            operation, 
            self.retry_configs['default']
        )
        
        # Try primary API first
        try:
            result = await self._execute_with_retry(
                api=primary_api,
                func=primary_func,
                context=context,
                retry_config=retry_config,
                **kwargs
            )
            return result
            
        except Exception as primary_error:
            logger.warning(
                f"Primary API {primary_api.value} failed for {operation.value}: {primary_error}"
            )
            context.aggregate_errors.append(primary_error)
            
            # Determine fallback reason
            reason = self._classify_error(primary_error)
            
            # Try fallback if available and appropriate
            if fallback_api and fallback_func and self._should_fallback(reason, retry_config):
                try:
                    self.fallback_stats['total_fallbacks'] += 1
                    
                    logger.info(
                        f"Attempting fallback to {fallback_api.value} for {operation.value}"
                    )
                    
                    result = await self._execute_with_retry(
                        api=fallback_api,
                        func=fallback_func,
                        context=context,
                        retry_config=retry_config,
                        reason=reason,
                        **kwargs
                    )
                    
                    self.fallback_stats['successful_fallbacks'] += 1
                    self._update_fallback_stats(reason)
                    
                    logger.info(
                        f"Fallback to {fallback_api.value} succeeded for {operation.value}"
                    )
                    
                    return result
                    
                except Exception as fallback_error:
                    logger.error(
                        f"Fallback API {fallback_api.value} also failed for {operation.value}: {fallback_error}"
                    )
                    context.aggregate_errors.append(fallback_error)
                    self.fallback_stats['failed_fallbacks'] += 1
                    self._update_fallback_stats(reason)
            
            # All attempts failed - raise aggregate error
            raise self._create_aggregate_error(context)
    
    async def _execute_with_retry(
        self,
        api: APIType,
        func: Callable,
        context: FallbackContext,
        retry_config: RetryConfig,
        reason: Optional[FallbackReason] = None,
        **kwargs
    ) -> Any:
        """Execute function with retry logic"""
        
        circuit_breaker = self.circuit_breakers[api]
        
        for attempt in range(retry_config.max_retries + 1):
            attempt_record = FallbackAttempt(
                api=api,
                operation=context.operation,
                attempt_number=attempt,
                start_time=time.time(),
                reason=reason
            )
            
            context.attempts.append(attempt_record)
            
            try:
                # Execute with circuit breaker protection
                if asyncio.iscoroutinefunction(func):
                    result = await circuit_breaker.call(func, **kwargs)
                else:
                    result = circuit_breaker.call(func, **kwargs)
                
                # Success!
                attempt_record.end_time = time.time()
                attempt_record.success = True
                attempt_record.response_time = attempt_record.end_time - attempt_record.start_time
                
                logger.debug(
                    f"API {api.value} succeeded on attempt {attempt + 1} "
                    f"for {context.operation.value}"
                )
                
                return result
                
            except Exception as error:
                attempt_record.end_time = time.time()
                attempt_record.error = error
                attempt_record.response_time = attempt_record.end_time - attempt_record.start_time
                
                # Check if we should retry
                if not self._should_retry(error, retry_config, attempt):
                    logger.debug(
                        f"Not retrying {api.value} for {context.operation.value}: {error}"
                    )
                    raise error
                
                # Calculate delay before retry
                if attempt < retry_config.max_retries:
                    delay = self._calculate_retry_delay(retry_config, attempt)
                    logger.debug(
                        f"Retrying {api.value} in {delay:.2f}s (attempt {attempt + 1}/{retry_config.max_retries})"
                    )
                    await asyncio.sleep(delay)
                else:
                    # Max retries reached
                    raise error
        
        # Should not reach here
        raise APIError(f"Unexpected retry loop exit for {api.value}")
    
    def _should_retry(
        self, 
        error: Exception, 
        retry_config: RetryConfig, 
        attempt: int
    ) -> bool:
        """Determine if error should trigger retry"""
        
        # Check max retries
        if attempt >= retry_config.max_retries:
            return False
        
        # Check no-retry conditions
        for no_retry_type in retry_config.no_retry_on:
            if isinstance(error, no_retry_type):
                return False
        
        # Check retry conditions
        for retry_type in retry_config.retry_on:
            if isinstance(error, retry_type):
                return True
        
        return False
    
    def _should_fallback(
        self, 
        reason: FallbackReason, 
        retry_config: RetryConfig
    ) -> bool:
        """Determine if error should trigger fallback"""
        
        # Never fallback for authentication errors
        if reason == FallbackReason.AUTHENTICATION_FAILURE:
            return False
        
        # Never fallback for invalid requests
        if reason == FallbackReason.INVALID_REQUEST:
            return False
        
        return True
    
    def _classify_error(self, error: Exception) -> FallbackReason:
        """Classify error to determine fallback reason"""
        
        if isinstance(error, AuthenticationError):
            return FallbackReason.AUTHENTICATION_FAILURE
        elif isinstance(error, QuotaExceededError):
            return FallbackReason.QUOTA_EXCEEDED
        elif isinstance(error, APIError) and error.status_code and error.status_code >= 500:
            return FallbackReason.NETWORK_ERROR
        elif isinstance(error, InvalidRequestError):
            return FallbackReason.INVALID_REQUEST
        elif "timeout" in str(error).lower():
            return FallbackReason.TIMEOUT
        else:
            return FallbackReason.PRIMARY_API_ERROR
    
    def _calculate_retry_delay(
        self, 
        retry_config: RetryConfig, 
        attempt: int
    ) -> float:
        """Calculate delay before retry attempt"""
        
        if retry_config.strategy == RetryStrategy.LINEAR:
            delay = retry_config.base_delay * (attempt + 1)
        elif retry_config.strategy == RetryStrategy.EXPONENTIAL:
            delay = retry_config.base_delay * (retry_config.backoff_multiplier ** attempt)
        elif retry_config.strategy == RetryStrategy.FIBONACCI:
            fib_a, fib_b = 1, 1
            for _ in range(attempt):
                fib_a, fib_b = fib_b, fib_a + fib_b
            delay = retry_config.base_delay * fib_a
        else:
            delay = retry_config.base_delay
        
        # Apply max delay limit
        delay = min(delay, retry_config.max_delay)
        
        # Add jitter if enabled
        if retry_config.jitter:
            import random
            delay *= (0.5 + random.random() * 0.5)
        
        return delay
    
    def _create_aggregate_error(self, context: FallbackContext) -> Exception:
        """Create aggregate error from all failed attempts"""
        
        error_messages = []
        for i, error in enumerate(context.aggregate_errors):
            error_messages.append(f"Attempt {i + 1}: {error}")
        
        total_time = time.time() - context.total_start_time
        
        message = (
            f"All attempts failed for {context.operation.value} after {total_time:.2f}s:\n" +
            "\n".join(error_messages)
        )
        
        # Return the most specific error type from attempts
        if any(isinstance(e, AuthenticationError) for e in context.aggregate_errors):
            return AuthenticationError(message)
        elif any(isinstance(e, QuotaExceededError) for e in context.aggregate_errors):
            return QuotaExceededError(message)
        elif any(isinstance(e, InvalidRequestError) for e in context.aggregate_errors):
            return InvalidRequestError(message)
        else:
            return APIError(message)
    
    def _build_retry_configs(self) -> Dict[Union[str, OperationType], RetryConfig]:
        """Build retry configurations for different operation types"""
        
        # Default configuration
        default_config = RetryConfig(
            max_retries=self.config.get('max_retries', 3),
            strategy=RetryStrategy(self.config.get('retry_strategy', 'exponential')),
            base_delay=self.config.get('base_delay', 1.0),
            max_delay=self.config.get('max_delay', 60.0),
            backoff_multiplier=self.config.get('backoff_multiplier', 2.0)
        )
        
        # Operation-specific configurations
        configs = {
            'default': default_config,
            
            # Report operations - more retries for long-running operations
            OperationType.CREATE_REPORT: RetryConfig(
                max_retries=5, base_delay=2.0, max_delay=120.0
            ),
            OperationType.DOWNLOAD_REPORT: RetryConfig(
                max_retries=5, base_delay=5.0, max_delay=300.0
            ),
            
            # Metadata operations - fast retries
            OperationType.GET_DIMENSIONS: RetryConfig(
                max_retries=2, base_delay=0.5, max_delay=10.0
            ),
            OperationType.GET_METRICS: RetryConfig(
                max_retries=2, base_delay=0.5, max_delay=10.0
            ),
            
            # Line item operations - careful retries
            OperationType.CREATE_LINE_ITEM: RetryConfig(
                max_retries=2, base_delay=3.0, max_delay=30.0
            ),
            OperationType.UPDATE_LINE_ITEM: RetryConfig(
                max_retries=2, base_delay=3.0, max_delay=30.0
            ),
        }
        
        return configs
    
    def _update_fallback_stats(self, reason: FallbackReason):
        """Update fallback statistics"""
        reason_key = reason.value
        if reason_key not in self.fallback_stats['fallback_reasons']:
            self.fallback_stats['fallback_reasons'][reason_key] = 0
        self.fallback_stats['fallback_reasons'][reason_key] += 1
    
    def get_fallback_stats(self) -> Dict[str, Any]:
        """Get fallback statistics summary"""
        total = self.fallback_stats['total_fallbacks']
        if total > 0:
            success_rate = self.fallback_stats['successful_fallbacks'] / total
        else:
            success_rate = 0.0
        
        return {
            **self.fallback_stats,
            'fallback_success_rate': success_rate
        }
    
    def reset_stats(self):
        """Reset fallback statistics"""
        self.fallback_stats = {
            'total_fallbacks': 0,
            'successful_fallbacks': 0,
            'failed_fallbacks': 0,
            'fallback_reasons': {},
            'avg_fallback_time': 0.0
        }