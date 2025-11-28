"""
Logging configuration for Google Ad Manager API.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_dir: str = "logs",
    format_string: Optional[str] = None,
    include_console: bool = True,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Setup logging configuration for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Log file name (defaults to gam_api.log)
        log_dir: Directory for log files
        format_string: Custom log format string
        include_console: Whether to include console logging
        max_file_size: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        
    Returns:
        Configured logger instance
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Default format
    if format_string is None:
        format_string = (
            '%(asctime)s - %(name)s - %(levelname)s - '
            '%(filename)s:%(lineno)d - %(message)s'
        )
    
    formatter = logging.Formatter(format_string)
    
    # Create root logger
    logger = logging.getLogger('gam_api')
    logger.setLevel(numeric_level)
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console handler
    if include_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file or log_dir:
        log_dir_path = Path(log_dir)
        log_dir_path.mkdir(parents=True, exist_ok=True)
        
        log_file_path = log_dir_path / (log_file or "gam_api.log")
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file_path,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Prevent propagation to avoid duplicate logs
    logger.propagate = False
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"gam_api.{name}")


class StructuredLogger:
    """Logger that supports structured logging for better observability."""
    
    def __init__(self, name: str):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name
        """
        self.logger = get_logger(name)
    
    def log_api_request(self, method: str, url: str, status_code: Optional[int] = None, 
                       response_time: Optional[float] = None, error: Optional[str] = None):
        """
        Log API request with structured data.
        
        Args:
            method: HTTP method
            url: Request URL
            status_code: Response status code
            response_time: Response time in seconds
            error: Error message if any
        """
        extra = {
            'event': 'api_request',
            'method': method,
            'url': url,
            'status_code': status_code,
            'response_time': response_time
        }
        
        if error:
            self.logger.error(f"API request failed: {method} {url} - {error}", extra=extra)
        elif status_code and status_code >= 400:
            self.logger.warning(f"API request failed: {method} {url} - {status_code}", extra=extra)
        else:
            self.logger.info(f"API request: {method} {url}", extra=extra)
    
    def log_report_lifecycle(self, event: str, report_id: str, **kwargs):
        """
        Log report lifecycle events.
        
        Args:
            event: Event type (created, running, completed, failed, etc.)
            report_id: Report ID
            **kwargs: Additional context
        """
        extra = {
            'event': 'report_lifecycle',
            'report_event': event,
            'report_id': report_id,
            **kwargs
        }
        
        message = f"Report {event}: {report_id}"
        
        if event in ['failed', 'timeout']:
            self.logger.error(message, extra=extra)
        elif event == 'completed':
            self.logger.info(message, extra=extra)
        else:
            self.logger.debug(message, extra=extra)
    
    def log_auth_event(self, event: str, success: bool, error: Optional[str] = None):
        """
        Log authentication events.
        
        Args:
            event: Event type (login, token_refresh, etc.)
            success: Whether the event was successful
            error: Error message if any
        """
        extra = {
            'event': 'auth',
            'auth_event': event,
            'success': success
        }
        
        if success:
            self.logger.info(f"Auth {event} successful", extra=extra)
        else:
            self.logger.error(f"Auth {event} failed: {error}", extra=extra)
    
    def log_cache_event(self, event: str, key: str, hit: Optional[bool] = None):
        """
        Log cache events.
        
        Args:
            event: Event type (get, set, delete, clear)
            key: Cache key
            hit: Whether it was a cache hit (for get events)
        """
        extra = {
            'event': 'cache',
            'cache_event': event,
            'cache_key': key,
            'cache_hit': hit
        }
        
        if event == 'get':
            status = 'hit' if hit else 'miss'
            self.logger.debug(f"Cache {status}: {key}", extra=extra)
        else:
            self.logger.debug(f"Cache {event}: {key}", extra=extra)
    
    def log_function_call(self, func_name: str, args: tuple = (), kwargs: dict = None):
        """
        Log function call with arguments.
        
        Args:
            func_name: Name of the function being called
            args: Positional arguments
            kwargs: Keyword arguments
        """
        kwargs = kwargs or {}
        extra = {
            'event': 'function_call',
            'function': func_name,
            'args': str(args),
            'kwargs': str(kwargs)
        }
        self.logger.debug(f"Calling {func_name}(*{args}, **{kwargs})", extra=extra)


# Global logger instances
_main_logger: Optional[logging.Logger] = None
_structured_loggers = {}


def get_main_logger() -> logging.Logger:
    """Get the main application logger."""
    global _main_logger
    if _main_logger is None:
        _main_logger = setup_logging()
    return _main_logger


def get_structured_logger(name: str) -> StructuredLogger:
    """
    Get or create a structured logger for a module.
    
    Args:
        name: Module name
        
    Returns:
        StructuredLogger instance
    """
    if name not in _structured_loggers:
        _structured_loggers[name] = StructuredLogger(name)
    return _structured_loggers[name]


# Convenience functions for common logging patterns

def log_function_call(func_name: str, args: tuple = (), kwargs: dict = None):
    """Log function call with arguments."""
    logger = get_logger('function_calls')
    kwargs = kwargs or {}
    logger.debug(f"Calling {func_name}(*{args}, **{kwargs})")


def log_performance(operation: str, duration: float, **context):
    """Log performance metrics."""
    logger = get_structured_logger('performance')
    extra = {
        'event': 'performance',
        'operation': operation,
        'duration': duration,
        **context
    }
    logger.logger.info(f"Performance: {operation} took {duration:.3f}s", extra=extra)


# Compatibility aliases
configure_logging = setup_logging
performance_logger = log_performance