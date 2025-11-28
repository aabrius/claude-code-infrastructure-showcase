"""
Performance tests for the GAM SDK.

Tests performance characteristics with large datasets, concurrent operations,
and memory usage patterns.
"""

import pytest
import time
import psutil
import os
import tempfile
from unittest.mock import Mock, patch
from datetime import date, timedelta
import pandas as pd

from src.sdk.client import GAMClient
from src.sdk.reports import ReportBuilder, ReportResult
from src.sdk.config import ConfigManager
from tests.utils.test_helpers import PerformanceTimer


class TestReportPerformance:
    """Test report generation and manipulation performance."""
    
    @pytest.fixture
    def large_report_data(self):
        """Generate large report dataset."""
        rows = []
        ad_units = [f'Ad Unit {i}' for i in range(100)]  # 100 different ad units
        
        # Generate 50,000 rows
        for day in range(1, 501):  # 500 days
            for ad_unit_idx in range(100):  # 100 ad units per day
                impressions = 1000 + (day * 10) + ad_unit_idx
                clicks = impressions // 20  # 5% CTR
                
                rows.append({
                    'dimensionValues': [f'2024-{(day % 12) + 1:02d}-{(day % 28) + 1:02d}', ad_units[ad_unit_idx]],
                    'metricValueGroups': [{'primaryValues': [str(impressions), str(clicks)]}]
                })
        
        return ReportResult(
            rows,
            ['DATE', 'AD_UNIT_NAME'],
            ['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 'TOTAL_LINE_ITEM_LEVEL_CLICKS'],
            {'generated_at': '2024-01-01T00:00:00Z', 'total_rows': len(rows)}
        )
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_large_dataset_creation_performance(self, large_report_data):
        """Test performance of creating large ReportResult."""
        with PerformanceTimer() as timer:
            # Access properties to trigger lazy loading
            _ = large_report_data.row_count
            _ = large_report_data.column_count
            _ = large_report_data.headers
        
        # Should complete within reasonable time
        assert timer.elapsed < 1.0  # Less than 1 second
        assert large_report_data.row_count == 50000
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_dataframe_conversion_performance(self, large_report_data):
        """Test performance of converting large dataset to DataFrame."""
        with PerformanceTimer() as timer:
            df = large_report_data.to_dataframe()
        
        # Should complete within reasonable time
        assert timer.elapsed < 5.0  # Less than 5 seconds
        assert len(df) == 50000
        assert len(df.columns) == 4
        
        # Test that caching works (second call should be faster)
        with PerformanceTimer() as timer2:
            df2 = large_report_data.to_dataframe()
        
        assert timer2.elapsed < 0.1  # Cached version should be very fast
        assert df is df2  # Should return same object
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_filtering_performance(self, large_report_data):
        """Test performance of filtering large datasets."""
        with PerformanceTimer() as timer:
            filtered = large_report_data.filter(
                lambda row: row.get('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 0) > 25000
            )
        
        # Should complete within reasonable time
        assert timer.elapsed < 3.0  # Less than 3 seconds
        assert len(filtered) > 0
        assert len(filtered) < len(large_report_data)
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_sorting_performance(self, large_report_data):
        """Test performance of sorting large datasets."""
        with PerformanceTimer() as timer:
            sorted_result = large_report_data.sort('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', ascending=False)
        
        # Should complete within reasonable time
        assert timer.elapsed < 5.0  # Less than 5 seconds
        
        # Verify sorting worked
        df = sorted_result.to_dataframe()
        impressions = df['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS'].values
        assert all(impressions[i] >= impressions[i+1] for i in range(len(impressions)-1))
    
    @pytest.mark.performance
    def test_export_performance(self, large_report_data):
        """Test performance of exporting large datasets."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            csv_path = f.name
        
        try:
            with PerformanceTimer() as timer:
                large_report_data.to_csv(csv_path)
            
            # Should complete within reasonable time
            assert timer.elapsed < 10.0  # Less than 10 seconds
            assert os.path.exists(csv_path)
            
            # Verify file size is reasonable
            file_size = os.path.getsize(csv_path)
            assert file_size > 1000000  # At least 1MB for 50k rows
            
        finally:
            os.unlink(csv_path)
    
    @pytest.mark.performance
    def test_memory_usage_large_dataset(self, large_report_data):
        """Test memory usage with large datasets."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create DataFrame (memory intensive operation)
        df = large_report_data.to_dataframe()
        
        current_memory = process.memory_info().rss
        memory_increase = current_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB for 50k rows)
        assert memory_increase < 100 * 1024 * 1024  # 100MB
        
        # Test that filtering doesn't create excessive memory overhead
        filtered_memory_start = process.memory_info().rss
        filtered = large_report_data.filter(lambda row: True)  # Identity filter
        filtered_memory_end = process.memory_info().rss
        
        filter_memory_increase = filtered_memory_end - filtered_memory_start
        # Filtering should not double memory usage
        assert filter_memory_increase < memory_increase


class TestConcurrentOperations:
    """Test performance of concurrent operations."""
    
    @pytest.mark.performance
    def test_multiple_report_builders(self, mock_config):
        """Test performance of multiple concurrent report builders."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager:
            
            mock_get_config.return_value = mock_config
            mock_auth = Mock()
            mock_auth_manager.return_value = mock_auth
            
            client = GAMClient(auto_authenticate=False)
            
            with PerformanceTimer() as timer:
                # Create multiple report builders
                builders = []
                for i in range(100):
                    builder = (client
                              .reports()
                              .dimensions('DATE', 'AD_UNIT_NAME')
                              .metrics('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS')
                              .last_30_days()
                              .name(f'Report {i}'))
                    builders.append(builder)
            
            # Should create 100 builders quickly
            assert timer.elapsed < 1.0
            assert len(builders) == 100
    
    @pytest.mark.performance
    def test_multiple_config_operations(self, mock_config):
        """Test performance of multiple configuration operations."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager:
            
            mock_get_config.return_value = mock_config
            mock_auth = Mock()
            mock_auth_manager.return_value = mock_auth
            
            client = GAMClient(auto_authenticate=False)
            config = client.config()
            
            with PerformanceTimer() as timer:
                # Perform many configuration operations
                for i in range(1000):
                    config.set(f'test.setting_{i}', f'value_{i}')
            
            # Should handle 1000 operations quickly
            assert timer.elapsed < 1.0
            assert config.has_pending_changes()
            assert len(config.get_pending_changes()) == 1000
    
    @pytest.mark.performance
    def test_multiple_data_manipulations(self):
        """Test performance of multiple data manipulation operations."""
        # Create medium-sized dataset
        rows = []
        for i in range(1000):
            rows.append({
                'dimensionValues': [f'2024-01-{(i % 31) + 1:02d}', f'Ad Unit {i % 10}'],
                'metricValueGroups': [{'primaryValues': [str(1000 + i), str(50 + i)]}]
            })
        
        result = ReportResult(
            rows,
            ['DATE', 'AD_UNIT_NAME'],
            ['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 'TOTAL_LINE_ITEM_LEVEL_CLICKS'],
            {}
        )
        
        with PerformanceTimer() as timer:
            # Chain multiple operations
            processed = (result
                        .filter(lambda row: row.get('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 0) > 1200)
                        .sort('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', ascending=False)
                        .head(100))
        
        # Should complete quickly
        assert timer.elapsed < 2.0
        assert len(processed) <= 100


class TestMemoryEfficiency:
    """Test memory efficiency patterns."""
    
    @pytest.mark.performance
    def test_memory_cleanup_after_operations(self):
        """Test that memory is properly cleaned up after operations."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Perform memory-intensive operations
        for i in range(10):
            rows = []
            for j in range(5000):
                rows.append({
                    'dimensionValues': [f'2024-01-{(j % 31) + 1:02d}', f'Ad Unit {j}'],
                    'metricValueGroups': [{'primaryValues': [str(1000 + j), str(50 + j)]}]
                })
            
            result = ReportResult(rows, ['DATE', 'AD_UNIT_NAME'], ['IMPRESSIONS', 'CLICKS'], {})
            df = result.to_dataframe()
            
            # Force garbage collection
            import gc
            gc.collect()
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be minimal after cleanup
        assert memory_increase < 50 * 1024 * 1024  # Less than 50MB
    
    @pytest.mark.performance
    def test_lazy_loading_efficiency(self):
        """Test that lazy loading improves performance."""
        rows = []
        for i in range(10000):
            rows.append({
                'dimensionValues': [f'2024-01-{(i % 31) + 1:02d}', f'Ad Unit {i}'],
                'metricValueGroups': [{'primaryValues': [str(1000 + i), str(50 + i)]}]
            })
        
        # Creating ReportResult should be fast (lazy loading)
        with PerformanceTimer() as timer:
            result = ReportResult(rows, ['DATE', 'AD_UNIT_NAME'], ['IMPRESSIONS', 'CLICKS'], {})
            _ = result.row_count  # This should be immediate
            _ = result.column_count  # This should be immediate
        
        assert timer.elapsed < 0.1  # Very fast for basic properties
        
        # DataFrame conversion should take longer (actual work)
        with PerformanceTimer() as timer:
            df = result.to_dataframe()
        
        assert timer.elapsed > 0.1  # Should take some time for real work
        assert len(df) == 10000


class TestScalabilityLimits:
    """Test scalability limits and thresholds."""
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_maximum_reasonable_dataset_size(self):
        """Test handling of maximum reasonable dataset size."""
        # Test with 100,000 rows (large but realistic)
        rows = []
        for i in range(100000):
            rows.append({
                'dimensionValues': [f'2024-{(i % 365) + 1:03d}', f'Ad Unit {i % 1000}'],
                'metricValueGroups': [{'primaryValues': [str(i * 10), str(i)]}]
            })
        
        with PerformanceTimer() as timer:
            result = ReportResult(rows, ['DATE', 'AD_UNIT_NAME'], ['IMPRESSIONS', 'CLICKS'], {})
            df = result.to_dataframe()
        
        # Should complete within reasonable time even for very large dataset
        assert timer.elapsed < 30.0  # Less than 30 seconds
        assert len(df) == 100000
    
    @pytest.mark.performance
    def test_filtering_efficiency_with_size(self):
        """Test that filtering efficiency scales reasonably."""
        sizes = [1000, 5000, 10000, 20000]
        times = []
        
        for size in sizes:
            rows = []
            for i in range(size):
                rows.append({
                    'dimensionValues': [f'2024-01-{(i % 31) + 1:02d}', f'Ad Unit {i}'],
                    'metricValueGroups': [{'primaryValues': [str(1000 + i), str(50 + i)]}]
                })
            
            result = ReportResult(rows, ['DATE', 'AD_UNIT_NAME'], ['IMPRESSIONS', 'CLICKS'], {})
            
            with PerformanceTimer() as timer:
                filtered = result.filter(lambda row: row.get('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 0) > size // 2)
            
            times.append(timer.elapsed)
        
        # Filtering time should scale roughly linearly
        # Time for 20k should be less than 4x time for 5k (allowing for overhead)
        time_ratio = times[-1] / times[1]  # 20k vs 5k
        size_ratio = sizes[-1] / sizes[1]  # 4x
        
        assert time_ratio < size_ratio * 2  # Allow for 2x overhead factor
    
    @pytest.mark.performance
    def test_export_scaling(self):
        """Test that export performance scales reasonably."""
        sizes = [1000, 5000, 10000]
        times = []
        
        for size in sizes:
            rows = []
            for i in range(size):
                rows.append({
                    'dimensionValues': [f'2024-01-{(i % 31) + 1:02d}', f'Ad Unit {i}'],
                    'metricValueGroups': [{'primaryValues': [str(1000 + i), str(50 + i)]}]
                })
            
            result = ReportResult(rows, ['DATE', 'AD_UNIT_NAME'], ['IMPRESSIONS', 'CLICKS'], {})
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                csv_path = f.name
            
            try:
                with PerformanceTimer() as timer:
                    result.to_csv(csv_path)
                
                times.append(timer.elapsed)
                
            finally:
                os.unlink(csv_path)
        
        # Export time should scale roughly linearly
        time_ratio = times[-1] / times[0]  # 10k vs 1k
        size_ratio = sizes[-1] / sizes[0]  # 10x
        
        assert time_ratio < size_ratio * 3  # Allow for 3x overhead factor


class TestConfigurationPerformance:
    """Test configuration system performance."""
    
    @pytest.mark.performance
    def test_config_file_operations_performance(self, mock_config):
        """Test performance of configuration file operations."""
        manager = ConfigManager(mock_config)
        
        # Add many configuration changes
        with PerformanceTimer() as timer:
            for i in range(1000):
                manager.set(f'section_{i // 100}.setting_{i}', f'value_{i}')
        
        assert timer.elapsed < 1.0  # Should be very fast
        
        # Test save performance
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml_path = f.name
        
        try:
            with PerformanceTimer() as timer:
                manager.save_to_file(yaml_path)
            
            assert timer.elapsed < 5.0  # Should save 1000 settings quickly
            
        finally:
            os.unlink(yaml_path)
    
    @pytest.mark.performance
    def test_config_validation_performance(self, mock_config):
        """Test performance of configuration validation."""
        manager = ConfigManager(mock_config)
        
        # Add many settings to validate
        for i in range(100):
            manager.set(f'test.setting_{i}', f'value_{i}')
        
        with PerformanceTimer() as timer:
            manager.validate()
        
        # Validation should be reasonably fast
        assert timer.elapsed < 2.0