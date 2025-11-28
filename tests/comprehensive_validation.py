#!/usr/bin/env python3
"""
Comprehensive Validation of Unified Client Implementation

This script validates all major components of the unified client:
1. Basic functionality works
2. Configuration system works
3. API selection logic works
4. Error handling works
5. Performance tracking works
6. Documentation exists

Run with: python tests/comprehensive_validation.py
"""

import sys
import os
import asyncio
from unittest.mock import Mock, patch
from typing import List, Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def validate_imports() -> bool:
    """Validate all critical imports work"""
    print("🔍 Validating imports...")
    
    try:
        # Core unified client
        from src.core.unified import GAMUnifiedClient, create_unified_client, UnifiedClientConfig
        from src.core.unified.strategy import APISelectionStrategy, OperationType, APIType
        from src.core.unified.fallback import FallbackManager, RetryStrategy
        
        # Configuration
        from src.core.config import load_config, ConfigLoader
        
        # Exceptions
        from src.core.exceptions import (
            APIError, AuthenticationError, ConfigurationError,
            NetworkError, NotFoundError, ReportNotReadyError
        )
        
        print("   ✅ All imports successful")
        return True
        
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False


def validate_configuration() -> bool:
    """Validate configuration system works"""
    print("⚙️  Validating configuration...")
    
    try:
        from src.core.unified import GAMUnifiedClient, UnifiedClientConfig
        from src.core.exceptions import ConfigurationError
        
        # Test valid config
        valid_config = {
            'auth': {
                'network_code': '123456',
                'client_id': 'test-client',
                'client_secret': 'test-secret',
                'refresh_token': 'test-token'
            }
        }
        
        with patch('src.core.unified.client.SOAPAdapter'), \
             patch('src.core.unified.client.RESTAdapter'):
            client = GAMUnifiedClient(valid_config)
            assert client.network_code == '123456'
        
        # Test invalid config
        invalid_config = {
            'auth': {
                'network_code': 'YOUR_NETWORK_CODE_HERE'
            }
        }
        
        try:
            GAMUnifiedClient(invalid_config)
            print("   ❌ Should have failed with invalid config")
            return False
        except ConfigurationError:
            pass  # Expected
        
        # Test UnifiedClientConfig
        unified_config = UnifiedClientConfig(
            api_preference='rest',
            max_retries=5
        )
        assert unified_config.api_preference == 'rest'
        assert unified_config.max_retries == 5
        
        print("   ✅ Configuration validation works")
        return True
        
    except Exception as e:
        print(f"   ❌ Configuration validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def validate_api_selection() -> bool:
    """Validate API selection logic works"""
    print("🧠 Validating API selection...")
    
    try:
        from src.core.unified.strategy import (
            APISelectionStrategy, OperationType, APIType, OperationContext
        )
        
        strategy = APISelectionStrategy()
        
        # Test report operation (should prefer REST)
        context = OperationContext(
            operation=OperationType.CREATE_REPORT,
            params={}
        )
        primary, fallback = strategy.select_api(context)
        assert primary == APIType.REST
        assert fallback == APIType.SOAP
        
        # Test line item operation (should use SOAP only)
        context = OperationContext(
            operation=OperationType.GET_LINE_ITEMS,
            params={}
        )
        primary, fallback = strategy.select_api(context)
        assert primary == APIType.SOAP
        assert fallback is None
        
        # Test user preference override
        context = OperationContext(
            operation=OperationType.CREATE_REPORT,
            params={},
            user_preference=APIType.SOAP
        )
        primary, fallback = strategy.select_api(context)
        assert primary == APIType.SOAP
        
        print("   ✅ API selection logic works")
        return True
        
    except Exception as e:
        print(f"   ❌ API selection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def validate_fallback_logic() -> bool:
    """Validate fallback and retry logic works"""
    print("🔄 Validating fallback logic...")
    
    try:
        from src.core.unified.fallback import FallbackManager, RetryStrategy, CircuitBreaker
        from src.core.exceptions import APIError
        
        manager = FallbackManager()
        
        # Test circuit breaker
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)
        assert breaker.state == 'CLOSED'
        
        # Test failures
        for _ in range(2):
            try:
                breaker.call(lambda: 1/0)
            except ZeroDivisionError:
                pass
        
        assert breaker.state == 'OPEN'
        
        # Test retry config
        from src.core.unified.fallback import RetryConfig
        config = RetryConfig(
            max_retries=3,
            strategy=RetryStrategy.EXPONENTIAL
        )
        assert config.max_retries == 3
        assert config.strategy == RetryStrategy.EXPONENTIAL
        
        print("   ✅ Fallback logic works")
        return True
        
    except Exception as e:
        print(f"   ❌ Fallback validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def validate_client_functionality() -> bool:
    """Validate unified client basic functionality"""
    print("🚀 Validating client functionality...")
    
    try:
        from src.core.unified import GAMUnifiedClient
        
        config = {
            'auth': {
                'network_code': '123456',
                'client_id': 'test-client',
                'client_secret': 'test-secret',
                'refresh_token': 'test-token'
            }
        }
        
        with patch('src.core.unified.client.SOAPAdapter') as mock_soap, \
             patch('src.core.unified.client.RESTAdapter') as mock_rest:
            
            # Mock adapter instances
            soap_instance = Mock()
            rest_instance = Mock()
            soap_instance.test_connection = Mock(return_value=True)
            rest_instance.test_connection = Mock(return_value=True)
            
            mock_soap.return_value = soap_instance
            mock_rest.return_value = rest_instance
            
            # Create client
            client = GAMUnifiedClient(config)
            
            # Test properties
            assert client.network_code == '123456'
            assert client.has_soap
            assert client.has_rest
            
            # Test performance tracking
            stats = client.get_performance_summary()
            assert 'client_metrics' in stats
            assert 'strategy_performance' in stats
            
            # Test API preference configuration
            client.configure_api_preference('rest')
            assert client.unified_config.api_preference == 'rest'
            
            # Test context manager
            with client as c:
                assert c is client
        
        print("   ✅ Client functionality works")
        return True
        
    except Exception as e:
        print(f"   ❌ Client functionality failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def validate_documentation() -> bool:
    """Validate documentation exists and is comprehensive"""
    print("📚 Validating documentation...")
    
    try:
        import os
        
        # Check main documentation files exist
        docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs')
        
        required_docs = [
            'UNIFIED_CLIENT_GUIDE.md',
            'UNIFIED_CLIENT_QUICK_REFERENCE.md'
        ]
        
        for doc_file in required_docs:
            doc_path = os.path.join(docs_dir, doc_file)
            if not os.path.exists(doc_path):
                print(f"   ❌ Missing documentation: {doc_file}")
                return False
            
            # Check file has content
            with open(doc_path, 'r') as f:
                content = f.read()
                if len(content) < 1000:  # Should have substantial content
                    print(f"   ❌ Documentation too short: {doc_file}")
                    return False
        
        # Check examples exist
        examples_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'examples')
        demo_path = os.path.join(examples_dir, 'unified_client_demo.py')
        
        if not os.path.exists(demo_path):
            print("   ❌ Missing demo example")
            return False
        
        print("   ✅ Documentation complete")
        return True
        
    except Exception as e:
        print(f"   ❌ Documentation validation failed: {e}")
        return False


def validate_test_suite() -> bool:
    """Validate test suite exists and is comprehensive"""
    print("🧪 Validating test suite...")
    
    try:
        import os
        
        # Check test files exist
        test_dir = os.path.join(os.path.dirname(__file__), 'unit', 'unified')
        
        required_tests = [
            'test_unified_client.py',
            'test_strategy.py', 
            'test_fallback.py'
        ]
        
        for test_file in required_tests:
            test_path = os.path.join(test_dir, test_file)
            if not os.path.exists(test_path):
                print(f"   ❌ Missing test file: {test_file}")
                return False
            
            # Check file has content
            with open(test_path, 'r') as f:
                content = f.read()
                if len(content) < 1000:  # Should have substantial tests
                    print(f"   ❌ Test file too short: {test_file}")
                    return False
        
        # Check functional tests exist
        functional_dir = os.path.join(os.path.dirname(__file__), 'functional')
        functional_test = os.path.join(functional_dir, 'test_unified_integration.py')
        
        if not os.path.exists(functional_test):
            print("   ❌ Missing functional tests")
            return False
        
        print("   ✅ Test suite complete")
        return True
        
    except Exception as e:
        print(f"   ❌ Test validation failed: {e}")
        return False


async def main():
    """Run comprehensive validation"""
    print("GAM UNIFIED CLIENT - COMPREHENSIVE VALIDATION")
    print("=" * 60)
    
    validations = [
        ("Imports", validate_imports),
        ("Configuration", validate_configuration),
        ("API Selection", validate_api_selection),
        ("Fallback Logic", validate_fallback_logic),
        ("Client Functionality", validate_client_functionality),
        ("Documentation", validate_documentation),
        ("Test Suite", validate_test_suite)
    ]
    
    results = []
    
    for name, validator in validations:
        if asyncio.iscoroutinefunction(validator):
            result = await validator()
        else:
            result = validator()
        results.append((name, result))
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} validations passed")
    
    if passed == len(results):
        print("\n🎉 ALL VALIDATIONS PASSED!")
        print("The unified client is production-ready! 🚀")
        return True
    else:
        print(f"\n⚠️  {len(results) - passed} validations failed")
        print("Please fix the issues before deploying to production.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)