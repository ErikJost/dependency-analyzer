#!/usr/bin/env python3
"""
Unit tests for schemas module.

This module tests the JSON schema definitions used for validation.
"""

import pytest
import jsonschema
from schemas import (
    TOOL_SCHEMAS, 
    LIST_PROJECTS_SCHEMA,
    ADD_PROJECT_SCHEMA,
    ANALYZE_DEPENDENCIES_SCHEMA,
    GET_DEPENDENCY_GRAPH_SCHEMA,
    FIND_ORPHANED_FILES_SCHEMA,
    CHECK_CIRCULAR_DEPENDENCIES_SCHEMA,
    get_schema_for_tool
)

class TestSchemas:
    """Tests for the schemas module"""

    def test_schema_structure(self):
        """Test that all schemas have the required structure"""
        for name, schema in TOOL_SCHEMAS.items():
            assert "type" in schema
            assert schema["type"] == "object"
            assert "properties" in schema
            assert isinstance(schema["properties"], dict)

    def test_get_schema_for_tool(self):
        """Test the get_schema_for_tool function"""
        # Test getting schemas for known tools
        assert get_schema_for_tool("list_projects") == LIST_PROJECTS_SCHEMA
        assert get_schema_for_tool("add_project") == ADD_PROJECT_SCHEMA
        assert get_schema_for_tool("analyze_dependencies") == ANALYZE_DEPENDENCIES_SCHEMA
        assert get_schema_for_tool("get_dependency_graph") == GET_DEPENDENCY_GRAPH_SCHEMA
        assert get_schema_for_tool("find_orphaned_files") == FIND_ORPHANED_FILES_SCHEMA
        assert get_schema_for_tool("check_circular_dependencies") == CHECK_CIRCULAR_DEPENDENCIES_SCHEMA
        
        # Test getting schema for unknown tool
        assert get_schema_for_tool("unknown_tool") is None

    def test_list_projects_schema(self):
        """Test the list_projects schema"""
        schema = LIST_PROJECTS_SCHEMA
        
        # Valid empty parameters (no params needed)
        jsonschema.validate({}, schema)
        
        # Invalid with extra parameters
        with pytest.raises(jsonschema.exceptions.ValidationError):
            jsonschema.validate({"extra": "value"}, schema)

    def test_add_project_schema(self):
        """Test the add_project schema"""
        schema = ADD_PROJECT_SCHEMA
        
        # Valid parameters
        valid_params = {
            "name": "test-project",
            "source": "https://github.com/user/repo.git"
        }
        jsonschema.validate(valid_params, schema)
        
        # Valid with optional branch
        valid_with_branch = {
            "name": "test-project",
            "source": "https://github.com/user/repo.git",
            "branch": "main"
        }
        jsonschema.validate(valid_with_branch, schema)
        
        # Invalid missing required name
        invalid_missing_name = {
            "source": "https://github.com/user/repo.git"
        }
        with pytest.raises(jsonschema.exceptions.ValidationError):
            jsonschema.validate(invalid_missing_name, schema)
        
        # Invalid missing required source
        invalid_missing_source = {
            "name": "test-project"
        }
        with pytest.raises(jsonschema.exceptions.ValidationError):
            jsonschema.validate(invalid_missing_source, schema)
        
        # Invalid empty name
        invalid_empty_name = {
            "name": "",
            "source": "https://github.com/user/repo.git"
        }
        with pytest.raises(jsonschema.exceptions.ValidationError):
            jsonschema.validate(invalid_empty_name, schema)
        
        # Invalid with extra parameter
        invalid_extra_param = {
            "name": "test-project",
            "source": "https://github.com/user/repo.git",
            "extra": "value"
        }
        with pytest.raises(jsonschema.exceptions.ValidationError):
            jsonschema.validate(invalid_extra_param, schema)

    def test_analyze_dependencies_schema(self):
        """Test the analyze_dependencies schema"""
        schema = ANALYZE_DEPENDENCIES_SCHEMA
        
        # Valid with just project_id
        valid_params = {
            "project_id": "test-project"
        }
        jsonschema.validate(valid_params, schema)
        
        # Valid with options
        valid_with_options = {
            "project_id": "test-project",
            "options": {
                "exclude": ["node_modules", "dist"]
            }
        }
        jsonschema.validate(valid_with_options, schema)
        
        # Invalid missing required project_id
        invalid_missing_project_id = {
            "options": {
                "exclude": ["node_modules"]
            }
        }
        with pytest.raises(jsonschema.exceptions.ValidationError):
            jsonschema.validate(invalid_missing_project_id, schema)
        
        # Invalid options type
        invalid_options_type = {
            "project_id": "test-project",
            "options": "not an object"
        }
        with pytest.raises(jsonschema.exceptions.ValidationError):
            jsonschema.validate(invalid_options_type, schema)
        
        # Invalid exclude type
        invalid_exclude_type = {
            "project_id": "test-project",
            "options": {
                "exclude": "not an array"
            }
        }
        with pytest.raises(jsonschema.exceptions.ValidationError):
            jsonschema.validate(invalid_exclude_type, schema)

    def test_get_dependency_graph_schema(self):
        """Test the get_dependency_graph schema"""
        schema = GET_DEPENDENCY_GRAPH_SCHEMA
        
        # Valid with just project_id
        valid_params = {
            "project_id": "test-project"
        }
        jsonschema.validate(valid_params, schema)
        
        # Valid with format
        valid_with_format = {
            "project_id": "test-project",
            "format": "d3"
        }
        jsonschema.validate(valid_with_format, schema)
        
        # Invalid format value
        invalid_format = {
            "project_id": "test-project",
            "format": "invalid-format"
        }
        with pytest.raises(jsonschema.exceptions.ValidationError):
            jsonschema.validate(invalid_format, schema) 