#!/usr/bin/env python3
"""
Unit tests for validation module.

This module tests the validation functionality for both tools and resources.
"""

import pytest
from validation import validate_tool_parameters, validate_resource_uri

class TestValidation:
    """Tests for the validation module"""

    def test_validate_valid_add_project_params(self):
        """Test validation with valid add_project parameters"""
        tool_name = "add_project"
        params = {
            "name": "test-project",
            "source": "https://github.com/user/repo.git"
        }

        is_valid, error_details = validate_tool_parameters(tool_name, params)
        
        assert is_valid is True
        assert error_details is None

    def test_validate_invalid_add_project_params(self):
        """Test validation with invalid add_project parameters (missing source)"""
        tool_name = "add_project"
        params = {
            "name": "test-project"
        }

        is_valid, error_details = validate_tool_parameters(tool_name, params)
        
        assert is_valid is False
        assert error_details is not None
        assert error_details["code"] == "validation_error"
        assert "source" in error_details["message"].lower() or "source" in str(error_details["details"]).lower()

    def test_validate_unknown_tool(self):
        """Test validation with an unknown tool"""
        tool_name = "nonexistent_tool"
        params = {}

        is_valid, error_details = validate_tool_parameters(tool_name, params)
        
        # Unknown tools are considered valid as there's no schema to validate against
        assert is_valid is True
        assert error_details is None

    def test_validate_valid_resource_uri(self):
        """Test validation with a valid resource URI"""
        resource_uri = "project://test-project/structure"

        is_valid, error_details = validate_resource_uri(resource_uri)
        
        assert is_valid is True
        assert error_details is None

    def test_validate_unsupported_resource_uri(self):
        """Test validation with an unsupported resource URI scheme"""
        resource_uri = "unsupported://test"

        is_valid, error_details = validate_resource_uri(resource_uri)
        
        assert is_valid is False
        assert error_details is not None
        assert error_details["code"] == "invalid_resource_uri"
        assert "unsupported" in error_details["message"].lower() or "unsupported" in str(error_details["details"]).lower()

    def test_validate_invalid_project_resource_uri(self):
        """Test validation with an invalid project URI (no resource type)"""
        resource_uri = "project://test-project"

        is_valid, error_details = validate_resource_uri(resource_uri)
        
        assert is_valid is False
        assert error_details is not None
        assert error_details["code"] == "invalid_resource_uri"

    def test_validate_invalid_resource_type(self):
        """Test validation with an invalid resource type"""
        resource_uri = "project://test-project/invalid-type"

        is_valid, error_details = validate_resource_uri(resource_uri)
        
        assert is_valid is False
        assert error_details is not None
        assert error_details["code"] == "invalid_resource_uri"
        assert "invalid" in error_details["message"].lower() or "invalid" in str(error_details["details"]).lower()

    def test_validate_file_dependency_uri(self):
        """Test validation with a valid file dependency URI"""
        resource_uri = "project://test-project/file/src/components/Button/dependencies"

        is_valid, error_details = validate_resource_uri(resource_uri)
        
        assert is_valid is True
        assert error_details is None

    def test_validate_invalid_file_dependency_uri(self):
        """Test validation with an invalid file dependency URI (missing dependencies)"""
        resource_uri = "project://test-project/file/src/components/Button"

        is_valid, error_details = validate_resource_uri(resource_uri)
        
        assert is_valid is False
        assert error_details is not None
        assert error_details["code"] == "invalid_resource_uri" 