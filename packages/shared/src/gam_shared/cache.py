"""
Caching utilities for Google Ad Manager API.
"""

import os
import json
import time
import hashlib
from typing import Any, Optional, Dict, Callable
from datetime import datetime, timedelta
from pathlib import Path
import threading
from dataclasses import dataclass, field


@dataclass
class CacheStats:
    """Statistics tracking for cache operations."""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    errors: int = 0
    
    @property
    def total_requests(self) -> int:
        """Total number of cache requests."""
        return self.hits + self.misses
    
    @property
    def hit_rate(self) -> float:
        """Cache hit rate as a percentage."""
        total = self.total_requests
        return (self.hits / total * 100) if total > 0 else 0.0
    
    @property
    def miss_rate(self) -> float:
        """Cache miss rate as a percentage."""
        total = self.total_requests
        return (self.misses / total * 100) if total > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            'hits': self.hits,
            'misses': self.misses,
            'sets': self.sets,
            'deletes': self.deletes,
            'evictions': self.evictions,
            'errors': self.errors,
            'total_requests': self.total_requests,
            'hit_rate': round(self.hit_rate, 2),
            'miss_rate': round(self.miss_rate, 2)
        }


class CacheBackend:
    """Base class for cache backends."""
    
    def __init__(self):
        """Initialize cache backend with stats tracking."""
        self.stats = CacheStats()
        self._stats_lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        raise NotImplementedError
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL in seconds."""
        raise NotImplementedError
    
    def delete(self, key: str):
        """Delete value from cache."""
        raise NotImplementedError
    
    def clear(self):
        """Clear all cache entries."""
        raise NotImplementedError
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        raise NotImplementedError
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        with self._stats_lock:
            return CacheStats(**self.stats.__dict__)
    
    def reset_stats(self):
        """Reset cache statistics."""
        with self._stats_lock:
            self.stats = CacheStats()


class FileCache(CacheBackend):
    """File-based cache implementation."""
    
    def __init__(self, cache_dir: str = ".cache/gam_api", max_size_mb: int = 100):
        """
        Initialize file cache.
        
        Args:
            cache_dir: Directory to store cache files
            max_size_mb: Maximum cache size in MB
        """
        super().__init__()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self.max_size_bytes = max_size_mb * 1024 * 1024
    
    def _get_cache_path(self, key: str) -> Path:
        """Get file path for cache key."""
        # Hash the key to avoid filesystem issues
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        cache_path = self._get_cache_path(key)
        
        with self._lock:
            if not cache_path.exists():
                with self._stats_lock:
                    self.stats.misses += 1
                return None
            
            try:
                with open(cache_path, 'r') as f:
                    data = json.load(f)
                
                # Check expiration
                expires_at = data.get('expires_at')
                if expires_at and time.time() > expires_at:
                    # Expired, delete and return None
                    cache_path.unlink()
                    with self._stats_lock:
                        self.stats.misses += 1
                        self.stats.evictions += 1
                    return None
                
                with self._stats_lock:
                    self.stats.hits += 1
                return data.get('value')
                
            except (json.JSONDecodeError, IOError):
                # Corrupted cache file, delete it
                cache_path.unlink(missing_ok=True)
                with self._stats_lock:
                    self.stats.misses += 1
                    self.stats.errors += 1
                return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL."""
        cache_path = self._get_cache_path(key)
        
        # Check cache size limit
        if self._get_cache_size() >= self.max_size_bytes:
            self._evict_oldest()
        
        data = {
            'key': key,
            'value': value,
            'created_at': time.time(),
            'expires_at': time.time() + ttl if ttl > 0 else None
        }
        
        with self._lock:
            try:
                with open(cache_path, 'w') as f:
                    json.dump(data, f, default=str)
                with self._stats_lock:
                    self.stats.sets += 1
            except (IOError, TypeError) as e:
                # Failed to cache, log but don't raise
                print(f"Failed to cache {key}: {e}")
                with self._stats_lock:
                    self.stats.errors += 1
    
    def delete(self, key: str):
        """Delete value from cache."""
        cache_path = self._get_cache_path(key)
        
        with self._lock:
            if cache_path.exists():
                cache_path.unlink()
                with self._stats_lock:
                    self.stats.deletes += 1
    
    def clear(self):
        """Clear all cache entries."""
        with self._lock:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return self.get(key) is not None
    
    def cleanup_expired(self):
        """Remove expired cache entries."""
        with self._lock:
            evicted = 0
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r') as f:
                        data = json.load(f)
                    
                    expires_at = data.get('expires_at')
                    if expires_at and time.time() > expires_at:
                        cache_file.unlink()
                        evicted += 1
                        
                except (json.JSONDecodeError, IOError):
                    # Corrupted file, delete it
                    cache_file.unlink(missing_ok=True)
                    evicted += 1
            
            if evicted > 0:
                with self._stats_lock:
                    self.stats.evictions += evicted
    
    def _get_cache_size(self) -> int:
        """Get total size of cache directory in bytes."""
        total_size = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                total_size += cache_file.stat().st_size
            except OSError:
                pass
        return total_size
    
    def _evict_oldest(self):
        """Evict oldest cache entries to make room."""
        cache_files = []
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                mtime = cache_file.stat().st_mtime
                cache_files.append((mtime, cache_file))
            except OSError:
                pass
        
        # Sort by modification time (oldest first)
        cache_files.sort()
        
        # Remove oldest files until we're under 80% of max size
        target_size = int(self.max_size_bytes * 0.8)
        evicted = 0
        
        while self._get_cache_size() > target_size and cache_files:
            _, file_path = cache_files.pop(0)
            try:
                file_path.unlink()
                evicted += 1
            except OSError:
                pass
        
        if evicted > 0:
            with self._stats_lock:
                self.stats.evictions += evicted


