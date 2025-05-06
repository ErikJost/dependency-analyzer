#!/usr/bin/env python3
"""
Unit tests for error_handler module.

This module tests the error handling functionality.
"""

import pytest
from error_handler import create_error_response, handle_exception, get_http_status_for_error

class TestErrorHandler:
    """Tests for the error_handler module"""

    def test_create_error_response_basic(self):
        """Test creating a basic error response"""
        error_code = "not_found"
        error_message = "Resource not found"
        
        response = create_error_response(error_code, error_message)
        
        assert response is not None
        assert response["status"] == "error"
        assert "error" in response
        assert response["error"]["code"] == error_code
        assert response["error"]["message"] == error_message
        assert "timestamp" in response
        assert "correlation_id" in response
        assert "error_id" in response["error"]

    def test_create_error_response_with_details(self):
        """Test creating an error response with details"""
        error_code = "validation_error"
        error_message = "Invalid parameters"
        details = {"field": "name", "issue": "required"}
        
        response = create_error_response(error_code, error_message, details)
        
        assert response is not None
        assert response["status"] == "error"
        assert response["error"]["code"] == error_code
        assert response["error"]["message"] == error_message
        assert "details" in response["error"]
        assert response["error"]["details"] == details

    def test_create_error_response_with_request_id(self):
        """Test creating an error response with a request ID"""
        error_code = "server_error"
        error_message = "Internal server error"
        request_id = "test-request-123"
        
        response = create_error_response(error_code, error_message, request_id=request_id)
        
        assert response is not None
        assert response["status"] == "error"
        assert response["error"]["code"] == error_code
        assert response["error"]["message"] == error_message
        assert response["request_id"] == request_id

    def test_handle_exception(self):
        """Test handling an exception"""
        exception = ValueError("Test exception")
        context = {"location": "test", "operation": "unit_test"}
        
        response = handle_exception(exception, context)
        
        assert response is not None
        assert response["status"] == "error"
        assert response["error"]["code"] == "server_error"
        assert "Test exception" in response["error"]["message"]
        assert "details" in response["error"]
        assert response["error"]["details"]["type"] == "ValueError"
        assert "error_id" in response["error"]["details"]

    def test_get_http_status_for_known_error(self):
        """Test getting HTTP status code for known error codes"""
        assert get_http_status_for_error("not_found") == 404
        assert get_http_status_for_error("validation_error") == 400
        assert get_http_status_for_error("server_error") == 500
        assert get_http_status_for_error("forbidden") == 403
        assert get_http_status_for_error("unauthorized") == 401

    def test_get_http_status_for_unknown_error(self):
        """Test getting HTTP status code for unknown error codes"""
        assert get_http_status_for_error("unknown_code") == 500  # Should default to 500 