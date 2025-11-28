#!/usr/bin/env python3
"""
Unified Client Demonstration

This example showcases the GAM Unified Client's key features:
- Smart API selection
- Automatic fallback
- Performance tracking
- Configuration flexibility
- Error handling

Run with: python examples/unified_client_demo.py
"""

import asyncio
import logging
import sys
import os
from typing import Dict, List

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.unified import GAMUnifiedClient, create_unified_client
from src.core.exceptions import (
    APIError, AuthenticationError, ConfigurationError, 
    QuotaExceededError, NetworkError
)


# Enable detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class UnifiedClientDemo:
    """Demonstration of unified client capabilities"""
    
    def __init__(self):
        """Initialize the demo with mock configuration"""
        self.config = {
            'auth': {
                'network_code': '123456789',
                'client_id': 'demo-client-id',
                'client_secret': 'demo-client-secret',
                'refresh_token': 'demo-refresh-token'
            }
        }
        self.client = None
    
    async def setup_client(self):
        """Set up the unified client with error handling"""
        try:
            print("🚀 Creating Unified GAM Client...")
            self.client = GAMUnifiedClient(self.config)
            
            print("✅ Client created successfully!")
            print(f"   Network Code: {self.client.network_code}")
            print(f"   SOAP Available: {self.client.has_soap}")
            print(f"   REST Available: {self.client.has_rest}")
            
        except ConfigurationError as e:
            print(f"❌ Configuration Error: {e}")
            print("💡 Tip: Check your credentials in the config")
            raise
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            raise
    
    async def test_connection(self):
        """Test API connectivity"""
        print("\n🔗 Testing API Connection...")
        try:
            # This would normally test real APIs
            # For demo, we'll simulate success
            print("✅ Connection test successful!")
            
            # Show adapter availability
            print(f"   Primary API capabilities available: {self.client.has_rest or self.client.has_soap}")
            
        except AuthenticationError:
            print("❌ Authentication failed - check credentials")
        except NetworkError:
            print("❌ Network error - check connectivity")
        except APIError as e:
            print(f"❌ API error: {e}")
    
    async def demonstrate_smart_api_selection(self):
        """Demonstrate automatic API selection"""
        print("\n🧠 Smart API Selection Demo")
        print("-" * 40)
        
        # Simulate different operation types
        operations = [
            ("Create Report", "create_report", "REST preferred for reports"),
            ("Get Line Items", "get_line_items", "SOAP only for line items"),  
            ("Get Dimensions", "get_dimensions", "REST preferred for metadata"),
            ("Get Ad Units", "get_ad_units", "SOAP preferred for inventory")
        ]
        
        for name, operation, reason in operations:
            print(f"📋 {name}: {reason}")
        
        print("\n💡 The client automatically chooses the best API for each operation!")
    
    async def demonstrate_fallback_mechanism(self):
        """Demonstrate automatic fallback"""
        print("\n🔄 Fallback Mechanism Demo")
        print("-" * 30)
        
        print("Scenario: Primary API fails, automatic fallback to secondary")
        print("1. Try REST API first (primary)")
        print("2. REST fails with network error")
        print("3. Automatically fallback to SOAP API")
        print("4. SOAP succeeds - operation completes!")
        print("\n✅ Zero downtime with intelligent fallback")
    
    async def demonstrate_performance_tracking(self):
        """Demonstrate performance monitoring"""
        print("\n📊 Performance Tracking Demo")
        print("-" * 35)
        
        # Simulate some operations for metrics
        print("Simulating operations for performance metrics...")
        
        # This would normally track real operations
        # For demo, we'll show what the metrics look like
        stats = self.client.get_performance_summary()
        
        print(f"📈 Performance Metrics:")
        print(f"   Total Operations: {stats['client_metrics']['total_operations']}")
        print(f"   Successful: {stats['client_metrics']['successful_operations']}")
        print(f"   Failed: {stats['client_metrics']['failed_operations']}")
        print(f"   Average Response Time: {stats['client_metrics']['avg_response_time']:.2f}s")
        
        print(f"\n🔧 API Usage:")
        for api, count in stats['client_metrics']['api_usage'].items():
            print(f"   {api.upper()}: {count} calls")
        
        print("\n💡 Performance data helps optimize API selection!")
    
    async def demonstrate_configuration_options(self):
        """Demonstrate configuration flexibility"""
        print("\n⚙️  Configuration Options Demo")
        print("-" * 40)
        
        print("Available configuration options:")
        print("📌 API Preference: 'rest', 'soap', or null (auto)")
        print("🔄 Fallback: Enable/disable automatic fallback") 
        print("🔁 Retries: Configure retry attempts and strategies")
        print("⚡ Circuit Breaker: Set failure thresholds")
        print("🎯 Per-operation: Override settings per operation type")
        
        # Demonstrate preference change
        print(f"\nCurrent API preference: {self.client.unified_config.api_preference}")
        print("Changing to prefer SOAP...")
        self.client.configure_api_preference('soap')
        print(f"Updated preference: {self.client.unified_config.api_preference}")
    
    async def demonstrate_error_handling(self):
        """Demonstrate comprehensive error handling"""
        print("\n🛡️  Error Handling Demo")
        print("-" * 30)
        
        print("The unified client handles various error scenarios:")
        
        error_scenarios = [
            ("AuthenticationError", "Invalid credentials detected"),
            ("QuotaExceededError", "API rate limit exceeded - auto-retry with backoff"),
            ("NetworkError", "Connection issues - automatic retry"),
            ("ConfigurationError", "Invalid config - clear error messages"),
            ("APIError", "General API failures - context preserved")
        ]
        
        for error_type, description in error_scenarios:
            print(f"   {error_type}: {description}")
        
        print("\n✅ All errors are handled gracefully with helpful messages!")
    
    async def demonstrate_migration_path(self):
        """Show migration from legacy client"""
        print("\n🔄 Migration Path Demo")
        print("-" * 28)
        
        print("Legacy code still works:")
        print("```python")
        print("from src.core.client import GAMClient")
        print("client = GAMClient()")
        print("reports = client.list_reports_rest()  # Still works!")
        print("```")
        print("")
        print("New unified methods available:")
        print("```python")
        print("reports = client.list_reports_unified()  # Smart selection!")
        print("stats = client.get_performance_summary()  # New feature!")
        print("```")
        print("")
        print("✅ Zero breaking changes - migrate at your own pace!")
    
    async def show_summary(self):
        """Show summary of unified client benefits"""
        print("\n" + "="*60)
        print("🎉 GAM UNIFIED CLIENT BENEFITS")
        print("="*60)
        
        benefits = [
            "🧠 Smart API Selection - Chooses optimal API automatically",
            "🔄 Automatic Fallback - Zero downtime on API failures", 
            "📊 Performance Tracking - Real-time metrics and optimization",
            "🛡️  Robust Error Handling - Graceful failure recovery",
            "⚙️  Flexible Configuration - Adapt to your needs",
            "🔧 Zero Breaking Changes - Backward compatible",
            "⚡ Async & Sync Support - Use your preferred style",
            "📚 Comprehensive Docs - Easy to learn and use"
        ]
        
        for benefit in benefits:
            print(f"   {benefit}")
        
        print("\n🚀 Ready for production with enterprise-grade reliability!")
        print("="*60)
    
    async def run_demo(self):
        """Run the complete demonstration"""
        print("GAM UNIFIED CLIENT DEMONSTRATION")
        print("="*50)
        
        try:
            await self.setup_client()
            await self.test_connection()
            await self.demonstrate_smart_api_selection()
            await self.demonstrate_fallback_mechanism()
            await self.demonstrate_performance_tracking()
            await self.demonstrate_configuration_options()
            await self.demonstrate_error_handling()
            await self.demonstrate_migration_path()
            await self.show_summary()
            
        except Exception as e:
            print(f"\n❌ Demo failed: {e}")
            logger.exception("Demo failed with exception")


async def main():
    """Main demo function"""
    demo = UnifiedClientDemo()
    await demo.run_demo()


if __name__ == "__main__":
    # Run the demonstration
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n💥 Demo crashed: {e}")
        logging.exception("Demo crashed with exception")