class MemoryCache(CacheBackend):
    """In-memory cache implementation."""
    
    def __init__(self, max_items: int = 1000):
        """Initialize memory cache.
        
        Args:
            max_items: Maximum number of items to store
        """
        super().__init__()
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self.max_items = max_items
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self._lock:
            entry = self._cache.get(key)
            
            if not entry:
                with self._stats_lock:
                    self.stats.misses += 1
                return None
            
            # Check expiration
            expires_at = entry.get('expires_at')
            if expires_at and time.time() > expires_at:
                # Expired, delete and return None
                del self._cache[key]
                with self._stats_lock:
                    self.stats.misses += 1
                    self.stats.evictions += 1
                return None
            
            with self._stats_lock:
                self.stats.hits += 1
            return entry.get('value')
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL."""
        with self._lock:
            # Check if we need to evict items
            if len(self._cache) >= self.max_items and key not in self._cache:
                self._evict_lru()
            
            self._cache[key] = {
                'value': value,
                'created_at': time.time(),
                'expires_at': time.time() + ttl if ttl > 0 else None,
                'last_access': time.time()
            }
            
            with self._stats_lock:
                self.stats.sets += 1
    
    def delete(self, key: str):
        """Delete value from cache."""
        with self._lock:
            if key in self._cache:
                self._cache.pop(key)
                with self._stats_lock:
                    self.stats.deletes += 1
    
    def clear(self):
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return self.get(key) is not None
    
    def _evict_lru(self):
        """Evict least recently used item."""
        if not self._cache:
            return
        
        # Find the least recently accessed item
        lru_key = None
        lru_time = float('inf')
        
        for key, entry in self._cache.items():
            last_access = entry.get('last_access', entry.get('created_at', 0))
            if last_access < lru_time:
                lru_time = last_access
                lru_key = key
        
        if lru_key:
            del self._cache[lru_key]
            with self._stats_lock:
                self.stats.evictions += 1


class Cache:
    """High-level cache interface with decorators."""
    
    def __init__(self, backend: Optional[CacheBackend] = None):
        """
        Initialize cache.
        
        Args:
            backend: Cache backend to use (defaults to FileCache)
        """
        self.backend = backend or FileCache()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        return self.backend.get(key)
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache."""
        self.backend.set(key, value, ttl)
    
    def delete(self, key: str):
        """Delete value from cache."""
        self.backend.delete(key)
    
    def clear(self):
        """Clear all cache entries."""
        self.backend.clear()
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        return self.backend.exists(key)
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        return self.backend.get_stats()
    
    def reset_stats(self):
        """Reset cache statistics."""
        self.backend.reset_stats()
    
    def cached(self, key_func: Optional[Callable] = None, ttl: int = 3600):
        """
        Decorator to cache function results.
        
        Args:
            key_func: Function to generate cache key from arguments
            ttl: Time to live in seconds
            
        Usage:
            @cache.cached(ttl=300)
            def expensive_function(arg1, arg2):
                return do_expensive_computation(arg1, arg2)
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    # Default key generation
                    key_parts = [func.__name__]
                    if args:
                        key_parts.extend(str(arg) for arg in args)
                    if kwargs:
                        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                    cache_key = ":".join(key_parts)
                
                # Check cache
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    return cached_value
                
                # Call function and cache result
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl)
                
                return result
            
            return wrapper
        return decorator


# Global cache instance
_cache: Optional[Cache] = None


# Compatibility alias
CacheManager = Cache

def get_cache(backend: Optional[CacheBackend] = None) -> Cache:
    """
    Get or create global cache instance.
    
    Args:
        backend: Optional cache backend
        
    Returns:
        Cache instance
    """
    global _cache
    if _cache is None or backend:
        _cache = Cache(backend)
    return _cache


# Cache key generators for common use cases

def report_list_key(network_code: str, page_size: int = 50) -> str:
    """Generate cache key for report list."""
    return f"reports:list:{network_code}:{page_size}"


def report_metadata_key(report_id: str) -> str:
    """Generate cache key for report metadata."""
    return f"report:metadata:{report_id}"


def dimensions_metrics_key(report_type: str = "HISTORICAL") -> str:
    """Generate cache key for dimensions and metrics."""
    return f"metadata:dims_metrics:{report_type}"


def report_results_key(report_id: str, page: int = 1) -> str:
    """Generate cache key for report results."""
    return f"report:results:{report_id}:page{page}"


# Convenience decorators

def cache_report_list(ttl: int = 300):
    """Cache report list results for 5 minutes."""
    cache = get_cache()
    return cache.cached(
        key_func=lambda self, limit=50: report_list_key(self.client.network_code, limit),
        ttl=ttl
    )


def cache_dimensions_metrics(ttl: int = 3600):
    """Cache dimensions and metrics for 1 hour."""
    cache = get_cache()
    return cache.cached(
        key_func=lambda report_type="HISTORICAL": dimensions_metrics_key(report_type),
        ttl=ttl
    )