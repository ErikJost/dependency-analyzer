#!/usr/bin/env python3
"""
Structured logging configuration for MCP API.

This module provides structured JSON logging for the MCP API,
with consistent log formatting and correlation IDs.
"""

import os
import sys
import json
import uuid
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List, Union

try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False

# Import the configuration module
try:
    from config import config, initialize_config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

# Default log level - first try config, then environment, then fallback to INFO
def get_default_log_level():
    if CONFIG_AVAILABLE:
        return config.get("logging.level", "INFO").upper()
    return os.environ.get("LOG_LEVEL", "INFO").upper()

DEFAULT_LOG_LEVEL = get_default_log_level()
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

def get_log_level(level_name: str = None) -> int:
    """Get the numeric log level from a string name."""
    level_name = level_name or DEFAULT_LOG_LEVEL
    return LOG_LEVELS.get(level_name.upper(), logging.INFO)

def get_log_format():
    """Get the log format (json or text) from config."""
    if CONFIG_AVAILABLE:
        return config.get("logging.format", "json").lower()
    return "json"  # Default to JSON if config is not available

def setup_logging(name: str, level: str = None, output_stream=sys.stderr):
    """
    Set up structured logging.
    
    Args:
        name: The logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        output_stream: Where to send logs (default: stderr)
        
    Returns:
        A configured logger
    """
    log_level = get_log_level(level)
    log_format = get_log_format()
    
    if STRUCTLOG_AVAILABLE:
        # Use structlog for structured logging
        processors = [
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
        ]
        
        # Add the renderer based on format preference
        if log_format == "json":
            processors.append(structlog.processors.JSONRenderer())
        else:
            processors.append(structlog.dev.ConsoleRenderer())
        
        structlog.configure(
            processors=processors,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        # Set up the underlying stdlib logger
        handler = logging.StreamHandler(output_stream)
        handler.setFormatter(logging.Formatter('%(message)s'))
        
        stdlib_logger = logging.getLogger(name)
        stdlib_logger.setLevel(log_level)
        stdlib_logger.addHandler(handler)
        stdlib_logger.propagate = False
        
        # Create and return a structured logger
        logger = structlog.get_logger(name)
        return logger
    else:
        # Fall back to standard logging with JSON formatting
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_record = {
                    "timestamp": datetime.now().isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage()
                }
                
                if hasattr(record, 'correlation_id'):
                    log_record['correlation_id'] = record.correlation_id
                
                if record.exc_info:
                    log_record['exception'] = self.formatException(record.exc_info)
                
                if hasattr(record, 'data') and record.data:
                    log_record.update(record.data)
                
                return json.dumps(log_record)
        
        class TextFormatter(logging.Formatter):
            def format(self, record):
                parts = []
                parts.append(f"{datetime.now().isoformat()} [{record.levelname}] {record.name}:")
                parts.append(record.getMessage())
                
                if hasattr(record, 'correlation_id'):
                    parts.append(f"correlation_id: {record.correlation_id}")
                
                if record.exc_info:
                    parts.append(f"exception: {self.formatException(record.exc_info)}")
                
                if hasattr(record, 'data') and record.data:
                    for key, value in record.data.items():
                        parts.append(f"{key}: {value}")
                
                return " | ".join(parts)
        
        # Create a logger with the appropriate formatting
        logger = logging.getLogger(name)
        logger.setLevel(log_level)
        
        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Add a new handler with JSON or text formatting based on config
        handler = logging.StreamHandler(output_stream)
        
        if log_format == "json":
            handler.setFormatter(JsonFormatter())
        else:
            handler.setFormatter(TextFormatter())
            
        logger.addHandler(handler)
        logger.propagate = False
        
        # Add methods to attach correlation IDs and data
        def log_with_context(original_method, correlation_id=None, **data):
            def wrapped_method(msg, *args, **kwargs):
                extra = kwargs.get('extra', {})
                if correlation_id:
                    extra['correlation_id'] = correlation_id
                if data:
                    extra['data'] = data
                kwargs['extra'] = extra
                return original_method(msg, *args, **kwargs)
            return wrapped_method
        
        # Enhance the logger with a with_correlation_id method
        def with_correlation_id(self, correlation_id):
            new_logger = logging.getLogger(f"{name}.{correlation_id[:8]}")
            new_logger.setLevel(logger.level)
            
            # Copy handlers
            for handler in logger.handlers:
                new_logger.addHandler(handler)
            
            # Wrap log methods
            new_logger.debug = log_with_context(new_logger.debug, correlation_id)
            new_logger.info = log_with_context(new_logger.info, correlation_id)
            new_logger.warning = log_with_context(new_logger.warning, correlation_id)
            new_logger.error = log_with_context(new_logger.error, correlation_id)
            new_logger.critical = log_with_context(new_logger.critical, correlation_id)
            
            return new_logger
        
        # Add with_correlation_id method to logger
        logger.with_correlation_id = with_correlation_id.__get__(logger)
        
        return logger

def get_logger(name: str, level: str = None):
    """
    Get a configured logger.
    
    Args:
        name: The logger name
        level: Optional log level override
        
    Returns:
        A configured logger
    """
    return setup_logging(name, level)

def create_correlation_id() -> str:
    """Generate a unique correlation ID for request tracking."""
    return str(uuid.uuid4())

# Initialize config if available
if CONFIG_AVAILABLE:
    initialize_config()

# Default application logger
app_logger = get_logger("mcp_api") 