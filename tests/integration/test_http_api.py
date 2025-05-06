#!/usr/bin/env python3
"""
Integration tests for HTTP API endpoints.

This module tests the interaction between API endpoints and the core functionality.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

# Import the server module - adjust import path as needed
import server_mcp
from server_mcp import app

@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    with app.test_client() as client:
        yield client

class TestHttpApi:
    """Tests for the HTTP API endpoints"""

    def test_health_endpoint(self, client):
        """Test the health endpoint returns 200 OK"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'
        assert 'version' in data

    def test_list_projects_endpoint(self, client, mocker):
        """Test the list_projects endpoint"""
        # Mock the function that lists projects
        mock_list_projects = mocker.patch('server_mcp.list_projects')
        mock_list_projects.return_value = {
            'status': 'success',
            'projects': [
                {
                    'id': 'test-project',
                    'name': 'Test Project',
                    'source': 'https://github.com/user/test-project.git'
                }
            ]
        }

        # Make the request
        response = client.post('/api/tools/list_projects', json={})
        
        # Assert response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'projects' in data
        assert len(data['projects']) == 1
        assert data['projects'][0]['id'] == 'test-project'
        
        # Verify the mock was called correctly
        mock_list_projects.assert_called_once_with({})

    def test_add_project_endpoint(self, client, mocker):
        """Test the add_project endpoint"""
        # Mock the function that adds projects
        mock_add_project = mocker.patch('server_mcp.add_project')
        mock_add_project.return_value = {
            'status': 'success',
            'project': {
                'id': 'new-project',
                'name': 'New Project',
                'source': 'https://github.com/user/new-project.git'
            }
        }

        # Request parameters
        params = {
            'name': 'New Project',
            'source': 'https://github.com/user/new-project.git'
        }

        # Make the request
        response = client.post('/api/tools/add_project', json=params)
        
        # Assert response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'project' in data
        assert data['project']['id'] == 'new-project'
        
        # Verify the mock was called correctly
        mock_add_project.assert_called_once_with(params)

    def test_analyze_dependencies_endpoint(self, client, mocker):
        """Test the analyze_dependencies endpoint"""
        # Mock the function that analyzes dependencies
        mock_analyze = mocker.patch('server_mcp.analyze_dependencies')
        mock_analyze.return_value = {
            'status': 'success',
            'analysis_id': 'analysis-123',
            'project_id': 'test-project',
            'files_analyzed': 25,
            'dependencies_found': 42
        }

        # Request parameters
        params = {
            'project_id': 'test-project'
        }

        # Make the request
        response = client.post('/api/tools/analyze_dependencies', json=params)
        
        # Assert response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['analysis_id'] == 'analysis-123'
        assert data['files_analyzed'] == 25
        
        # Verify the mock was called correctly
        mock_analyze.assert_called_once_with(params)

    def test_get_dependency_graph_endpoint(self, client, mocker, mock_dependency_graph):
        """Test the get_dependency_graph endpoint"""
        # Mock the function that gets dependency graphs
        mock_get_graph = mocker.patch('server_mcp.get_dependency_graph')
        mock_get_graph.return_value = {
            'status': 'success',
            'project_id': 'test-project',
            'graph': mock_dependency_graph
        }

        # Request parameters
        params = {
            'project_id': 'test-project'
        }

        # Make the request
        response = client.post('/api/tools/get_dependency_graph', json=params)
        
        # Assert response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['project_id'] == 'test-project'
        assert 'graph' in data
        
        # Verify the mock was called correctly
        mock_get_graph.assert_called_once_with(params)

    def test_find_orphaned_files_endpoint(self, client, mocker):
        """Test the find_orphaned_files endpoint"""
        # Mock the function that finds orphaned files
        mock_find_orphaned = mocker.patch('server_mcp.find_orphaned_files')
        mock_find_orphaned.return_value = {
            'status': 'success',
            'project_id': 'test-project',
            'orphaned_files': [
                'src/unused/Component.tsx',
                'src/utils/deprecated.ts'
            ]
        }

        # Request parameters
        params = {
            'project_id': 'test-project'
        }

        # Make the request
        response = client.post('/api/tools/find_orphaned_files', json=params)
        
        # Assert response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['project_id'] == 'test-project'
        assert 'orphaned_files' in data
        assert len(data['orphaned_files']) == 2
        
        # Verify the mock was called correctly
        mock_find_orphaned.assert_called_once_with(params)

    def test_invalid_tool_endpoint(self, client):
        """Test calling a non-existent tool endpoint"""
        response = client.post('/api/tools/nonexistent_tool', json={})
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'error' in data
        assert data['error']['code'] == 'not_found'

    def test_validation_error(self, client):
        """Test validation error handling"""
        # Missing required parameters for add_project
        params = {
            'name': 'New Project'
            # Missing 'source'
        }

        response = client.post('/api/tools/add_project', json=params)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'error' in data
        assert data['error']['code'] == 'validation_error' 