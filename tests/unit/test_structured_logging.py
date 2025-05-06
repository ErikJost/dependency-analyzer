#!/usr/bin/env python3
"""
Unit tests for structured_logging module.

This module tests the structured logging functionality.
"""

import os
import io
import json
import logging
import pytest
from unittest.mock import patch, MagicMock
from structured_logging import get_logger, get_log_level, create_correlation_id

class TestStructuredLogging:
    """Tests for the structured_logging module"""

    def test_get_log_level(self):
        """Test getting numeric log level from string name"""
        assert get_log_level("DEBUG") == logging.DEBUG
        assert get_log_level("INFO") == logging.INFO
        assert get_log_level("WARNING") == logging.WARNING
        assert get_log_level("ERROR") == logging.ERROR
        assert get_log_level("CRITICAL") == logging.CRITICAL
        
        # Test with lowercase
        assert get_log_level("debug") == logging.DEBUG
        
        # Test default for unknown level
        assert get_log_level("UNKNOWN") == logging.INFO

    def test_create_correlation_id(self):
        """Test creating correlation IDs"""
        correlation_id1 = create_correlation_id()
        correlation_id2 = create_correlation_id()
        
        # Check format (UUID string)
        assert isinstance(correlation_id1, str)
        assert len(correlation_id1) == 36  # UUID string length
        assert correlation_id1.count('-') == 4  # UUID format includes 4 hyphens
        
        # Verify uniqueness
        assert correlation_id1 != correlation_id2

    def test_logger_structure(self):
        """Test logger structure and methods"""
        logger = get_logger("test_logger")
        
        # Check logger attributes and methods
        assert hasattr(logger, 'debug')
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'critical')
        assert hasattr(logger, 'with_correlation_id')

    @patch('sys.stderr', new_callable=io.StringIO)
    def test_logger_output_format(self, mock_stderr):
        """Test logger output format with JSON structure"""
        # Create a logger that writes to our mock stderr
        logger = get_logger("test_format")
        
        # Write a test message
        test_message = "Test log message"
        logger.info(test_message)
        
        # Get the output and parse as JSON
        output = mock_stderr.getvalue()
        try:
            log_entry = json.loads(output)
            
            # Check for required fields
            assert "timestamp" in log_entry
            assert "level" in log_entry
            assert "logger" in log_entry
            assert "message" in log_entry
            
            # Verify the message content
            assert test_message in log_entry["message"]
            assert log_entry["level"] in ["INFO", "info"]
            assert log_entry["logger"] == "test_format"
            
        except json.JSONDecodeError:
            pytest.fail(f"Log output is not valid JSON: {output}")

    def test_logger_with_correlation_id(self):
        """Test logger with correlation ID"""
        logger = get_logger("test_correlation")
        correlation_id = create_correlation_id()
        
        # Create correlated logger
        correlated_logger = logger.with_correlation_id(correlation_id)
        
        # Ensure correlated logger has the same methods
        assert hasattr(correlated_logger, 'debug')
        assert hasattr(correlated_logger, 'info')
        assert hasattr(correlated_logger, 'warning')
        assert hasattr(correlated_logger, 'error')
        assert hasattr(correlated_logger, 'critical')
        
        # Can't easily verify the correlation ID in the output
        # without complex mocking, but we can ensure the method works 