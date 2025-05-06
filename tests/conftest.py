#!/usr/bin/env python3
"""
Pytest configuration and fixtures for the MCP server tests.

This module contains shared fixtures and configuration for all tests.
"""

import os
import json
import pytest
import tempfile
from typing import Dict, Any, List

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def mock_project_metadata():
    """Create mock project metadata for testing"""
    return {
        "id": "test-project",
        "name": "Test Project",
        "source": "https://github.com/user/test-project.git",
        "branch": "main",
        "path": "/path/to/test-project",
        "created_at": "2023-07-01T12:00:00Z"
    }

@pytest.fixture
def mock_dependency_graph():
    """Create a mock dependency graph for testing"""
    return {
        "src/components/Button.tsx": {
            "imports": [
                "src/styles/common.css",
                "src/utils/theme.ts"
            ]
        },
        "src/styles/common.css": {
            "imports": []
        },
        "src/utils/theme.ts": {
            "imports": [
                "src/constants/colors.ts"
            ]
        },
        "src/constants/colors.ts": {
            "imports": []
        },
        "src/pages/Home.tsx": {
            "imports": [
                "src/components/Button.tsx",
                "src/layouts/MainLayout.tsx"
            ]
        },
        "src/layouts/MainLayout.tsx": {
            "imports": [
                "src/components/Header.tsx",
                "src/components/Footer.tsx"
            ]
        },
        "src/components/Header.tsx": {
            "imports": [
                "src/utils/theme.ts"
            ]
        },
        "src/components/Footer.tsx": {
            "imports": [
                "src/utils/theme.ts"
            ]
        }
    }

@pytest.fixture
def mock_circular_dependency_graph():
    """Create a mock dependency graph with circular dependencies for testing"""
    return {
        "src/components/A.tsx": {
            "imports": [
                "src/components/B.tsx"
            ]
        },
        "src/components/B.tsx": {
            "imports": [
                "src/components/C.tsx"
            ]
        },
        "src/components/C.tsx": {
            "imports": [
                "src/components/A.tsx"
            ]
        },
        "src/utils/X.ts": {
            "imports": [
                "src/utils/Y.ts"
            ]
        },
        "src/utils/Y.ts": {
            "imports": [
                "src/utils/X.ts"
            ]
        }
    }

@pytest.fixture
def mock_project_structure():
    """Create a mock project structure for testing"""
    return {
        "type": "directory",
        "name": "test-project",
        "children": [
            {
                "type": "directory",
                "name": "src",
                "children": [
                    {
                        "type": "directory",
                        "name": "components",
                        "children": [
                            {
                                "type": "file",
                                "name": "Button.tsx",
                                "path": "src/components/Button.tsx",
                                "extension": "tsx"
                            },
                            {
                                "type": "file",
                                "name": "Header.tsx",
                                "path": "src/components/Header.tsx",
                                "extension": "tsx"
                            },
                            {
                                "type": "file",
                                "name": "Footer.tsx",
                                "path": "src/components/Footer.tsx",
                                "extension": "tsx"
                            }
                        ]
                    },
                    {
                        "type": "directory",
                        "name": "pages",
                        "children": [
                            {
                                "type": "file",
                                "name": "Home.tsx",
                                "path": "src/pages/Home.tsx",
                                "extension": "tsx"
                            }
                        ]
                    },
                    {
                        "type": "directory",
                        "name": "utils",
                        "children": [
                            {
                                "type": "file",
                                "name": "theme.ts",
                                "path": "src/utils/theme.ts",
                                "extension": "ts"
                            }
                        ]
                    }
                ]
            },
            {
                "type": "file",
                "name": "package.json",
                "path": "package.json",
                "extension": "json"
            }
        ]
    } 