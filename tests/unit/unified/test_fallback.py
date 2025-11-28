"""
Unit tests for the Fallback Manager.

Tests cover:
- Retry strategies
- Circuit breaker functionality
- Error classification
- Fallback execution
- Context preservation
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch

try:
    from src.core.unified.fallback import (
        FallbackManager, RetryStrategy, RetryConfig, FallbackReason,
        FallbackContext, CircuitBreaker
    )
    from src.core.unified.strategy import APIType, OperationType
    from src.core.exceptions import (
        APIError, AuthenticationError, QuotaExceededError,
        InvalidRequestError, NetworkError
    )
except ImportError as e:
    pytest.skip(f"Fallback dependencies not available: {e}", allow_module_level=True)


class TestCircuitBreaker:
    """Test circuit breaker functionality"""
    
    def test_circuit_breaker_initial_state(self):
        """Test circuit breaker starts in CLOSED state"""
        breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60.0)
        
        assert breaker.state == 'CLOSED'
        assert breaker.failure_count == 0
        assert breaker.last_failure_time is None
    
    def test_circuit_breaker_opens_after_threshold(self):
        """Test circuit breaker opens after failure threshold"""
        breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60.0)
        
        # Simulate failures
        for i in range(3):
            try:
                breaker.call(lambda: 1/0)  # Will raise ZeroDivisionError
            except ZeroDivisionError:
                pass
        
        assert breaker.state == 'OPEN'
        assert breaker.failure_count == 3
    
    def test_circuit_breaker_rejects_when_open(self):
        """Test circuit breaker rejects calls when open"""
        breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=60.0)
        
        # Open the breaker
        try:
            breaker.call(lambda: 1/0)
        except ZeroDivisionError:
            pass
        
        # Should reject next call
        with pytest.raises(APIError) as exc_info:
            breaker.call(lambda: "success")
        
        assert "Circuit breaker is OPEN" in str(exc_info.value)
    
    def test_circuit_breaker_recovery(self):
        """Test circuit breaker recovery after timeout"""
        breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)
        
        # Open the breaker
        try:
            breaker.call(lambda: 1/0)
        except ZeroDivisionError:
            pass
        
        assert breaker.state == 'OPEN'
        
        # Wait for recovery timeout
        time.sleep(0.2)
        
        # Should move to HALF_OPEN and allow call
        result = breaker.call(lambda: "success")
        assert result == "success"
        assert breaker.state == 'CLOSED'
        assert breaker.failure_count == 0


class TestRetryConfig:
    """Test retry configuration and strategies"""
    
    def test_default_retry_config(self):
        """Test default retry configuration"""
        config = RetryConfig()
        
        assert config.max_retries == 3
        assert config.strategy == RetryStrategy.EXPONENTIAL
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0
        assert config.backoff_multiplier == 2.0
        assert config.jitter is True
    
    def test_custom_retry_config(self):
        """Test custom retry configuration"""
        config = RetryConfig(
            max_retries=5,
            strategy=RetryStrategy.LINEAR,
            base_delay=2.0,
            retry_on=[NetworkError],
            no_retry_on=[AuthenticationError]
        )
        
        assert config.max_retries == 5
        assert config.strategy == RetryStrategy.LINEAR
        assert config.base_delay == 2.0
        assert NetworkError in config.retry_on
        assert AuthenticationError in config.no_retry_on


class TestFallbackManager:
    """Test fallback manager functionality"""
    
    @pytest.fixture
    def manager(self):
        """Create fallback manager with default config"""
        return FallbackManager()
    
    @pytest.mark.asyncio
    async def test_successful_primary_execution(self, manager):
        """Test successful execution without fallback"""
        primary_func = AsyncMock(return_value="success")
        fallback_func = AsyncMock()
        
        result = await manager.execute_with_fallback(
            primary_api=APIType.REST,
            fallback_api=APIType.SOAP,
            operation=OperationType.CREATE_REPORT,
            primary_func=primary_func,
            fallback_func=fallback_func,
            params={}
        )
        
        assert result == "success"
        primary_func.assert_called_once()
        fallback_func.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_fallback_on_primary_failure(self, manager):
        """Test fallback execution when primary fails"""
        primary_func = AsyncMock(side_effect=APIError("Primary failed"))
        fallback_func = AsyncMock(return_value="fallback success")
        
        result = await manager.execute_with_fallback(
            primary_api=APIType.REST,
            fallback_api=APIType.SOAP,
            operation=OperationType.CREATE_REPORT,
            primary_func=primary_func,
            fallback_func=fallback_func,
            params={}
        )
        
        assert result == "fallback success"
        primary_func.assert_called()
        fallback_func.assert_called_once()
        
        # Check stats
        stats = manager.get_fallback_stats()
        assert stats['total_fallbacks'] == 1
        assert stats['successful_fallbacks'] == 1
    
    @pytest.mark.asyncio
    async def test_both_apis_fail(self, manager):
        """Test when both primary and fallback fail"""
        primary_func = AsyncMock(side_effect=APIError("Primary failed"))
        fallback_func = AsyncMock(side_effect=APIError("Fallback failed"))
        
        with pytest.raises(APIError) as exc_info:
            await manager.execute_with_fallback(
                primary_api=APIType.REST,
                fallback_api=APIType.SOAP,
                operation=OperationType.CREATE_REPORT,
                primary_func=primary_func,
                fallback_func=fallback_func,
                params={}
            )
        
        assert "All attempts failed" in str(exc_info.value)
        assert "Primary failed" in str(exc_info.value)
        assert "Fallback failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_no_fallback_on_auth_error(self, manager):
        """Test no fallback for authentication errors"""
        primary_func = AsyncMock(
            side_effect=AuthenticationError("Invalid credentials")
        )
        fallback_func = AsyncMock()
        
        with pytest.raises(AuthenticationError):
            await manager.execute_with_fallback(
                primary_api=APIType.REST,
                fallback_api=APIType.SOAP,
                operation=OperationType.CREATE_REPORT,
                primary_func=primary_func,
                fallback_func=fallback_func,
                params={}
            )
        
        primary_func.assert_called()
        fallback_func.assert_not_called()  # Should not fallback
    
    @pytest.mark.asyncio
    async def test_retry_with_exponential_backoff(self, manager):
        """Test retry logic with exponential backoff"""
        call_count = 0
        
        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise NetworkError("Network error")
            return "success after retries"
        
        # Mock sleep to speed up test
        with patch('asyncio.sleep', new_callable=AsyncMock):
            result = await manager.execute_with_fallback(
                primary_api=APIType.REST,
                fallback_api=None,
                operation=OperationType.CREATE_REPORT,
                primary_func=flaky_func,
                fallback_func=None,
                params={}
            )
        
        assert result == "success after retries"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self, manager):
        """Test behavior when max retries exceeded"""
        primary_func = AsyncMock(side_effect=NetworkError("Network error"))
        
        config = {'max_retries': 2}
        manager = FallbackManager(config)
        
        with patch('asyncio.sleep', new_callable=AsyncMock):
            with pytest.raises(NetworkError):
                await manager.execute_with_fallback(
                    primary_api=APIType.REST,
                    fallback_api=None,
                    operation=OperationType.CREATE_REPORT,
                    primary_func=primary_func,
                    fallback_func=None,
                    params={}
                )
        
        # Should be called initial + 2 retries = 3 times
        assert primary_func.call_count == 3


class TestRetryStrategies:
    """Test different retry strategies"""
    
    @pytest.fixture
    def manager(self):
        """Create fallback manager"""
        return FallbackManager()
    
    def test_linear_retry_delay(self, manager):
        """Test linear retry delay calculation"""
        config = RetryConfig(strategy=RetryStrategy.LINEAR, base_delay=2.0)
        
        assert manager._calculate_retry_delay(config, 0) == 2.0
        assert manager._calculate_retry_delay(config, 1) == 4.0
        assert manager._calculate_retry_delay(config, 2) == 6.0
    
    def test_exponential_retry_delay(self, manager):
        """Test exponential retry delay calculation"""
        config = RetryConfig(
            strategy=RetryStrategy.EXPONENTIAL,
            base_delay=1.0,
            backoff_multiplier=2.0
        )
        
        assert manager._calculate_retry_delay(config, 0) == 1.0
        assert manager._calculate_retry_delay(config, 1) == 2.0
        assert manager._calculate_retry_delay(config, 2) == 4.0
    
    def test_fibonacci_retry_delay(self, manager):
        """Test fibonacci retry delay calculation"""
        config = RetryConfig(strategy=RetryStrategy.FIBONACCI, base_delay=1.0)
        
        assert manager._calculate_retry_delay(config, 0) == 1.0
        assert manager._calculate_retry_delay(config, 1) == 1.0
        assert manager._calculate_retry_delay(config, 2) == 2.0
        assert manager._calculate_retry_delay(config, 3) == 3.0
        assert manager._calculate_retry_delay(config, 4) == 5.0
    
    def test_max_delay_limit(self, manager):
        """Test max delay limit is respected"""
        config = RetryConfig(
            strategy=RetryStrategy.EXPONENTIAL,
            base_delay=10.0,
            backoff_multiplier=10.0,
            max_delay=50.0
        )
        
        # Even with large exponential growth, should cap at max_delay
        assert manager._calculate_retry_delay(config, 5) <= 50.0
    
    def test_jitter_adds_randomness(self, manager):
        """Test jitter adds randomness to delays"""
        config = RetryConfig(base_delay=10.0, jitter=True)
        
        delays = [manager._calculate_retry_delay(config, 0) for _ in range(10)]
        
        # All delays should be different due to jitter
        assert len(set(delays)) > 1
        # All should be within expected range (5.0 to 10.0)
        assert all(5.0 <= d <= 10.0 for d in delays)


class TestErrorClassification:
    """Test error classification for fallback decisions"""
    
    @pytest.fixture
    def manager(self):
        """Create fallback manager"""
        return FallbackManager()
    
    def test_classify_authentication_error(self, manager):
        """Test authentication error classification"""
        error = AuthenticationError("Invalid token")
        reason = manager._classify_error(error)
        assert reason == FallbackReason.AUTHENTICATION_FAILURE
    
    def test_classify_quota_error(self, manager):
        """Test quota exceeded error classification"""
        error = QuotaExceededError("Rate limit exceeded")
        reason = manager._classify_error(error)
        assert reason == FallbackReason.QUOTA_EXCEEDED
    
    def test_classify_network_error(self, manager):
        """Test network error classification"""
        error = NetworkError("Connection refused")
        reason = manager._classify_error(error)
        assert reason == FallbackReason.NETWORK_ERROR
    
    def test_classify_timeout_error(self, manager):
        """Test timeout error classification"""
        error = Exception("Request timeout")
        reason = manager._classify_error(error)
        assert reason == FallbackReason.TIMEOUT
    
    def test_classify_generic_error(self, manager):
        """Test generic error classification"""
        error = APIError("Unknown error")
        reason = manager._classify_error(error)
        assert reason == FallbackReason.PRIMARY_API_ERROR
    
    def test_should_retry_logic(self, manager):
        """Test retry decision logic"""
        config = RetryConfig()
        
        # Should retry network errors
        assert manager._should_retry(NetworkError("Network error"), config, 0)
        
        # Should not retry auth errors
        assert not manager._should_retry(
            AuthenticationError("Invalid token"), config, 0
        )
        
        # Should not retry after max attempts
        assert not manager._should_retry(
            NetworkError("Network error"), config, 3
        )
    
    def test_should_fallback_logic(self, manager):
        """Test fallback decision logic"""
        config = RetryConfig()
        
        # Should fallback for most errors
        assert manager._should_fallback(
            FallbackReason.PRIMARY_API_ERROR, config
        )
        assert manager._should_fallback(
            FallbackReason.NETWORK_ERROR, config
        )
        
        # Should not fallback for auth errors
        assert not manager._should_fallback(
            FallbackReason.AUTHENTICATION_FAILURE, config
        )
        
        # Should not fallback for invalid requests
        assert not manager._should_fallback(
            FallbackReason.INVALID_REQUEST, config
        )


class TestFallbackStatistics:
    """Test fallback statistics tracking"""
    
    @pytest.fixture
    def manager(self):
        """Create fallback manager"""
        return FallbackManager()
    
    def test_initial_stats(self, manager):
        """Test initial statistics state"""
        stats = manager.get_fallback_stats()
        
        assert stats['total_fallbacks'] == 0
        assert stats['successful_fallbacks'] == 0
        assert stats['failed_fallbacks'] == 0
        assert stats['fallback_success_rate'] == 0.0
        assert len(stats['fallback_reasons']) == 0
    
    @pytest.mark.asyncio
    async def test_stats_tracking(self, manager):
        """Test statistics are tracked correctly"""
        # Successful fallback
        primary_func = AsyncMock(side_effect=NetworkError("Network error"))
        fallback_func = AsyncMock(return_value="success")
        
        await manager.execute_with_fallback(
            primary_api=APIType.REST,
            fallback_api=APIType.SOAP,
            operation=OperationType.CREATE_REPORT,
            primary_func=primary_func,
            fallback_func=fallback_func,
            params={}
        )
        
        stats = manager.get_fallback_stats()
        assert stats['total_fallbacks'] == 1
        assert stats['successful_fallbacks'] == 1
        assert stats['fallback_success_rate'] == 1.0
        assert stats['fallback_reasons']['network_error'] == 1
    
    def test_reset_stats(self, manager):
        """Test resetting statistics"""
        # Modify stats
        manager.fallback_stats['total_fallbacks'] = 10
        manager.fallback_stats['successful_fallbacks'] = 8
        
        # Reset
        manager.reset_stats()
        
        # Check reset
        stats = manager.get_fallback_stats()
        assert stats['total_fallbacks'] == 0
        assert stats['successful_fallbacks'] == 0